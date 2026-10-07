# AI Copilot for Racesimulation: the simulator rig (Group 1)

This is the repository and setup guide for **Group 1**, seven students (one Master and six Bachelors), of the student project,
winter semester 2026/27, FH Aachen. The rig arrives prebuilt. Your job is to turn it into a **measured, documented source of racing
data** for the AI copilot, and to build what sits around it: the data flow, the pipeline, a dashboard, and
a local AI model.

**Keep this README true.** When you find a step that is wrong or missing, fix it in a merge request. Task 2
(rig bring-up) is finished when someone who has never touched the rig can follow this guide from a fresh
machine.

Where to go next:

- **First week:** [docs/START-HERE.md](docs/START-HERE.md)
- **Tasks, squads and hours:** [docs/TASKS.md](docs/TASKS.md)
- **What you hand to Group 2:** [docs/INTERFACE.md](docs/INTERFACE.md)
- **The hardware, with specifications:** [docs/HARDWARE.md](docs/HARDWARE.md)
- **How we work:** [docs/WORKFLOW.md](docs/WORKFLOW.md)
- **The rule about data:** [docs/DATA-RULE.md](docs/DATA-RULE.md)

**The rig is not here yet.** Delivery is mid-November at the very earliest, and probably later. That is why
most of this guide, and most of your work until December, is built and tested **without** the rig, against
the mock stream in this repository. Section 3b says what to do while you wait, and what happens on 11
December if the rig has still not arrived.

## The project in plain words

A race engineer has a belief about a driver, for example "he loses time in corner 2 because he brakes
early". A **claim checker** (the other group's repository) tests that belief against lap data and answers
Supported, Contradicted or Can't tell yet. Group 2 finds out how often it is right. To know whether their
result holds beyond fake data, they need a second source: **a simulator, with data whose timing can be
trusted.** That is you.

Your chain, from left to right:

```
racing game  ->  reader  ->  ROS 2  ->  pipeline (store, check, replay)  ->  lap files for Group 2
(3 games)       (task 3)    (task 5)         (task 6)                          (task 7)
                                |
                                +-->  interface tests and dashboard on the second PC (task 9)  and  local AI model (task 10)
```

## Your twelve tasks in plain words

1. **Onboarding.** Learn the plan; run the mock data stream.
2. **Rig bring-up and setup guide.** Set up the delivered rig; keep this guide correct.
3. **Game readers and game comparison.** Read data from rFactor 2, Assetto Corsa and iRacing. Test all three
   and recommend which to use for the test sessions. Luke gives you his existing reader code to start from.
4. **Clocks and timestamps.** Measure how far the clocks of the three machines disagree.
5. **Data flow with ROS 2.** Move the data between machines; record and replay it.
6. **Data pipeline.** Store every session in one layout, check its quality, cut it into laps, replay it.
7. **Lap files and labelled sessions.** Convert sessions for Group 2's checker; drive 10 labelled test sessions.
8. **Different setups and the delay model.** Measure delay in at least three setups; build a simulation of it.
9. **Interface tests and dashboard.** Test the interfaces between the parts and the data reporting (the test code is in the repositories), then build a dashboard on the evaluation PC that pulls the data and evaluates it. This dashboard is what you present at the end.
10. **Local AI: setting up and testing models.** Set up the AI machine, compare at least three local models on speed and memory, check them on ten example sentences and pick one. Group 2 runs the full accuracy study on 100 claims.
11. **Cameras, raw inputs and heart rate.** A later stage: record and align further sources.
12. **Meetings, report and final talk.**

## Terms explained

**The data**
- **Telemetry:** measurements recorded while driving: speed, throttle, brake, steering, position.
- **Sample:** one set of telemetry values at one moment. At 60 samples a second, a lap is thousands of samples.
- **Timestamp:** the time written next to a sample. In this project every sample carries **two**: the **source
  time** (when the game produced it) and the **receive time** (when your recorder got it). They are on
  different clocks, so never merge them into one number.
- **Delay (latency):** how late data arrives. **Jitter:** how much that delay varies. **Lost data (packet loss):**
  samples that never arrive.
- **Clock offset and drift:** how far two machines' clocks disagree, and how that grows over time.
- **Lap file:** a text file in the layout of a GPS data logger (`.vbo`) that Group 2's checker reads.
- **Interface (German: Schnittstelle):** the place where one part hands data to the next, for example game to reader, reader to ROS 2, or lap file to Group 2's checker.
- **Pipeline:** the steps that take a raw recording to a checked, stored, replayable session.
- **Dashboard:** a live display of data on a screen.

