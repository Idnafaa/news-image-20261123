#!/usr/bin/env python3
"""Fresh renderer for the 23 November 2026 one-day broadsheet.

Structure invented for this edition:
  - masthead band with date plate
  - lead story as a wide editorial panel with a cracked-globe motif
  - six illustrated cards in a 3x2 grid, each with its own tiny pictogram
  - twenty-four briefs in three ruled columns at the foot of the page
Drawn with Pillow at 2x scale then down-sampled for crisp type.
Output is deterministic: fixed palette, fixed fonts, no timestamps.
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap

W = H = 1024
S = 2  # supersample factor

PAPER = (247, 243, 232)
INK = (17, 17, 17)
MUTED = (82, 76, 66)
RED = (185, 28, 28)
NAVY = (30, 58, 95)
TEAL = (15, 118, 110)
GOLD = (180, 83, 9)
SLATE = (71, 85, 105)
RULE = (180, 172, 155)

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"

def font(path, size):
    return ImageFont.truetype(path, int(size * S))

def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(draw, xy, text, fnt, fill, max_w, leading, max_lines=99):
    x, y = xy
    for line in wrap(draw, text, fnt, max_w)[:max_lines]:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y

def pill(draw, xy, text, fill, fnt):
    x, y = xy
    tw = draw.textlength(text, font=fnt)
    pad = 6 * S
    draw.rounded_rectangle([x, y, x + tw + pad * 2, y + 16 * S], radius=8 * S, fill=fill)
    draw.text((x + pad, y + 2 * S), text, font=fnt, fill=(255, 255, 255))
    return x + tw + pad * 2

# --- tiny pictograms, drawn per-card -------------------------------------

def icon_ship(d, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    d.polygon([(x0+6*S, cy+10*S), (x1-6*S, cy+10*S), (x1-14*S, cy+22*S), (x0+14*S, cy+22*S)], fill=col)
    d.rectangle([cx-18*S, cy-6*S, cx+18*S, cy+10*S], fill=col)
    d.line([(cx, cy-20*S), (cx, cy-6*S)], fill=col, width=3*S)
    for dx in (-20, 0, 20):
        d.arc([cx+dx*S-10*S, cy+22*S, cx+dx*S+10*S, cy+32*S], 0, 180, fill=TEAL, width=2*S)

def icon_capitol(d, box, col):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    d.arc([cx-24*S, y0+8*S, cx+24*S, y0+44*S], 180, 360, fill=col, width=3*S)
    d.rectangle([cx-3*S, y0+2*S, cx+3*S, y0+14*S], fill=col)
    d.rectangle([x0+8*S, y0+30*S, x1-8*S, y1-10*S], outline=col, width=2*S)
    for i in range(5):
        xx = x0 + (14 + i * 11) * S
        d.line([(xx, y0+34*S), (xx, y1-14*S)], fill=col, width=2*S)

def icon_flame(d, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0+x1)//2, (y0+y1)//2
    d.polygon([(cx, y0+4*S), (cx+16*S, cy+8*S), (cx+10*S, y1-6*S), (cx-10*S, y1-6*S), (cx-16*S, cy+8*S)], fill=col)
    d.polygon([(cx, cy-2*S), (cx+7*S, cy+12*S), (cx-7*S, cy+12*S)], fill=(251,191,36))

def icon_drone(d, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0+x1)//2, (y0+y1)//2
    d.ellipse([cx-8*S, cy-8*S, cx+8*S, cy+8*S], fill=col)
    for dx, dy in [(-22,-14),(22,-14),(-22,14),(22,14)]:
        d.line([(cx,cy),(cx+dx*S,cy+dy*S)], fill=col, width=2*S)
        d.ellipse([cx+dx*S-6*S, cy+dy*S-3*S, cx+dx*S+6*S, cy+dy*S+3*S], outline=col, width=2*S)

def icon_handshake(d, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0+x1)//2, (y0+y1)//2
    d.ellipse([x0+8*S, cy-18*S, x0+34*S, cy+8*S], outline=col, width=3*S)
    d.ellipse([x1-34*S, cy-18*S, x1-8*S, cy+8*S], outline=col, width=3*S)
    d.line([(x0+20*S, cy+10*S), (x1-20*S, cy+10*S)], fill=col, width=3*S)
    d.text((cx, cy-8*S), "IN  NP", font=font(SANS_B, 9), fill=col, anchor="mm")

def icon_chip(d, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0+x1)//2, (y0+y1)//2
    d.rounded_rectangle([cx-18*S, cy-18*S, cx+18*S, cy+18*S], radius=4*S, outline=col, width=3*S)
    d.rounded_rectangle([cx-8*S, cy-8*S, cx+8*S, cy+8*S], radius=2*S, fill=col)
    for i in range(-1, 2):
        d.line([(cx+i*12*S, cy-18*S),(cx+i*12*S, cy-26*S)], fill=col, width=2*S)
        d.line([(cx+i*12*S, cy+18*S),(cx+i*12*S, cy+26*S)], fill=col, width=2*S)
        d.line([(cx-18*S, cy+i*12*S),(cx-26*S, cy+i*12*S)], fill=col, width=2*S)
        d.line([(cx+18*S, cy+i*12*S),(cx+26*S, cy+i*12*S)], fill=col, width=2*S)

ICONS = [icon_ship, icon_capitol, icon_flame, icon_drone, icon_handshake, icon_chip]

# --- editorial content: 1 lead + 6 cards + 24 briefs = 31 stories ---------

LEAD = {
    "kicker": "ANTALYA  •  CLIMATE",
    "head": "COP31 COLLAPSES AS FOSSIL-FUEL ROW SINKS DEAL",
    "deck": "Longest-ever UN climate summit ends with no pact after EU and others reject a text that never mentions coal, oil or gas. Guterres: 'deeply disappointed.'",
}

CARDS = [
    ("MIDDLE EAST", NAVY, "HORMUZ ON EDGE: 14 TANKERS, A US BLOCKADE",
     "Iran gathers tankers at Kharg to test the US naval blockade; Trump dares Tehran to try. Two tankers struck in the strait Saturday."),
    ("UNITED STATES", RED, "DEMOCRATS WIN 258 HOUSE SEATS — BEST SINCE 1992",
     "North Carolina win seals historic majority. Democrats take House and Senate in January; Republicans keep at least 173 seats."),
    ("INDONESIA", GOLD, "CANDY FACTORY FIRE: 24 BODY BAGS REMOVED",
     "Serang blaze at Milkita maker PT Fonusa: 3 confirmed dead, dozens missing. Search to resume Monday; DNA tests for victims."),
    ("UKRAINE", SLATE, "DRONES HIT KYIV REGION SHOP AND HOMES",
     "At least 4 killed Sunday in Dymer and Vyshneve grocery-store strike; 15 wounded. Zelensky urges more Patriot missiles."),
    ("SOUTH ASIA", TEAL, "NEPAL'S PM IN DELHI FOR TALKS WITH MODI",
     "Balendra Shah's first foreign visit as PM: energy, trade and connectivity top the 23 Nov agenda, with MoUs to be exchanged."),
    ("TECHNOLOGY", NAVY, "ANTHROPIC'S RECORD $1.5 TRILLION DEBUT",
     "$81bn IPO — biggest ever, topping SpaceX — priced at $83. Nonprofits now brace for a wave of AI-founder giving."),
]

BRIEFS = [
    ("SPORT", "Liverpool 4-0 Man Utd: nightmare debut for Pochettino, Yoro sent off in 8th minute"),
    ("CRICKET", "India 720/9d in Wellington — highest Test total ever in New Zealand"),
    ("S. KOREA", "Education minister resigns over AI-cheating chaos in CSAT exam"),
    ("CHIPS", "US seeks answers from Nvidia on China sales; Bessent cools on Huang return"),
    ("YEMEN", "Saudi-led coalition intercepts Houthi missile in west"),
    ("WEST BANK", "Settler arson branded 'Jewish terrorism' by Eisenkot"),
    ("SUDAN", "Drone hits UN area in Khartoum; UN calls risk unacceptable"),
    ("POLAND", "Warsaw: Russian missiles, drone cross border a provocation"),
    ("EUROPE", "UK-EU 'Brexit reset' deal on food, carbon, youth mobility; fees row remains"),
    ("DIPLOMACY", "Trump, Xi and Putin hold first trilateral meeting at APEC Shenzhen"),
    ("INDIA", "Amit Shah launches Rs 4,000 crore infrastructure push in Arunachal"),
    ("INDIA", "India, Bulgaria discuss IMEC corridor and Black Sea situation"),
    ("MYANMAR", "Army-backed government calls ASEAN decision 'unfair and imbalanced'"),
    ("PORTUGAL", "Thousands march in Lisbon as living costs fuel anger"),
    ("BALTIC", "Russian cargo ship still burning off Finland after suspected drone attack"),
    ("US", "FBI crime database suffers suspected breach, Trump confirms hack"),
    ("AUTOS", "Waymo suspends driverless taxis from all US freeways after California ban"),
    ("CINEMA", "IFFI 2026 hosts BRICS roundtable to strengthen film partnerships"),
    ("SNOOKER", "Anupama successfully defends IBSF World Women's Snooker title"),
    ("HEALTH", "Indiana reports 200+ measles cases as US loses elimination status"),
    ("GAZA", "Children with diabetes struggle to find insulin amid siege"),
    ("S. SUDAN", "First national elections delayed to February 2027"),
    ("NFL", "Vikings-49ers in Mexico City: first Sunday Night Football outside US"),
    ("AI", "OpenAI proposes shared limits on frontier AI tied to safety milestones"),
]

def main():
    img = Image.new("RGB", (W * S, H * S), PAPER)
    d = ImageDraw.Draw(img)
    M = 28 * S  # margin

    # masthead
    d.rectangle([0, 0, W * S, 104 * S], fill=INK)
    d.text((M, 10 * S), "THE WORLD IN ONE DAY", font=font(SERIF_B, 38), fill=(255, 255, 255))
    d.text((M, 58 * S), "One front page for the whole planet  •  31 stories, cross-checked", font=font(SANS_I, 13), fill=(210, 205, 190))
    # date plate on right
    px0 = W * S - M - 250 * S
    d.rounded_rectangle([px0, 12 * S, W * S - M, 92 * S], radius=8 * S, fill=RED)
    d.text((px0 + 125 * S, 28 * S), "MONDAY", font=font(SANS_B, 11), fill=(255, 255, 255), anchor="ma")
    d.text((px0 + 125 * S, 44 * S), "23 NOVEMBER 2026", font=font(SERIF_B, 20), fill=(255, 255, 255), anchor="ma")
    d.text((px0 + 125 * S, 72 * S), "WORLD EDITION", font=font(SANS_B, 10), fill=(255, 230, 220), anchor="ma")

    y = 116 * S
    # lead panel
    lead_h = 168 * S
    d.rounded_rectangle([M, y, W * S - M, y + lead_h], radius=10 * S, fill=(255, 255, 255), outline=RULE, width=2 * S)
    d.rectangle([M, y, M + 8 * S, y + lead_h], fill=RED)
    # cracked globe motif on right of lead
    gx, gy, gr = W * S - M - 92 * S, y + 84 * S, 62 * S
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=NAVY, width=4 * S, fill=(219, 234, 254))
    d.arc([gx - gr, gy - 22 * S, gx + gr, gy + 22 * S], 0, 360, fill=NAVY, width=2 * S)
    d.line([(gx, gy - gr), (gx, gy + gr)], fill=NAVY, width=2 * S)
    d.line([(gx - 10 * S, gy - gr + 6 * S), (gx + 8 * S, gy - 18 * S), (gx - 14 * S, gy + 10 * S), (gx + 6 * S, gy + gr - 8 * S)], fill=RED, width=4 * S)
    d.text((gx, gy + gr + 8 * S), "ANTALYA, TURKIYE", font=font(SANS_B, 8), fill=MUTED, anchor="ma")

    lx = M + 22 * S
    pill(d, (lx, y + 14 * S), LEAD["kicker"], RED, font(SANS_B, 9))
    ly = draw_wrapped(d, (lx, y + 38 * S), LEAD["head"], font(SERIF_B, 27), INK, 660 * S, 31 * S, max_lines=2)
    draw_wrapped(d, (lx, ly + 4 * S), LEAD["deck"], font(SANS, 13.5), MUTED, 660 * S, 18 * S, max_lines=3)
    y += lead_h + 14 * S

    # six cards, 3 x 2
    cols, rows, gap = 3, 2, 12 * S
    cw = (W * S - 2 * M - (cols - 1) * gap) // cols
    ch = 172 * S
    for idx, (cat, col, head, body) in enumerate(CARDS):
        r, c = divmod(idx, cols)
        x0 = M + c * (cw + gap)
        y0 = y + r * (ch + gap)
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=8 * S, fill=(255, 255, 255), outline=RULE, width=1 * S)
        d.rectangle([x0, y0, x0 + cw, y0 + 6 * S], fill=col)
        ICONS[idx](d, (x0 + cw - 72 * S, y0 + 12 * S, x0 + cw - 8 * S, y0 + 68 * S), col)
        pill(d, (x0 + 12 * S, y0 + 14 * S), cat, col, font(SANS_B, 8))
        hy = draw_wrapped(d, (x0 + 12 * S, y0 + 38 * S), head, font(SERIF_B, 14.5), INK, cw - 84 * S, 17 * S, max_lines=3)
        draw_wrapped(d, (x0 + 12 * S, max(hy + 2 * S, y0 + 92 * S)), body, font(SANS, 11), MUTED, cw - 24 * S, 14 * S, max_lines=4)
    y += rows * ch + (rows - 1) * gap + 16 * S

    # briefs header
    d.line([(M, y), (W * S - M, y)], fill=INK, width=2 * S)
    d.text((M, y + 6 * S), "THE DAY IN BRIEF  —  24 MORE STORIES", font=font(SANS_B, 13), fill=INK)
    d.text((W * S - M, y + 6 * S), "23 NOV 2026", font=font(SANS_B, 11), fill=RED, anchor="ra")
    y += 30 * S

    # 24 briefs in 3 columns x 8
    bcols = 3
    bw = (W * S - 2 * M - (bcols - 1) * 16 * S) // bcols
    per_col = 8
    row_h = 38 * S
    for i, (cat, text) in enumerate(BRIEFS):
        c, r = divmod(i, per_col)
        x0 = M + c * (bw + 16 * S)
        y0 = y + r * row_h
        if r:
            d.line([(x0, y0 - 3 * S), (x0 + bw, y0 - 3 * S)], fill=RULE, width=1 * S)
        d.text((x0, y0), cat, font=font(SANS_B, 8), fill=RED)
        draw_wrapped(d, (x0, y0 + 12 * S), text, font(SANS, 10.5), INK, bw, 13 * S, max_lines=2)

    # footer
    fy = H * S - 30 * S
    d.rectangle([0, fy, W * S, H * S], fill=INK)
    d.text((M, fy + 8 * S), "Sources cross-checked across Reuters, AP, AFP and regional press  •  Monday 23 November 2026", font=font(SANS, 9), fill=(220, 215, 200))
    d.text((W * S - M, fy + 8 * S), "31 STORIES", font=font(SANS_B, 9), fill=(255, 255, 255), anchor="ra")

    out = img.resize((W, H), Image.LANCZOS)
    out.save("entry.png", format="PNG", optimize=True)

if __name__ == "__main__":
    main()
