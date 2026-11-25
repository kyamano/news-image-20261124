#!/usr/bin/env python3
"""The World in One Day - Tuesday 24 November 2026.

Pure standard-library program: a small framebuffer rasteriser, a hand-made
5x7 bitmap font and a PNG encoder (zlib + struct) draw a one-page newspaper
that sums up the world news of 24 November 2026. No network, no files read,
deterministic output to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
"""
import os
import struct
import zlib

W = 1024
H = 1024

INK = (24, 24, 28)
PAPER = (246, 242, 230)
WHITE = (255, 255, 255)
GREY = (105, 100, 92)
RULE = (60, 58, 54)
RED = (166, 32, 28)
BLUE = (28, 74, 140)
GREEN = (28, 110, 70)
GOLD = (176, 124, 20)
TEAL = (18, 110, 120)
PURPLE = (96, 52, 140)
PANEL = (255, 253, 246)

# ---------------------------------------------------------------- font ----
# Each glyph is 7 rows of 5 pixels, '#' is ink.
FONT = {
"A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
"C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
"D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
"E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
"F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
"G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
"H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
"J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
"K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
"L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
"M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
"N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
"O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
"Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
"R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
"S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
"T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
"U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
"X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
"Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
"Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
"0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
"1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
"2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
"3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
"4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
"5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
"6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
"7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
"8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
"9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
" ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
"-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
"!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
"?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
"/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
"(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
"$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
"%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
"+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
"&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
}

# ------------------------------------------------------------- canvas -----
FB = bytearray(W * H * 3)


def set_px(x, y, colour):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        FB[i] = colour[0]
        FB[i + 1] = colour[1]
        FB[i + 2] = colour[2]


def rect(x, y, w, h, colour):
    for yy in range(y, y + h):
        if 0 <= yy < H:
            base = yy * W * 3
            for xx in range(max(0, x), min(W, x + w)):
                i = base + xx * 3
                FB[i] = colour[0]
                FB[i + 1] = colour[1]
                FB[i + 2] = colour[2]


def hline(x, y, w, colour, thick=1):
    rect(x, y, w, thick, colour)


def vline(x, y, h, colour, thick=1):
    rect(x, y, thick, h, colour)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, colour, scale=1):
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = glyph[r]
            for c in range(5):
                if row[c] == "#":
                    rect(cx + c * scale, y + r * scale, scale, scale, colour)
        cx += 6 * scale
    return cx - x


def wrap(s, max_chars):
    words = s.split()
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, colour, scale, max_chars, line_h, max_lines=None):
    lines = wrap(s, max_chars)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(x, y + i * line_h, ln, colour, scale)
    return len(lines)

# ------------------------------------------------------------ content -----
TITLE = "THE WORLD IN ONE DAY"
DATE_LINE = "TUESDAY 24 NOVEMBER 2026"

