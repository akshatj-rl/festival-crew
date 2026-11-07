#!/usr/bin/env python3
"""Is the daily transit pass worth it in this city?

Usage:
  python3 pass-check.py ../data/cities/paris.json [rides-today]

Break-even = ceil(day_pass / single). Rides at or above it -> BUY IT.
"""
import json
import math
import sys


def main():
    with open(sys.argv[1]) as f:
        city = json.load(f)
    t = city["transit"]
    single, day = float(t["single"]), float(t["day_pass"])
    be = math.ceil(day / single)
    rides = int(sys.argv[2]) if len(sys.argv) > 2 else None
    verdict = ("BUY IT - %d rides beats %d singles (%.2f vs %.2f)" % (rides, rides, day, rides * single)
               if rides and rides >= be
               else "skip - you ride fewer than %d times; singles win" % be)
    print("%s: single %s / day pass %s / break-even %d rides -> %s" % (
        city["city"], single, day, be, verdict))


if __name__ == "__main__":
    main()
