# AI Copilot for Racesimulation: the simulator rig

Code and setup guide for **Group 1**, WS 2026/27, FH Aachen. The rig arrives
prebuilt; your job is to turn it into a measured, documented data source for the AI
copilot. This README is the setup guide. **Keep it true**: when you find a step that is
wrong or missing, fix it in a pull request. Task S1 is finished when someone who has
never touched the rig can follow it from a fresh machine.

Start with [docs/START-HERE.md](docs/START-HERE.md) (your first week). Tasks, squads
and hours: [docs/TASKS.md](docs/TASKS.md). What you hand to Group 2:
[docs/INTERFACE.md](docs/INTERFACE.md). The rule about data:
[docs/DATA-RULE.md](docs/DATA-RULE.md).

**The rig is not here yet.** Delivery is mid-November at the very earliest, and probably
later. That is why most of this guide, and most of your work until December, is built and
tested **without** the rig, against the mock stream in this repository. Section 3b says what
to do while you wait, and what happens on 11 December if it has still not arrived.

---

## 1. What you are setting up

| machine / part | what it is | role |
|---|---|---|
| **Sim PC** | Bernax GT Track: built-in PC with software installed, 49″ curved monitor | runs the sims; the telemetry source |
| Wheel base, wheel, pedals | Simagic Alpha EVO base, X-330 wheel, P1000 dual pedals | driver input; later read raw (S10) |
| Seat shaker, FIA-approved seat, frame | part of the set | not read by software, but part of the rig |
| **AI machine** | ASUS Ascent GX10: NVIDIA GB10, 128 GB unified memory, 1 TB SSD, Linux (DGX OS, Ubuntu 24.04, arm64) | local model server; runs ROS 2 |
| **Evaluation PC** | ASUS ExpertCenter PN54: Ryzen AI 7 350, 32 GB, Windows 11, two 2.5 GbE ports, Bluetooth 5.4 | recording, evaluation, network experiments, BLE for the heart-rate strap |
| Switch | Netgear GS308E, 8-port | one observable network for all three machines |
| Second monitor | Dell 27″ QHD | telemetry and model output |
| Cameras | 2 × Logitech MX Brio (4K) | driver and scene video (S8) |
| UPS | APC Back-UPS BX950MI | clean shutdown; protects the rig |
| Chest straps | 2 × Polar H10 | heart rate, RR intervals, ECG (S10) |
| Software | rFactor 2 (Steam), Assetto Corsa Ultimate Edition (Steam), iRacing (24-month membership) | the three sims |

Source: the proposal "Lehrdemonstrator KI-Co-Pilot im Rennsimulator" and its supplier
offers. **Details not known until delivery** (fill in during S1):

| unknown | where to look | answer |
|---|---|---|
| Sim PC: Windows version, CPU, GPU, RAM, free disk | System settings, `msinfo32` | |
| Does the sim PC have Bluetooth? | Device Manager | |
| What is already installed on the sim PC? | Programs list; ask the vendor | |
| Which accounts own the Steam and iRacing licences? | Luke | |
| Wheel base peak torque setting and firmware | Simagic software | |

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
  inject the faults in software inside your bridge, is a decision for S5 and S7. Write down
  the decision and why.
- **Clocks:** three machines, three clocks. Decide who is the time reference (suggestion:
  the AI machine, running `chrony` as a local NTP server), measure the offset and drift
  (S4), and record both timestamps in every sample (`source_t`, `receive_t`, see
  [simlab/records.py](simlab/records.py)). Never overwrite one with the other.

| machine | address | OS | role |
|---|---|---|---|
| sim PC | | | |
| evaluation PC | | | |
| AI machine | | | |

## 3. Phase 0: before the rig arrives (weeks 1 to 6)

Everything here runs on your laptops.

1. One person per group forks this repository (public, no invitation needed) and adds the group as collaborators; everyone clones the fork, and also clones `ai-copilot-lab` next to it. Then (this is real work, not waiting: see 3b):
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
   (phase 5). You are developing the method for S4 now, so the real measurement is quick.
4. Read the sim telemetry interfaces (phases 3.1 to 3.3). Do not write against them yet:
   without the sims running you cannot tell whether you read them right.
5. Prepare the checklists in section 14 as files you will tick on the day.

## 3b. While the rig is late

Delivery date: mid-November at the earliest. Nobody can promise more. Until it arrives, every
task has a part that needs no rig:

