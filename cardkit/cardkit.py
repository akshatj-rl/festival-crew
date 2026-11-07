#!/usr/bin/env python3
"""cardkit — renders The Crew's chat cards in the Superconnect theme.

Every agent in the trip room posts these PNGs instead of raw markdown walls:
  day-plan    a day's schedule: timeline + legs + schematic route map
  budget      the money so far, line by line, with a remaining bar
  pass-grid   which cities' daily transit pass is worth buying (and why)
  approval    the human gate: what it costs, approve or deny
  detour      an on-the-way city: extra city, ~zero extra cost
  finds       places pulled from reels / blogs / local sites, tagged by source
  badge       the 512x512 crew badge (avatar) for one agent

Theme: Superconnect warm paper (#fbf7ef), ink (#221d17), dot-matrix badge
texture, Georgia serif headers / Avenir Next body / Menlo numbers.

Usage:
  python3 cardkit.py <card-type> <data.json> <out.png>
  python3 cardkit.py badge <agent-key> <out.png>
  python3 cardkit.py samples <outdir>
"""
import json
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- theme ----
PAPER = (251, 247, 239)
NIGHT = (20, 17, 14)
INK = (34, 29, 23)
SAND = (239, 231, 216)
SAND_DEEP = (227, 216, 195)
MUTED = (122, 111, 95)
LINE = (210, 199, 178)

SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SANS = "/System/Library/Fonts/Avenir Next.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"

AGENT_COLORS = {
    "trip-planner": (107, 129, 151),    # dusk
    "booking-agent": (70, 88, 108),     # dusk deep
    "social-finder": (194, 96, 62),     # terra
    "blog-finder": (217, 138, 103),     # terra light
    "local-guide": (166, 124, 46),      # ochre deep
    "day-planner": (124, 143, 107),     # sage
    "budget-keeper": (199, 154, 59),    # ochre
    "deal-finder": (138, 90, 114),      # plum
    "trip-butler": (176, 127, 152),     # plum light
}
AGENT_LABELS = {
    "trip-planner": "Trip Planner",
    "booking-agent": "Booking Agent",
    "social-finder": "Social Finder",
    "blog-finder": "Blog Finder",
    "local-guide": "Local Guide",
    "day-planner": "Day Planner",
    "budget-keeper": "Budget Keeper",
    "deal-finder": "Deal Finder",
    "trip-butler": "Trip Butler",
}
AGENT_ROLES = {
    "trip-planner": "cities · flights · hotels · the big picture",
    "booking-agent": "tickets · hotels · nothing booked without you",
    "social-finder": "reels · vlogs · what the internet is hyping",
    "blog-finder": "guides · deep dives · hidden corners",
    "local-guide": "events · local sites · what this city is doing now",
    "day-planner": "your day, hour by hour, map included",
    "budget-keeper": "every number, counted and checked",
    "deal-finder": "discounts · offers · free days · passes",
    "trip-butler": "nudges · reminders · on-the-go changes",
}

_fonts = {}


def font(kind, size):
    key = (kind, size)
    if key not in _fonts:
        path = {"serif": SERIF, "sans": SANS, "mono": MONO}[kind]
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def alpha(color, a):
    return tuple(int(c * a) for c in color[:3])


