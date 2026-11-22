#!/usr/bin/env python3
"""Draw the 21 November 2026 front page as a 1024x1024 PNG.

Layout (all pixels, top to bottom): a navy masthead with the title
and the date, one full-width lead card, a 2x2 grid of cards, one
full-width bottom card, and a footer naming the day and the sources.
Everything is drawn with Pillow only; no network, no downloaded
images. Run: python3 render.py  ->  writes entry.png next to this file.

Vertical budget, measured so no text overlaps: masthead 24-164,
lead 178-400 (red band, white 46pt headline, body at 20pt so the
missile-and-drone + air-defence wording fits in 3 lines), grid rows
412-608 and 620-816, bottom card 828-962, footer lines at 972 and
990. Grid bodies are wrapped to three lines at 16pt (the Science
card gets four lines at 14pt: its headline is one line, so the
extra line fits above the source line; the Mexico card gets four
lines at 15pt with 16pt leading: its full toll sentence needs the
fourth line, and the card's assert still passes). No body is ever
cut silently: fit_text marks a cut with an ellipsis and an assert
fails the render if a body would run into its source line, and a
hard width assert in fit_text fails the render on any line wider
than its budget. The lead headline carries its own assert that it
fits its 1-line width budget. font() raises instead of falling
back to Pillow's bitmap default.
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (255, 255, 255)
INK = (17, 17, 17)
NAVY = (11, 31, 58)
RED = (178, 24, 24)
GOLD = (255, 211, 77)
CREAM = (255, 244, 224)
SKY = (232, 240, 248)
TEAL = (0, 110, 110)
GREEN = (28, 110, 48)
GREY = (90, 90, 90)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    # Fail loudly: a missing font file must never silently become
    # Pillow's bitmap default, or the committed PNG would stop
    # being reproducible from this script.
    return ImageFont.truetype(path, size)


def wrap_text(text, fnt, max_w):
    """Split text into lines that fit max_w pixels (greedy, by word)."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if fnt.getlength(trial) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fit_text(text, fnt, max_w, max_lines):
    """Wrap text to at most max_lines. A cut line ends with an
    ellipsis, so a sentence lost to trimming stays visible
    instead of vanishing silently."""
    lines = wrap_text(text, fnt, max_w)
    if len(lines) <= max_lines:
        for line in lines:
            assert fnt.getlength(line) <= max_w, \
                "fit_text line exceeds width budget: " + line
        return lines
    kept = lines[:max_lines]
    last = kept[-1]
    while fnt.getlength(last + " …") > max_w and len(last) > 1:
        last = last[:-1].rstrip()
    kept[-1] = last + " …"
    for line in kept:
        assert fnt.getlength(line) <= max_w, \
            "fit_text line exceeds width budget: " + line
    return kept


