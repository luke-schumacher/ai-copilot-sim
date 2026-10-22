# Comparing the three games (task 3)

Fill this in as you test. How to test is in the README, section 6.5. Same kind of car and the same track in
all three games, 10 laps each, recorded with the reader.

| | rFactor 2 | Assetto Corsa | iRacing |
|---|---|---|---|
| how the data comes out | plugin and shared memory | shared memory, or UDP | shared memory (SDK) |
| stated update rate | | about 333 per second (UDP, documented) | about 60 per second (header) |
| measured update rate (median, longest gap) | | | |
| fields we need, with units |Velocity (m/s, vector), throttle (0–1), brake input (0–1), steering input (−1 to +1), local XYZ position (m), lap information |Speed (km/h), gas (0–1), brake input (0–1), steering (unit to verify), local XYZ coordinates, completed laps |Speed (m/s), throttle (0–1), brake input (0–1), steering wheel angle (rad), lateral acceleration (m/s²), lap progress; brake line pressure channels (bar) |
| stable over 10 laps? | | | |
| must be in the foreground? | | | |
| effort to set up (hours) | | | |
| cost and account | | | |
| recommended for the test sessions? | | | |

## Recommendation

(Which game or games, and why. Agreed with Luke at a direction call on: )