**ROS and friends**
- **ROS** stands for **Robot Operating System**. Despite the name it is not an operating system: it is a free
  toolkit for passing messages between programs, which can run on different machines. **ROS 2** is its second
  generation, and **Jazzy** (full name Jazzy Jalisco) is the release we use.
- A **node** is a program that takes part. A **topic** is a named channel, for example `/telemetry`. A node
  *publishes* messages to a topic and other nodes *subscribe* to it. A **message** is one piece of data with a
  fixed layout. A **bag** is a recording of messages that can be replayed with its original timing.

**How games hand over data**
- **Shared memory:** a block of the computer's memory that a game writes and other programs on the same
  machine can read. **Plugin:** an add-on that a game loads. **SDK** (software development kit): the toolbox a
  maker provides for programmers.
- **UDP:** a simple way of sending small messages over a network without checking that each one arrives. Fast,
  but data can be lost.
- **Canned buffers:** saved raw data from a game, used to test a reader without running the game.
- **Mock:** a stand-in data source used before the real one exists.

**Time**
- **NTP** (Network Time Protocol) keeps clocks in step over a network. **chrony** does this on Linux and
  **w32tm** on Windows.
- **SimPy:** a Python library for simulating events over time. We use it to model delays.

**The machines and the AI part**
- **AI machine:** the separate ASUS computer for running AI models. It has an NVIDIA GB10 chip and runs Linux on
  an **arm64** processor, a processor design that differs from a normal PC, so software needs arm64 builds.
- **GPU:** a graphics processor; it runs AI models fast. **Local AI model:** a language model that runs on our
  own machine instead of a cloud service. **Inference:** running the model to get an answer.
- **UPS:** uninterruptible power supply, a battery that lets the rig shut down cleanly.
- **BLE** (Bluetooth Low Energy) is how the Polar H10 chest strap talks. **GATT** is BLE's way of organising data
  into services. **ECG** is the heart's electrical trace; **RR intervals** are the times between heartbeats.

**Tools**
- **uv** creates the Python environment; **pytest** runs the tests; **Docker** runs software in a container.
- **Fork, branch, merge request:** your own copy of a repository; a line of work in it; a request to merge it
  back (GitHub calls it a pull request). See [docs/WORKFLOW.md](docs/WORKFLOW.md).

---

## 1. What you are setting up

This table lists everything in the rig, what it is, and what it does in our project. The specifications are in [docs/HARDWARE.md](docs/HARDWARE.md); here we only need to know what each part is for.

| machine / part | what it is | role |
|---|---|---|
| **Sim PC** | Bernax GT simulator with a fully installed game PC (RTX 5070, 32 GB RAM, Ryzen 7 or Ultra 7, 1 TB SSD), 49″ curved monitor, 144 Hz or more | runs the sims; the telemetry source |
| Wheel base, wheel, pedals | Simagic Alpha base, DTM-style wheel (GT NEO or GTC, to be confirmed at delivery), P1000 two-pedal set | driver input; later read raw (task 11) |
| Seat shaker, seat, frame, monitor stand | LTEC GT seat, mounted seat shaker | not read by software, but part of the rig |
| **AI machine** | ASUS Ascent GX10: NVIDIA GB10, 128 GB unified memory, 1 TB SSD, Linux (DGX OS, Ubuntu 24.04, arm64) | local model server; runs ROS 2 |
| **Evaluation PC** | ASUS ExpertCenter PN54: Ryzen AI 7 350, 32 GB, Windows 11, two 2.5 GbE ports, Bluetooth 5.4 | recording, evaluation, network experiments, BLE for the heart-rate strap |
| Switch | Netgear GS308E, 8-port | one observable network for all three machines |
| Second monitor | Dell 27″ QHD | telemetry and model output |
| Cameras | 2 × Logitech MX Brio (4K) | driver and scene video (task 11) |
| UPS | APC Back-UPS BX950MI | clean shutdown; protects the rig |
| Chest straps | 2 × Polar H10 | heart rate, RR intervals, ECG (task 11) |
| Software | rFactor 2 (Steam), Assetto Corsa Ultimate Edition (Steam), iRacing (24-month membership) | the three sims |

