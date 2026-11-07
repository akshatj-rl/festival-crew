# Trip folder — what the Switch room needs

When you import `switch/crew.template.yaml` in Switch Console, point the
**Trip folder** parameter at a folder that contains:

- `ledger.json`   (copy from here — the Budget Keeper's source of truth)
- `out/`          (where cardkit writes the PNG cards)
- `cardkit/`, `data/`, `scripts/`  (copied from the repo root, or clone the
  whole repo here instead — the agents' instructions call these paths)

Then create the Telegram bot token, pick Telegram as the bridge in the
template form, and the kickoff posts the crew introductions.
