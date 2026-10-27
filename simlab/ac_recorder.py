"""
Record Assetto Corsa and watch it live in the browser.

    python -m simlab.ac_recorder                     # the game runs on this PC
    python -m simlab.ac_recorder --host 10.0.0.5     # the game runs on another PC
    python -m simlab.ac_recorder --lan               # also open the page from other PCs

Then open http://localhost:8765, type a driver code, press Start and drive. Recording
starts when the car next crosses the start line, so every file begins with a whole lap.
Press Stop when you are done. Each recording becomes four files in
`recordings/<code>/<date>/`:

    ac_<date>-<time>.jsonl        every datagram as it arrived (simlab.records format)
    ac_<date>-<time>.100hz.csv    the same on a 100 Hz grid (see simlab.ac_files)
    ac_<date>-<time>.laps.json    one summary per lap
    ac_<date>-<time>.json         car, track, driver code, note, start time

Esc -> Restart in the game closes the current file; the next one starts at the next
line crossing. Use driver codes, never names. Recordings never go into git.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

from simlab import ac_files
from simlab.ac_telemetry import PORT, Connection, GameClock, parse

CODE = re.compile(r"^[A-Za-z0-9_-]{1,20}$")
LAPS_SHOWN = 8


def _short(x):
    """Six significant digits are plenty and keep the file a third of the size."""
    return float(f"{x:.6g}") if isinstance(x, float) else x


class Recorder:
    """Reads the game on one thread; the page asks for state and sends Start and Stop."""

    def __init__(self, host: str = "127.0.0.1", port: int = PORT, out: str | Path = "recordings") -> None:
        self.addr = (host, port)
        self.out = Path(out)
        self.lock = threading.Lock()
        self.want = False
        self.driver = self.note = ""
        self.status = "waiting for the game"
        self.game = {"car": "", "track": "", "layout": ""}
        self.live: dict = {}
        self.laps: list = []
        self.saved: list = []
        self._file = None
        self._path: Optional[Path] = None
        self._clock = GameClock()
        self._written = 0
        self._prev_lap: Optional[int] = None
        self._rate = [time.monotonic(), 0, 0.0]   # window start, count, last rate
        self._stop = threading.Event()
        self._jobs: list = []

    # -- commands from the page -------------------------------------------------

    def start(self, driver: str, note: str = "") -> None:
        if not CODE.match(driver):
            raise ValueError("Driver code: letters, digits, - or _ only, at most 20. Never a name.")
        with self.lock:
            self.driver, self.note, self.want = driver, note.strip()[:200], True

    def stop(self) -> None:
        with self.lock:
            self.want = False
            self._close()

    def state(self) -> dict:
        with self.lock:
            return {"status": self.status, "game": self.game, "live": self.live, "laps": self.laps[-LAPS_SHOWN:],
                    "recording": self._path.name if self._path else "", "armed": self.want,
                    "driver": self.driver, "written": self._written, "saved": self.saved[-5:]}

    # -- the game ---------------------------------------------------------------

    def run(self) -> None:
        """Connect, read until the game goes quiet, reconnect. Runs until `shutdown`."""
        while not self._stop.is_set():
            try:
                with Connection(*self.addr) as game:
                    with self.lock:
                        self.game = {"car": game.car, "track": game.track, "layout": game.layout}
                        self.status = "connected"
                    for receive_t, raw in game.datagrams():
                        self._handle(receive_t, raw)
                        if self._stop.is_set():
                            break
            except OSError:
                pass
            with self.lock:
                self._close()
                self.status = "waiting for the game"
                self._prev_lap = None
            self._stop.wait(1.0)

    def shutdown(self) -> None:
        self._stop.set()
        self.stop()
        for job in self._jobs:
            job.join()

    def _handle(self, receive_t: float, raw: bytes) -> None:
        v = parse(raw)
        with self.lock:
            prev, self._prev_lap = self._prev_lap, v["lap"]
            crossed = prev is not None and v["lap"] > prev
            restarted = prev is not None and v["lap"] < prev
            if crossed:
                self.laps.append({"n": prev + 1, "ms": v["last_lap_ms"]})
            if restarted:
                self._close()           # a new stint gets a new file
            if self.want and self._file is None and crossed:
                self._open()
            if self._file is not None:
                t = self._clock.update(v["lap_time_ms"], v["lap"], v["last_lap_ms"])
                if t is not None:
                    line = {"source_t": t, "receive_t": receive_t, **{k: _short(x) for k, x in v.items()}}
                    self._file.write(json.dumps(line) + "\n")
                    self._written += 1
            w = self._rate
            w[1] += 1
            if receive_t - w[0] >= 1.0:
                w[2], w[0], w[1] = w[1] / (receive_t - w[0]), receive_t, 0
            self.live = {"kmh": round(v["kmh"]), "gear": v["gear"], "rpm": round(v["rpm"]),
                         "gas": round(v["gas"], 2), "brake": round(v["brake"], 2), "lap": v["lap"] + 1,
                         "lap_time_s": round(v["lap_time_ms"] / 1000, 1), "in_pit": v["in_pit"],
                         "per_s": round(w[2])}
            self.status = ("recording" if self._file else
                           "armed: recording starts at the start line" if self.want else "connected")

    # -- files (called with the lock held) --------------------------------------

    def _open(self) -> None:
        now = dt.datetime.now()
        folder = self.out / self.driver / now.strftime("%Y-%m-%d")
        folder.mkdir(parents=True, exist_ok=True)
        self._path = folder / f"ac_{now:%Y%m%d-%H%M%S}.jsonl"
        self._file = self._path.open("w", encoding="utf-8")
        self._clock, self._written = GameClock(), 0
        meta = {**self.game, "driver": self.driver, "note": self.note,
                "started_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds"),
                "receive_t_at_start": time.monotonic(),
                "about": "receive_t is this PC's monotonic clock; receive_t_at_start ties it to UTC."}
        self._path.with_suffix(".json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

    def _close(self) -> None:
        if self._file is None:
            return
        self._file.close()
        path, self._file, self._path = self._path, None, None
        # The CSV takes a few seconds for a long drive; the game must not wait for it.
        job = threading.Thread(target=self._convert, args=(path,), daemon=True)
        self._jobs.append(job)
        job.start()

    def _convert(self, path: Path) -> None:
        written = ac_files.write(path)
        with self.lock:
            self.saved.append(str(path.parent / path.stem) + ".*")
        print("saved", path, *[p.name for p in written])


PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>AC recorder</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family:system-ui,sans-serif;margin:20px;background:#f6f7f9;color:#1f2328}
.row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.box{background:#fff;border:1px solid #d0d7de;border-radius:8px;padding:12px 16px;min-width:120px}
.big{font-size:44px;font-weight:700}.small{color:#6b7280;font-size:13px}
.bar{height:14px;background:#e5e7eb;border-radius:7px;overflow:hidden;width:220px}
.bar div{height:100%}#gas div{background:#16a34a}#brake div{background:#dc2626}
#status{font-weight:600}.rec{color:#dc2626}
button{font-size:16px;padding:8px 18px;border-radius:6px;border:1px solid #888;cursor:pointer}
input{font-size:16px;padding:7px;border:1px solid #888;border-radius:6px}
table{border-collapse:collapse}td{padding:2px 12px 2px 0}
</style></head><body>
<h2>Assetto Corsa recorder</h2>
<div class="row"><div class="box">Status: <span id="status">-</span><div class="small" id="game"></div></div></div>
<div class="row">
 <div class="box"><div class="small">km/h</div><div class="big" id="kmh">-</div></div>
 <div class="box"><div class="small">gear</div><div class="big" id="gear">-</div></div>
 <div class="box"><div class="small">rpm</div><div class="big" id="rpm">-</div></div>
 <div class="box"><div class="small">lap</div><div class="big" id="lap">-</div><div class="small" id="laptime"></div></div>
</div>
<div class="row"><div class="box">
 <div class="small">gas</div><div class="bar" id="gas"><div></div></div>
 <div class="small">brake</div><div class="bar" id="brake"><div></div></div>
 <div class="small" id="rate"></div></div>
 <div class="box"><div class="small">last laps</div><table id="laps"></table></div></div>
<div class="row"><div class="box">
 Driver code <input id="driver" size="8" placeholder="S01"> Note <input id="note" size="24" placeholder="card 1">
 <button onclick="send('start')">Start</button> <button onclick="send('stop')">Stop</button>
 <div class="small" id="msg"></div><div class="small" id="saved"></div></div></div>
<script>
const $=id=>document.getElementById(id);
const fmt=ms=>ms==null?'-':Math.floor(ms/60000)+':'+((ms%60000)/1000).toFixed(3).padStart(6,'0');
async function send(cmd){
 const body=JSON.stringify({driver:$('driver').value.trim(),note:$('note').value});
 const r=await fetch('/'+cmd,{method:'POST',body});const j=await r.json();$('msg').textContent=j.error||'';}
async function tick(){
 try{const s=await (await fetch('/state')).json();const l=s.live||{};
  $('status').textContent=s.status+(s.recording?' ('+s.recording+', '+s.written+' samples)':'');
  $('status').className=s.status=='recording'?'rec':'';
  $('game').textContent=[s.game.car,s.game.track,s.game.layout].filter(x=>x).join(' / ');
  for(const k of ['kmh','rpm','lap'])$(k).textContent=l[k]??'-';
  $('gear').textContent=l.gear==null?'-':l.gear<0?'R':l.gear==0?'N':l.gear;
  $('laptime').textContent=l.lap_time_s==null?'':l.lap_time_s+' s'+(l.in_pit?' (pits)':'');
  $('gas').firstChild.style.width=(100*(l.gas||0))+'%';$('brake').firstChild.style.width=(100*(l.brake||0))+'%';
  $('rate').textContent=l.per_s?l.per_s+' datagrams per second':'';
  $('laps').innerHTML=s.laps.slice().reverse().map(x=>'<tr><td>lap '+x.n+'</td><td>'+fmt(x.ms)+'</td></tr>').join('');
  $('saved').textContent=s.saved.length?'Saved: '+s.saved.join(', '):'';
 }catch(e){$('status').textContent='recorder not running';}
 setTimeout(tick,200);}
tick();
</script></body></html>"""


