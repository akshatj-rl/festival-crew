#!/usr/bin/env python3
"""The Trip Butler's nudge math — deterministic, no LLM clock-watching.

Given a day plan (stops with times) and the current time, it computes the
next stop and whether the reminder window is open.

Usage:
  python3 nudge.py day.json --now 14:00 [--window 45]

day.json: {"stops": [{"time": "14:40", "name": "Orsay", "leg": "walk 25 min"}]}
"""
import argparse
import json
import sys


def to_min(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--now", required=True)
    ap.add_argument("--window", type=int, default=45)
    args = ap.parse_args()

    with open(args.plan) as f:
        plan = json.load(f)
    now = to_min(args.now)
    upcoming = [s for s in plan["stops"] if to_min(s["time"]) >= now]
    if not upcoming:
        print("NODAY: nothing left today — day is done.")
        return
    nxt = upcoming[0]
    delta = to_min(nxt["time"]) - now
    leg = nxt.get("leg", "check the route")
    if delta <= args.window:
        print("NUDGE: Heads up: %s in %d min. %s." % (nxt["name"], delta, leg))
    else:
        print("QUIET: next is %s at %s (%d min) — outside the %d-min window." % (
            nxt["name"], nxt["time"], delta, args.window))


if __name__ == "__main__":
    main()
