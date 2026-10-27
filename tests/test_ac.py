import json
import socket
import struct
import threading
import time

import numpy as np
import pytest

from simlab import ac_files
from simlab.ac_recorder import Recorder
from simlab.ac_telemetry import (DISMISS, HANDSHAKE, SIZE, SUBSCRIBE_UPDATE, GameClock, pack, pack_handshake,
                                 parse, parse_handshake, plausible)
from simlab.records import Sample, check_stamps, read_jsonl

LAP_MS, STEP_MS = 10_000, 5


def frames(start_ms=7_000, end_ms=35_000):
    """A car going round a 10-second lap, one datagram every 5 ms of game time."""
    last = 0
    for t in range(start_ms, end_ms, STEP_MS):
        lap, lap_time = divmod(t, LAP_MS)
        if lap_time == 0 and lap:
            last = LAP_MS
        yield {"kmh": 150.0 + 50 * np.sin(t / 1000), "gas": 0.8, "brake": 0.0, "clutch": 1.0, "rpm": 6000.0,
               "steer_deg": 10.0, "gear": 4, "lap": lap, "lap_time_ms": lap_time, "last_lap_ms": last,
               "pos": lap_time / LAP_MS, "x": 100.0 * np.cos(t / 1591), "z": 100.0 * np.sin(t / 1591),
               "acc_lat_g": 1.2, "acc_long_g": 0.1, "load_fl_n": 3000.0}


def samples(values):
    clock, out = GameClock(), []
    for i, v in enumerate(values):
        v = parse(pack(v))
        t = clock.update(v["lap_time_ms"], v["lap"], v["last_lap_ms"])
        if t is not None:
            out.append(Sample(t, 1000.0 + i * 0.004, v))
    return out


def test_a_datagram_round_trips():
    v = next(frames())
    raw = pack(v)
    assert len(raw) == SIZE == 328
    back = parse(raw)
    for k in ("kmh", "rpm", "steer_deg", "pos", "load_fl_n", "acc_lat_g"):
        assert back[k] == pytest.approx(v[k], rel=1e-6)
    assert back["gear"] == 4 and back["lap"] == 0
    assert plausible(back) == []


def test_the_handshake_cuts_at_the_percent_sign():
    raw = pack_handshake("ks_porsche_cayman_gt4_clubsport", "ks_nurburgring", "layout_gp_a")
    assert parse_handshake(raw) == ("ks_porsche_cayman_gt4_clubsport", "ks_nurburgring", "layout_gp_a")


def test_the_game_clock_runs_across_the_line_and_ignores_pauses_and_restarts():
    c = GameClock()
    assert c.update(9_990, 0, 0) == 0.0
    assert c.update(9_995, 0, 0) == pytest.approx(0.005)
    assert c.update(9_995, 0, 0) is None                        # paused: same frame again
    assert c.update(3, 1, 9_998) == pytest.approx(0.011)        # 3 ms left of the lap + 3 ms
    assert c.update(0, 0, 0) is None                            # Esc -> Restart: no step back


def test_the_grid_is_100_hz_with_the_columns_of_our_files():
    g = ac_files.to_grid(samples(frames()))
    assert np.allclose(np.diff(g["t_s"]), 0.01)
    assert list(g) == list(dict.fromkeys(g)) and set(ac_files.COLUMNS) <= set(g)
    assert ac_files.csv_text(g).splitlines()[0].split(",") == ac_files.COLUMNS
    assert len(ac_files.COLUMNS) == 48


def test_only_laps_seen_from_line_to_line_are_complete():
    laps = ac_files.laps(samples(frames()))
    assert [(x["n"], x["ms"], x["complete"]) for x in laps] == [
        (1, 10_000, False), (2, 10_000, True), (3, 10_000, True), (4, None, False)]
    assert [x["best"] for x in laps] == [False, True, False, False]


def test_the_out_lap_after_a_restart_is_not_complete():
    restart = [dict(v, in_pit=1) for v in frames(0, 2_000)]   # rolling out of the pits
    out = ac_files.laps(samples(list(frames(7_000, 12_000)) + restart))
    assert out[-1]["n"] == 1 and out[-1]["complete"] is False


class FakeGame:
    """Answers the handshake like AC, then sends the frames."""

    def __init__(self, values):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.values = list(values)
        self.done = threading.Event()
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self):
        while True:
            msg, addr = self.sock.recvfrom(64)
            op = struct.unpack("<iii", msg)[2]
            if op == HANDSHAKE:
                self.sock.sendto(pack_handshake("car", "track", "layout"), addr)
            elif op == SUBSCRIBE_UPDATE:
                for i, v in enumerate(self.values):
                    self.sock.sendto(pack(v), addr)
                    if i % 5 == 0:
                        time.sleep(0.001)   # about as fast as the game; faster overflows the buffer
                self.done.set()
            elif op == DISMISS:
                return


def test_the_recorder_writes_files_from_the_line(tmp_path):
    game = FakeGame(frames())
    rec = Recorder("127.0.0.1", game.port, tmp_path)
    rec.start("T01", "test")
    threading.Thread(target=rec.run, daemon=True).start()
    assert game.done.wait(20)
    written = -1
    while rec.state()["written"] != written:     # let the recorder catch up
        written = rec.state()["written"]
        time.sleep(0.3)
    rec.stop()
    rec.shutdown()

    jsonl = list(tmp_path.glob("T01/*/ac_*.jsonl"))
    assert len(jsonl) == 1
    recorded = list(read_jsonl(jsonl[0]))
    assert check_stamps(recorded) == []
    assert recorded[0].values["lap"] == 1 and recorded[0].values["lap_time_ms"] == 0   # opened at the line
    laps = json.loads(jsonl[0].with_suffix("").with_suffix(".laps.json").read_text())["laps"]
    assert [(x["n"], x["complete"]) for x in laps] == [(2, True), (3, True), (4, False)]
    meta = json.loads(jsonl[0].with_suffix(".json").read_text())
    assert meta["driver"] == "T01" and meta["track"] == "track"
    assert jsonl[0].with_suffix("").with_suffix(".100hz.csv").exists()


def test_a_name_is_not_a_driver_code():
    with pytest.raises(ValueError):
        Recorder().start("Max Mustermann")
