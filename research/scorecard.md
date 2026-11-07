# Flip the Switch — Competitor Scorecard (2026-11-08)

Rubric: Switch use 30 · Technical execution 25 · Creativity & impact 25 · Presentation 20.
Sources: READMEs cached in /tmp/readme_*.md and /tmp/rm2_*.md.

| Rank | Project (repo) | Switch 30 | Tech 25 | Creative 25 | Present 20 | Total 100 | One-liner |
|---|---|---|---|---|---|---|---|
| 1 | Quarantine (edycutjong) | 29 | 23 | 23 | 19 | 94 | Uses Switch *addressing policy* as a prompt-injection wall; measured timings; video with timestamps. Most "Switch-native" in the field. |
| 2 | Handshake (Ishaan-Gpt) | 28 | 22 | 24 | 19 | 93 | Two companies' agents negotiate a contract; private side-room + private playbook doc per side; every offer needs a human yes. CI badge, site, blog. |
| 3 | Baton (neweraXX) | 28 | 23 | 22 | 19 | 92 | Shift-handover relay; only non-LLM protocol agent in the field (Node.js WebSocket + HTTP ledger, no LLM); subtitled 2:37 video; dev.to blog. |
| 4 | LeaseDesk (singha105) | 28 | 22 | 21 | 19 | 90 | JIT AWS access in plain English; named-human approval; IAM lease expires by itself. Best governance design: human-owned docs as trust boundary, linked rooms for security escalation, exclusive roles, agent-written lease ledger. |
| 5 | TripCrew (xxycoc) | 25 | 23 | 21 | 19 | 88 | Telegram trip crew: Planner (Claude) + Budget (Codex) + Reel Adder; reel → places → itinerary, voice notes, cost splits; real Osaka–Kyoto trip tested. Direct rival to our travel idea. |
| 6 | Vaaradhi (yerramsettysuchita) | 24 | 22 | 22 | 18 | 86 | Reviewers check *proof*, not AI diffs: one agent runs each PR and posts evidence, a second agent from a different vendor tries to break it, a third ships only on human approval. Planted bug caught 3/3, 0 broken changes shipped. |
| 7 | Issue Desk (JemIIahh) | 25 | 23 | 18 | 17 | 83 | 3 agents compare 4 competing PRs on a 55-comment "assign me" issue; nothing touches GitHub until maintainer clicks an approval card; scripted reproducible demo. |
| 8 | BudgetRoom (oulael-laabi) | 23 | 22 | 19 | 18 | 82 | Deterministic `budget.py` computes every number; "Karim: approve 1" money gate; multilingual. |
| 9 | LabRoom (riponcm) | 24 | 22 | 18 | 18 | 82 | Seven agents answer a research PI's three weekly questions (decided? blocked? done?) from chat + meetings + git in ~7s; 2:27 video, 15-min quickstart. |
| 10 | Commander-Room (pooja-bhavani) | 23 | 22 | 17 | 16 | 78 | 2 agents, real k8s cluster: read-only inspector + release agent that rolls back only after "approve". Solid, small, honest ("nothing faked"). |
| 11 | SwitchOps (BishtNikhil) | 23 | 21 | 16 | 18 | 78 | Incident war room + release escort, 3 agents, Slack/Teams/Discord/Telegram, dev.to blog, Wispr badge. Polished but in the saturated DevOps cluster. |
| 12 | Incident-Sentinel (ronitgupta138) | 22 | 20 | 16 | 14 | 72 | SRE incident + canary safety room; heavy ASCII branding, thinner execution evidence; same saturated cluster. |

Not scored (weaker or proposal-only): Study-Nexus (~76), Society-Room (~74), BLACKBOX, kind, kartavya, flip-all-agent, vayu (all DevOps-cluster, ~72-80), LabQuorum (~50, proposal only).

## What the top scorers actually do (the pattern)
1. **Outcome enforced in a real external system** — IAM lease expiry (LeaseDesk), k8s rollback (Commander-Room), GitHub PR state (Issue Desk, Vaaradhi), a real trip (TripCrew). The room is where decisions happen; reality is where proof is shown.
2. **Switch mechanics ARE the feature, not plumbing** — addressing policy as a security wall (Quarantine), linked rooms for escalation (LeaseDesk), exclusive roles so exactly one agent can execute (LeaseDesk/Issue Desk), human-owned docs vs agent-owned ledger docs (LeaseDesk).
3. **Exactly one human gate at the expensive step, and the decision is logged in the room** — approval cards, named approvers, lease threads.
4. **Template YAML = the artifact** — one import creates rooms, roles, instructions, docs, agents. CI badge + clean-room run + reproducible sandbox.
5. **Measured evidence** — timings, caught-3/3 counts, deterministic calculators, subtitled timed videos.
6. **Pass the remove-Switch test explicitly** — top READMEs state "remove Switch and it stops working" with the reasons.

## Saturation warning
DevOps/incident-response is the most crowded cluster (SwitchOps, Commander-Room, Incident-Sentinel, BLACKBOX, kind, kartavya, flip-all-agent, vayu ≈ 8 projects). Travel/personal (TripCrew + our planned entry) is sparse.
