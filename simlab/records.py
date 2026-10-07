"""
One telemetry sample, with two clocks.

`source_t` is when the simulator (or sensor) produced the value, in seconds on the
source's clock. `receive_t` is when the recorder got it, in seconds on the recorder's
clock. They are different clocks until task 4 shows how far apart they are; never merge
them into one number. Honest timestamps matter more than clean ones.

The recording format is JSON Lines: one object per line, human-readable, easy to diff.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List


@dataclass(frozen=True)
class Sample:
    source_t: float
    receive_t: float
    values: Dict[str, float]


def write_jsonl(path: str | Path, samples: Iterable[Sample]) -> int:
    """Write samples, one JSON object per line. Returns how many were written."""
    n = 0
    with Path(path).open("w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps({"source_t": s.source_t, "receive_t": s.receive_t, **s.values}) + "\n")
            n += 1
    return n


def read_jsonl(path: str | Path) -> Iterator[Sample]:
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            yield Sample(d.pop("source_t"), d.pop("receive_t"), d)


def check_stamps(samples: Iterable[Sample]) -> List[str]:
    """
    Problems with the timestamps of a recording; empty if there are none.

    source_t must strictly increase (one value per sample). receive_t must not go
    backwards. Out-of-order arrival is a finding, not something to repair silently.
    """
    problems: List[str] = []
    prev = None
    for i, s in enumerate(samples):
        if prev is not None:
            if s.source_t <= prev.source_t:
                problems.append(f"sample {i}: source_t does not increase ({prev.source_t} -> {s.source_t})")
            if s.receive_t < prev.receive_t:
                problems.append(f"sample {i}: receive_t goes backwards ({prev.receive_t} -> {s.receive_t})")
        prev = s
    return problems