# ---------------------------------------------------------------- base ----
def paper_bg(size, noise=0.035):
    img = Image.new("RGB", size, PAPER)
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    w, h = size
    for _ in range(w * h // 140):
        x, y = rnd.randrange(w), rnd.randrange(h)
        d.point((x, y), fill=alpha(INK, noise * rnd.random() + 0.01))
    for y in range(0, h, 3):  # fine horizontal grille, like the pass stage
        d.line([(0, y), (w, y)], fill=alpha(INK, 0.028))
    return img


def dot_matrix(draw, box, color=INK, step=14, dot=1.7, a=0.10):
    x0, y0, x1, y1 = box
    for x in range(x0, x1, step):
        for y in range(y0, y1, step):
            draw.ellipse([x, y, x + dot, y + dot], fill=alpha(color, a))


def card_frame(w, h, accent, kicker, title, subtitle=None):
    """Standard card: paper, top dot strip, accent bar, serif title."""
    img = paper_bg((w, h))
    d = ImageDraw.Draw(img)
    dot_matrix(d, (0, 0, w, 46))
    d.rectangle([0, 46, w, 50], fill=accent)
    d.text((36, 64), kicker, font=font("mono", 13), fill=MUTED)
    d.text((36, 86), title, font=font("serif", 34), fill=INK)
    y = 134
    if subtitle:
        d.text((36, 130), subtitle, font=font("sans", 16), fill=MUTED)
        y = 162
    return img, d, y


def footer(d, w, h, agent_key, note=""):
    label = AGENT_LABELS.get(agent_key, agent_key)
    d.rectangle([0, h - 44, w, h], fill=SAND)
    d.rectangle([0, h - 44, w, h - 42], fill=SAND_DEEP)
    d.text((36, h - 33), label, font=font("sans", 14), fill=INK)
    if note:
        tw = d.textlength(note, font=font("mono", 12))
        d.text((w - 36 - tw, h - 32), note, font=font("mono", 12), fill=MUTED)


def money(v, cur="€"):
    if v == int(v):
        return "%s%d" % (cur, int(v))
    return "%s%.2f" % (cur, v)


# ------------------------------------------------------------- day plan ----
def schematic_map(d, box, points, accent):
    """The route as a dot-matrix map: grid, numbered stops, route line."""
    x0, y0, x1, y1 = box
    dot_matrix(d, box, step=18, dot=1.4, a=0.07)
    lats = [p["lat"] for p in points]
    lngs = [p["lng"] for p in points]
    lat0, lat1 = min(lats), max(lats)
    lng0, lng1 = min(lngs), max(lngs)
    pad = 34

    def xy(p):
        la = (lat1 - p["lat"]) / (lat1 - lat0 or 1e-9)
        lo = (p["lng"] - lng0) / (lng1 - lng0 or 1e-9)
        x = x0 + pad + lo * (x1 - x0 - 2 * pad)
        y = y0 + pad + la * (y1 - y0 - 2 * pad)
        return x, y

    pts = [xy(p) for p in points]
    d.line(pts, fill=accent, width=3, joint="curve")
    for i, (x, y) in enumerate(pts, 1):
        d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=PAPER, outline=accent, width=3)
        t = str(i)
        tw = d.textlength(t, font=font("sans", 15))
        d.text((x - tw / 2, y - 8), t, font=font("sans", 15), fill=accent)
        name = points[i - 1].get("name", "")
        if name:
            d.text((x + 18, y - 8), name, font=font("sans", 13), fill=INK)


def day_plan(data, out):
    accent = AGENT_COLORS[data.get("agent", "day-planner")]
    cur = data.get("currency", "€")
    stops = data["stops"]
    legs = data.get("legs", [])
    w = 1080
    map_h = 300
    row_h = 46
    leg_h = 26
    h = 190 + len(stops) * row_h + len(legs) * leg_h + map_h + 120
    img, d, y = card_frame(
        w, h, accent,
        "DAY %d · %s" % (data.get("day", 1), data.get("date", "")),
        data.get("city", "Day plan"),
        "your day, hour by hour — %s" % data.get("note", ""),
    )
    mx0, my0, mx1, my1 = 640, y, w - 36, y + map_h
    if len(data.get("map_points", [])) >= 2:
        d.rectangle([mx0 - 10, my0 - 10, mx1 + 10, my1 + 10], outline=LINE, width=1)
        schematic_map(d, (mx0, my0, mx1, my1), data["map_points"], accent)
    sy = y
    for i, s in enumerate(stops, 1):
        d.ellipse([36, sy + 6, 52, sy + 22], fill=accent)
        d.text((38, sy + 7), str(i), font=font("sans", 12), fill=PAPER)
        d.text((64, sy), s["time"], font=font("mono", 15), fill=MUTED)
        d.text((130, sy - 2), s["name"], font=font("serif", 19), fill=INK)
        note = s.get("note", "")
        cost = s.get("cost")
        if cost is not None:
            tag = money(cost, cur) + ("  (free)" if cost == 0 else "")
        else:
            tag = ""
        d.text((130, sy + 24), (note + ("   " if note and tag else "")) + tag,
               font=font("sans", 14), fill=MUTED)
        sy += row_h
        if i < len(stops) and i - 1 < len(legs):
            leg = legs[i - 1]
            d.line([(140, sy - 18), (140, sy - 4)], fill=SAND_DEEP, width=2)
            d.text((150, sy - 18),
                   "→ %s · %s min%s" % (leg.get("mode", "walk"), leg.get("min", "?"),
                                        " · " + money(leg["cost"], cur) if leg.get("cost") else ""),
                   font=font("mono", 12), fill=MUTED)
            sy += leg_h
    total_cost = sum(s.get("cost", 0) or 0 for s in stops) + sum(l.get("cost", 0) or 0 for l in legs)
    d.line([(36, h - 64), (w - 36, h - 64)], fill=LINE)
    d.text((36, h - 58), "day total", font=font("mono", 13), fill=MUTED)
    tc = money(total_cost, cur)
    d.text((w - 36 - d.textlength(tc, font=font("mono", 16)), h - 60),
           tc, font=font("mono", 16), fill=accent)
    footer(d, w, h, data.get("agent", "day-planner"), "the-crew")
    img.save(out)
    return out


