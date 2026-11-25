#!/usr/bin/env python3
"""news-image-20261124: one-day world news broadsheet poster.

Draws a 1024x1024 PNG summing up Tuesday 24 November 2026 world news and
writes it to /output/entry.png ($MAKEFUN_OUTPUT_DIR overrides the directory).
No network, stdlib + Pillow only, fully deterministic: repeated runs write
identical bytes.

Page plan (1024x1024): masthead with date + story counts -> DAY IN NUMBERS
strip (six figures, each first reported 24 Nov) -> STORIES BY REGION bar ->
hero tier of the day's three consensus leads, each with a map or diagram
(Hormuz strait, Huawei verdict, Ukraine's two-sea ship strikes) -> ten more
illustrated picture stories -> dotted world map (red pins 1-13 picture
stories, dots 14-36 briefs) -> 23 briefs grouped by region -> footer with
DATE CHECK (explicit exclusions split by day + a Not yet line), HOW SURE
legend and HOW TO READ box. All 36 stories first reported Tue 24 Nov 2026.
"""

import hashlib
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT_PATH = os.path.join(OUT_DIR, "entry.png")

# ---- palette: cool newsprint broadsheet, ink on paper ----
PAPER = (246, 242, 230)
INK = (18, 18, 18)
MUTED = (96, 90, 78)
FAINT = (150, 143, 126)
RED = (178, 30, 42)
NAVY = (26, 56, 92)
TEAL = (13, 108, 108)
GOLD = (172, 120, 20)
GREEN = (30, 118, 58)
CARD = (255, 255, 255)
LINE = (198, 190, 170)
SKY = (176, 212, 232)
SEA = (138, 188, 220)
LAND = (230, 220, 194)
SAND = (212, 194, 148)
PURPLE = (96, 58, 128)
ORANGE = (196, 96, 24)

REGION_COLORS = {
    "Middle East": (178, 30, 42),
    "Europe": (26, 56, 92),
    "Asia": (13, 108, 108),
    "Africa": (172, 120, 20),
    "Americas": (30, 118, 58),
    "Global": (96, 58, 128),
}

CONF_COLORS = {
    "CONFIRMED": (30, 118, 58),
    "OFFICIAL": (26, 56, 92),
    "REPORTED": (172, 120, 20),
    "CLAIM": (196, 96, 24),
    "FORECAST": (96, 58, 128),
}

# ---- fonts ----
_FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts",
]


def _find_font(bold=False):
    names = ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"] if bold else [
        "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    for d in _FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return p
    return None


_FONTS = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _FONTS:
        path = _find_font(bold)
        if path:
            _FONTS[key] = ImageFont.truetype(path, size)
        else:
            _FONTS[key] = ImageFont.load_default()
    return _FONTS[key]


def text_w(draw, s, size, bold=False):
    return draw.textlength(s, font=font(size, bold))


def wrap(draw, s, size, max_w, bold=False):
    """Greedy word wrap returning a list of lines fitting max_w."""
    f = font(size, bold)
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, s, size, max_w, fill=INK, bold=False, leading=None):
    """Draw wrapped paragraph; return y just below the last line."""
    lh = leading if leading is not None else size + 3
    for line in wrap(draw, s, size, max_w, bold):
        draw.text((x, y), line, font=font(size, bold), fill=fill)
        y += lh
    return y


def headline(draw, x, y, s, size, max_w, fill=INK, bold=True, leading=None):
    return para(draw, x, y, s, size, max_w, fill=fill, bold=bold, leading=leading)


def tag(draw, x, y, label, fill):
    """Small confidence tag chip; returns width used."""
    f = font(9, True)
    w = int(draw.textlength(label, font=f)) + 10
    draw.rounded_rectangle([x, y, x + w, y + 14], radius=3, fill=fill)
    draw.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def rule(draw, x0, x1, y, fill=LINE, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def pin(draw, cx, cy, n, r=9):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                 outline=(255, 255, 255), width=2)
    f = font(10, True)
    tw = draw.textlength(str(n), font=f)
    draw.text((cx - tw / 2, cy - 7), str(n), font=f, fill=(255, 255, 255))


def dot(draw, cx, cy, r=3, fill=NAVY):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
                 outline=(255, 255, 255), width=1)

# =====================================================================
# Layout sections. Each takes the canvas draw object and a data dict.
# =====================================================================

def draw_masthead(d):
    d.rectangle([0, 0, W, 66], fill=INK)
    d.text((18, 8), "THE WORLD IN ONE DAY", font=font(30, True),
           fill=(247, 243, 232))
    d.text((18, 42), "TUESDAY 24 NOVEMBER 2026  ·  36 STORIES  ·  6 REGIONS  ·  13 PICTURED",
           font=font(13, True), fill=(212, 176, 60))
    d.text((W - 18, 10), "ONE DAY.", font=font(20, True),
           fill=(247, 243, 232), anchor="ra")
    d.text((W - 18, 36), "ONE IMAGE.", font=font(20, True),
           fill=(212, 176, 60), anchor="ra")


