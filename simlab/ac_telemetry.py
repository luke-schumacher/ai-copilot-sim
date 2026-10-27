"""
Read Assetto Corsa's live telemetry over UDP. This is Luke's reader for task 3.

While a session runs, AC answers on UDP port 9996. Three steps:

1. send a handshake; the reply names the car and the track,
2. subscribe; from then on the game sends one `RTCarInfo` datagram (328 bytes) per
   rendered frame, not per physics step. We measured 95 to 305 per second on our rig,
   and the rate moves within a session,
3. send DISMISS when you are done, or the game keeps sending.

Nothing has to be switched on in the game. The game can run on another machine; give
its address as `host`.

Things we measured that the documentation gets wrong (9 Oct 2026, Cayman GT4,
Nürburgring, with a wheel):

- Of the three acceleration floats, **the first is lateral and the second vertical**.
  Lateral is positive to the left, longitudinal positive when speeding up, vertical
  0 on a level road. Gravity is not included.
- `steer` is **degrees at the steering wheel**, not -1..1.
- `clutch` is 1 with the pedal up (engaged) and 0 fully pressed.
- `gear` from the game is 0 = reverse, 1 = neutral, 2 = first. `parse` turns it into
  -1 / 0 / 1, as on a dashboard.

The layout is documented, not published, so treat it as a hypothesis: a wrong offset
gives believable numbers, not garbage. `plausible()` is the cheap check.
"""
from __future__ import annotations

import socket
import struct
import time
from typing import Dict, Iterator, Optional, Tuple

PORT = 9996
HANDSHAKE, SUBSCRIBE_UPDATE, DISMISS = 0, 1, 3

#: The reply to a handshake: car, driver, two ints, track, track layout. The strings
#: are 50 UTF-16 characters each.
HANDSHAKE_FMT = "<100s100sii100s100s"
HANDSHAKE_SIZE = struct.calcsize(HANDSHAKE_FMT)

#: RTCarInfo. The padding is explicit: a char followed by an int costs 3 bytes of
#: alignment, and the six bools 2 more. Get either wrong and every later field shifts.
FMT = (
    "<c3x"   # identifier 'a' + alignment
    "i"      # size
    "3f"     # speed km/h, mph, m/s
    "6?2x"   # ABS enabled, ABS in action, TC in action, TC enabled, in pit, limiter
    "3f"     # accelerations: lateral, vertical, longitudinal (as measured, see above)
    "4i"     # lapTime, lastLap, bestLap (ms), lapCount
    "5f"     # gas, brake, clutch, rpm, steer
    "i"      # gear
    "f"      # height of the centre of gravity, m
    "56f"    # 14 per-wheel arrays of 4, in WHEEL_ARRAYS order
    "f"      # position on the lap, 0..1
    "f"      # slope
    "3f"     # x, y, z in the game world, m
)
SIZE = struct.calcsize(FMT)
WHEELS = ("fl", "fr", "rl", "rr")
WHEEL_ARRAYS = (
    "wheelAngularSpeed", "slipAngle", "slipAngle_ContactPatch", "slipRatio",
    "tyreSlip", "ndSlip", "load", "Dy", "Mz", "tyreDirtyLevel",
    "camberRAD", "tyreRadius", "tyreLoadedRadius", "suspensionHeight",
)
#: The per-wheel arrays we keep, and their column names.
WHEEL_COLUMNS = {
    "load": "load_{w}_n", "slipRatio": "slip_ratio_{w}", "slipAngle": "slip_angle_{w}_deg",
    "ndSlip": "nd_slip_{w}", "Dy": "mu_{w}", "suspensionHeight": "susp_height_{w}_m",
}

_STRUCT = struct.Struct(FMT)


def parse(raw: bytes) -> Dict[str, float]:
    """One datagram as named values, in the column names of our 100 Hz CSV files."""
    f = _STRUCT.unpack(raw)
    v: Dict[str, float] = {
        "kmh": f[2],
        "abs_active": int(f[6]), "tc_active": int(f[7]), "in_pit": int(f[9]), "limiter": int(f[10]),
        "acc_lat_g": f[11], "acc_vert_g": f[12], "acc_long_g": f[13],
        "lap_time_ms": f[14], "last_lap_ms": f[15], "best_lap_ms": f[16], "lap": f[17],
        "gas": f[18], "brake": f[19], "clutch": f[20], "rpm": f[21], "steer_deg": f[22],
        "gear": f[23] - 1,
        "cg_height_m": f[24],
        "pos": f[81], "x": f[83], "y": f[84], "z": f[85],
    }
    for name, pattern in WHEEL_COLUMNS.items():
        base = 25 + WHEEL_ARRAYS.index(name) * 4
        for i, w in enumerate(WHEELS):
            v[pattern.format(w=w)] = f[base + i]
    return v