def serve(rec: Recorder, host: str, port: int) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, body: bytes, kind: str, code: int = 200) -> None:
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            if self.path == "/state":
                self._send(json.dumps(rec.state()).encode(), "application/json")
            elif self.path == "/":
                self._send(PAGE.encode(), "text/html; charset=utf-8")
            else:
                self._send(b"not found", "text/plain", 404)

        def do_POST(self):  # noqa: N802
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
            try:
                args = json.loads(body or b"{}")
                if self.path == "/start":
                    rec.start(args.get("driver", ""), args.get("note", ""))
                elif self.path == "/stop":
                    rec.stop()
                else:
                    return self._send(b"not found", "text/plain", 404)
                self._send(b"{}", "application/json")
            except ValueError as exc:
                self._send(json.dumps({"error": str(exc)}).encode(), "application/json", 400)

        def log_message(self, *args):   # keep the terminal for what matters
            pass

    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1", help="the PC the game runs on")
    ap.add_argument("--port", type=int, default=PORT, help="the game's telemetry port")
    ap.add_argument("--out", default="recordings", help="folder for the recordings")
    ap.add_argument("--page-port", type=int, default=8765)
    ap.add_argument("--lan", action="store_true", help="open the page to other PCs on the network too")
    a = ap.parse_args()
    rec = Recorder(a.host, a.port, a.out)
    threading.Thread(target=rec.run, daemon=True).start()
    server = serve(rec, "0.0.0.0" if a.lan else "127.0.0.1", a.page_port)
    print(f"Recorder page: http://localhost:{a.page_port}   (Ctrl+C to quit)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        rec.shutdown()


if __name__ == "__main__":
    main()