NUMBERS = [
    ("$41bn", "Sanofi to buy Insmed", "Sanofi"),
    ("103.3", "US consumer confidence", "Conf. Board"),
    ("-5.9%", "Nvidia gives back Tue", "Nasdaq"),
    ("+3.9%", "Nikkei, Tue close", "Tokyo"),
    ("11", "hurt in Riyadh tower hit", "Riyadh"),
    ("25", "hostages in Cartagena", "Colombia"),
]


def draw_numbers(d, y0=72):
    d.rectangle([0, y0, W, y0 + 52], fill=(255, 255, 255))
    rule(d, 0, W, y0 + 51)
    d.text((18, y0 + 6), "DAY IN NUMBERS", font=font(11, True), fill=RED)
    d.text((18, y0 + 24), "every figure first reported 24 Nov",
           font=font(10), fill=MUTED)
    cw = (W - 260) // 6
    for i, (num, label, _src) in enumerate(NUMBERS):
        x = 250 + i * cw
        d.text((x, y0 + 4), num, font=font(20, True), fill=INK)
        for j, ln in enumerate(wrap(d, label, 9, cw - 8)):
            d.text((x, y0 + 28 + j * 11), ln, font=font(9), fill=MUTED)


REGION_COUNTS = [
    ("Middle East", 5),
    ("Europe", 6),
    ("Asia", 8),
    ("Americas", 10),
    ("Africa", 4),
    ("Global", 3),
]


def draw_region_bar(d, y0=130):
    d.text((18, y0), "STORIES BY REGION", font=font(11, True), fill=INK)
    total = sum(c for _, c in REGION_COUNTS)
    x = 18
    bar_w = W - 36
    y = y0 + 18
    for name, c in REGION_COUNTS:
        w = bar_w * c / total
        d.rectangle([x, y, x + w - 1, y + 14], fill=REGION_COLORS[name])
        x += w
    x = 18
    d.text((18, y0 + 36), "", font=font(9))
    labels = []
    for name, c in REGION_COUNTS:
        labels.append((name, c))
    lx = 18
    for name, c in labels:
        col = REGION_COLORS[name]
        d.rectangle([lx, y0 + 38, lx + 8, y0 + 46], fill=col)
        t = "%s %d" % (name, c)
        d.text((lx + 12, y0 + 37), t, font=font(10, True), fill=INK)
        lx += int(text_w(d, t, 10, True)) + 26

# =====================================================================
# Hero tier: three illustrated features, each a map or a diagram.
# =====================================================================

def hero_hormuz(d, x, y, w, h):
    """Strait of Hormuz diagram: mines, tankers, IRGC claim."""
    d.rectangle([x, y, x + w, y + h], fill=SKY, outline=LINE)
    # land masses top (Iran) and bottom (Oman/UAE), strait channel between
    d.polygon([(x, y), (x + w, y), (x + w, y + 26), (x + 150, y + 44),
               (x + 60, y + 30), (x, y + 40)], fill=LAND)
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 30),
               (x + 180, y + h - 52), (x + 90, y + h - 34), (x, y + h - 44)],
              fill=SAND)
    d.text((x + 8, y + 6), "IRAN", font=font(10, True), fill=MUTED)
    d.text((x + w - 52, y + h - 18), "OMAN", font=font(10, True), fill=MUTED)
    # strait channel
    d.line([(x + 30, y + 58), (x + w - 30, y + 62)], fill=NAVY, width=3)
    d.text((x + w // 2 - 44, y + 68), "STRAIT OF HORMUZ", font=font(9, True),
           fill=NAVY)
    # tankers + mines
    for tx, ty in [(x + 60, y + 84), (x + 150, y + 94), (x + 235, y + 80)]:
        d.rectangle([tx - 16, ty - 5, tx + 16, ty + 5], fill=(60, 60, 60))
        d.rectangle([tx - 4, ty - 11, tx + 6, ty - 5], fill=(120, 120, 120))
        d.text((tx - 18, ty + 8), "TANKER", font=font(8, True), fill=INK)
    for mx, my in [(x + 95, y + 76), (x + 190, y + 88), (x + 262, y + 72)]:
        d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((mx - 3, my - 4), "*", font=font(9, True), fill=(255, 255, 255))


def hero_huawei(d, x, y, w, h):
    """Huawei verdict diagram: three counts, two guilty, one acquitted."""
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE)
    d.text((x + 10, y + 6), "US v HUAWEI — NEW YORK · 10 OF 12 COUNTS",
           font=font(11, True), fill=INK)
    rows = [
        ("Trade secrets", "GUILTY", GREEN),
        ("Bank fraud", "GUILTY", GREEN),
        ("Racketeering", "ACQUITTED", RED),
    ]
    yy = y + 28
    for name, verdict, col in rows:
        d.rectangle([x + 10, yy, x + w - 10, yy + 22], fill=(246, 242, 230))
        d.text((x + 16, yy + 5), name, font=font(11, True), fill=INK)
        vw = int(text_w(d, verdict, 11, True)) + 12
        d.rectangle([x + w - 16 - vw, yy + 3, x + w - 16, yy + 19], fill=col)
        d.text((x + w - 10 - vw, yy + 5), verdict, font=font(11, True),
               fill=(255, 255, 255))
        yy += 25