# (tag, colour, headline, body)
PANELS = [
    ("COURTS / TECH", RED,
     "HUAWEI GUILTY ON 10 OF 12 COUNTS IN US TRIAL",
     "BROOKLYN JURY: GUILTY OF STEALING TRADE SECRETS, BANK FRAUD AND SANCTIONS VIOLATIONS OVER IRAN. ACQUITTED OF RACKETEERING. APPEAL PLANNED."),
    ("HORMUZ", BLUE,
     "IRAN: FOUR TANKERS HIT MINES IN THE STRAIT",
     "IRGC SAYS TANKERS STRUCK NAVAL MINES AND CAUGHT FIRE. TEHRAN CLOSES THE STRAIT FURTHER; MINE CLAIMS UNCONFIRMED BY MARITIME CENTRE."),
    ("UKRAINE WAR", TEAL,
     "UKRAINE HITS RUSSIAN SHIPS OFF LIBYA AND FINLAND",
     "DRONES STRIKE CARGO SHIP SPARTA II IN GULF OF FINLAND; CORVETTE MERKURY SUNK OFF LIBYA. KYIV CALLS IT SELF-DEFENCE AFTER TRIPOLI PROTEST."),
    ("AI / MARKETS", PURPLE,
     "NVIDIA FALLS 5%+ AS HUANG COMEBACK RALLY FIZZLES",
     "AFTER MONDAY'S 31.5% SURGE ON JENSEN HUANG'S RETURN AS CEO, SHARES SLIDE ON LEGAL AND TARIFF WORRIES. US BLACKLISTS MEGASPEED."),
    ("CHINA", RED,
     "POLITBURO MEMBER CHEN JINING UNDER INVESTIGATION",
     "XINHUA: SHANGHAI PARTY CHIEF PROBED FOR SEVERE VIOLATIONS. FOURTH POLITBURO MEMBER INVESTIGATED SINCE 2025; BODY DOWN TO 21."),
    ("SPORT", GREEN,
     "SENEGAL REGAIN AFRICA CUP TITLE ON APPEAL",
     "SPORTS COURT CAS OVERTURNS CAF RULING THAT GAVE TROPHY TO MOROCCO. SENEGAL'S 1-0 EXTRA-TIME FINAL WIN IS REINSTATED."),
    ("MIDDLE EAST", GOLD,
     "RIYADH PIF TOWER HIT; AT LEAST 11 WOUNDED",
     "SAUDI OFFICIALS BLAME A HOUTHI DRONE ATTACK ON THE FINANCE DISTRICT TOWER HOUSING THE PUBLIC INVESTMENT FUND. SECOND HIT IN A WEEK."),
    ("SPACE", BLUE,
     "SHENZHOU-24 CREW: FIRST PAKISTANI ASTRONAUT",
     "CHINA UNVEILS CREW FOR TIANGONG: TANG HONGBO, WU YI AND PAKISTAN'S ZEESHAN ALI, FIRST FOREIGN ASTRONAUT TO BOARD THE STATION."),
    ("BRITAIN", TEAL,
     "INQUIRY INTO NUCLEAR TESTS' EFFECT ON VETERANS",
     "PM BURNHAM SETS UP INDEPENDENT PANEL UNDER BISHOP JAMES JONES TO EXAMINE 45 UK TESTS, 1952-1991, AND THEIR HEALTH LEGACY."),
    ("PACIFIC", GREEN,
     "SOLOMONS TO END CHINA PACT, SIGN AUSTRALIA TREATY",
     "HONIARA TELLS BEIJING IT WILL NOT RENEW THE 2022 SECURITY PACT. NEW TREATY MAKES AUSTRALIA ITS PRIMARY SECURITY PARTNER."),
]

BRIEFS_LEFT = [
    "TURKISH AIR FORCE HELICOPTER CRASH KILLS FIVE NEAR ESKISEHIR",
    "IRGC SAYS IT ATTACKED A CONTAINER SHIP IN STRAIT OF HORMUZ",
    "ARMED MEN HOLD 25 HOSTAGES AT CARTAGENA SUPERMARKET, COLOMBIA",
    "YEMEN: HOUTHIS 60 KM FROM ADEN AND READY TO ATTACK, ARMY SAYS",
    "LIBYA'S HAFTAR VISITS TURKEY FOR FIRST TIME, TO MEET ERDOGAN",
    "UK SANCTIONS YEMEN'S HOUTHIS AND FOUR SENIOR OFFICIALS",
    "CAR BOMB IN VILLAVICENCIO, COLOMBIA INJURES 23 PEOPLE",
    "ISRAEL KILLS HAMAS INTERNAL SECURITY CHIEF IN GAZA STRIKE",
    "IRAQ ORDERS FEDERAL CONTROL OF KURDISH OILFIELDS, CROSSINGS",
    "SAUDI STRIKES ON YEMEN BUSES LEAVE 25 DEAD OR MISSING",
]
BRIEFS_RIGHT = [
    "GAZA MENINGITIS EPIDEMIC ALERT AFTER 272 CASES IN OCTOBER",
    "DR CONGO SEARCHES FOR MISSING PLANE; REBELS CLAIM SHOOTDOWN",
    "HANOI RESTAURANT EXPLOSION KILLS AT LEAST SIX PEOPLE",
    "MALAYSIA TO SEND THOUSANDS OF MIGRANTS BACK TO MYANMAR",
    "SOUTH KOREA: SHELTER ON ULLEUNGDO AS RUSSIAN JETS APPROACH",
    "HASINA PLANS RETURN TO BANGLADESH FROM EXILE ON 16 DECEMBER",
    "INDONESIA NAMES TWO CANDIDATES TO REPLACE VICE PRESIDENT",
    "CHINA SENTENCES OFFICIAL TO DEATH FOR SPYING ABROAD",
    "US DRONE HELPED CAPTURE EL CHAPO ISIDRO; MEXICO TO TRY HIM",
    "PENTAGON REBUKES CANADA OVER DEFENCE SPENDING, F-35 REVIEW",
]

