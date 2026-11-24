#!/usr/bin/env python3
"""
The World Today -- 24 November 2026.

A one-page newspaper front sheet, drawn entirely with Pillow.
Every shape and every letter below is placed by this script;
there are no image assets, no downloads and no network access.

Usage:  python3 draw.py [output.png]
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette

PAPER = (247, 242, 231)
SHEET = (255, 254, 248)
INK = (26, 25, 23)
FADED = (92, 86, 76)
RED = (168, 44, 38)
NAVY = (31, 55, 92)
GREEN = (21, 110, 64)
HAIRLINE = (196, 188, 168)

PAGE = 1024
EDGE = 36                      # outer margin on every side
GUTTER = 16                    # gap between neighbouring panels

# ---------------------------------------------------------------- fonts

_FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _load(name, size):
    path = os.path.join(_FONT_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


class Type:
    """The handful of type styles the page is set in."""

    def __init__(self):
        self.masthead = _load("DejaVuSerif-Bold.ttf", 57)
        self.dateline = _load("DejaVuSans.ttf", 15)
        self.kicker = _load("DejaVuSans-Bold.ttf", 13)
        self.lead_head = _load("DejaVuSans-Bold.ttf", 38)
        self.lead_body = _load("DejaVuSans.ttf", 16)
        self.head = _load("DejaVuSans-Bold.ttf", 20)
        self.head_mid = _load("DejaVuSans-Bold.ttf", 19)
        self.head_big = _load("DejaVuSans-Bold.ttf", 25)
        self.body = _load("DejaVuSans.ttf", 14)
        self.body_tight = _load("DejaVuSans.ttf", 13)
        self.wide_body = _load("DejaVuSans.ttf", 15)
        self.stat_num = _load("DejaVuSans-Bold.ttf", 30)
        self.stat_lab = _load("DejaVuSans.ttf", 12)
        self.brief_head = _load("DejaVuSans-Bold.ttf", 14)
        self.foot = _load("DejaVuSans.ttf", 11)


# ---------------------------------------------------------------- text help

def wrap_to(draw, text, font, width):
    """Greedy word wrap driven by real glyph widths."""
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def lay_text(draw, xy, text, font, fill, width, leading, max_lines=None):
    """Draw wrapped text; returns the y just past the last line."""
    x, y = xy
    lines = wrap_to(draw, text, font, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .,;:") + "…"
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- panels

def panel_frame(draw, box, fill=SHEET):
    draw.rectangle(box, fill=fill, outline=INK, width=2)


def story(draw, box, kicker, headline, body, t,
          head_font=None, body_font=None, head_leading=25, body_leading=19):
    """One news story inside its frame: kicker, headline, then copy."""
    panel_frame(draw, box)
    x0, y0, x1, y1 = box
    pad = 16
    inner_w = (x1 - x0) - 2 * pad
    head_font = head_font or t.head
    body_font = body_font or t.body
    y = y0 + pad
    if kicker:
        draw.rectangle([x0 + pad, y + 2, x0 + pad + 4, y + 15], fill=RED)
        draw.text((x0 + pad + 11, y), kicker, font=t.kicker, fill=RED)
        y += 22
    y = lay_text(draw, (x0 + pad, y), headline, head_font, INK,
                 inner_w, head_leading)
    y += 5
    room = int((y1 - pad - y) // body_leading)
    lay_text(draw, (x0 + pad, y), body, body_font, INK,
             inner_w, body_leading, max_lines=max(room, 1))


# ---------------------------------------------------------------- page parts

def masthead(draw, t):
    draw.line([(EDGE, 26), (PAGE - EDGE, 26)], fill=INK, width=3)
    title = "The World Today"
    w = draw.textlength(title, font=t.masthead)
    draw.text(((PAGE - w) / 2, 38), title, font=t.masthead, fill=INK)
    line = "Tuesday · 24 November 2026 · One page, the whole day"
    w = draw.textlength(line, font=t.dateline)
    draw.text(((PAGE - w) / 2, 108), line, font=t.dateline, fill=FADED)
    draw.line([(EDGE, 134), (PAGE - EDGE, 134)], fill=INK, width=2)
    draw.line([(EDGE, 139), (PAGE - EDGE, 139)], fill=INK, width=1)


def lead_story(draw, t):
    box = (EDGE, 156, 660, 476)
    panel_frame(draw, box)
    x0, y0, x1, y1 = box
    pad = 18
    inner_w = (x1 - x0) - 2 * pad
    y = y0 + pad
    draw.rectangle([x0 + pad, y + 2, x0 + pad + 4, y + 15], fill=RED)
    draw.text((x0 + pad + 11, y), "BUSINESS — THE LEAD",
              font=t.kicker, fill=RED)
    y += 26
    y = lay_text(draw, (x0 + pad, y),
                 "HUANG BACK AT NVIDIA; SHARES SOAR 31%",
                 t.lead_head, INK, inner_w, 46)
    y += 8
    body = (
        "NVIDIA's board voted unanimously to bring Jensen Huang back as "
        "president, chief executive and director — eleven days after his "
        "resignation, and following intervention by President Trump. "
        "Investors cheered the return of the company's founder."
    )
    lay_text(draw, (x0 + pad, y), body, t.lead_body, INK, inner_w, 23)
    # stat strip along the bottom of the lead panel
    strip_y = y1 - 74
    draw.line([(x0 + pad, strip_y - 10), (x1 - pad, strip_y - 10)],
              fill=HAIRLINE, width=1)
    mid = (x0 + x1) // 2
    for cx, num, lab in (
        (x0 + pad, "+31%", "one-day jump in the share price"),
        (mid + 8, "≈ $950B", "market value added in a day"),
    ):
        draw.text((cx, strip_y), num, font=t.stat_num, fill=GREEN)
        draw.text((cx, strip_y + 38), lab, font=t.stat_lab, fill=FADED)
    draw.text((x0 + pad, strip_y + 56),
              "The largest one-day gain ever recorded for a US company.",
              font=t.stat_lab, fill=FADED)


def briefs_band(draw, t):
    box = (EDGE, 842, PAGE - EDGE, 984)
    panel_frame(draw, box, fill=(243, 238, 226))
    x0, y0, x1, y1 = box
    draw.text((x0 + 16, y0 + 12), "ALSO TODAY", font=t.kicker, fill=NAVY)
    draw.line([(x0 + 16, y0 + 36), (x1 - 16, y0 + 36)], fill=HAIRLINE, width=1)
    col_w = (x1 - x0 - 32 - 2 * GUTTER) // 3
    briefs = [
        ("UKRAINE'S SEA DRONES",
         "Kyiv confirms seven sea drones sank the Russian corvette "
         "Merkury at Benghazi and hit the cargo ship Angara."),
        ("AI SAFETY FRAMEWORK",
         "UN chief António Guterres wants a global AI safety "
         "framework agreed within a year."),
        ("STATES SUE OVER GROK",
         "US states are suing SpaceX over sexualised images "
         "generated by its Grok chatbot."),
    ]
    for i, (head, body) in enumerate(briefs):
        cx = x0 + 16 + i * (col_w + GUTTER)
        cy = lay_text(draw, (cx, y0 + 48), head, t.brief_head, INK,
                      col_w, 18)
        lay_text(draw, (cx, cy + 4), body, t.body_tight, INK, col_w, 18,
                 max_lines=4)


# ---------------------------------------------------------------- assemble

def build_page():
    t = Type()
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(img)

    masthead(draw, t)
    lead_story(draw, t)

    # top-right story, beside the lead
    story(draw, (676, 156, PAGE - EDGE, 476), "THE HAGUE",
          "14 NATIONS BACK ICJ GENOCIDE RULING",
          "Fourteen countries jointly acknowledged the International "
          "Court of Justice ruling of 19 November that Myanmar "
          "committed genocide against the Rohingya. Britain formally "
          "recognised the genocide and sanctioned five senior "
          "military figures.",
          t, head_leading=26, body_leading=20)

    # middle row: three stories side by side
    row_y0, row_y1 = 492, 714
    story(draw, (EDGE, row_y0, 340, row_y1), "MOSCOW",
          "MEDVEDEV FLOATS PREVENTIVE NUCLEAR STRIKE",
          "In a 23 November article, Dmitry Medvedev argued a massive "
          "conventional attack could justify a preventive nuclear "
          "strike. Moscow told Estonia its actions were “on the "
          "verge of triggering open war.”",
          t, head_font=t.head_mid, head_leading=23,
          body_font=t.body_tight, body_leading=17)
    story(draw, (356, row_y0, 660, row_y1), "BERLIN",
          "NATO VOWS TO DEFEND SPACE ITSELF",
          "Western intelligence believes Russia's nuclear-armed "
          "satellite “Sputnik-S” could launch within about 60 days. "
          "In Berlin, Mark Rutte said NATO's pledge covers space; "
          "the Kremlin dismissed it.",
          t, head_font=t.head_mid, head_leading=23,
          body_font=t.body_tight, body_leading=17)
    story(draw, (676, row_y0, PAGE - EDGE, row_y1), "NEPAL",
          "5.6 QUAKE SHAKES NEPAL NEAR TIBET",
          "Magnitude 5.6 at 07:17 on Tuesday near Olangchung Gola, "
          "Taplejung, Koshi province, by the Tibet border. Felt in "
          "Kathmandu; no casualties or major damage so far. Other "
          "agencies recorded 5.3.",
          t, head_font=t.head_mid, head_leading=23,
          body_font=t.body_tight, body_leading=17)

    # wide business story
    wide = (EDGE, 728, PAGE - EDGE, 826)
    panel_frame(draw, wide)
    draw.text((EDGE + 16, 744), "DEALS", font=t.kicker, fill=RED)
    draw.text((EDGE + 16, 766), "SANOFI TO BUY INSMED FOR $41 BILLION",
              font=t.head_big, fill=INK)
    draw.text((EDGE + 16, 800),
              "Announced Tuesday: $175 a share in cash — the biggest "
              "biotech takeover in nearly three years.",
              font=t.wide_body, fill=INK)

    briefs_band(draw, t)

    foot = "Drawn in code with Pillow · Facts checked against the day's reporting"
    w = draw.textlength(foot, font=t.foot)
    draw.text(((PAGE - w) / 2, 996), foot, font=t.foot, fill=FADED)
    return img


def main(argv):
    out = argv[1] if len(argv) > 1 else "entry.png"
    page = build_page()
    assert page.size == (PAGE, PAGE), page.size
    page.save(out, format="PNG", optimize=True)
    print(f"wrote {out}: {page.size[0]}x{page.size[1]}, "
          f"{os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main(sys.argv)
