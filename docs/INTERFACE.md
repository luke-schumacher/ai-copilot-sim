# The interface to Group 2

Group 1 delivers **lap files** and, for live use, a **ROS 2 topic**. Group 2 owns the contract
(`docs/LAP-FORMAT.md` in `ai-copilot-lab`) and the validator
(`python -m claimcheck.validate file.vbo`). **Draft: agreed by 13 November** between your S5 and
S6 and their T8.

## Lap files

The layout of a Racelogic VBOX `.vbo` file, with the channel names and units in the lab
repository's LAP-FORMAT.md: time, position in minutes (longitude positive west), `velocity kmh`,
`throttle_pct`, `brake_bar`, `steering_deg`, `accel_lat_g`, and so on. Your converter (S6) writes
them. A file is acceptable when the validator reports no error and the checker loads it.

Things you will have to decide with Group 2:
- which of the channels each sim can really supply, and in which unit
- how a sim's own lap timing maps to the start/finish gate in `[laptiming]`
- which car constants (wheelbase, steering ratio) each sim uses

## ROS 2 topic (draft)

Topic `/telemetry`, one message per sample:

```
std_msgs/Header header                    # stamp = source time (the sim's clock)
builtin_interfaces/Time received          # when the recorder got it (the recorder's clock)
string sim                                # rfactor2 | ac | iracing
float32 speed_kph
float32 throttle_pct
float32 brake_bar
float32 steering_deg
float32 accel_lat_g
float32 accel_long_ms2
float64 latitude_deg
float64 longitude_deg
uint32 lap_number
```

Open questions: how a sim without GPS gives position (a sim has track coordinates, not
latitude and longitude); the sampling rate; what a missing field looks like.

## Timestamps, the part that matters most

- Two clocks, always: `source_t` and `receive_t`. Never merge them.
- `source_t` must strictly increase; `receive_t` must not go backwards.
- State the measured clock offset (S4) next to every recording.
- A late or lost sample is data, not something to repair silently.
