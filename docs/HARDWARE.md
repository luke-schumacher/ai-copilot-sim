# The hardware

What the simulator rig is made of, what each part does in our project, and what you should check
when it arrives. The setup guide is the README of the repository `ai-copilot-sim`. The PDF hardware sheet
has the same content as this page.

**Status:** planned. **Delivery date not confirmed**: mid-November at the very earliest, and probably later.
Until then you work on laptops with the mock stream (README, section 3b). On Friday 11 December we decide
what happens if the rig has still not arrived.

## The five main parts

| # | part | specification | what it does for us |
|---|---|---|---|
| 1 | **Simulator** (Bernax GT simulator) | Turnkey driving simulator, installed and explained in Aachen. Monitor stand, LTEC GT seat with the wheel mount, mounted seat shaker. Simagic Alpha base, DTM-style wheel (GT NEO or GTC, not yet decided), P1000 two-pedal set. | The driver sits here. Wheel and pedals are the driver's inputs. |
| 1a | **Sim PC** (part of the simulator) | Game PC, fully installed with software. RTX 5070 graphics card, 32 GB RAM, recent Ryzen 7 or Ultra 7 processor, 1 TB SSD, network port. | Runs the three games. This is where the telemetry comes from. |
| 1b | **Monitor** (part of the simulator) | 49″ curved, 144 Hz or more, 1800R. | What the driver sees. |
| 2 | **AI machine** (ASUS Ascent GX10, a DGX Spark class machine) | NVIDIA GB10 Grace Blackwell processor (10 Cortex-X925 and 10 Cortex-A725 cores), 128 GB shared LPDDR5X memory, 1 TB M.2 PCIe 4.0 SSD, up to 1000 TOPS (a measure of AI computing speed), 10 Gbit/s Ethernet (10GBase-T), two QSFP56 network ports, Wi-Fi 7. Runs NVIDIA DGX OS (Linux, Ubuntu-based, **arm64**). | Runs local AI models. Also a second Linux machine for ROS 2. |
| 3 | **Evaluation PC** (ASUS ExpertCenter PN54) | AMD Ryzen AI 7 350, 32 GB DDR5-5600, 1 TB M.2 PCIe 4.0 SSD, Windows 11 Pro, two 2.5 Gbit/s Ethernet ports, USB4, Wi-Fi 7, Bluetooth 5.4. | Recording, evaluation and the dashboard. Bluetooth for the heart-rate strap. |
| 4 | **Second monitor** (Dell Pro 27 Plus P2725D) | 27″ IPS, 2560×1440, 100 Hz, matte, HDMI and DisplayPort. | Shows the dashboard and the model output next to the evaluation PC. |

If the ASUS ExpertCenter cannot be delivered, we use a **Minisforum MS-A2** instead: AMD Ryzen 9 9955HX
(16 cores), 32 GB DDR5, 1 TB NVMe SSD, two 2.5 Gbit/s Ethernet ports and two 10 Gbit/s SFP+ ports, Wi-Fi 6E.
You would learn which one arrives from me.

## The small parts

| # | part | specification | what it does for us |
|---|---|---|---|
| 5 | **Network switch** (Netgear GS308E) | 8 ports, Gigabit Ethernet, managed through a web page, fanless. | Connects the three machines in one network we can observe and measure. |
| 6 | **Two webcams** (Logitech MX Brio) | 4K at 30 frames per second, 1080p at 60, autofocus, two microphones. | Driver and scene video (task 11). |
| 7 | **Battery backup** (APC Back-UPS 950 VA) | 950 VA / 520 W, four protected sockets, USB link to the PC. | Lets the rig shut down cleanly when the power fails. |
| 8 | **Two chest straps** (Polar H10) | Heart rate and beat-to-beat intervals over Bluetooth Low Energy and ANT+, ECG trace, waterproof to 30 m, about 400 hours battery. | Heart rate and an ECG trace (task 11). |

## The games

| game | how we get it | what it gives us |
|---|---|---|
| rFactor 2 | Steam, with extra cars and tracks | A plugin that exposes telemetry (README, section 6). |
| Assetto Corsa Ultimate Edition | Steam, base game plus 12 car and track packs | Shared memory and a UDP stream. |
| iRacing | 24-month membership | A telemetry SDK. |

Who holds the Steam and iRacing accounts is still open: I (Luke) clarify it. Until then, whoever already owns
a game can use it to try the reader code.

## How the machines connect

```
Sim PC  ---+
           |
AI machine +--- Switch (8 ports) ---  Evaluation PC --- Second monitor
           |
     (cameras and chest straps connect to the evaluation PC and the sim PC)
```

All three machines sit on the switch. The evaluation PC runs Windows 11 and the AI machine runs Linux on arm64.
Both facts matter for ROS 2: the README, section 9, says what works where.

## What to check when it arrives

- [ ] Every part on the lists above is there and undamaged.
- [ ] The sim PC specification matches (graphics card, RAM, processor, SSD): write the real values into the README.
- [ ] Which wheel arrived (GT NEO or GTC) and which firmware version the wheel base has.
- [ ] Whether the sim PC has Bluetooth.
- [ ] The Windows version and what is already installed on the sim PC.
- [ ] Make a backup image of the sim PC **before** you change anything (README, task 2).
