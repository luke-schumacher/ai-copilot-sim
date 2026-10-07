"""
A stand-in for the simulator: replays a synthetic session as a stream of samples.

Needs the lab repository's package, `claimcheck`, installed next to this one:

    pip install -e ../ai-copilot-lab

The values use the lap-format channel names (docs/INTERFACE.md), so everything you
build on the mock works unchanged on the real recorders.

    python -m simlab.mock_source out.jsonl        # writes a synthetic session as samples
"""
from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path
from typing import Iterator, Optional

from simlab.records import Sample, write_jsonl

CHANNELS = ["velocity kmh", "throttle_pct", "brake_bar", "steering_deg", "accel_lat_g"]


def stream(vbo_path: str | Path, realtime: bool = False) -> Iterator[Sample]:
    """Yield one Sample per row of a .vbo. With `realtime`, sleep to match the logged rate."""
    from claimcheck.ingest.vbo import read_vbo

    s = read_vbo(vbo_path)
    t = s.elapsed_s
    lat, lon = s.latitude_deg, s.longitude_deg
    t0 = time.monotonic()
    for i in range(s.n_samples):
        if realtime:
            wait = t[i] - (time.monotonic() - t0)
            if wait > 0:
                time.sleep(wait)
        values = {c: float(s[c][i]) for c in CHANNELS if c in s}
        values["latitude_deg"], values["longitude_deg"] = float(lat[i]), float(lon[i])
        # A mock has no network: the "receive" clock is the source clock for now.
        yield Sample(float(t[i]), float(t[i]), values)


def make_session(directory: Optional[str | Path] = None) -> Path:
    """Generate one synthetic driver's session and return its path."""
    from claimcheck import synth

    d = Path(directory) if directory else Path(tempfile.mkdtemp(prefix="simlab-mock-"))
    return synth.write_session(d / "AA.vbo", synth.Style("AA", seed=1), laps=3)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if len(argv) != 1:
        print("usage: python -m simlab.mock_source out.jsonl", file=sys.stderr)
        return 2
    n = write_jsonl(argv[0], stream(make_session()))
    print(f"wrote {n} samples to {argv[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
