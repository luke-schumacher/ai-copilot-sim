"""
Turn an Assetto Corsa recording into the files you got from our rig: a 100 Hz CSV and a
lap summary.

The recording (`.jsonl`, the format of `simlab.records`) holds every datagram as it
arrived, with two clocks: `source_t` is the game's own time, `receive_t` this machine's.
The CSV puts it on a fixed grid of **game time**, one row every 10 ms:

- AC sends one datagram per rendered frame, so the rate changes all the time. On a
  fixed grid two laps of the same length have the same number of rows.
- `hole_ms` is the gap between the two datagrams a row was interpolated from. Normally
  3 to 12 ms; above 50 ms the game or the machine stalled.
- Paused time is dropped, because the game's clock does not move.

The columns and their order are the same as the first 48 columns of the files from
27 October, so code written for those files works on your own recordings.

    python -m simlab.ac_files recordings/S01/2026-11-02/ac_20261102-141500.jsonl
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np

from simlab.ac_telemetry import WHEEL_COLUMNS, WHEELS
from simlab.records import Sample, read_jsonl

HZ = 100.0
#: Above this, in g, the three accelerations together count as an impact (a crash or a
#: hard kerb strike). Do not compare lap times of laps with an impact.
IMPACT_G = 3.0

CONTINUOUS = ["kmh", "gas", "brake", "clutch", "steer_deg", "rpm"]
HELD = ["gear", "lap", "limiter", "abs_active", "tc_active", "in_pit"]
WHEEL_NAMES = [p.format(w=w) for p in WHEEL_COLUMNS.values() for w in WHEELS]
COLUMNS = (["t_s", "recv_monotonic_s", "hole_ms", "lap", "lap_time_s", "pos", "kmh", "gas", "brake",
            "clutch", "steer_deg", "gear", "rpm", "limiter", "acc_lat_g", "acc_long_g", "acc_vert_g",
            "x", "y", "z", "abs_active", "tc_active", "in_pit", "cg_height_m"] + WHEEL_NAMES)
_FORMAT = {"t_s": "%.3f", "recv_monotonic_s": "%.4f", "lap_time_s": "%.3f", "hole_ms": "%.1f",
           "pos": "%.6f", "x": "%.2f", "y": "%.2f", "z": "%.2f"}


def to_grid(samples: List[Sample], hz: float = HZ) -> Dict[str, np.ndarray]:
    """The recording on a fixed grid of game time. Empty if it has fewer than 2 samples."""
    if len(samples) < 2:
        return {}
    ts = np.array([s.source_t for s in samples])
    col = lambda k: np.array([s.values[k] for s in samples], dtype=float)  # noqa: E731
    t = np.arange(np.ceil(ts[0] * hz) / hz, ts[-1] + 1e-9, 1.0 / hz)
    nxt = np.clip(np.searchsorted(ts, t, side="left"), 0, len(ts) - 1)
    prev = np.clip(np.searchsorted(ts, t, side="right") - 1, 0, len(ts) - 1)

    out: Dict[str, np.ndarray] = {"t_s": t - ts[0]}
    out["recv_monotonic_s"] = np.interp(t, ts, [s.receive_t for s in samples])
    out["hole_ms"] = (ts[nxt] - ts[prev]) * 1000.0
    lap_start = ts - col("lap_time_ms") / 1000.0
    out["lap_time_s"] = t - lap_start[prev]
    # The position wraps at the line. Interpolated naively, the row between 0.999 and
    # 0.001 would land at 0.5, on the far side of the track.
    pos = col("pos")
    d = np.diff(pos)
    unwrapped = pos + np.r_[0, np.cumsum((d < -0.5).astype(float) - (d > 0.5))]
    out["pos"] = np.mod(np.interp(t, ts, unwrapped), 1.0)
    for k in CONTINUOUS + ["acc_lat_g", "acc_long_g", "acc_vert_g", "x", "y", "z", "cg_height_m"] + WHEEL_NAMES:
        out[k] = np.interp(t, ts, col(k))
    for k in HELD:
        out[k] = col(k)[prev].astype(int)   # interpolating a gear is meaningless
    return out


def laps(samples: List[Sample]) -> List[dict]:
    """
    One summary per lap seen in the recording.

    `n` is the lap number the game shows: the CSV's `lap` column (laps finished) + 1.
    `complete` is true when the recording saw the car cross the line at both ends of the
    lap. The first lap after Esc -> Restart starts in the pits, so it never is. `ms` is
    the game's own lap time, read at the crossing; None for a lap that did not end.
    """
    out: List[dict] = []
    cur = None
    for s in samples:
        v = s.values
        if cur is None or v["lap"] != cur["lap"]:
            if cur is None:
                # A recording opened at a crossing (the recorder's default) starts a lap.
                started = v["lap_time_ms"] <= 500 and not v["in_pit"]
            else:
                started = v["lap"] > cur["lap"]
                cur["ms"] = int(v["last_lap_ms"]) if started else None
                cur["complete"] = cur["started"] and cur["ms"] is not None
                out.append(cur)
            cur = {"lap": int(v["lap"]), "n": int(v["lap"]) + 1, "started": started, "ms": None,
                   "max_kmh": 0.0, "peak_g": 0.0}
        cur["max_kmh"] = max(cur["max_kmh"], v["kmh"])
        g = (v["acc_lat_g"] ** 2 + v["acc_long_g"] ** 2 + v["acc_vert_g"] ** 2) ** 0.5
        cur["peak_g"] = max(cur["peak_g"], g)
    if cur is not None:
        cur["complete"] = False
        out.append(cur)
    timed = [lap for lap in out if lap["complete"]]
    best = min(timed, key=lambda lap: lap["ms"]) if timed else None
    for lap in out:
        lap.pop("started")
        lap.pop("lap")
        lap["max_kmh"] = round(lap["max_kmh"], 1)
        lap["peak_g"] = round(lap["peak_g"], 2)
        lap["impact"] = lap["peak_g"] > IMPACT_G
        lap["best"] = lap is best
    return out


def csv_text(grid: Dict[str, np.ndarray]) -> str:
    fmt = [_FORMAT.get(k, "%d" if k in HELD else "%.6g") for k in COLUMNS]
    buf = io.StringIO()
    np.savetxt(buf, np.column_stack([grid[k] for k in COLUMNS]), fmt=fmt, delimiter=",",
               header=",".join(COLUMNS), comments="")
    return buf.getvalue()


def write(jsonl: str | Path) -> List[Path]:
    """Write `<name>.100hz.csv` and `<name>.laps.json` next to a recording. Returns the paths."""
    jsonl = Path(jsonl)
    samples = list(read_jsonl(jsonl))
    stem = jsonl.with_suffix("")
    written = []
    grid = to_grid(samples)
    if grid:
        p = stem.with_name(stem.name + ".100hz.csv")
        p.write_text(csv_text(grid), encoding="utf-8")
        written.append(p)
    p = stem.with_name(stem.name + ".laps.json")
    p.write_text(json.dumps({"recording": jsonl.name, "hz": HZ, "rows": len(grid.get("t_s", [])),
                             "laps": laps(samples)}, indent=1), encoding="utf-8")
    written.append(p)
    return written


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        for path in write(arg):
            print("written", path)
