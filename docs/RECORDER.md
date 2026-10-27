# Recording Assetto Corsa

This is the reader code that task 3 talks about, for Assetto Corsa. It records the game
and shows a small live page in your browser. It writes the same files you got from our
lab rig on 27 October, so code you write for those files also works on your own
recordings.

## What you need

- Assetto Corsa (Steam) on a Windows PC, or on Linux with Proton.
- Python 3.10 or newer and this repository installed (README, section 3).
- Nothing to switch on in the game. While a session runs, AC sends its data on UDP port 9996.

## Record

1. Start Assetto Corsa and start a session (any car, any track).
2. In this repository, run:
   ```bash
   uv run python -m simlab.ac_recorder
   ```
   - The game runs on another PC? Add `--host <its IP address>`.
   - You want to open the page from another PC? Add `--lan`.
3. Open http://localhost:8765. The status says **connected** and you see the speed.
4. Type a driver code (for example `S01`, never a name). Add a note if you like (for example `card 1`). Press **Start**.
5. Drive. Recording starts the next time the car crosses the start line, so every file begins with a whole lap.
6. Press **Stop** when you are done. In the game, Esc then Restart also ends the file; the next
   one starts at the next line crossing.

## The files

They go to `recordings/<code>/<date>/`. Git ignores this folder: never commit recordings.

| File | What is in it |
|---|---|
| `ac_<date>-<time>.jsonl` | Every datagram as it arrived, with two clocks: `source_t` (the game's time) and `receive_t` (this PC's clock). It is the format of `simlab.records`, so `read_jsonl` and `check_stamps` work on it. About 12 MB per minute. |
| `ac_<date>-<time>.100hz.csv` | The same on a fixed grid, one row every 10 ms of game time. The columns are the first 48 columns of the 27 October files, in the same order. |
| `ac_<date>-<time>.laps.json` | One entry per lap: lap number, lap time in ms, `complete`, top speed, peak g, `impact`, `best`. |
| `ac_<date>-<time>.json` | Car, track, layout, driver code, note, and the start time in UTC. |

You can rebuild the CSV and the laps file from a `.jsonl` at any time:

```bash
uv run python -m simlab.ac_files recordings/S01/2026-11-02/ac_20261102-141500.jsonl
```

## Use it in your own code

```python
from simlab.ac_telemetry import Connection, parse

with Connection("127.0.0.1") as game:
    print(game.car, game.track, game.layout)
    for receive_t, raw in game.datagrams():
        v = parse(raw)
        print(v["kmh"], v["gear"], v["lap"])
```

## Differences from our lab files

- Our lab files also have tyre temperatures, tyre pressures and tyre wear. They come from a small
  app inside the game, which is not part of this reader. Your CSV has the first 48 columns.
- In `.laps.json`, `complete` means the same as `valid` in our files: the car crossed the line at
  both ends of the lap. The first lap after Esc then Restart starts in the pits, so it is never complete.

## Known limits (your task 3)

- Assetto Corsa only. The readers for rFactor 2 and iRacing are yours to write.
- The data layout is documented by players, not by the game maker. What we measured is written at the
  top of `simlab/ac_telemetry.py`. Check the rest against a real drive.
- The CSV is made when you press Stop. For a 20-minute drive this takes a few seconds.
- The page is only open on your own PC, unless you start the recorder with `--lan`.

The tests (`tests/test_ac.py`) run the whole recorder against a fake game, so they work without
Assetto Corsa installed.