# --------------------------------------------------------------- budget ----
def budget(data, out):
    accent = AGENT_COLORS["budget-keeper"]
    cur = data.get("currency", "€")
    items = data["items"]
    w = 980
    h = 240 + len(items) * 40 + 130
    img, d, y = card_frame(w, h, accent, "MONEY", "Budget so far",
                           data.get("trip", "the trip"))
    x_item, x_amt = 36, w - 36
    for it in items:
        amt = it["amount"]
        sign = "−" if amt < 0 else "+"
        d.text((x_item, y), it["label"], font=font("sans", 16), fill=INK)
        s = "%s%s" % (sign, money(abs(amt), cur))
        d.text((x_amt - d.textlength(s, font=font("mono", 16)), y), s,
               font=font("mono", 16), fill=accent if amt < 0 else INK)
        y += 40
    total = data["total"]
    spent = data["spent"]
    left = total - spent
    d.line([(36, y - 14), (w - 36, y - 14)], fill=LINE)
    d.text((x_item, y), "budget / spent / left", font=font("mono", 13), fill=MUTED)
    summary = "%s / %s / %s" % (money(total, cur), money(spent, cur), money(left, cur))
    d.text((x_amt - d.textlength(summary, font=font("mono", 15)), y),
           summary, font=font("mono", 15), fill=INK)
    y += 34
    bar_y = y
    frac = max(0.0, min(1.0, spent / total if total else 0))
    d.rectangle([36, bar_y, w - 36, bar_y + 18], outline=LINE)
    d.rectangle([37, bar_y + 1, int(36 + (w - 74) * frac), bar_y + 17],
                fill=accent if frac < 0.85 else (194, 96, 62))
    d.text((36, bar_y + 24),
           "%d%% used — %s" % (int(frac * 100),
                               "on track" if frac < 0.7 else "tight — Deal Finder, work" if frac < 0.9 else "over plan"),
           font=font("sans", 14), fill=MUTED)
    footer(d, w, h, "budget-keeper", "the-crew")
    img.save(out)
    return out


# ------------------------------------------------------------- pass grid ----
def pass_grid(data, out):
    accent = AGENT_COLORS["deal-finder"]
    cur = data.get("currency", "€")
    rows = data["cities"]
    w = 1080
    h = 220 + len(rows) * 58 + 90
    img, d, y = card_frame(w, h, accent, "OFFERS", "Transit pass worth it?",
                           "buy the daily pass when rides × single fare beats the pass")
    cols = [36, 320, 560, 760, 920]
    d.text((cols[0], y), "city", font=font("mono", 13), fill=MUTED)
    d.text((cols[1], y), "single", font=font("mono", 13), fill=MUTED)
    d.text((cols[2], y), "day pass", font=font("mono", 13), fill=MUTED)
    d.text((cols[3], y), "break-even", font=font("mono", 13), fill=MUTED)
    d.text((cols[4], y), "verdict", font=font("mono", 13), fill=MUTED)
    y += 30
    for r in rows:
        be = math.ceil(r["pass"] / r["single"])
        verdict = "BUY IT" if r["rides"] >= be else "skip"
        d.text((cols[0], y), r["city"], font=font("serif", 18), fill=INK)
        d.text((cols[1], y + 2), money(r["single"], cur), font=font("mono", 15), fill=INK)
        d.text((cols[2], y + 2), money(r["pass"], cur), font=font("mono", 15), fill=INK)
        d.text((cols[3], y + 2), "%d rides" % be, font=font("mono", 15), fill=INK)
        d.text((cols[4], y + 2), verdict, font=font("mono", 15),
               fill=(124, 143, 107) if verdict == "BUY IT" else MUTED)
        d.line([(36, y + 40), (w - 36, y + 40)], fill=SAND_DEEP)
        y += 58
    d.text((36, y + 4), data.get("note", "prices verified against the operators' sites — see the room doc"),
           font=font("sans", 13), fill=MUTED)
    footer(d, w, h, "deal-finder", "the-crew")
    img.save(out)
    return out


