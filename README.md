# The Crew — the festive-season trip crew

One kind of person, one festive-season headache: **you're home for Diwali and
a family wedding in the same trip**, and now you have to run it — peak-season
prices, sold-out tickets, gifts unshopped, the sangeet at 19:00, and the
least free time of any trip you take.

Nine agents, five shared documents, one human gate. The crew plans, books,
budgets and nudges the trip so you spend it instead of managing it.

Built for **"Build something people actually use this season"**
(Diwali → New Year) — and it runs the same way on **Switch**
(WeMakeDevs × DevTools Academy × SandboxAQ): one template import creates the
whole room.

**The demo:** Delhi → Agra → Jaipur, Diwali morning to wedding morning,
6 days, ₹60,000. The crew's signature moves:
- the **on-the-way detour** — the Taj Mahal is 45 min off the NH48 you were
  driving anyway: 3 hours, not a day
- **closure placement** — Taj closed Mondays, Humayun's Tomb closed Mondays:
  the crew places both correctly without being told
- the **worth-it grid** — Vande Bharat vs cab vs bus, run by script, not vibes
- **wedding-season money** — the flat Diwali hotel rate beats the wedding-week
  rate by ₹17,400, and the human approves the only expensive booking

## The roster

| Agent | Alias | Job | Accent |
|---|---|---|---|
| Trip Planner | @planner | cities, trains, hotels, on-the-way detours, free-day placement | dusk |
| Booking Agent | @booker | tickets and hotels; nothing booked without your "approve" | dusk deep |
| Social Finder | @social | reels and vlogs — what the internet is hyping, tagged | terra |
| Blog Finder | @blog | guides and deep dives — the hidden corners | terra light |
| Local Guide | @local | events, markets, closures — the city, right now | ochre deep |
| Day Planner | @day | the hour-by-hour day, route map, day cost | sage |
| Budget Keeper | @money | the ledger — every euro, by script, never by a brain | ochre |
| Deal Finder | @deals | free days, offers, coupons, the transit pass grid | plum |
| Trip Butler | @butler | the only one who speaks first: reminders, on-the-go re-plans | plum light |

Every agent posts **cards** (warm-paper PNGs in the Superconnect theme)
instead of markdown walls: day plans with route maps, budget cards, the
pass-worth-it grid, finds cards, detour cards, and the approval card.

## How it works on Switch

- **One room per trip**, created from `switch/crew.template.yaml` (the
  artifact: one import creates all nine agents, the room, five documents,
  five exclusive roles, and the kickoff).
- **Shared state = room documents with ownership.** `trip-brief` is
  human-owned (agents read, never edit — the trust boundary); `itinerary`,
  `bookings`, `budget-ledger`, `day-plans` each have exactly one owner.
- **Handoffs by @mention** with `!follow-ups off`: the agent named answers;
  nobody else does. Scout finds a free museum day, @planner rewrites the
  itinerary, @money books the delta.
- **One human gate.** Anything that spends money ends in an approval card
  from the Booking Agent and waits for a human "approve" in the room. The
  decision is logged.
- **Deterministic math.** `scripts/budget.py` and `scripts/pass-check.py`
  produce every budget and transit-pass number. No LLM arithmetic.
- **Remove-Switch test:** without the room, the agents cannot hand off,
  cannot share the brief, and the approval gate has nowhere to live.

## Layout

```
switch/crew.template.yaml   the artifact — import this in Switch Console
agents/*.md                 the nine agent briefs (what the template inlines)
cardkit/cardkit.py          the card renderer (Superconnect theme)
data/cities/*.json          curated city data: places, hours, costs, transit, free days
data/trip-example.json      the demo trip: Paris -> Brussels -> Amsterdam, 5 days, 900 EUR
scripts/budget.py           the ledger math
scripts/pass-check.py       transit pass break-even
demo/runbook.md             the 90-second demo, beat by beat
out/                        generated cards and badges
```

## Live dashboard (no Switch Console needed)

A chat-style room UI that runs the crew live — same cardkit cards, same city
data, same `budget.py` / `nudge.py` math:

```
python3 app/launch.py 8901        # daemonizes; survives shell exit
open http://127.0.0.1:8901
```

- **Run 1 · plan the trip** — macro plan, detour card, pass grid, finds,
  then the approval gate: click **approve** (or type "approve") and watch the
  booking land in the state panel and the ledger bar move to 40%.
- **Run 2 · on the go** — a voice-note message, the Butler relays in two
  lines, the Day Planner re-plans with the day card, and the Butler's nudge
  (from `scripts/nudge.py`) fires 40 minutes out.
- The ledger, booked list and room state on the right are live state, not
  screenshots.

## Run it (in Switch)

Prereqs: Switch Console running locally, the bridge app connected (Telegram
recommended: mobile, voice notes, one bot token), Claude Code (or Codex CLI)
signed in, Python 3 with Pillow.

1. `python3 cardkit/cardkit.py samples out` — renders all card types and the
   nine badges (check the look first).
2. Switch Console → **Templates → Import** → `switch/crew.template.yaml`.
3. Fill the form: trip name `paris-amsterdam`, bridge **Telegram**, trip
   folder = a fresh folder containing `ledger.json`, `out/`, and copies of
   `cardkit/`, `data/`, `scripts/` (or clone this repo into it).
4. The room posts the kickoff; the Butler turns follow-ups off.
5. Run 1 (macro) and Run 2 (on-the-go) per `demo/runbook.md`.

## Honest limits
- City data is a curated demo set (three cities); prices carry a
  `prices_as_of` stamp and must be re-verified for a real trip.
- The agents research live (web tools) but the map on day cards is a
  schematic rendered from the coordinates — no map API key needed.
- Booking = the agent finds the exact option and link; paying with a card
  stays with the human (by design — that is the gate).

## Stretches (not in v1)
- WhatsApp bridge (custom bridge contribution — doubles as a Track 3 PR).
- Gmail receipt scanning into the ledger (Budget Keeper).
- A live fare source for one city (free-museum days from the official API).
