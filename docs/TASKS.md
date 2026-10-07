# Group 1 tasks

h = hours for the whole group. B = Bachelor, M = Master-led, B+M = shared.
Every student: 10 h onboarding + 75 h core tasks + 35 h meetings, report, talk = 120 h.
Start in week 1, without hardware: S0, S2 and S3 (interfaces first), S4 (method, on laptops), S5 (mock stream), S7 (assumed values).
Group 2's tasks are in the `ai-copilot-lab` repository.

| # | task | goal | input → output | done when | h | lvl | depends on |
|---|---|---|---|---|---|---|---|
| S0 | **Onboarding** | Learn the rig, the rules and the repositories. | In: repositories, setup guide. Out: everyone runs the mock stream into the recorder. | Every student has run the mock stream into a recorded file and passes a 5-question quiz on the data rule. Rig safety and access sorted. | 60 (6×10) | B+M | none · week 1 |
| S1 | **Rig bring-up and setup guide** | Get the delivered rig into a known-good state and keep the README setup guide true. | In: delivered rig, README guide. Out: rig in known-good state, corrected guide, backup image. | Someone who has not touched the rig reproduces a fresh setup of all three sims from the README alone. Checklist signed. Backup image taken. | 30 | B | rig delivery (mid-Nov at the earliest) |
| S2 | **rFactor 2 capture** | Read rFactor 2 telemetry at a fixed rate and record it with honest timestamps. | In: rFactor 2 interface (documented), canned buffers, later the sim. Out: reader + recorder, source and receive time. | Reader unit-tested on canned buffers. Then a 10-lap session recorded with no gap over two sample periods, on the rig or any Windows PC with the sim. Real update rate measured. | 45 | B+M | none · interface first |
| S3 | **Assetto Corsa and iRacing capture** | Do the same for Assetto Corsa and iRacing. | In: AC and iRacing interfaces (documented), canned buffers. Out: two readers, a sim × field × unit × rate table. | Both readers unit-tested on canned buffers. Then both record a 10-lap session (rig or any Windows PC). Measured rates compared with what the sims claim. | 40 | B | S2 pattern · interface first |
| S4 | **Clocks and timestamps** | Define source time and receive time, and measure how far the machines' clocks disagree. | In: sim PC, evaluation PC, AI machine on the switch. Out: timestamp policy, measurement script, results. | Offset and drift between the three machines measured over 1 h, with intervals. A worst-case timestamp error budget stated. Method first tested on laptops. | 55 | M | none · method in week 1 |
| S5 | **ROS 2 data flow** | Move telemetry through ROS 2 with its timestamps intact. | In: mock stream (from the lab repo), later the real recorders. Out: message definition, bridge, bag recording and replay. | Message definition in the repo and agreed with Group 2 by 13 Nov. A stream is recorded to a bag and replayed with original timing; stamps preserved. | 45 | B+M | none · mock first |
| S6 | **Lap files and labelled sessions** | Turn recordings into lap files, then drive labelled sessions. | In: recordings (mock until real), Group 2's driving cards. Out: converter + at least 10 labelled sessions. | Converter output passes the validator and loads in the checker. At least 10 sessions of 6+ laps with a planted mistake and metadata: on the rig, or any PC sim if the rig is late. | 50 | B | S2 or S5, Group 2's T8, T1 |
| S7 | **SimPy latency model** | Model acquisition, transport and processing: latency, jitter, loss, sampling rate. | In: S4 measurements. Out: calibrated model + parameter ranges for Group 2. | Model reproduces the measured end-to-end latency (median and 95th percentile within a stated tolerance) in at least two configurations. Ranges handed to Group 2 (T9). | 60 | M | S4 (start with assumed values) |
| S8 | **Cameras** | Capture the two cameras with timestamps and measure their offset to telemetry. | In: two Logitech MX Brio (a laptop webcam until then), S4. Out: capture tool, measured offset. | Capture tool built and tested on a laptop webcam. Frame timestamps recorded; offset to telemetry measured from a known visual event; dropped frames counted over 10 min. | 30 | B | S4 · laptop first |
| S9 | **Local AI machine** | Set up the AI machine and measure what a request over the network costs. | In: a laptop first, then the AI machine. Out: running local model server, latency table. | A model server runs on a laptop with latency measured at three prompt sizes, then on the AI machine; a request from the sim PC gets an answer. Setup written into the guide. | 40 | B+M | laptop first · AI machine delivery |
| S10 | **Stage 2: raw inputs and heart rate** | Read raw wheel and pedal data and the Polar H10 chest strap, aligned to telemetry. | In: S4, S5, canned BLE packets, later wheel base, pedals, Polar H10. Out: aligned recordings of inputs, heart rate, RR intervals. | Parsers unit-tested on canned packets. Then raw inputs and 10 min of heart rate and RR recorded and aligned to telemetry, with the alignment error stated. | 55 | B+M | S4, S5 |
| S11 | **Meetings, report, final talk** | Weekly meetings, a short report, the final presentation. | In: all results. Out: report ≤ 12 pages + talk. | Report reviewed by Luke. Talk rehearsed once. | 210 (6×35) | B+M | all |

## Squads and hours per person

Squad A (Capture and data): M1, B1, B2; the first named is the Master and leads.
Squad B (Timing, models and AI): M2, B3, B4; the first named is the Master and leads.

| | S0 | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 | total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M1 (squad A) | 10 |  | 15 | 10 |  | 25 | 10 |  |  |  | 15 | 35 | 120 |
| B1 (squad A) | 10 | 15 | 15 | 15 |  | 10 | 20 |  |  |  |  | 35 | 120 |
| B2 (squad A) | 10 | 15 | 15 | 15 |  | 10 | 20 |  |  |  |  | 35 | 120 |
| M2 (squad B) | 10 |  |  |  | 25 |  |  | 30 |  | 10 | 10 | 35 | 120 |
| B3 (squad B) | 10 |  |  |  | 15 |  |  | 15 | 15 | 15 | 15 | 35 | 120 |
| B4 (squad B) | 10 |  |  |  | 15 |  |  | 15 | 15 | 15 | 15 | 35 | 120 |
| group | 60 | 30 | 45 | 40 | 55 | 45 | 50 | 60 | 30 | 40 | 55 | 210 | 720 |

Milestones: 30 Oct first result; 13 Nov interface v0 agreed; 4 Dec core working; 22 Dec to 6 Jan nothing due; 25 Jan evaluation done; 12 Feb report draft; week of 22 Feb final presentation.