# -------------------------------------------------------------- drawing ---
def draw_header():
    rect(0, 0, W, H, PAPER)
    rect(0, 0, W, 96, INK)
    tw = text_width(TITLE, 4)
    draw_text((W - tw) // 2, 14, TITLE, WHITE, 4)
    dw = text_width(DATE_LINE, 2)
    draw_text((W - dw) // 2, 58, DATE_LINE, (240, 210, 120), 2)
    hline(0, 96, W, RED, 4)
    rect(0, 100, W, 20, (232, 224, 204))
    strip = "FINAL EDITION - 30 STORIES - EACH FIRST REPORTED ON 24 NOVEMBER 2026"
    sw = text_width(strip, 1)
    draw_text((W - sw) // 2, 106, strip, INK, 1)


def draw_panel(x, y, w, h, tag, colour, headline, body, number):
    rect(x, y, w, h, PANEL)
    vline(x, y, h, colour, 5)
    hline(x, y, w, RULE, 1)
    hline(x, y + h - 1, w, RULE, 1)
    vline(x + w - 1, y, h, RULE, 1)
    rect(x + 10, y + 6, 22, 13, colour)
    draw_text(x + 13, y + 9, "%02d" % number, WHITE, 1)
    draw_text(x + 38, y + 9, tag, colour, 1)
    hline(x + 12, y + 24, w - 24, (214, 206, 188), 1)
    draw_wrapped(x + 12, y + 29, headline, INK, 2, 34, 17, 2)
    draw_wrapped(x + 12, y + 66, body, (66, 62, 56), 1, 76, 10, 4)


def draw_panels():
    x0, y0 = 12, 128
    pw, ph = 494, 112
    gap = 12
    for i, (tag, colour, head, body) in enumerate(PANELS):
        col = i % 2
        row = i // 2
        draw_panel(x0 + col * (pw + gap), y0 + row * (ph + 7), pw, ph,
                   tag, colour, head, body, i + 1)


def draw_briefs():
    y0 = 730
    hline(12, y0 - 8, W - 24, INK, 3)
    draw_text(12, y0, "ALSO ON 24 NOVEMBER - IN BRIEF", RED, 2)
    draw_text(760, y0 + 3, "STORIES 11-30", GREY, 1)
    y = y0 + 28
    row_h = 23
    for i, item in enumerate(BRIEFS_LEFT):
        if i % 2 == 0:
            rect(8, y + i * row_h - 4, 500, 19, (238, 231, 214))
        draw_text(12, y + i * row_h, "%02d" % (11 + i), RED, 1)
        draw_wrapped(36, y + i * row_h, item, INK, 1, 78, 10, 1)
    for i, item in enumerate(BRIEFS_RIGHT):
        if i % 2 == 0:
            rect(514, y + i * row_h - 4, 502, 19, (238, 231, 214))
        draw_text(518, y + i * row_h, "%02d" % (21 + i), RED, 1)
        draw_wrapped(542, y + i * row_h, item, INK, 1, 78, 10, 1)
    fy = y + 10 * row_h + 4
    hline(12, fy, W - 24, INK, 2)
    foot = "EVERY STORY CROSS-CHECKED IN TWO OR MORE OUTLETS: REUTERS - AP - BBC - AL JAZEERA - CNN"
    fw = text_width(foot, 1)
    draw_text((W - fw) // 2, fy + 9, foot, GREY, 1)
    foot2 = "ONE IMAGE, ONE DAY: THE WORLD ON TUESDAY 24 NOVEMBER 2026"
    fw2 = text_width(foot2, 1)
    draw_text((W - fw2) // 2, fy + 22, foot2, GREY, 1)


def render():
    draw_header()
    draw_panels()
    draw_briefs()


# ------------------------------------------------------------ PNG out -----
def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    row_bytes = W * 3
    for yy in range(H):
        raw.append(0)
        raw += FB[yy * row_bytes:(yy + 1) * row_bytes]
    png = bytearray(b"\x89PNG\r\n\x1a\n")
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    render()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