def hero_ships(d, x, y, w, h):
    """Two-sea map: Gulf of Finland + Benghazi, Libya."""
    d.rectangle([x, y, x + w, y + h], fill=SEA, outline=LINE)
    # stylised Europe/Africa land
    d.polygon([(x, y), (x + w, y), (x + w, y + 40), (x + 190, y + 55),
               (x + 120, y + 30), (x, y + 46)], fill=LAND)
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h - 34),
               (x + 170, y + h - 60), (x + 80, y + h - 40), (x, y + h - 52)],
              fill=SAND)
    d.text((x + 8, y + 6), "EUROPE", font=font(10, True), fill=MUTED)
    d.text((x + w - 46, y + h - 18), "AFRICA", font=font(10, True), fill=MUTED)
    # Gulf of Finland pin (top right) and Benghazi pin (bottom)
    pin(d, x + 250, y + 48, 1, r=10)
    d.text((x + 168, y + 32), "GULF OF", font=font(8, True), fill=INK)
    d.text((x + 168, y + 42), "FINLAND", font=font(8, True), fill=INK)
    pin(d, x + 110, y + 72, 1, r=10)
    d.text((x + 126, y + 64), "BENGHAZI", font=font(8, True), fill=INK)
    # drone path arc (Gulf of Finland strike only)
    d.arc([x + 90, y + 40, x + 260, y + 104], start=200, end=340, fill=RED,
          width=2)

# =====================================================================
# Picture-story illustrations: small procedural vector scenes.
# Each draws inside (x, y, w, h).
# =====================================================================