def draw_lines(draw, lines, fnt, x, y, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def shrink_to_fit(text, path, start_size, max_w, max_lines, min_size=14):
    """Largest font size whose wrapped text fits in max_lines lines."""
    size = start_size
    while size > min_size:
        fnt = font(path, size)
        if len(wrap_text(text, fnt, max_w)) <= max_lines:
            return fnt
        size -= 1
    return font(path, min_size)


def card(draw, box, strip, kicker, headline, body, source, bg=PAPER,
         max_body_lines=3, body_size=16, body_leading=20):
    """A grid card: colour strip, kicker, headline (<=2 lines),
    body (<= max_body_lines lines), source line at the bottom.
    The body is never cut silently: fit_text marks a cut with an
    ellipsis, and the assert fails the render if the body would
    run into the source line."""
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=bg, outline=INK, width=2)
    draw.rectangle([x0, y0, x1, y0 + 9], fill=strip)
    pad = 16
    cx = x0 + pad
    cw = x1 - x0 - 2 * pad
    y = y0 + 18
    kf = font(SANS_B, 16)
    draw.text((cx, y), kicker, font=kf, fill=RED)
    y += 24
    hf = shrink_to_fit(headline, SERIF_B, 27, cw, 2)
    lines = wrap_text(headline, hf, cw)
    y = draw_lines(draw, lines, hf, cx, y, INK, 30)
    y += 4
    bf = font(SANS, body_size)
    blines = fit_text(body, bf, cw, max_body_lines)
    y = draw_lines(draw, blines, bf, cx, y, (40, 40, 40), body_leading)
    assert y <= y1 - 24, "card body overflows into source line: " + kicker
    sf = font(SANS_B, 13)
    draw.text((cx, y1 - 24), source, font=sf, fill=GREY)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead: navy band, red rule, title + date ----
    d.rectangle([24, 24, 1000, 158], fill=NAVY)
    d.rectangle([24, 158, 1000, 164], fill=RED)
    title = "Six Stories, One Saturday"
    tf = shrink_to_fit(title, SERIF_B, 62, 940, 1, min_size=40)
    tw = tf.getlength(title)
    d.text(((W - tw) / 2, 44), title, font=tf, fill=(255, 255, 255))
    date = "SATURDAY  21  NOVEMBER  2026"
    df = font(SANS_B, 26)
    dw = df.getlength(date)
    d.text(((W - dw) / 2, 116), date, font=df, fill=GOLD)

    # ---- Lead card: full width, red band, white headline ----
    # The red band is the thumbnail anchor: at 256px the navy
    # masthead plus this band and the white headline still read as
    # one bold block; at 128px it reads as a colour block (the
    # masthead title stays readable). A pictorial "21" device was
    # tried in round 2 and reverted: a gold ring badge crowded the
    # headline's "Bahrain" and read as a speck at 128px, and a
    # giant watermark "21" behind the text read as a smudge.
    lx0, ly0, lx1, ly1 = 24, 178, 1000, 400
    d.rectangle([lx0, ly0, lx1, ly1], fill=RED, outline=INK, width=2)
    pad = 30
    cx = lx0 + pad
    cw = lx1 - lx0 - 2 * pad
    y = ly0 + 16
    kf = font(SANS_B, 19)
    d.text((cx, y), "LEAD  ·  MIDDLE EAST", font=kf, fill=GOLD)
    y += 30
    lead_headline = "Iran says it hit US bases in Bahrain"
    hf = shrink_to_fit(lead_headline, SERIF_B, 46, cw, 1)
    assert hf.getlength(lead_headline) <= cw, \
        "lead headline exceeds its 1-line width budget"
    d.text((cx, y), lead_headline, font=hf, fill=(255, 255, 255))
    y += 56
    bf = font(SANS, 20)
    body = ("Late Saturday, Iran's Revolutionary Guards say their missile-and-drone attack hit US "
            "bases at al-Riffa and Awali in Bahrain, claiming two Patriot air-defence radars destroyed. Bahrain says an "
            "industrial site caught fire, no injuries there; air "
            "defences intercepted more attacks.")
    blines = fit_text(body, bf, cw, 3)
    y = draw_lines(d, blines, bf, cx, y, CREAM, 29)
    assert y <= ly1 - 28, "lead body overflows into the source line"
    sf = font(SANS_B, 15)
    d.text((cx, ly1 - 28), "REUTERS  ·  AL JAZEERA", font=sf, fill=(255, 235, 235))

    # ---- 2x2 grid of cards ----
    grid = [
        ((24, 412, 503, 608), TEAL, "MEXICO  —  ANNOUNCED SATURDAY",
         "Mexico seizes\n'El Chapo Isidro'",
         "Special forces seized 'El Chapo Isidro', one of the FBI's 10 most "
         "wanted, in Guasave Friday night. Eleven died — seven gunmen, four soldiers — "
         "the Defence Ministry said. Gunfire halted a baseball game; fans fled.",
         "REUTERS  ·  AP", 4, 15, 16),
        ((521, 412, 1000, 608), NAVY, "SCIENCE",
         "Riemann proof certified",
         "Claimed Friday 20 Nov by Levent Alpoge, with help from Claude, Anthropic's AI; "
         "certified Saturday by the Lean and Mathlib teams. The 17-million-line "
         "Lean code checks out. The generalised hypothesis is not yet "
         "certified; no peer review yet.",
         "SCIENTIFIC AMERICAN  ·  THE HINDU", 4, 14, 18),
        ((24, 620, 503, 816), RED, "SPORT  —  FORMULA 1",
         "Verstappen wins Vegas thriller",
         "Verstappen beat Norris by 0.639s to win in Las Vegas. "
         "Russell hit the wall three laps from the end and finished "
         "ninth, with Piastri third.",
         "REUTERS  ·  FORMULA1.COM  ·  FIA", 3, 16, 20),
        ((521, 620, 1000, 816), GREEN, "SPORT  —  CRICKET",
         "Rahul's 136 puts India ahead",
         "KL Rahul's 136 runs and Shubman Gill's 98 carried India to 486–4 "
         "at the close on Day 3 in Wellington, a lead of 118 over "
         "New Zealand's 368.",
         "TELEGRAPH INDIA  ·  DECCAN HERALD", 3, 16, 20),
    ]
    for box, strip, kicker, head, body, src, max_lines, bsize, blead in grid:
        card(d, box, strip, kicker, head, body, src,
             max_body_lines=max_lines, body_size=bsize, body_leading=blead)

    # ---- Bottom card: Akvan, full width, pale blue ----
    # Source rides on the kicker line (right-aligned) so the two
    # body lines and the headline all fit inside 134px.
    bx0, by0, bx1, by1 = 24, 828, 1000, 962
    d.rectangle([bx0, by0, bx1, by1], fill=SKY, outline=INK, width=2)
    d.rectangle([bx0, by0, bx1, by0 + 9], fill=NAVY)
    cx = bx0 + 30
    cw = bx1 - bx0 - 60
    y = by0 + 16
    kf = font(SANS_B, 17)
    d.text((cx, y), "INDIA  —  WEATHER", font=kf, fill=RED)
    sf = font(SANS_B, 14)
    src = "THE HINDU  ·  DT NEXT"
    d.text((bx1 - 30 - sf.getlength(src), y), src, font=sf, fill=GREY)
    y += 26
    hf = shrink_to_fit("Odisha: no lives lost", SERIF_B, 30, cw, 1)
    d.text((cx, y), "Odisha: no lives lost", font=hf, fill=INK)
    y += 40
    bf = font(SANS, 18)
    body = ("After Friday's landfall near Gopalpur, Cyclone Akvan weakened "
            "to a depression. Odisha reports no major damage and no deaths "
            "after more than 440,000 people were moved to safety before "
            "it hit.")
    y = draw_lines(d, fit_text(body, bf, cw, 2), bf, cx, y, (40, 40, 40), 24)
    assert y <= by1 - 4, "Akvan body overflows the bottom card"

    # ---- Footer ----
    ff = font(SANS_B, 12)
    f1 = "SIX STORIES FROM SATURDAY 21 NOVEMBER 2026"
    f2 = "SOURCES: REUTERS · AP · AL JAZEERA · SCIENTIFIC AMERICAN · THE HINDU · FORMULA1.COM · FIA · TELEGRAPH INDIA · DECCAN HERALD · DT NEXT"
    for i, line in enumerate((f1, f2)):
        lw = ff.getlength(line)
        d.text(((W - lw) / 2, 972 + i * 18), line, font=ff, fill=GREY)

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
