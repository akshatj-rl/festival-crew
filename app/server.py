#!/usr/bin/env python3
"""The Crew — local live dashboard.

A chat-style room UI that runs the crew live: scenarios stream agent
messages and cardkit-rendered cards, the approval gate pauses for your
click, and the budget ledger updates from real script math.

Stdlib only. Run:  python3 app/server.py [port]   (default 8901)
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cardkit"))
import cardkit  # noqa: E402

LIVE_DIR = ROOT / "out" / "live"
LIVE_DIR.mkdir(parents=True, exist_ok=True)


def ledger_math(ledger):
    total = float(ledger["total"])
    spent = -sum(float(i["amount"]) for i in ledger["items"] if i["amount"] < 0)
    return total, spent, total - spent


class Engine:
    def __init__(self):
        self.lock = threading.Lock()
        self.events = []          # append-only, id = index + 1
        self.event_wait = threading.Event()
        self.busy = False
        self.pending_decision = None   # (resolve_event, on_approve, on_deny)
        self.ledger = json.loads((ROOT / "trip" / "ledger.json").read_text())
        self.booked = [
            "Delhi → Agra train, 07:00, Day 3 — ref SBC-118842",
            "Agra → Jaipur Vande Bharat, 10:40, Day 4 — ref VBC-111221",
            "Agra hotel, 1 night near the Taj (separate budget) — ref AGA-27110",
        ]
        self.seq = 0

    # -- event plumbing --------------------------------------------------
    def push(self, ev):
        with self.lock:
            self.events.append(ev)
            self.event_wait.set()
            self.event_wait.clear()

    def drain(self, after):
        with self.lock:
            evs = self.events[after:]
        return evs

    def state(self):
        total, spent, left = ledger_math(self.ledger)
        with self.lock:
            return {
                "total": total, "spent": spent, "left": left,
                "pct": int(100 * spent / total) if total else 0,
                "items": self.ledger["items"],
                "booked": list(self.booked),
                "busy": self.busy,
                "decision": self.pending_decision is not None,
            }

    # -- scenarios -------------------------------------------------------
    def start(self, name):
        if self.busy:
            self.push({"type": "sys", "text": "The crew is mid-run. Let it finish, then run the next one."})
            return
        path = ROOT / "app" / "scenarios" / (name + ".json")
        scenario = json.loads(path.read_text())
        self.busy = True
        threading.Thread(target=self._run, args=(scenario,), daemon=True).start()

    def _run(self, scenario):
        steps = list(scenario["steps"])
        self.push({"type": "sys", "text": "— %s —" % scenario["title"]})
        while steps:
            step = steps.pop(0)
            time.sleep(step.get("t", 1.0))
            kind = step["kind"]
            if kind == "msg":
                self.push({"type": "msg", "who": step["who"], "text": step["text"],
                           "voice": step.get("voice", False)})
            elif kind == "card":
                url = self._render(step)
                self.push({"type": "card", "who": step["who"], "url": url,
                           "text": step.get("text", "")})
            elif kind == "book":
                self.booked.append(step["text"])
                self.push({"type": "booked", "text": step["text"]})
            elif kind == "ledger":
                self.ledger["items"].append(step["item"])
                total, spent, left = ledger_math(self.ledger)
                self.push({"type": "ledger", "item": step["item"],
                           "total": total, "spent": spent, "left": left,
                           "pct": int(100 * spent / total)})
            elif kind == "nudge":
                line = self._nudge(step)
                self.push({"type": "msg", "who": step["who"], "text": line, "nudge": True})
            elif kind == "decision":
                url = self._render(step)
                self.push({"type": "decision", "who": step["who"], "url": url,
                           "text": step.get("text", "")})
                choice = self._wait_decision()
                branch = step["on_approve" if choice == "approve" else "on_deny"]
                steps = branch + steps
        self.busy = False
        self.push({"type": "done", "text": "Run complete."})

    def _render(self, step):
        self.seq += 1
        out = LIVE_DIR / ("step-%03d.png" % self.seq)
        data = step.get("data", {})
        if step.get("render_from_ledger"):
            total, spent, left = ledger_math(self.ledger)
            data = {"trip": self.ledger.get("trip", "the trip"), "total": total,
                    "spent": spent, "items": self.ledger["items"]}
        cardkit.CARDS[step["card"]](data, str(out))
        return "/live/%s" % out.name

    def _wait_decision(self):
        ev = threading.Event()
        box = {}
        self.pending_decision = (ev, box)
        ev.wait()
        self.pending_decision = None
        return box.get("choice")

    def decide(self, choice):
        with self.lock:
            pd = self.pending_decision
        if not pd:
            return False
        pd[1]["choice"] = choice
        pd[0].set()
        return True

    def say(self, text):
        self.push({"type": "msg", "who": "human", "text": text})
        low = text.lower()
        if self.pending_decision:
            if re.search(r"approv|yes|book|do it|haan|ok", low):
                self.decide("approve")
            elif re.search(r"den|no|drop|skip", low):
                self.decide("deny")
        elif re.search(r"plan|trip|brief", low):
            self.start("run1")
        elif re.search(r"done|finished|next|what.?s next", low):
            self.start("run2")
        else:
            self.push({"type": "msg", "who": "trip-butler",
                       "text": "Got it. For the demo, the quick actions above run the two scenes — or type “plan the trip” / “I just finished the Louvre”."})

    def _nudge(self, step):
        plan_file = ROOT / step["plan_file"]
        out = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "nudge.py"), str(plan_file),
             "--now", step.get("now", "09:00")],
            capture_output=True, text=True)
        line = out.stdout.strip() or out.stderr.strip()
        return line


ENGINE = Engine()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[%s] %s" % (time.strftime("%H:%M:%S"), fmt % args))

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        u = urlparse(self.path)
        p = u.path
        if p == "/":
            body = (ROOT / "app" / "static" / "index.html").read_bytes()
            self._send(200, body, "text/html; charset=utf-8")
        elif p == "/events":
            after = int(parse_qs(u.query).get("after", ["0"])[0])
            self._send(200, {"events": ENGINE.drain(after), "state": ENGINE.state()})
        elif p.startswith("/live/"):
            f = LIVE_DIR / os.path.basename(p)
            if f.exists():
                self._send(200, f.read_bytes(), "image/png")
            else:
                self._send(404, b"no card")
        elif p.startswith("/badge/"):
            f = ROOT / "out" / (os.path.basename(p))
            if f.exists():
                self._send(200, f.read_bytes(), "image/png")
            else:
                self._send(404, b"no badge")
        else:
            self._send(404, b"not found")

    def do_POST(self):
        u = urlparse(self.path)
        body = self._json()
        if u.path == "/run":
            ENGINE.start(body.get("scenario", "run1"))
            self._send(200, {"ok": True})
        elif u.path == "/decide":
            self._send(200, {"ok": ENGINE.decide(body.get("choice", "deny"))})
        elif u.path == "/say":
            ENGINE.say(body.get("text", ""))
            self._send(200, {"ok": True})
        else:
            self._send(404, b"not found")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8901
    # make sure badges exist
    badges = [str(p) for p in (ROOT / "out").glob("badge-*.png")]
    if not badges:
        cardkit.SAMPLES  # noqa
        for key in cardkit.AGENT_COLORS:
            cardkit.badge(key, str(ROOT / "out" / ("badge-%s.png" % key)))
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("The Crew dashboard:  http://127.0.0.1:%d" % port)
    srv.serve_forever()


if __name__ == "__main__":
    main()