# -------------------------------------------------------------- approval ----
def approval(data, out):
    accent = (194, 96, 62)
    w, h = 900, 460
    img, d, y = card_frame(w, h, accent, "APPROVAL NEEDED", "Human decision",
                           "nothing spends your money without a yes from you")
    d.text((36, y), data["what"], font=font("serif", 22), fill=INK)
    y += 44
    for line in data.get("lines", []):
        d.text((36, y), "· " + line, font=font("sans", 16), fill=MUTED)
        y += 28
    y += 10
    d.rectangle([36, y, w - 36, y + 92], outline=accent, width=2)
    d.text((56, y + 18), "cost change:  %s" % data["delta"], font=font("mono", 24), fill=accent)
    d.text((56, y + 56), "reply “approve” to book it   ·   reply “deny” to drop it",
           font=font("sans", 15), fill=INK)
    d.text((36, y + 112), "requested by %s · decision will be logged in the room" %
           AGENT_LABELS.get(data.get("from", "booking-agent"), data.get("from", "")),
           font=font("mono", 12), fill=MUTED)
    footer(d, w, h, data.get("from", "booking-agent"), "the-crew")
    img.save(out)
    return out


# --------------------------------------------------------------- detour ----
def detour(data, out):
    accent = AGENT_COLORS["trip-planner"]
    w, h = 1080, 520
    img, d, y = card_frame(w, h, accent, "ON THE WAY", "Add a city. Not a cost.",
                           "%s → %s with a stop in %s" % (data["from"], data["to"], data["detour"]))
    ax, ay = 140, y + 120
    bx, by = w - 140, y + 260
    cx, cy = (ax + bx) // 2, min(ay, by) - 90
    d.line([(ax, ay), (cx, cy), (bx, by)], fill=accent, width=3, joint="curve")
    for x, yy, name in ((ax, ay, data["from"]), (cx, cy, data["detour"]), (bx, by, data["to"])):
        d.ellipse([x - 16, yy - 16, x + 16, yy + 16], fill=accent if name == data["detour"] else PAPER,
                  outline=accent, width=3)
        tw = d.textlength(name, font=font("serif", 22))
        d.text((x - tw / 2, yy + 26), name, font=font("serif", 22),
               fill=accent if name == data["detour"] else INK)
    d.text((36, y + 300), "extra time:   %s" % data["extra_time"], font=font("mono", 17), fill=INK)
    d.text((36, y + 334), "extra money:  %s" % data["extra_cost"], font=font("mono", 17), fill=accent)
    d.text((36, y + 372), data.get("why", ""), font=font("sans", 15), fill=MUTED)
    footer(d, w, h, "trip-planner", "the-crew")
    img.save(out)
    return out