Source: [docs/HARDWARE.md](docs/HARDWARE.md) and the supplier's quotation. **Details not known until delivery**
(fill in during task 2):

| unknown | where to look | answer |
|---|---|---|
| Sim PC: Windows version, exact CPU, free disk (GPU RTX 5070 and 32 GB RAM are in the quotation) | System settings, `msinfo32` | |
| Does the sim PC have Bluetooth? | Device Manager | |
| What is already installed on the sim PC? | Programs list; ask the vendor | |
| Which accounts own the Steam and iRacing licences? | Luke | |
| Which wheel arrives (GT NEO or GTC), wheel base peak torque setting and firmware | Simagic software | |

## 2. The plan for the network and clocks

```
 Sim PC (Windows)  ---\
                       +--- Switch (GS308E) ---+--- AI machine (Linux, ROS 2)
 Evaluation PC (Win11) /                       |
                                          (Dell monitor on the evaluation PC)
```

- One subnet, fixed addresses, written into the table below. Suggested:
  `192.168.50.0/24`: sim PC `.10`, evaluation PC `.20`, AI machine `.30`.
- The evaluation PC has two Ethernet ports, so it can also sit **inline** between the
  sim PC and the switch to disturb traffic (delay, loss). Whether to do that, or to
  inject the faults in software inside your bridge, is a decision for tasks 5 and 8. Write down
  the decision and why.
- **Clocks:** three machines, three clocks. Decide who is the time reference (suggestion:
  the AI machine, running `chrony` as a local NTP server), measure the offset and drift
  (task 4), and record both timestamps in every sample (`source_t`, `receive_t`, see
  [simlab/records.py](simlab/records.py)). Never overwrite one with the other.

Fill in this table once the addresses are fixed. Everyone who touches the network then knows where each machine is.

| machine | address | OS | role |
|---|---|---|---|
| sim PC | | | |
| evaluation PC | | | |
| AI machine | | | |

## 3. Phase 0: before the rig arrives (weeks 1 to 6)

Everything here runs on your laptops.