def ill_tower(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 32, 48))
    for i in range(5):
        d.rectangle([x + 14 + i * 3, y + 12, x + 16 + i * 3, y + h - 14],
                    fill=(212, 176, 60))
    # PIF tower
    d.rectangle([x + w // 2 - 22, y + 14, x + w // 2 + 22, y + h - 12],
                fill=(120, 140, 170))
    for r in range(6):
        d.line([(x + w // 2 - 22, y + 22 + r * 10),
                (x + w // 2 + 22, y + 22 + r * 10)], fill=(200, 210, 225),
               width=1)
    # drone + smoke
    d.ellipse([x + w - 42, y + 18, x + w - 30, y + 26], fill=(220, 220, 220))
    d.line([(x + w - 46, y + 22), (x + w - 26, y + 22)], fill=INK, width=2)
    d.ellipse([x + w // 2 - 6, y + 8, x + w // 2 + 14, y + 20],
              fill=(200, 200, 200))
    d.text((x + 6, y + h - 14), "RIYADH", font=font(8, True), fill=(255, 255, 255))


def ill_pills(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 244, 238))
    # rising bars
    vals = [10, 17, 15, 25, 34]
    bw = (w - 24) // 5
    for i, v in enumerate(vals):
        bx = x + 12 + i * bw
        d.rectangle([bx, y + h - 14 - v, bx + bw - 6, y + h - 14],
                    fill=TEAL if i < 4 else GREEN)
    d.text((x + 8, y + 6), "$41bn", font=font(16, True), fill=INK)
    # pill
    d.ellipse([x + w - 46, y + 8, x + w - 14, y + 24], fill=(255, 255, 255),
              outline=RED, width=2)
    d.line([(x + w - 30, y + 8), (x + w - 30, y + 24)], fill=RED, width=2)


def ill_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 20, 44))
    for sx, sy in [(x + 16, y + 12), (x + 40, y + 30), (x + w - 20, y + 16),
                   (x + w - 44, y + 40), (x + 24, y + h - 20)]:
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    d.ellipse([x + w - 46, y + 10, x + w - 14, y + 42], fill=(240, 230, 200))
    # rocket body
    d.polygon([(x + w // 2, y + 12), (x + w // 2 + 10, y + 30),
               (x + w // 2 + 10, y + 62), (x + w // 2, y + 72),
               (x + w // 2 - 10, y + 62), (x + w // 2 - 10, y + 30)],
              fill=(255, 255, 255), outline=RED)
    d.ellipse([x + w // 2 - 4, y + 30, x + w // 2 + 4, y + 38], fill=SKY,
              outline=NAVY)
    d.polygon([(x + w // 2 - 12, y + 66), (x + w // 2 - 22, y + h - 10),
               (x + w // 2 - 6, y + 66)], fill=RED)
    d.polygon([(x + w // 2 + 12, y + 66), (x + w // 2 + 22, y + h - 10),
               (x + w // 2 + 6, y + 66)], fill=RED)
    d.polygon([(x + w // 2 - 5, y + 72), (x + w // 2 + 5, y + 72),
               (x + w // 2 + 12, y + h - 6), (x + w // 2 - 12, y + h - 6)],
              fill=GOLD)


def ill_store(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(246, 232, 210))
    # storefront
    d.rectangle([x + 10, y + 26, x + w - 10, y + h - 8], fill=(255, 255, 255),
                outline=INK)
    d.rectangle([x + 10, y + 26, x + w - 10, y + 38], fill=RED)
    d.text((x + 16, y + 28), "SUPERMARKET", font=font(9, True),
           fill=(255, 255, 255))
    d.rectangle([x + 20, y + 42, x + w // 2 - 6, y + h - 8], fill=SKY,
                outline=INK)
    d.rectangle([x + w // 2 + 6, y + 42, x + w - 20, y + h - 8], fill=SKY,
                outline=INK)
    d.text((x + 8, y + 8), "25 HOSTAGES", font=font(12, True), fill=RED)


def ill_heli(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 238))
    d.line([(x + 10, y + 30), (x + w - 10, y + 30)], fill=INK, width=3)
    d.ellipse([x + w // 2 - 34, y + 34, x + w // 2 + 30, y + 58],
              fill=(90, 110, 90))
    d.ellipse([x + w // 2 + 8, y + 38, x + w // 2 + 26, y + 52], fill=SKY)
    d.rectangle([x + w // 2 + 28, y + 42, x + w - 12, y + 50], fill=(90, 110, 90))
    d.line([(x + w // 2 - 8, y + 58), (x + w // 2 - 2, y + 70)], fill=INK,
           width=3)
    d.line([(x + w // 2 + 14, y + 58), (x + w // 2 + 20, y + 70)], fill=INK,
           width=3)
    d.text((x + 8, y + h - 14), "ESKISEHIR", font=font(8, True), fill=MUTED)


def ill_medical(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    d.rectangle([x + 10, y + 10, x + 34, y + 34], fill=RED)
    d.rectangle([x + 19, y + 13, x + 25, y + 31], fill=(255, 255, 255))
    d.rectangle([x + 13, y + 19, x + 31, y + 25], fill=(255, 255, 255))
    # case curve rising
    pts = [(x + 44, y + h - 20), (x + 70, y + h - 26), (x + 96, y + h - 24),
           (x + 122, y + h - 40), (x + 148, y + 26)]
    d.line(pts, fill=RED, width=3)
    d.text((x + 44, y + 10), "272 cases", font=font(14, True), fill=INK)
    d.text((x + 10, y + h - 14), "in October", font=font(10), fill=MUTED)


def ill_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 220))
    d.line([(x + 8, y + h // 2), (x + w - 8, y + h // 2)], fill=FAINT, width=1)
    pts = [(x + 8, y + h // 2), (x + 30, y + h // 2), (x + 40, y + h // 2 - 18),
           (x + 50, y + h // 2 + 14), (x + 60, y + h // 2 - 30),
           (x + 70, y + h // 2 + 22), (x + 80, y + h // 2 - 8),
           (x + 95, y + h // 2), (x + 120, y + h // 2 - 12),
           (x + 135, y + h // 2 + 10), (x + w - 8, y + h // 2)]
    d.line(pts, fill=RED, width=2)
    d.text((x + 8, y + 6), "M 5.6", font=font(16, True), fill=INK)
    d.text((x + 8, y + h - 16), "NEPAL", font=font(9, True), fill=MUTED)


def ill_car(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 238, 246))
    d.line([(x, y + h - 16), (x + w, y + h - 16)], fill=INK, width=2)
    # robotaxi body
    d.rounded_rectangle([x + 18, y + 34, x + w - 18, y + h - 22], radius=10,
                        fill=(255, 255, 255), outline=NAVY, width=2)
    d.polygon([(x + 44, y + 34), (x + 58, y + 18), (x + w - 58, y + 18),
               (x + w - 44, y + 34)], fill=SKY, outline=NAVY)
    d.ellipse([x + 34, y + h - 30, x + 50, y + h - 14], fill=INK)
    d.ellipse([x + w - 50, y + h - 30, x + w - 34, y + h - 14], fill=INK)
    # lidar puck + sensor arc
    d.rectangle([x + w // 2 - 8, y + 10, x + w // 2 + 8, y + 18], fill=NAVY)
    d.arc([x + w // 2 - 30, y + 2, x + w // 2 + 30, y + 32], start=180,
          end=360, fill=TEAL, width=2)
    d.text((x + 8, y + h - 14), "NO DRIVER", font=font(8, True), fill=NAVY)


def ill_phone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 30, 40))
    d.rounded_rectangle([x + w // 2 - 22, y + 8, x + w // 2 + 22, y + h - 8],
                        radius=8, fill=(255, 255, 255), outline=(200, 200, 200))
    d.rectangle([x + w // 2 - 16, y + 16, x + w // 2 + 16, y + 26], fill=INK)
    d.text((x + w // 2 - 14, y + 18), "TikTok", font=font(8, True),
           fill=(255, 255, 255))
    # error bars
    for i, hh in enumerate([10, 18, 8, 22]):
        bx = x + w // 2 - 16 + i * 9
        d.rectangle([bx, y + 62 - hh, bx + 6, y + 62], fill=RED)
    d.text((x + w // 2 - 20, y + 68), "25,000 reports", font=font(8, True),
           fill=(255, 255, 255))
    d.text((x + 8, y + 8), "OUTAGE", font=font(10, True), fill=(255, 120, 120))


def ill_trophy(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 90, 50))
    # trophy cup
    d.polygon([(x + w // 2 - 18, y + 14), (x + w // 2 + 18, y + 14),
               (x + w // 2 + 12, y + 40), (x + w // 2 - 12, y + 40)],
              fill=GOLD)
    d.arc([x + w // 2 - 30, y + 12, x + w // 2 - 10, y + 34], start=90,
          end=270, fill=GOLD, width=4)
    d.arc([x + w // 2 + 10, y + 12, x + w // 2 + 30, y + 34], start=270,
          end=90, fill=GOLD, width=4)
    d.rectangle([x + w // 2 - 4, y + 40, x + w // 2 + 4, y + 52], fill=GOLD)
    d.rectangle([x + w // 2 - 14, y + 52, x + w // 2 + 14, y + 58], fill=GOLD)
    d.text((x + 8, y + h - 16), "AFCON CHAMPIONS", font=font(9, True),
           fill=(255, 255, 255))
    d.text((x + 8, y + 8), "SENEGAL", font=font(11, True),
           fill=(255, 255, 255))

# =====================================================================
# Story data. Every story first reported Tue 24 Nov 2026 (UTC).
# conf: CONFIRMED 2+ outlets / OFFICIAL the body itself / REPORTED one
# outlet / CLAIM one side / FORECAST expected.
# =====================================================================

HEROES = [
    {
        "n": 1, "region": "Middle East", "conf": "REPORTED",
        "title": "Mines in the Strait of Hormuz",
        "summary": ("Tankers hit mines in the strait; Iran's Guard says it "
                    "struck a container ship too."),
        "outlet": "Gulf News / Al Jazeera", "ill": "hormuz",
    },
    {
        "n": 2, "region": "Asia", "conf": "CONFIRMED",
        "title": "Huawei guilty on 10 of 12 counts",
        "summary": ("A New York jury convicts Huawei of trade-secret theft "
                    "and bank fraud; acquits on racketeering."),
        "outlet": "Reuters / WSJ", "ill": "huawei",
    },
    {
        "n": 3, "region": "Europe", "conf": "OFFICIAL",
        "title": "Ukraine hits Russian ship Sparta II in the Gulf of Finland",
        "summary": ("Kyiv says drones hit the cargo ship Sparta II; it also "
                    "targets Russian networks in Libya, Sudan, Mali."),
        "outlet": "Daily Summary / HTT", "ill": "ships",
    },
]

PICTURES = [
    {
        "n": 4, "region": "Middle East", "conf": "CONFIRMED",
        "title": "Houthi drone hits Riyadh's PIF Tower",
        "summary": ("A drone strikes the 80-storey PIF Tower; 11 hurt, the second hit in a week."),
        "outlet": "Arab News", "ill": ill_tower,
    },
    {
        "n": 5, "region": "Europe", "conf": "OFFICIAL",
        "title": "Sanofi agrees to buy Insmed for $41bn",
        "summary": ("Sanofi agrees a $175-a-share cash deal for the US biotech Insmed."),
        "outlet": "Sanofi / WSJ", "ill": ill_pills,
    },
    {
        "n": 6, "region": "Asia", "conf": "OFFICIAL",
        "title": "China names Shenzhou-24 crew",
        "summary": ("Pakistan's Zeeshan Ali will be the first foreign astronaut on Tiangong."),
        "outlet": "Xinhua", "ill": ill_rocket,
    },
    {
        "n": 7, "region": "Americas", "conf": "OFFICIAL",
        "title": "25 hostages held in Cartagena supermarket",
        "summary": ("Armed men seize a Cartagena supermarket and hold 25 people hostage."),
        "outlet": "President's office", "ill": ill_store,
    },
    {
        "n": 8, "region": "Europe", "conf": "OFFICIAL",
        "title": "Turkish helicopter crashes, five killed",
        "summary": ("An AS-532 crashes after take-off from Eskisehir; all five crew die."),
        "outlet": "Defence ministry", "ill": ill_heli,
    },
    {
        "n": 9, "region": "Middle East", "conf": "OFFICIAL",
        "title": "Gaza declares meningitis alert",
        "summary": ("Gaza declares a Strip-wide alert after 272 meningitis cases in October."),
        "outlet": "Xinhua / Al Jazeera", "ill": ill_medical,
    },
    {
        "n": 10, "region": "Asia", "conf": "REPORTED",
        "title": "Magnitude 5.6 quake hits Nepal",
        "summary": ("A 5.6-magnitude quake strikes near the Chinese border."),
        "outlet": "Horizon / wires", "ill": ill_quake,
    },
    {
        "n": 11, "region": "Americas", "conf": "OFFICIAL",
        "title": "Driverless robotaxis roll out in the Bay Area",
        "summary": ("Nuro, Lucid and Uber begin fully driverless tests in the Bay Area."),
        "outlet": "Nuro / Morningstar", "ill": ill_car,
    },
    {
        "n": 12, "region": "Global", "conf": "REPORTED",
        "title": "TikTok goes down for an hour",
        "summary": ("Videos and search fail to load; ~25,000 outage reports "
                    "filed before service returns."),
        "outlet": "The Verge", "ill": ill_phone,
    },
    {
        "n": 13, "region": "Africa", "conf": "REPORTED",
        "title": "CAS restores Senegal as AFCON champions",
        "summary": ("CAS overturns CAF's ruling; Senegal's 1-0 win stands."),
        "outlet": "Daily Summary", "ill": ill_trophy,
    },
]

# Briefs: (number, region, confidence, one-line headline, outlet)
BRIEFS = [
    (14, "Europe", "REPORTED",
     "Putin vows retaliation as Ukraine hits Russian refineries", "Al Jazeera"),
    (15, "Europe", "CLAIM",
     "Poland accuses Russia of drone airspace violation", "Al Jazeera"),
    (16, "Middle East", "CONFIRMED",
     "Gaza strikes kill Hamas security chief Abu Nahal", "Al Jazeera"),
    (17, "Asia", "CONFIRMED",
     "Russian jets enter S. Korea ADIZ; false Ulleung alert", "Yonhap"),
    (18, "Global", "OFFICIAL",
     "UN: 47,000 women, girls killed by partners, family", "UN News"),
    (19, "Americas", "OFFICIAL",
     "UN chief marks 10 years of Colombia peace deal", "UN News"),
    (20, "Africa", "OFFICIAL",
     "Ebola team trapped in DR Congo hospital amid fighting", "WHO / UN"),
    (21, "Africa", "REPORTED",
     "Nigerian court nullifies Omo-Agege's 2027 ticket", "Green White Green"),
    (22, "Asia", "REPORTED",
     "Solomon Islands to end China security pact", "SMH"),
    (23, "Asia", "REPORTED",
     "Hasina says she will return to Bangladesh 16 Dec", "Reuters"),
    (24, "Africa", "OFFICIAL",
     "UN warns Sudan drone strikes kill civilians, block aid", "OCHA"),
    (25, "Americas", "REPORTED",
     "Nvidia gives back $240bn a day after its 31% surge", "Motley Fool"),
    (26, "Americas", "OFFICIAL",
     "US confidence jumps to 103.3, highest since Jan 2025", "Conf. Board"),
    (27, "Asia", "CONFIRMED",
     "Nikkei surges 3.91% to 58,644 on its first day back", "Nikkei"),
    (28, "Asia", "OFFICIAL",
     "Japan cuts spending view, first since Feb 2024", "Reuters"),
    (29, "Americas", "OFFICIAL",
     "FDA approves Cogent's Ekitna for advanced GIST", "FDA"),
    (30, "Americas", "OFFICIAL",
     "FDA approves Rinvoq for vitiligo, first systemic therapy", "AbbVie"),
    (31, "Europe", "OFFICIAL",
     "Russia launches Progress 97 cargo ship to the ISS", "NASA"),
    (32, "Global", "CONFIRMED",
     "Beaver Supermoon reaches full phase", "The Hindu"),
    (33, "Americas", "REPORTED",
     "New York bans AI chatbot toys for five years", "ABC7NY"),
    (34, "Americas", "REPORTED",
     "US prepares fresh tariff hikes on China, EU, others", "Moneycontrol"),
    (35, "Americas", "REPORTED",
     "Anthropic falls below its $83 IPO price in the AI sell-off", "Motley Fool"),
    (36, "Middle East", "OFFICIAL",
     "Iran: no talks with the US until seven conditions are met", "Gulf News"),
]

DATE_CHECK = [
    ("23 Nov", "Nvidia's Huang returns as CEO (+31%); Ukraine sinks a "
     "Russian corvette off Libya; CrowdStrike buys Zscaler ($43.9bn); "
     "US blacklists 7 firms; Vance & Rubio meet Qatar's PM"),
    ("22 Nov", "COP31 collapses without a fossil-fuel deal; Sudan drone "
     "strikes on Omdurman (UN warning is 24 Nov)"),
    ("21 Nov", "BepiColombo enters Mercury orbit"),
    ("Not yet", "Solomon Islands-Australia treaty signing (25 Nov); "
     "Hasina's return (16 Dec); Awami League shutdown (27-28 Nov)"),
]

# Map pins: (number, lon, lat) for picture stories; dots for briefs.
PINS = {
    1: (58, 27), 2: (-74, 41), 3: (24, 60), 4: (45, 23), 5: (2, 49),
    6: (100, 40), 7: (-75, 10), 8: (30, 40), 9: (33, 32), 10: (84, 28),
    11: (-122, 37), 12: (-118, 34), 13: (-17, 15),
}
DOTS = {
    14: (37, 56), 15: (21, 52), 16: (36, 33), 17: (131, 37), 18: (-73, 40),
    19: (-74, 5), 20: (30, 2), 21: (6, 5), 22: (160, -9), 23: (90, 24),
    24: (32, 16), 25: (-77, 39), 26: (-75, 41), 27: (140, 36),
    28: (139, 35), 29: (-77, 38), 30: (-87, 42), 31: (63, 46),
    32: (0, 82), 33: (-74, 43), 34: (-79, 39), 35: (-123, 38),
    36: (52, 36),
}

# =====================================================================
# Section renderers
# =====================================================================

HERO_ILLS = {"hormuz": hero_hormuz, "huawei": hero_huawei, "ships": hero_ships}


def draw_hero_card(d, x, y, w, h, story):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE)
    HERO_ILLS[story["ill"]](d, x + 1, y + 1, w - 2, 108)
    yy = y + 114
    yy = headline(d, x + 8, yy, "%d. %s" % (story["n"], story["title"]), 13,
                  w - 16, leading=15)
    yy = para(d, x + 8, yy + 2, story["summary"], 10, w - 16, fill=MUTED,
              leading=12)
    tw = tag(d, x + 8, yy, story["conf"], CONF_COLORS[story["conf"]])
    d.text((x + 8 + tw + 6, yy + 1), story["outlet"], font=font(9), fill=FAINT)


def draw_pic_card(d, x, y, w, h, story):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE)
    story["ill"](d, x + 1, y + 1, w - 2, 62)
    yy = y + 68
    yy = headline(d, x + 7, yy, "%d. %s" % (story["n"], story["title"]), 11,
                  w - 14, leading=12)
    yy = para(d, x + 7, yy + 1, story["summary"], 9, w - 14, fill=MUTED,
              leading=11)
    tag(d, x + 7, yy, story["conf"], CONF_COLORS[story["conf"]])


# Simplified continent outlines (lon, lat) for the dotted world map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 62), (-75, 58), (-65, 60), (-60, 52), (-70, 45), (-75, 38),
     (-80, 32), (-85, 29), (-90, 21), (-95, 19), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-135, 58), (-150, 60), (-165, 60)],
    # South America
    [(-80, 9), (-75, 11), (-65, 10), (-55, 6), (-50, 0), (-45, -5),
     (-38, -8), (-35, -15), (-40, -22), (-48, -28), (-55, -35), (-65, -42),
     (-70, -50), (-73, -40), (-73, -30), (-70, -18), (-78, -8), (-80, 0)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (12, 56),
     (18, 56), (21, 55), (24, 59), (28, 61), (30, 70), (40, 68), (45, 60),
     (40, 55), (35, 50), (30, 46), (28, 44), (23, 40), (20, 40), (15, 44),
     (10, 44), (5, 43), (0, 40), (-2, 37)],
    # Africa
    [(-17, 15), (-15, 27), (-10, 31), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (38, 20), (43, 12), (48, 11), (51, 2), (48, -5), (42, -12),
     (38, -20), (33, -26), (28, -33), (20, -35), (15, -28), (12, -18),
     (10, -8), (8, 4), (0, 5), (-8, 5), (-13, 8)],
    # Asia
    [(45, 60), (55, 68), (65, 70), (75, 73), (90, 75), (105, 77), (120, 73),
     (135, 72), (150, 70), (160, 66), (170, 65), (178, 65), (170, 60),
     (160, 55), (150, 45), (140, 40), (130, 35), (125, 30), (120, 25),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 8),
     (75, 8), (70, 20), (65, 25), (60, 25), (55, 26), (50, 29), (48, 30),
     (44, 35), (40, 40), (38, 45), (42, 50), (45, 55)],
    # Australia
    [(114, -22), (120, -33), (130, -32), (140, -38), (150, -37), (153, -27),
     (146, -19), (142, -11), (135, -12), (130, -13), (122, -14), (115, -20)],
]


def draw_world_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 244, 248), outline=LINE)
    d.text((x + 8, y + 5), "WHERE IT HAPPENED", font=font(10, True), fill=INK)
    d.text((x + 8, y + 19), "red pins 1-13 picture stories · dots 14-36 briefs",
           font=font(9), fill=MUTED)

    def proj(lon, lat):
        px = x + 8 + (lon + 180) / 360.0 * (w - 16)
        py = y + 34 + (82 - lat) / 142.0 * (h - 40)
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=(180, 168, 140))
    for n, (lon, lat) in sorted(PINS.items()):
        px, py = proj(lon, lat)
        pin(d, px, py, n, r=8)
    for n, (lon, lat) in sorted(DOTS.items()):
        px, py = proj(lon, lat)
        dot(d, px, py, r=3)
    d.text((x + w - 8, y + h - 14), "32 = the Moon (sky)", font=font(8),
           fill=MUTED, anchor="ra")


BRIEF_GROUPS = [
    ("Middle East", [16, 36]),
    ("Europe", [14, 15, 31]),
    ("Africa", [20, 21, 24]),
    ("Asia", [17, 22, 23, 27, 28]),
    ("Global", [18, 32]),
    ("Americas", [19, 25, 26, 29, 30, 33, 34, 35]),
]


def draw_briefs(d, x, y, w, h):
    by_n = {b[0]: b for b in BRIEFS}
    cols = [
        [("Middle East", [16, 36]), ("Europe", [14, 15, 31]),
         ("Africa", [20, 21, 24])],
        [("Asia", [17, 22, 23, 27, 28]), ("Global", [18, 32])],
        [("Americas", [19, 25, 26, 29, 30, 33, 34, 35])],
    ]
    cw = (w - 24) // 3
    for ci, groups in enumerate(cols):
        cx = x + ci * (cw + 12)
        cy = y
        for gname, nums in groups:
            d.text((cx, cy), gname.upper(), font=font(10, True),
                   fill=REGION_COLORS[gname])
            cy += 13
            for n in nums:
                _, region, conf, head, outlet = by_n[n]
                col = CONF_COLORS[conf]
                d.rectangle([cx, cy + 1, cx + 7, cy + 8], fill=col)
                line = "%d. %s" % (n, head)
                f = font(9, True)
                while d.textlength(line, font=f) > cw - 12 and len(line) > 12:
                    line = line[:-4].rstrip() + "…"
                d.text((cx + 11, cy), line, font=f, fill=INK)
                cy += 12
            cy += 3


def draw_footer(d, y0):
    d.rectangle([0, y0, W, H], fill=(238, 234, 222))
    rule(d, 0, W, y0, fill=INK, width=2)
    # DATE CHECK box, left
    d.text((18, y0 + 8), "DATE CHECK — TUESDAY 24 NOVEMBER 2026 ONLY",
           font=font(11, True), fill=RED)
    yy = y0 + 26
    for day, text in DATE_CHECK:
        d.text((18, yy), day + ":", font=font(9, True), fill=INK)
        yy = para(d, 72, yy, text, 9, 560, fill=INK, leading=11)
        yy += 1
    # HOW SURE legend, right
    rx = 660
    d.text((rx, y0 + 8), "HOW SURE", font=font(11, True), fill=INK)
    lx = rx
    for label, col in CONF_COLORS.items():
        lw = tag(d, lx, y0 + 26, label, col)
        lx += lw + 5
    d.text((rx, y0 + 46),
           "CONFIRMED 2+ outlets · OFFICIAL the body · REPORTED 1 outlet · "
           "CLAIM 1 side", font=font(9), fill=MUTED)
    yy = para(d, rx, y0 + 60,
              "HOW TO READ — thumbnail: date, 3 leads, 6 big numbers. Full "
              "size: 36 briefs by region, a world map, a date check.",
              9, W - rx - 18, fill=INK, leading=11)

# =====================================================================
# Assemble + write the poster. Deterministic: fixed palette, fixed
# fonts, fixed layout, PNG written with a fixed timestamp-free encoder
# (Pillow writes no time chunk for PNG by default).
# =====================================================================

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_numbers(d, y0=72)
    draw_region_bar(d, y0=130)
    # hero tier: 3 cards
    hx = [18, 350, 682]
    for i, story in enumerate(HEROES):
        draw_hero_card(d, hx[i], 186, 324, 184, story)
    # picture stories: 2 rows of 5
    px = [18 + i * 199 for i in range(5)]
    for row in range(2):
        for col in range(5):
            story = PICTURES[row * 5 + col]
            draw_pic_card(d, px[col], 376 + row * 142, 190, 138, story)
    # world map
    draw_world_map(d, 18, 662, 988, 120)
    # briefs grouped by region
    draw_briefs(d, 18, 788, 988, 140)
    # footer: date check + how sure + how to read
    draw_footer(d, 934)
    return img


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    img = build()
    img.save(OUT_PATH, format="PNG", optimize=True)
    data = open(OUT_PATH, "rb").read()
    print("wrote %s (%d bytes) sha256=%s" % (
        OUT_PATH, len(data), hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
