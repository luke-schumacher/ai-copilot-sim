"""
A SimPy skeleton of the chain: sim -> acquisition -> transport -> processing.

Each sample is produced at `rate_hz`, spends time in three stages, and may be lost in
transport. Stage delay is `base_s` plus an exponential tail with mean `jitter_s`. That
distribution is a placeholder: task 8 replaces it with whatever task 4's measurements show.
Processing is a single server, so if it is slower than the sampling period, samples queue
and latency grows: the effect the model exists to show.

    python -m simlab.latency
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import simpy


@dataclass(frozen=True)
class Stage:
    base_s: float
    jitter_s: float = 0.0
    loss: float = 0.0           # probability that a sample is lost in this stage


@dataclass(frozen=True)
class Chain:
    rate_hz: float = 60.0
    acquisition: Stage = Stage(0.002, 0.001)
    transport: Stage = Stage(0.001, 0.0005, 0.0)
    processing: Stage = Stage(0.003, 0.001)


@dataclass
class Result:
    latency_s: np.ndarray       # end-to-end, one per delivered sample
    sent: int
    lost: int

    def percentile(self, q: float) -> float:
        return float(np.percentile(self.latency_s, q)) if self.latency_s.size else float("nan")


def simulate(chain: Chain, n: int = 1000, seed: int = 0) -> Result:
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    server = simpy.Resource(env, capacity=1)
    out: List[float] = []
    lost = [0]

    def delay(stage: Stage) -> float:
        return stage.base_s + (rng.exponential(stage.jitter_s) if stage.jitter_s > 0 else 0.0)

    def sample(t_emit: float):
        yield env.timeout(delay(chain.acquisition))
        yield env.timeout(delay(chain.transport))
        if chain.transport.loss and rng.random() < chain.transport.loss:
            lost[0] += 1
            return
        with server.request() as req:
            yield req
            yield env.timeout(delay(chain.processing))
        out.append(env.now - t_emit)

    def source():
        for _ in range(n):
            env.process(sample(env.now))
            yield env.timeout(1.0 / chain.rate_hz)

    env.process(source())
    env.run()
    return Result(np.asarray(out), n, lost[0])


def main(argv: Optional[list] = None) -> int:
    for name, ch in [("baseline", Chain()),
                     ("lossy link", Chain(transport=Stage(0.001, 0.0005, 0.05))),
                     ("slow processing", Chain(processing=Stage(0.020)))]:
        r = simulate(ch)
        print(f"{name:16} delivered {r.sent - r.lost:4}/{r.sent}  "
              f"median {r.percentile(50) * 1000:7.1f} ms  p95 {r.percentile(95) * 1000:7.1f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
