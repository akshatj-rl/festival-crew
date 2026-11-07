#!/usr/bin/env python3
"""Deterministic budget math. The Budget Keeper runs this instead of doing
arithmetic in its head - every number on a budget card comes from this file.

Usage:
  python3 budget.py ledger.json            # summary
  python3 budget.py ledger.json card.json  # also write cardkit budget-card data

ledger.json: {"total": 900, "items": [{"label": "...", "amount": -12.5}, ...]}
"""
import json
import sys


def main():
    with open(sys.argv[1]) as f:
        ledger = json.load(f)
    total = float(ledger["total"])
    spent = -sum(float(it["amount"]) for it in ledger["items"] if it["amount"] < 0)
    left = total - spent
    frac = spent / total if total else 0.0
    status = "on track" if frac < 0.7 else "tight" if frac < 0.9 else "OVER PLAN"
    print("total     %s" % total)
    print("spent     %s" % spent)
    print("left      %s" % left)
    print("used      %.0f%%  %s" % (frac * 100, status))
    if len(sys.argv) > 2:
        card = {
            "trip": ledger.get("trip", "the trip"),
            "total": total,
            "spent": spent,
            "items": ledger["items"],
        }
        with open(sys.argv[2], "w") as f:
            json.dump(card, f, indent=2, ensure_ascii=False)
        print("card data ->", sys.argv[2])


if __name__ == "__main__":
    main()
