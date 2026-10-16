# Week 01 – Group 1 (simulator rig)

Period: 7–16 October 2026 · Submission: 16 October 2026

## Important information for Luke
- Because the communication in the first week was a bit off, we decided that it would be a better idea to perform the week-01-Group1.md as a group and not as single Files per person. 
- If its needed we will commit a week-01-Group1-StudentName for everyone from Group1 if needed.
- We will improve in the next week, there were many unexpectet circumstances and we need to step up our communication. 

## Done

- **Task 1, onboarding:** Fork cloned, `simlab` and `claimcheck` installed, all 9 tests pass. The mock stream runs (`python -m simlab.mock_source out.jsonl`, 2265 samples at 10 Hz) and the JSONL was checked. In the mock stream `source_t` and `receive_t` are identical, because nothing delays or re-stamps the samples on one machine. They will differ once data crosses machines, so both stay separate fields.
- **Task 3, game interfaces (preparation, no code yet):** Researched the telemetry interfaces of rFactor 2, Assetto Corsa and iRacing and prepared a preliminary comparison (below). It is a hypothesis; task 3 tests it with real recordings.
- **Task 4, clocks:** Method: `w32tm /stripchart /computer:time.windows.com /samples:10 /period:2 /dataonly` on both laptops, same network, within about one minute. Against the server, laptop A is at −512.8 ms (range 0.91 ms) and laptop B at +718.4 ms (range 1.46 ms). Relative offset between the laptops: about 1.231 s. Uncertainty: ±1.2 ms (sum of the two half-ranges). This covers sample scatter only, not Wi-Fi delay asymmetry or error of the reference server, so the real error is larger. Drift was not measured in this run.
- **Task 5, ROS 2:** Two independent runs with ROS 2 Jazzy in Docker. In both, a Python publisher sends each line of `out.jsonl` as `std_msgs/msg/String` and the stream is recorded with `ros2 bag record` and replayed with `ros2 bag play`.
  - Run A (topic `/mock_stream`, MCAP): the replayed JSON keeps `source_t` and `receive_t`. The bag held 2258 of 2265 messages.
  - Run B (topic `/telemetry`, image `ros:jazzy`, replayed and re-recorded): all 2265 samples arrived, content identical including `source_t` and `receive_t`. Spacing against `source_t`: p95 0.18 ms (record) and 0.25 ms (replay), max 5 ms. Replay follows the recorder's receive time, not `source_t`. One laptop, no real network.
- **Task 6, pipeline (sketch on paper):** recording → store → check → cut into laps → replay / lap files. A stored session is one folder with the samples (with `source_t` and `receive_t`), `meta.json` (driver code, simulator, clock offset with uncertainty, software versions, driving card), the laps and a quality report (gaps, jumps, impossible values, duplicates, time running backwards). Nothing is repaired silently.
- **Task 8, delay model (`python -m simlab.latency`):**

  | run | baseline median / p95 | lossy link delivered |
  |---|---|---|
  | unchanged | 8.2 / 11.3 ms | 953/1000 |
  | processing delay 3 → 1 ms | 6.2 / 9.3 ms | 953/1000 |
  | processing jitter 1 → 10 ms | 17.1 / 59.9 ms | 950/1000 |

  Lowering the delay by 2 ms lowers median and p95 by exactly 2 ms. More jitter hurts the tail much more than the median (p95 about 6×, median about 3×).

  The "slow processing" scenario uses its own processing time and does not change in the runs above. Changing it directly:

  | processing time | median latency |
  |---|---|
  | 20 ms (original) | 1689.2 ms (p95 3187.7 ms) |
  | 17 ms | 191 ms |
  | 15 ms | 19.4 ms |
  | 10 ms | 14.2 ms (p95 16.8 ms) |

  The latency flips at the sample period: at 60 Hz a new sample arrives every 16.7 ms, so above that the queue grows. At Assetto Corsa's roughly 333 Hz (period about 3 ms), the baseline processing (about 4 ms mean) would already queue. These values come from the simulation, not from real hardware.
- **Task 10, local AI:** Ollama with llama3.2 (3.2B parameters, Q4_K_M) on two machines.

  | | machine 1 | machine 2 |
  |---|---|---|
  | hardware | Core i9-9900K, 32 GB RAM, RTX 3080 | Core Ultra 7 155H, 16 GB RAM, CPU only |
  | memory | about 2.5 GB | 2.6 GB |
  | speed (eval rate) | 177–189 tokens/s | about 17 tokens/s |
  | first word, cold start | about 21 s | about 5 s |
  | first word, warm | about 0.17 s | about 0.06 s |

  Quality: the answers invent details and have no fixed format. On the instruction "turn this into a test" the model wrote an exam quiz instead of a structured test, so the prompt needs a fixed output format (for example JSON).

## Game comparison (hypothesis for task 3)

| | rFactor 2 | Assetto Corsa | iRacing |
|---|---|---|---|
| how the data comes out | shared-memory plugin | shared memory or UDP, no plugin needed | telemetry SDK (memory-mapped file) |
| documented rate | about 50 Hz | about 333 packets/s (UDP, README) | about 60 Hz (header, README) |

Assetto Corsa looks like a good first candidate: no extra plugin is needed and Luke already has a UDP reader. The documented rates are not measured; task 3 measures the real ones.

## Licences the rig needs (for Luke)

rFactor 2 (Steam, with extra cars and tracks), Assetto Corsa Ultimate Edition (Steam, base game plus 12 car/track packs), iRacing (24-month membership), configuration software for the Simagic wheel base and pedals. Owner of the Steam and iRacing accounts: open, Luke clarifies.

## Unclear points in the setup guide

1. Cloning needs a personal access token (FH Login, so the password is rejected): a token with `read_repository` and `write_repository`. This is not in section 3.
2. The fork is called `Sim-Fork-GR1`, so `git clone` creates that folder, but the README assumes `cd ai-copilot-sim`.
3. Section 3, step 4 says not to write against the sim interfaces yet, but section 3b says to write the reader now on canned buffers. Which applies?
4. Clock synchronization: will the AI machine be the time server, and how accurately do the three computers need to be synchronized?
5. Game readers: when does Luke hand over his reader code? Is there sample data to test the readers without running the games?
6. What is the maximum acceptable clock offset between the three computers during a recording?

## Five questions for Group 2

1. **Position:** How should we provide GPS coordinates if a simulator only gives local track coordinates?
2. **Brake data:** How should brake input in percent be handled if the lap format expects brake pressure in bar?
3. **Timestamps:** How should `source_t` and `receive_t` be included in the `.vbo` format?
4. **Lap detection:** Should we use the simulator's lap information or detect crossings using the `[laptiming]` section?
5. **Sampling rate:** Which sampling rates should the claim checker support, and how should missing samples be handled?

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

- One recording held 2258 of 2265 messages, the other all 2265. Find out why (start or stop of the recording?).
- Decide which timestamp replay should follow: the recorder's receive time (current behaviour) or `source_t`.
- Clocks: repeat after 30–60 minutes to get the drift.
- Local AI: the gap of 177 versus 17 tokens/s is probably GPU (RTX 3080) versus CPU only. Confirm with `ollama ps` (column PROCESSOR).
- rFactor 2 rate (about 50 Hz): add the source to `docs/SOURCES.md`.
- Helper scripts (ROS 2 publisher and analysis) are not committed yet.
- Format of the weekly notes: check against `notes/WEEK-TEMPLATE.md`.

## Hours this week

- Personal working time: **10 hours per person**