def pack(v: Dict[str, float]) -> bytes:
    """The reverse of `parse`, for tests and fake games. Missing values are 0."""
    g = lambda k: v.get(k, 0)  # noqa: E731
    wheels = [0.0] * 56
    for name, pattern in WHEEL_COLUMNS.items():
        base = WHEEL_ARRAYS.index(name) * 4
        for i, w in enumerate(WHEELS):
            wheels[base + i] = g(pattern.format(w=w))
    fields = [b"a", SIZE, g("kmh"), g("kmh") / 1.609, g("kmh") / 3.6,
              False, bool(g("abs_active")), bool(g("tc_active")), False, bool(g("in_pit")), bool(g("limiter")),
              g("acc_lat_g"), g("acc_vert_g"), g("acc_long_g"),
              int(g("lap_time_ms")), int(g("last_lap_ms")), int(g("best_lap_ms")), int(g("lap")),
              g("gas"), g("brake"), g("clutch"), g("rpm"), g("steer_deg"),
              int(g("gear")) + 1, g("cg_height_m"), *wheels,
              g("pos"), 0.0, g("x"), g("y"), g("z")]
    return _STRUCT.pack(*fields)


def plausible(v: Dict[str, float]) -> list:
    """Problems with a decoded datagram; empty if it looks physically possible."""
    bad = []
    checks = [("kmh", 0, 450), ("gas", 0, 1.05), ("brake", 0, 1.05), ("clutch", 0, 1.05),
              ("steer_deg", -900, 900), ("gear", -1, 8), ("pos", 0, 1.001), ("rpm", 0, 20000)]
    for key, lo, hi in checks:
        if not lo <= v[key] <= hi:
            bad.append(f"{key} = {v[key]:.3f} is outside {lo}..{hi}")
    return bad


def _wstr(raw: bytes) -> str:
    """A handshake string. AC ends it with '%' and leaves rubbish behind, so cut there too."""
    text = raw.decode("utf-16-le", errors="replace")
    for end in ("\x00", "%"):
        text = text.split(end, 1)[0]
    return text.strip()


def parse_handshake(raw: bytes) -> Tuple[str, str, str]:
    """(car, track, layout) from the handshake reply."""
    car, _driver, _ident, _version, track, layout = struct.unpack(HANDSHAKE_FMT, raw[:HANDSHAKE_SIZE])
    return _wstr(car), _wstr(track), _wstr(layout)


def pack_handshake(car: str, track: str, layout: str) -> bytes:
    """A handshake reply as AC sends it, for tests and fake games."""
    w = lambda s: (s + "%").encode("utf-16-le")[:100]  # noqa: E731
    return struct.pack(HANDSHAKE_FMT, w(car), w("driver"), 1, 1, w(track), w(layout))


class Connection:
    """
    A subscription to the game. Use it with `with`, so DISMISS is always sent.

        with Connection("127.0.0.1") as game:
            print(game.car, game.track, game.layout)
            for receive_t, raw in game.datagrams():
                values = parse(raw)
    """

    def __init__(self, host: str = "127.0.0.1", port: int = PORT, timeout: float = 2.0) -> None:
        self.addr = (host, port)
        self.timeout = timeout
        self.car = self.track = self.layout = ""
        self._sock: Optional[socket.socket] = None

    def _send(self, operation: int) -> None:
        assert self._sock is not None
        self._sock.sendto(struct.pack("<iii", 1, 1, operation), self.addr)

    def __enter__(self) -> "Connection":
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(self.timeout)
        try:
            self._send(HANDSHAKE)
            raw, _ = self._sock.recvfrom(4096)   # socket.timeout: no session is running
            if len(raw) >= HANDSHAKE_SIZE:
                self.car, self.track, self.layout = parse_handshake(raw)
            self._send(SUBSCRIBE_UPDATE)
        except OSError:
            self._sock.close()
            self._sock = None
            raise
        return self

    def __exit__(self, *exc) -> None:
        if self._sock is not None:
            try:
                self._send(DISMISS)
            except OSError:
                pass
            self._sock.close()
            self._sock = None

    def datagrams(self) -> Iterator[Tuple[float, bytes]]:
        """(receive time on this machine's monotonic clock, raw datagram), until the game goes quiet."""
        assert self._sock is not None, "use Connection with `with`"
        while True:
            try:
                raw, _ = self._sock.recvfrom(4096)
            except socket.timeout:
                return
            if len(raw) == SIZE:
                yield time.monotonic(), raw


class GameClock:
    """
    The game's own time in seconds, continuous across line crossings.

    `lapTime` is the physics clock but restarts at every crossing. Across one, the time
    that passed is what was left of the old lap (the new `lastLap` minus the old
    `lapTime`) plus how far into the new lap the game already is. A reset that is not a
    crossing (Esc -> Restart, back to the pits) adds nothing instead of a negative step.

    `update` returns the new time, or None when the game's clock did not move: a paused
    game keeps sending the same frame, and those are dropped.
    """

    def __init__(self) -> None:
        self.t_ms = 0
        self._prev: Optional[Tuple[int, int]] = None

    def update(self, lap_time_ms: int, lap: int, last_lap_ms: int) -> Optional[float]:
        if self._prev is None:
            self._prev = (lap_time_ms, lap)
            return 0.0
        prev_time, prev_lap = self._prev
        self._prev = (lap_time_ms, lap)
        across = last_lap_ms - prev_time + lap_time_ms
        if lap > prev_lap and across >= 0:
            step = across
        else:
            step = max(lap_time_ms - prev_time, 0)
        if step <= 0:
            return None
        self.t_ms += step
        return self.t_ms / 1000.0