# --------------------------------------------------------------- compare ----
def compare(data, out):
    accent = AGENT_COLORS["deal-finder"]
    rows = data["options"]
    w = 1000
    h = 220 + len(rows) * 62 + 90
    img, d, y = card_frame(w, h, accent, "WORTH IT?", data.get("title", "Same trip, different way"),
                           data.get("subtitle", "the crew ran the numbers"))
    cols = [36, 400, 580, 760, 880]
    d.text((cols[0], y), "option", font=font("mono", 13), fill=MUTED)
    d.text((cols[1], y), "time", font=font("mono", 13), fill=MUTED)
    d.text((cols[2], y), "cost", font=font("mono", 13), fill=MUTED)
    d.text((cols[3], y), "verdict", font=font("mono", 13), fill=MUTED)
    y += 30
    cur = data.get("currency", "\u20b9")
    for r in rows:
        win = r.get("pick", False)
        name = r["name"] + ("  \u2190 pick" if win else "")
        d.text((cols[0], y), name, font=font("serif" if win else "sans", 17 if win else 16),
               fill=accent if win else INK)
        d.text((cols[1], y + 2), r.get("time", ""), font=font("mono", 15), fill=INK)
        d.text((cols[2], y + 2), r.get("cost", ""), font=font("mono", 15), fill=INK)
        d.text((cols[3], y + 2), r.get("verdict", ""), font=font("mono", 15),
               fill=accent if win else MUTED)
        d.line([(36, y + 42), (w - 36, y + 42)], fill=SAND_DEEP)
        y += 62
    d.text((36, y + 4), data.get("note", ""), font=font("sans", 13), fill=MUTED)
    footer(d, w, h, "deal-finder", "the-crew")
    img.save(out)
    return out


# ---------------------------------------------------------------- finds ----
def finds(data, out):
    accent = AGENT_COLORS.get(data.get("agent", "social-finder"), AGENT_COLORS["social-finder"])
    items = data["items"]
    w = 1000
    h = 200 + len(items) * 66 + 80
    img, d, y = card_frame(w, h, accent, "FINDS", data.get("title", "What the internet says"),
                           data.get("subtitle", ""))
    for it in items:
        tag = it.get("source", "web")
        tw = d.textlength(tag.upper(), font=font("mono", 11))
        d.rectangle([36, y, 36 + tw + 18, y + 22], fill=accent)
        d.text((45, y + 4), tag.upper(), font=font("mono", 11), fill=PAPER)
        d.text((36 + tw + 34, y + 2), it["place"], font=font("serif", 19), fill=INK)
        d.text((36, y + 30), it.get("why", ""), font=font("sans", 14), fill=MUTED)
        y += 66
    footer(d, w, h, data.get("agent", "social-finder"), "the-crew")
    img.save(out)
    return out


# ---------------------------------------------------------------- badge ----
def badge(agent_key, out):
    accent = AGENT_COLORS[agent_key]
    w = h = 512
    img = paper_bg((w, h), noise=0.04)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 120], fill=accent)
    dot_matrix(d, (0, 0, w, 120), color=PAPER, step=16, dot=2, a=0.25)
    d.text((40, 44), "THE CREW", font=font("mono", 15), fill=alpha(PAPER, 0.9))
    d.text((40, 68), "trip room · switch", font=font("mono", 12), fill=alpha(PAPER, 0.7))
    d.rounded_rectangle([60, 150, w - 60, 400], radius=18, fill=PAPER, outline=SAND_DEEP, width=3)
    dot_matrix(d, (60, 150, w - 60, 400), step=14, a=0.05)
    name = AGENT_LABELS[agent_key]
    d.text((96, 220), name, font=font("serif", 44), fill=INK)
    role = AGENT_ROLES[agent_key]
    d.text((96, 286), role, font=font("sans", 16), fill=MUTED)
    d.rectangle([96, 330, 216, 338], fill=accent)
    d.text((96, 356), "@%s" % agent_key, font=font("mono", 14), fill=accent)
    d.text((40, 430), "flip the switch · 2026", font=font("mono", 12), fill=MUTED)
    img.save(out)
    return out