1. One person per group forks this repository on the FH Aachen GitLab (https://git.fh-aachen.de/ls9392e/ai-copilot-sim; sign in with your FH account and click Request access; Luke approves it) and invites the group to the fork (Manage, Members); everyone clones the fork, and also clones `ai-copilot-lab` (https://git.fh-aachen.de/ls9392e/ai-copilot-lab) next to it. Then (this is real work, not waiting: see 3b):
   ```bash
   git clone <this repo> && git clone <ai-copilot-lab>
   cd ai-copilot-sim
   uv venv && uv pip install -e ".[dev]" -e ../ai-copilot-lab
   uv run pytest
   uv run python -m simlab.mock_source out.jsonl      # a synthetic session as a stream of samples
   uv run python -m simlab.latency                    # the latency skeleton, three configurations
   ```
2. Install **ROS 2 Jazzy** (see phase 6) in a container or an Ubuntu 24.04 machine and
   publish the mock stream on a topic.
3. Measure the clock offset between two of your laptops with `chrony` or `w32tm`
   (phase 5). You are developing the method for task 4 now, so the real measurement is quick.
4. Read the sim telemetry interfaces (sections 6.1 to 6.3). Do not write against them yet:
   without the sims running you cannot tell whether you read them right.
5. Prepare the checklists in section 14 as files you will tick on the day.

## 3b. While the rig is late

Delivery date: mid-November at the earliest. Nobody can promise more. Until it arrives, every
task has a part that needs no rig:

| task | do now, without the rig | changes when the rig arrives |
|---|---|---|
| 2 rig bring-up | read this guide end to end; prepare the checklists; list what is unknown | the actual bring-up |
| 3 readers | write the reader interface; unit-test it on **canned buffers** (byte dumps that look like the sim's memory); read the interface documentation for each sim | run it against the real sim; measure the real update rate |
| 4 clocks | develop and test the measurement method on two laptops | repeat on the three real machines |
| 5 ROS 2 | mock stream, message definition, bag record and replay | swap the mock for the real recorder |
| 6 data pipeline | build the whole path on mock data: store, check, cut into laps, replay | feed it real recordings |
| 7 lap files | converter from stored sessions (mock first) that passes the validator | convert real sessions; drive the labelled sessions |
| 8 setups and delay model | build the model with assumed values; change them and see what moves; plan the setups to measure | measure the real setups; calibrate the model against them |
| 9 interface tests and dashboard | extend the interface tests; build the dashboard on replayed mock data on your own laptop | run it on the evaluation PC with live data |
| 10 local AI | run small models on a laptop; build the comparison test and the measurements | repeat on the AI machine; choose the model |
| 11 cameras, raw inputs, heart rate | capture tool on a laptop webcam; parsers tested on canned packets | the two cameras, the real straps and devices |

**Where a real sim helps even before the rig:** rFactor 2 and Assetto Corsa run on an ordinary
Windows PC. If the licences are available (Luke clarifies who buys them), the readers in task 3
can be tried against the real sims on a student's own PC, with a gamepad or a wheel.

**Decision point, Friday 11 December.** If the rig has not been delivered by then, the labelled
sessions for task 7 (and therefore Group 2's transfer experiment) are driven on any Windows PC with
the sims, using a gamepad or your own wheels. They are lower fidelity than the rig, and the report
must say so. If the rig arrives, they are driven on it.

## 4. Phase 1: unboxing and safety

- **The wheel base is a direct-drive motor and can apply strong torque.** Keep hands and
  loose clothing away from the wheel when the sim starts, and set the force limit low
  during setup (phase 4). Read the base's manual for the emergency stop and power-off
  procedure before the first power-on. Write that procedure on a card next to the rig.
- Check the delivery against the offer: frame, seat, PC, monitor, base, wheel, pedals,
  shaker, cables. Photograph the rig as delivered.
- Connect the **UPS** first; plug the sim PC, the monitor and the base into it. Test one
  clean shutdown from the UPS software before anything else.
- Power on, look for error beeps or lights, and let the vendor's installation boot to the
  desktop. Do not install updates yet.

## 5. Phase 2: sim PC base setup

1. Make a **backup image** of the vendor's installation before you change anything (task 2
   deliverable). Note the tool and where the image lives.
2. Windows Update: finish updates once, then set "active hours" to cover your sessions and
   pause updates during a recording week. A reboot in the middle of a session ruins data.
3. Install **Python 3.12 from python.org, not from the Microsoft Store.** The Store
   build's sandboxing breaks access to the sims' shared memory.
4. Install Git, then clone this repository and the lab repository to `C:\work\`.
5. Power plan: "High performance"; disable USB selective suspend (wheel and pedals must not
   sleep).
6. Create a folder `C:\recordings\` (git-ignored in the repository) for raw recordings.

## 6. Phase 3: the three sims

For each sim, finish with the same acceptance test: **drive 10 laps, record, and read the
file back**. Measure and write down the real update rate; do not assume it.

### 6.1 rFactor 2 (plugin interface)

rFactor 2 gets its telemetry from a shared-memory **plugin**.

1. Install rFactor 2 from Steam and start it once so it creates its folders.
2. Download the public plugin **rF2SharedMemoryMapPlugin** (author TheIronWolf, on GitHub:
   `TheIronWolfModding/rF2SharedMemoryMapPlugin`). Check its licence and note the release you
   used in `docs/SOURCES.md`.
3. Copy `rFactor2SharedMemoryMapPlugin64.dll` into `<rFactor 2 folder>\Bin64\Plugins\`.
4. Start rFactor 2. In **Settings, Gameplay, Plugins**, switch the plugin on. If it does not
   appear, install the Visual C++ 2013 (VC12) runtime from the game's `Support\Runtimes`
   folder and restart the game. (Le Mans Ultimate uses a similar setup with a manual entry
   in `CustomPluginVariables.JSON`; for rFactor 2 the in-game toggle is enough.)
5. Drive. The plugin mirrors the game's internal state into shared-memory buffers (telemetry,
   scoring and others). Read them from a separate process; the plugin repository documents the
   structures.
6. Task 3 builds the recorder on top of this.

### 6.2 Assetto Corsa

Assetto Corsa publishes telemetry through memory-mapped files, no plugin required: three
blocks named `acpmf_physics`, `acpmf_graphics` and `acpmf_static`. Read them from Python with
`mmap` and `ctypes` structures. Find the official shared-memory reference and link it in
`docs/SOURCES.md`; check any third-party reader library's licence before you use it. Remember:
**not the Microsoft Store Python**.

### 6.3 iRacing

iRacing exports telemetry through a memory-mapped file called `Local\IRSDKMemMapFileName`, with
a header that states the data version and the update rate (usually 60 Hz) and a tick counter. The
Python library `pyirsdk` reads it (`pip install pyirsdk`). iRacing must be running with a car on
track. Telemetry is only available while you drive.

### 6.4 Luke's reader code

Luke has existing code that reads data from the games (for example a reader for Assetto Corsa's UDP
interface) and hands it to you at the start of task 3. Use it as the starting point: run it, read it, fix it,
extend it, and add the tests. Until the hand-over, work from the documentation of each game.

Assetto Corsa also has a **UDP remote-telemetry interface** that works across the network; the documentation
states a rate of about 333 packets a second. Measure it: do not assume it.

### 6.5 Comparing the three games (task 3)

Which game or games will we use for the labelled test sessions? That is **to be decided, and you decide it
with data**. Test all three the same way, then recommend, and agree the choice with Luke at a direction call.

**How to test.** For each game, use the same kind of car (a GT-style car) and a track that exists in all
three. Drive 10 laps without stopping and record them with the reader. Then:

1. Work out the **real update rate**: the median time between samples, and the longest gap.
2. List the **fields you can read** (speed, throttle, brake, steering, position, lap number, others) with units.
3. Check **stability**: gaps, frozen values, jumps, values that stay at zero.
4. Check whether the game must be **in the foreground**, and whether the reader survives a pause or restart.
5. Count the **effort to set up** (hours, steps, extra software).
6. Note **cost and account needs**, and the choice of cars and tracks.

**Write the results in this table** (the "Sim comparison" table; copy it into `docs/game-comparison.md`):

| | rFactor 2 | Assetto Corsa | iRacing |
|---|---|---|---|
| how the data comes out | plugin and shared memory | shared memory, or UDP | shared memory (SDK) |
| stated update rate | | about 333 per second (UDP, documented) | about 60 per second (header) |
| measured update rate (median, longest gap) | | | |
| fields we need, with units | | | |
| stable over 10 laps? | | | |
| must be in the foreground? | | | |
| effort to set up (hours) | | | |
| cost and account | | | |
| recommended for the test sessions? | | | |

## 7. Phase 4: wheel, pedals, shaker

1. Install the vendor's configuration software for the wheel base and pedals (find the current
   name and version on the manufacturer's site; note it in `docs/SOURCES.md`).
2. Set the force limit **low** first. Raise it in steps once the rig is bolted down and the
   emergency procedure is on the card.
3. Calibrate the pedals (full travel, brake pressure curve). Save the profile and export it to
   `docs/rig-profiles/`.
4. Check that each sim sees the devices and that axes are not mixed up (brake on throttle is a
   classic).
5. Seat shaker: set its level in the sim, not in software that could add latency or hide
   telemetry. It is not read by anything.

## 8. Phase 5: network and clocks

1. Cable the three machines to the switch; set the fixed addresses from section 2; check
   `ping` both ways.
2. **AI machine as time reference** (Linux):
   ```bash
   sudo apt install chrony
   # /etc/chrony/chrony.conf: add
   #   local stratum 10
   #   allow 192.168.50.0/24
   sudo systemctl restart chrony
   chronyc tracking
   ```
3. **Windows machines** (administrator shell):
   ```
   w32tm /config /manualpeerlist:"192.168.50.30" /syncfromflags:manual /update
   w32tm /resync
   w32tm /query /status
   ```
4. Do not trust "synchronised". Task 4 **measures** the offset and drift between the machines, for
   an hour, and publishes the numbers with intervals. That error budget is what the timestamps in
   every recording are worth.

## 8b. Different setups to compare (task 8)

The delay a recording carries depends on the setup. Measure at least these and write the results in
one table:

| setup | what runs where |
|---|---|
| A | everything on the sim PC (reader, recorder, dashboard) |
| B | reader on the sim PC; recorder and dashboard on the evaluation PC, over the switch |
| C | reader on the sim PC; model requests go to the AI machine as well |
| D | B or C with the evaluation PC inline, adding delay and loss on purpose (or the same done in software) |

For each setup and at two sampling rates: median, 95th and 99th percentile of the delay, jitter, and the
share of samples lost. These numbers calibrate the SimPy model (`simlab/latency.py`) and are the value
ranges Group 2 uses to test timing faults. Until the rig is here, plan the measurement script and run it
between two laptops.

## 9. Phase 6: ROS 2

- **Version:** ROS 2 **Jazzy** (the long-term-support release for Ubuntu 24.04). It is a Tier 1
  platform on Ubuntu 24.04 for both amd64 and **arm64**, so the AI machine (DGX OS is Ubuntu 24.04
  on arm64) runs it natively. On Windows, Jazzy's Tier 1 platform is **Windows 10**, not Windows
  11; whether it works well on the delivered sim PC is something to **test**, not assume.
- **Two options for the sim PC side. Decide in task 5, write down why:**
  - **A. Bridge, no ROS 2 on the sim PC.** A small Python program reads the sim's shared memory
    and sends each sample, with its source timestamp, over the network (UDP or similar) to a ROS 2
    node on Linux that publishes it. Simple, and keeps the sim PC lean.
  - **B. ROS 2 on Windows.** One less hop; more setup risk.
- **Message:** one custom message with the source time in the header and the receive time as a
  separate field (draft in [docs/INTERFACE.md](docs/INTERFACE.md); agreed with Group 2 by 13 Nov).
- **Recording:** `ros2 bag record` the telemetry topic; replay with original timing; check that the
  stamps survive.
- Develop against the **mock stream** first. When the rig arrives, only the source changes.

## 10. Phase 7: recording, lap files, labelled sessions

1. Recorders (task 3) write [simlab/records.py](simlab/records.py) samples: `source_t`,
   `receive_t`, values.
2. The converter (task 7) turns a recording into a lap file in the layout of
   [docs/INTERFACE.md](docs/INTERFACE.md). **Done** when
   `python -m claimcheck.validate lapfile.vbo` (from the lab repository) reports no error, and
   the checker loads it.
3. Labelled sessions: Group 2's scenario catalogue (Group 2's task 2) contains **driving cards**, one-line
   instructions such as "brake 10 m earlier at T3". Drive them, record, and store with each
   session: the card, driver, car, track, sim, date, rig settings. At least 10 sessions of 6+
   laps by the end of January.

## 10b. Phase 7b: the data pipeline and the dashboard (tasks 6 and 9)

**Data pipeline.** One command takes a raw recording to a checked, stored session:

1. **Store:** one folder per session with the samples, and a `meta.json` holding simulator, car, track,
   driver, scenario card, clock offset and software versions.
2. **Check:** gaps longer than two sample periods, jumps, impossible values (negative speed, throttle
   above 100 %), duplicates, and time running backwards. `simlab.records.check_stamps` is the start.
   Every problem is written into a quality report; nothing is repaired silently.
3. **Cut into laps** and keep the lap boundaries in the stored session.
4. **Replay** a stored session at its original timing, so that the dashboard and the AI work can use
   recorded sessions exactly like live ones.

**Interface tests (task 9).** An interface is the place where one part hands data to the next: game to
reader, reader to ROS 2, ROS 2 to pipeline, pipeline to lap file, lap file to Group 2's checker. Test each one.
The code to start from is already here and in the lab repository: `tests/test_records.py` (timestamps),
`simlab/records.py` (`check_stamps`), and in the lab repository `claimcheck.validate` (lap files),
`tests/test_validate.py` and `tests/test_web.py` (the reporting). Run them, read them, extend them.

**Dashboard on the evaluation PC** (shown on the second monitor). **It pulls the data and evaluates it**: it
reads stored sessions or a live stream, runs Group 2's checker on them, and shows the checker's answers next
to the known answers for the labelled sessions. It also shows: speed, throttle and brake traces; lap times;
the delay of the data chain and the share of lost samples; and the output of the AI model. Choose the
simplest tool that updates at least five times a second, write down why you chose it, and keep it running
without a keyboard. **This dashboard is what you present at the end.**

## 11. Phase 8: the AI machine

1. First boot, create the account, update. Put it on the switch with its fixed address.
2. Check the GPU and the stack: `nvidia-smi`, and the vendor's quick checks. It is an arm64
   machine: packages and Python wheels must have arm64 builds.
3. Install ROS 2 Jazzy (phase 6) and `chrony` (phase 5).
4. Pick a model server (for example llama.cpp, vLLM or Ollama; compare briefly, note why) and a
   small open model. Serve it on the network.
5. **Choosing a model (task 10).** Pick at least three open models of different sizes that fit in the
   machine's memory. Give each the same two jobs: (a) turn a one-sentence claim into a structured test
   (Group 2's claim test set is the benchmark once it exists; until then use 20 sentences you write
   yourselves, in English and German), and (b) summarise a lap from numbers. For each model measure the
   time to the first word, words per second, memory use, and correctness on a fixed test set, repeating
   every run five times. Put the results in one table and recommend one model, with the reason.
6. **Cost of a request.** Measure the latency from the sim PC for three prompt sizes. The question the
   copilot will ask later is how long an answer takes, so measure the whole round trip, not just inference.
7. It is **separate from the sim PC on purpose**: load on the AI machine must not slow the sim.

## 12. Phase 9: cameras

Two Logitech MX Brio. Capture with a tool that gives you **frame timestamps** (not just a video
file). Measure the offset between video and telemetry from a known visual event (for example a
brake-light or an LED you switch together with a logged signal). Count dropped frames over ten
minutes. Video files are large and never go into git.

## 13. Phase 10, stage 2: raw wheel and pedal data, heart rate

Only after phases 3 to 7 work.

- **Raw inputs:** read the steering angle and pedal positions straight from the input devices
  and align them with the sim's telemetry, so you can see what the driver did, not only what the
  car did.
- **Polar H10:** heart rate and RR intervals use the standard Bluetooth heart-rate service
  (GATT service `0x180D`), which any BLE library can read. **ECG (130 Hz) uses Polar's own
  Measurement Data service**, documented in the Polar BLE SDK repository
  (`polarofficial/polar-ble-sdk`). The evaluation PC has Bluetooth 5.4. Python libraries such as
  `bleak` and `bleakheart` can read both; check their licences.
- Whatever you read, stamp it with both clocks and state the alignment error.
- Consent: a heart-rate recording of a person is personal data. **Ask Luke before recording
  anyone other than yourself**, and never publish a recording with a name on it.

## 14. Checklists

**Rig is "done" (end of task 2):**
- [ ] UPS test shutdown passed
- [ ] emergency procedure on a card at the rig
- [ ] backup image of the vendor installation exists
- [ ] rFactor 2, Assetto Corsa and iRacing each: 10 laps driven, telemetry read back
- [ ] real update rate of each measured and written in the comparison table
- [ ] all three machines on the switch, addresses in the table, `ping` both ways
- [ ] clock reference running; offset measured (task 4)
- [ ] a person who has not touched the rig has followed this README from a fresh start

**Before every recording session:**
- [ ] clocks synchronised and checked
- [ ] disk space on the sim PC
- [ ] Windows updates paused
- [ ] session card filled in (sim, car, track, driver, scenario card, rig settings)
- [ ] recorder started before the car moves, stopped after it stops

## 15. Troubleshooting

| you see | try |
|---|---|
| Python cannot open a sim's shared memory | Python from the Microsoft Store? Install from python.org. Sim not running or not on track? |
| rFactor 2 plugin missing in the plugin list | VC12 runtime installed? DLL in `Bin64\Plugins`? Restart the game |
| Telemetry values frozen | The sim lost focus or is paused; some interfaces only update while driving |
| Wheel or pedals drop out | USB selective suspend; different USB port; cable |
| Timestamps jump | clock stepped by a sync service; check `w32tm` / `chronyc` logs; this is why we log both clocks |
| Latency grows during a long session | processing slower than the sampling period (see `simlab.latency`), or the disk is slow |
| ROS 2 nodes on two machines do not see each other | firewall, different subnets, different ROS domain ID |

## 16. Sources

Keep links, versions and licences in `docs/SOURCES.md`. Starting points:
the rF2 shared-memory plugin repository (`TheIronWolfModding/rF2SharedMemoryMapPlugin`),
`pyirsdk` (`kutu/pyirsdk`), the ROS 2 Jazzy release and installation pages, the DGX OS 7 user
guide, the Polar BLE SDK repository (`polarofficial/polar-ble-sdk`), `bleakheart`.

## Repository

- `simlab/records.py`: the sample format with two clocks; `check_stamps` finds bad timestamps
- `simlab/mock_source.py`: a synthetic session as a stream, before the rig exists
- `simlab/latency.py`: SimPy skeleton of the latency chain (task 8 starts here)
- `tests/`: run `uv run pytest`

How we work (the weekly rhythm is in [docs/WORKFLOW.md](docs/WORKFLOW.md)): `main` here is protected and changes only through your weekly merge request to Luke; in your group's fork you work on one branch per task (`ros2-bridge`), merge by merge request
with one teammate's review and green tests; **done** means merged, tests pass, one command
reproduces the result, and this README or a docstring says how to run it.
