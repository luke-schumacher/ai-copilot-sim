# Week 01 – Group 1 (simulator rig)

Period: 7–16 October 2026 · Submission: 16 October 2026

## Done

- **Task 1, onboarding:** Fork cloned, `simlab` and `claimcheck` installed, all 9 tests pass. The mock stream runs (`python -m simlab.mock_source out.jsonl`, 2265 samples) and the JSONL was checked. In the mock stream `source_t` and `receive_t` are identical, because nothing delays or re-stamps the samples on one machine. They will differ once data crosses machines, so both stay separate fields.
- **Task 3, game interfaces (preparation, no code yet):** Researched the telemetry interfaces of rFactor 2, Assetto Corsa and iRacing and prepared a preliminary comparison (below). It is a hypothesis; task 3 tests it with real recordings.
- **Task 4, clocks:** Method: `w32tm /stripchart /computer:time.windows.com /samples:10 /period:2 /dataonly` on both laptops, same network, within about one minute. Against the server, laptop A is at −512.8 ms (range 0.91 ms) and laptop B at +718.4 ms (range 1.46 ms). Relative offset between the laptops: about 1.231 s. Uncertainty: ±1.2 ms (sum of the two half-ranges). This covers sample scatter only, not Wi-Fi delay asymmetry or error of the reference server, so the real error is larger. Drift was not measured in this run.
- **Task 5, ROS 2:** ROS 2 Jazzy in Docker. A Python publisher reads `out.jsonl` and publishes each line as `std_msgs/msg/String` on `/mock_stream`. Recorded with `ros2 bag record` (MCAP), replayed with `ros2 bag play`. `ros2 topic echo` shows the replayed JSON with `source_t` and `receive_t` intact.
- **Task 6, pipeline** Store → Check → Cut into laps → Replay. A stored session is one folder with: the samples (source_t and receive_t), meta.json (simulator, car, track, driver, scenario card, clock offset, software versions) and a quality report (gaps, jumps, impossible values, duplicates, time running backwards).
- **Task 8, delay model (`python -m simlab.latency`):**

  | run | baseline median / p95 | lossy link delivered | slow processing median / p95 |
  |---|---|---|---|
  | unchanged | 8.2 / 11.3 ms | 953/1000 | 1689.2 / 3187.7 ms |
  | processing delay 3 → 1 ms | 6.2 / 9.3 ms | 953/1000 | 1689.2 / 3187.7 ms |
  | processing jitter 1 → 10 ms | 17.1 / 59.9 ms | 950/1000 | 1689.2 / 3187.7 ms |

  Lowering the delay by 2 ms lowers median and p95 by exactly 2 ms. More jitter hurts the tail much more than the median (p95 about 6×, median about 3×). The "slow processing" column does not change in these runs because that scenario uses its own processing time (20 ms).

  In the slow-processing scenario itself, we changed the processing time from 20 ms to 10 ms: median 1689.2 → 14.2 ms, p95 3187.7 → 16.8 ms. At 60 Hz a new sample arrives about every 16.67 ms. With 20 ms of processing the system cannot keep up and a queue builds up; with 10 ms it keeps up. These values come from the simulation, not from real hardware.
**Task 10, local AI:** Ollama with llama3.2 (3.2B parameters, Q4_K_M) on a laptop ([CPU], [RAM], [GPU yes/no]). While answering: about 2.5 GB RAM and 42 % CPU; afterwards CPU about 0 %, RAM stays at 25 GB (model stays loaded). Measured: first run after idle (cold) total 21.8 s, of which prompt reading 20.9 s (model loading), eval rate 177 tokens/s. Warm follow-up question: total 1.7 s, first word after about 0.17 s, eval rate 189 tokens/s. First quality check: the model read "turn into a test" as an exam quiz instead of a structured test, so the prompt needs a fixed output format (e.g. JSON).
Processor: Intel(R) Core(TM) i9-9900K CPU @ 3.60GHz
RAM: 32 GB
GPU: NVIDIA GeForce RTX3080 

## Game comparison (hypothesis for task 3)

| | rFactor 2 | Assetto Corsa | iRacing |
|---|---|---|---|
| how the data comes out | shared-memory plugin | shared memory or UDP, no plugin needed | telemetry SDK (memory-mapped file) |
| documented rate | about 50 Hz | about 333 packets/s (UDP, README) | about 60 Hz (header, README) |

Assetto Corsa looks like a good first candidate: no extra plugin is needed and Luke already has a UDP reader. The documented rates are not measured; task 3 measures the real ones.

## Unclear points in the setup guide

1. **Clock synchronization:** Will the AI machine be the time server, and how accurately do the three computers need to be synchronized?
2. **Game readers:** When does Luke hand over his reader code? Is there sample data to test the readers without running the games?
3. **Clock synchronization:** What is the maximum acceptable clock offset between the three computers during a recording?

## Five questions for Group 2

1. **Position:** How should we provide GPS coordinates if a simulator only gives local track coordinates?
2. **Brake data:** How should brake input in percent be handled if the lap format expects brake pressure in bar?
3. **Timestamps:** How should `source_t` and `receive_t` be included in the `.vbo` format?
4. **Lap detection:** Should we use the simulator's lap information or detect crossings using the `[laptiming]` section?
5. **Sampling rate:** Which sampling rates should the claim checker support, and how should missing samples be handled?

## List of accounts and Licences 
- Licences the rig needs: rFactor 2 (Steam, with extra cars and tracks), Assetto Corsa Ultimate Edition (Steam, base game plus 12 car/track packs), iRacing (24-month membership), configuration software for the Simagic wheel base and pedals. 
- Owner of the Steam and iRacing accounts: open, Luke clarifies.

## Blocked / decisions needed

- Luke's game-reader code is needed for further task 3 work.
- The required telemetry fields and units need to be agreed with Group 2.

## Next week

- Task 3: continue with Luke's reader code once available; prepare the first real reader tests once software access is available.
- Check the required telemetry fields and unit conversions.
- Agree the open lap-file questions with Group 2 (`docs/INTERFACE.md`), due 13 November.
- Task 6: refine the data pipeline (stored session layout, quality checks) and start the code.
- Task 5: prepare the ROS 2 bridge for mock and later real data.
- Direction call with Luke on Thursday 22 October.

## Open points

- The bag holds 2258 messages, the source file 2265 lines. Find out why 7 are missing (start or stop of the recording?) and record again.
- Not yet checked: replay with the original timing, and whether the bag timestamps match `source_t`.
- Clocks: repeat after 30–60 minutes to get the drift.
- Local AI: add model tag, laptop specification, and measured speed (`ollama run <model> --verbose`: eval rate, load duration).
- rFactor 2 rate (about 50 Hz): add the source to `docs/SOURCES.md`.

## Hours this week

- Personal working time: **10 hours p.p.**