# --------------------------------------------------------------- samples ----
SAMPLES = {
    "day-plan": {
        "agent": "day-planner", "day": 1, "date": "Sun 3 Jan 2027", "city": "Paris",
        "note": "first Sunday — the free day",
        "stops": [
            {"time": "09:00", "name": "Louvre", "note": "free today (first Sunday, until 14:00)", "cost": 0},
            {"time": "13:00", "name": "Café Pigalle", "note": "lunch, 15 min walk", "cost": 18},
            {"time": "15:00", "name": "Musée d'Orsay", "note": "closed Mondays", "cost": 16},
            {"time": "18:30", "name": "Eiffel Tower, from Trocadéro", "note": "dusk, summit at 20:00", "cost": 26.6},
        ],
        "legs": [
            {"mode": "metro 2 stops", "min": 12, "cost": 2.5},
            {"mode": "walk via Seine", "min": 25, "cost": 0},
            {"mode": "walk", "min": 15, "cost": 0},
        ],
        "map_points": [
            {"lat": 48.8606, "lng": 2.3376, "name": "Louvre"},
            {"lat": 48.8807, "lng": 2.3406, "name": "Pigalle"},
            {"lat": 48.86, "lng": 2.3265, "name": "Orsay"},
            {"lat": 48.8584, "lng": 2.2945, "name": "Eiffel"},
        ],
    },
    "budget": {
        "trip": "Paris → Brussels → Amsterdam · 5 days · budget €900 (excl. hotels)",
        "total": 900, "spent": 342.6,
        "items": [
            {"label": "Day 1 Paris — Louvre (free, first Sunday)", "amount": 0},
            {"label": "Day 1 Paris — lunch + Orsay + Eiffel", "amount": -60.6},
            {"label": "Day 1 Paris — metro ×2", "amount": -5},
            {"label": "Day 2 Paris → Brussels, train (1 seat)", "amount": -52},
            {"label": "Day 2 Brussels — Atomium", "amount": -20.5},
            {"label": "Day 3 Brussels — waffle stop", "amount": -9},
            {"label": "Day 3 Brussels → Amsterdam, train", "amount": -38},
            {"label": "Day 3 Amsterdam — canal cruise", "amount": -20.5},
            {"label": "Daily food allowance so far (3 days)", "amount": -137},
        ],
    },
    "pass-grid": {
        "cities": [
            {"city": "Paris", "single": 2.5, "pass": 8.65, "rides": 5},
            {"city": "Brussels", "single": 3.6, "pass": 10.75, "rides": 2},
            {"city": "Amsterdam", "single": 4.69, "pass": 10.2, "rides": 4},
        ],
        "note": "Paris & Amsterdam: the pass pays back. Brussels: you'll ride twice — single tickets win.",
    },
    "approval": {
        "from": "booking-agent",
        "what": "Anne Frank House ticket, Day 4, 10:00",
        "lines": [
            "sells out weeks ahead; this is the only 10:00 slot left",
            "10:00 leaves 14:30 of Day 4 free — the Rijksmuseum closes at 17:00",
        ],
        "delta": "+€18",
    },
    "detour": {
        "from": "Paris", "to": "Amsterdam", "detour": "Brussels",
        "extra_time": "1h 52m of train you were going to take anyway (direct: 2h 35m, 2 transfers)",
        "extra_cost": "≈ €0 — same two train legs, one extra night",
        "why": "You were passing through it. Grand Place + a waffle stop costs you a lunch.",
    },
    "finds": {
        "agent": "social-finder",
        "title": "Paris, from 14 reels this week",
        "subtitle": "transcribed, deduped, sorted by how often people say 'go before 10'",
        "items": [
            {"source": "reel", "place": "Louvre, north wing at 9:00 sharp", "why": "11 reels mention empty galleries on first-Sunday mornings"},
            {"source": "reel", "place": "Crêpes at Le Consulaire, Saint-Germain", "why": "the one every food vlog queues for — 20 min at 12:30, 50 min at 13:30"},
            {"source": "reel", "place": "View from Sacré-Cœur steps, 19:00", "why": "city lights on, half the crowds gone"},
        ],
    },
}

CARDS = {
    "day-plan": day_plan, "budget": budget, "pass-grid": pass_grid,
    "approval": approval, "detour": detour, "finds": finds, "compare": compare,
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "badge":
        badge(sys.argv[2], sys.argv[3])
        print(sys.argv[3])
    elif cmd == "samples":
        outdir = sys.argv[2]
        os.makedirs(outdir, exist_ok=True)
        for name, payload in SAMPLES.items():
            CARDS[name](payload, os.path.join(outdir, name + ".png"))
        for key in AGENT_COLORS:
            badge(key, os.path.join(outdir, "badge-" + key + ".png"))
        print(outdir)
    elif cmd in CARDS:
        with open(sys.argv[2]) as f:
            data = json.load(f)
        CARDS[cmd](data, sys.argv[3])
        print(sys.argv[3])
    else:
        print("unknown card:", cmd)
        sys.exit(1)


if __name__ == "__main__":
    main()
