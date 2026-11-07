#!/usr/bin/env python3
"""Daemonize app/server.py (double-fork; survives shell/session exit).

Usage: python3 app/launch.py [port]
"""
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8901
LOG = Path("/tmp/crew-server.log")


def stop_existing():
    out = subprocess.run(["lsof", "-tiTCP:%d" % PORT, "-sTCP:LISTEN"],
                         capture_output=True, text=True).stdout
    for pid in out.split():
        try:
            os.kill(int(pid), signal.SIGTERM)
        except ProcessLookupError:
            pass


def main():
    stop_existing()
    if os.fork() > 0:
        sys.exit(0)
    os.setsid()
    if os.fork() > 0:
        sys.exit(0)
    log = open(LOG, "ab")
    os.dup2(log.fileno(), 1)
    os.dup2(log.fileno(), 2)
    os.dup2(os.open(os.devnull, os.O_RDONLY), 0)
    server = Path(__file__).resolve().parent / "server.py"
    os.execv(sys.executable, [sys.executable, str(server), str(PORT)])


if __name__ == "__main__":
    main()
