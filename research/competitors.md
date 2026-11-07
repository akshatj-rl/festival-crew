# Flip the Switch — competitor field map (public GitHub, scraped 2026-11-08 ~00:20 IST)

Sources: GitHub repo search (5 queries), `sandbox-quantum/switch` hackathon PRs +
`label:hackathon` issues, README pulls for the 6 closest projects.
Public GitHub is a floor — private-repo submissions aren't visible.

## Track 1 — Business workflow (saturated: incident/DevOps/triage cluster)

| Repo | What it is | Notes |
|---|---|---|
| suryafk/FlipTheSwitch (BLACKBOX) | Multi-agent incident response, sandboxed payment-service sim, Slack | |
| ronitgupta138/Incident-Sentinel | SRE incident response + canary deployment safety room | Same author as Study-Nexus (double entry) |
| pooja-bhavani/commander-room | Incident command room + real Kubernetes (kind) + Codex | |
| JemIIahh/issue-desk | Triage issue floods, compare competing PRs | |
| devprotim/switch-workflow (SwitchOps) | DevOps & bug-triage teammate + Wispr Flow | Wispr side-track entry |
| BishtNikhil/switchops | Incident war room & release escort; Claude Code + Antigravity + Codex + Wispr | Wispr side-track |
| singha105/leasedesk | Just-in-time AWS access desk: AI drafts/critiques, named human approves, IAM expires the lease | Strong "approval = real system" story |
| YashasviThakur/kartavya-crew | Website team: feedback → ticket → fix → check → owner-approved release | |
| yerramsettysuchita/vaaradhi | Two vendors' agents prove an AI-written change is safe; human ships | |
| majorML/flip-all-agent | DeFi / smart-contract security copilot in Discord | |
| ayushkumar2601/vayu_switchup | Cyber reasoning: vulnerability triage; Wispr voice | |
| edycutjong/quarantine | Prompt-injection defense: addressing policy (not prompts) as the wall; measured refusal times | Most "Switch-native" entry in the field |
| Ishaan-Gpt/handshake | Two companies' agents negotiate a deal in one room; private room + playbook doc per side; nothing crosses without your yes | Solves the "cross-org" problem inside one server — the pattern to steal |
| Ranger-Jay/hackathon-flip-the-switch | Council room workflow | |
| akashgoyal/ClaimDesk-FlipTheSwitch | Claim desk | |

## Track 2 — Personal/creative (thinner field — your lane)

| Repo | What it is | Notes |
|---|---|---|
| **xxycoc/tripcrew** | **DIRECT RIVAL**: solo-traveller AI crew in a Telegram group — Planner (Claude), Budget (Codex), Reel Adder (Claude). Drop a TikTok/IG reel → place identified → wishlist → itinerary. Voice notes, receipt photos, cost splits, 80%-of-category warnings, live pixel-art view. Tested on a real Osaka–Kyoto trip. Has YouTube demo. | |
| oulael-laabi/budgetroom | Budgeting coach in chat; deterministic `budget.py` for every number; parent-approval flow ("Karim: approve 1"); multilingual (MAD/EUR/FR) | Best "honest numbers" pattern in the field |
| ronitgupta138/Study-Nexus | Socratic study & research room; paper ingestion; Obsidian-ready notes | |
| abhinav162/society-room | Housing-society committee governance room | |
| chandranshgupta/CommunityAI | Team project, no details in desc | |

## Track 3 — Core contribution (14 open PRs, 65 issues)

- **Bridges**: Cisco Webex bridge (open) — proves custom messaging platforms are actively accepted; **WhatsApp is still open territory**.
- **Providers**: Grok Build, GitHub Copilot CLI, Kimi Code (3 PRs, one author).
- **Connectors**: PagerDuty, Cloudflare, Asana merged-in-progress; 20+ "add connector" issues open (Stripe, Notion, Salesforce, Grafana, Zendesk…).
- `!cancel` queued-turn command; addressing-policy-driven room invitations; 3 competing docs-quickstart PRs (crowded, avoid).

## What NOBODY in the public field has

1. **A proactive, always-on protocol daemon** — Baton has a deterministic
   "ledger" agent (Node.js, WebSocket + HTTP operations, no LLM), but it
   reacts to room events; nobody's agent *nudges first* on a schedule/state
   ("next stop in 25 min", budget drift, plan stale). Tier-3 differentiator intact.
2. **WhatsApp** — no bridge, no entry. You have the credentials.
3. **Time as the optimized resource** — TripCrew optimizes money + saved
   reels; nobody optimizes the traveler's *time* (travel legs, queues, opening
   hours, "you're going to miss the 17:40 train" warnings).
4. **The Handshake pattern** (private side-rooms + playbook docs + per-offer
   approval) — exists once, for negotiation; untried for personal planning
   (e.g., a "proposal" the planner drafts that you approve before it becomes
   "booked").

## Strategic read

- Track 1 is a knife-fight of ~13 incident/DevOps rooms; the differentiators
  there are "real system" integrations (kind, IAM) and security framing
  (quarantine's measured injection wall).
- Track 2 has ~5 visible entries; the strongest (TripCrew) is real-trip tested
  with a unique ingestion hook (reels) and a visual gimmick (pixel art).
- To beat TripCrew head-on on travel features is a losing race (they're ahead
  on build time). The winning move is a different axis:
  **proactive daemon (first nudge ever shown on camera) + WhatsApp (first
  bridge ever attempted) + time-optimization framing ("the most expensive
  thing on a trip is time")** — with the Handshake-style approval room for
  bookings.