| task | do now, without the rig | changes when the rig arrives |
|---|---|---|
| S2, S3 readers | write the reader interface; unit-test it on **canned buffers** (byte dumps that look like the sim's memory); read the interface documentation for each sim | run it against the real sim; measure the real update rate |
| S4 clocks | develop and test the measurement method on two laptops | repeat on the three real machines |
| S5 ROS 2 | mock stream, message definition, bag record and replay | swap the mock for the real recorder |
| S6 lap files | converter from recordings (mock first) that passes the validator | convert real sessions; drive the labelled sessions |
| S7 latency model | build it with assumed values; change them and see what moves | calibrate it against the measurements from S4 |
| S8 cameras | capture tool on a laptop webcam | the two MX Brio cameras |
| S9 AI machine | run a small model server on a laptop; measure latency at three prompt sizes | move it to the AI machine |
| S10 stage 2 | parsers for the heart-rate and raw-input data, tested on canned packets | the real straps and devices |
| S1 rig bring-up | read this guide end to end; prepare the checklists; list what is unknown | the actual bring-up |

**Where a real sim helps even before the rig:** rFactor 2 and Assetto Corsa run on an ordinary
Windows PC. If the licences are available (Luke clarifies who buys them), the readers in S2 and S3
can be tried against the real sims on a student's own PC, with a gamepad or a wheel.

**Decision point, Friday 11 December.** If the rig has not been delivered by then, the labelled
sessions for S6 (and therefore Group 2's transfer experiment) are driven on any Windows PC with
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

1. Make a **backup image** of the vendor's installation before you change anything (S1
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

### 3.1 rFactor 2 (plugin interface)

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
6. S2 builds the recorder on top of this.

### 3.2 Assetto Corsa

Assetto Corsa publishes telemetry through memory-mapped files, no plugin required: three
blocks named `acpmf_physics`, `acpmf_graphics` and `acpmf_static`. Read them from Python with
`mmap` and `ctypes` structures. Find the official shared-memory reference and link it in
`docs/SOURCES.md`; check any third-party reader library's licence before you use it. Remember:
**not the Microsoft Store Python**.

### 3.3 iRacing

iRacing exports telemetry through a memory-mapped file called `Local\IRSDKMemMapFileName`, with
a header that states the data version and the update rate (usually 60 Hz) and a tick counter. The
Python library `pyirsdk` reads it (`pip install pyirsdk`). iRacing must be running with a car on
track. Telemetry is only available while you drive.

### Sim comparison table (S3 fills this in)

| | rFactor 2 | Assetto Corsa | iRacing |
|---|---|---|---|
| interface | plugin, shared memory | shared memory | shared memory (SDK) |
| stated update rate | | | ~60 Hz (header) |
| measured update rate | | | |
| fields we need and their units | | | |
| needs the sim in the foreground? | | | |

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
4. Do not trust "synchronised". S4 **measures** the offset and drift between the machines, for
   an hour, and publishes the numbers with intervals. That error budget is what the timestamps in
   every recording are worth.

## 9. Phase 6: ROS 2

- **Version:** ROS 2 **Jazzy** (the long-term-support release for Ubuntu 24.04). It is a Tier 1
  platform on Ubuntu 24.04 for both amd64 and **arm64**, so the AI machine (DGX OS is Ubuntu 24.04
  on arm64) runs it natively. On Windows, Jazzy's Tier 1 platform is **Windows 10**, not Windows
  11; whether it works well on the delivered sim PC is something to **test**, not assume.
- **Two options for the sim PC side. Decide in S5, write down why:**
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

1. Recorders (S2, S3) write [simlab/records.py](simlab/records.py) samples: `source_t`,
   `receive_t`, values.
2. The converter (S6) turns a recording into a lap file in the layout of
   [docs/INTERFACE.md](docs/INTERFACE.md). **Done** when
   `python -m claimcheck.validate lapfile.vbo` (from the lab repository) reports no error, and
   the checker loads it.
3. Labelled sessions: Group 2's scenario catalogue (T1) contains **driving cards**, one-line
   instructions such as "brake 10 m earlier at T3". Drive them, record, and store with each
   session: the card, driver, car, track, sim, date, rig settings. At least 10 sessions of 6+
   laps by the end of January.

## 11. Phase 8: the AI machine

1. First boot, create the account, update. Put it on the switch with its fixed address.
2. Check the GPU and the stack: `nvidia-smi`, and the vendor's quick checks. It is an arm64
   machine: packages and Python wheels must have arm64 builds.
3. Install ROS 2 Jazzy (phase 6) and `chrony` (phase 5).
4. Pick a model server (for example llama.cpp, vLLM or Ollama; compare briefly, note why) and a
   small open model. Serve it on the network.
5. S9 measures the latency from the sim PC for three prompt sizes and writes it down. The question
   the copilot will ask later is how long an answer takes, so measure the whole round trip, not just
   inference.
6. It is **separate from the sim PC on purpose**: load on the AI machine must not slow the sim.

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

**Rig is "done" (end of S1):**
- [ ] UPS test shutdown passed
- [ ] emergency procedure on a card at the rig
- [ ] backup image of the vendor installation exists
- [ ] rFactor 2, Assetto Corsa and iRacing each: 10 laps driven, telemetry read back
- [ ] real update rate of each measured and written in the comparison table
- [ ] all three machines on the switch, addresses in the table, `ping` both ways
- [ ] clock reference running; offset measured (S4)
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
- `simlab/latency.py`: SimPy skeleton of the latency chain (S7 starts here)
- `tests/`: run `uv run pytest`

How we work (the weekly rhythm is in [docs/WORKFLOW.md](docs/WORKFLOW.md)): `main` here is protected and changes only through your weekly pull request to Luke; in your group's fork you work on one branch per task (`s5-ros2-bridge`), merge by pull request
with one teammate's review and green tests; **done** means merged, tests pass, one command
reproduces the result, and this README or a docstring says how to run it.
