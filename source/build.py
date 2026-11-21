"""Build the Departures theme for T3 Code: departures.json (round 3).

All gutter art lives on two pseudo-elements of the conversation area (board = ::before, clock = ::after) and is moved
from OUTER css by stepping background-position through sprite sheets. That keeps motion cheap (two small layers),
makes it replay whenever the busy selector flips (turn start rattles the board, turn end re-announces ON TIME), and
lets prefers-reduced-motion pick a static frame (SVG-internal media queries are not honoured in background images).
"""
import json, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
CREAM = "#f2e9d2"
AMBER = "#ffb000"
MONO = "ui-monospace,Menlo,monospace"
MONOF = 'ui-monospace,"SF Mono",Menlo,Consolas,monospace'
SANS = '"Helvetica Neue",Helvetica,"Arial Nova",Arial,sans-serif'


def data_uri(svg):
    out = svg.replace("%", "%25").replace("#", "%23").replace('"', "'").replace("<", "%3C").replace(">", "%3E")
    return "url(\"data:image/svg+xml," + out + "\")"


# ---------------------------------------------------------------- split-flap board (sprite sheets)
CW, CH, PITCH = 17, 26, 19
ROWS = ["LISBON  A2", "OSLO    B7", "KYOTO   C1", "LIMA    A5"]
ON_TIME, BOARDING = "ON TIME".center(10), "BOARDING".center(10)
ALPHA = "ABCDEFGHJKLMNOPRSTUVWXYZ0123456789"
FH = 212                       # frame height (viewBox units); frame width is 200
XS = " ".join(f"{14.5 + PITCH * c:g}" for c in range(10))
ROW_Y = [32 + 32 * r for r in range(4)] + [172]


def board_base():
    tiles = "".join(f"<use href='#t' x='{6 + PITCH * c}' y='{y}'/>" for y in ROW_Y for c in range(10))
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 212'>"
            "<defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='.5' stop-color='#26231c'/><stop offset='.5' stop-color='#1b1914'/></linearGradient>"
            "<g id='t'><rect width='17' height='26' rx='2' fill='url(#g)'/><path d='M0 13h17' stroke='#050403' stroke-width='1.3'/></g></defs>"
            "<rect x='.5' y='.5' width='199' height='211' rx='5' fill='#0b0a08' stroke='#3b362c'/>"
            f"<text x='8' y='16' fill='{CREAM}' style='font:700 11px {MONO};letter-spacing:.2em'>DEPARTURES</text>"
            f"<path d='M6 22.5h188M6 164.5h188' stroke='{AMBER}' stroke-opacity='.55' stroke-dasharray='2 3'/>"
            + tiles + "</svg>")


def cell_state(f, src, tgt, start, settle, rnd):
    """Character shown by one cell at frame f: src at rest, random flaps while 'start <= f < settle', then tgt."""
    if f < start:
        return src, False
    if f >= settle:
        return tgt, False
    if src == " " and tgt == " ":
        return " ", False
    return rnd.choice(ALPHA), True


def frame_svg(k, rows, status, lamp, status_fill=AMBER, rnd=None):
    """rows: list of (text, flipping-cell-mask) already resolved; returns one frame group."""
    y0 = k * FH
    out = [f"<g transform='translate(0 {y0})'>"]
    flap = []
    for r, (txt, mask) in enumerate(rows):
        out.append(f"<text x='{XS}' y='{ROW_Y[r] + 19}' fill='{CREAM}'>{txt.replace(' ', '&#160;')}</text>")
        for c, m in enumerate(mask):
            if m and rnd.random() < .45:
                flap.append(f"M{6 + PITCH * c} {ROW_Y[r]}h17v13h-17z")
    stxt, smask = status
    out.append(f"<text x='{XS}' y='{ROW_Y[4] + 19}' fill='{status_fill}'>{stxt.replace(' ', '&#160;')}</text>")
    for c, m in enumerate(smask):
        if m and rnd.random() < .45:
            flap.append(f"M{6 + PITCH * c} {ROW_Y[4]}h17v13h-17z")
    if flap:
        out.append(f"<path d='{''.join(flap)}' fill='#2e2a22'/>")
    out.append(f"<circle cx='186' cy='12' r='3.5' fill='{AMBER}' fill-opacity='{lamp}'/></g>")
    return "".join(out)


def sprite(frames, n):
    css = f"text{{font:700 19px {MONO};text-anchor:middle}}"
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 {FH * n}'><style>{css}</style>" + "".join(frames) + "</svg>")


W_FRAMES, W_REST, W_FLIP = 35, 29, [30, 31, 32, 33, 34]      # working sprite: 0-29 rattle then hold, 30-34 one-row refresh
D_FRAMES = 12                                                   # done sprite: BOARDING -> ON TIME + lamp flash


def working_sprite():
    rnd = random.Random(7)
    frames = []
    for f in range(W_FRAMES):
        rows = []
        for r in range(4):
            txt, mask = "", []
            for c, ch in enumerate(ROWS[r]):
                if f <= W_REST:
                    s = 5 + 3 * r + (c * 5 % 7)
                    v, m = cell_state(f, ch, ch, 1 + r, s, rnd)
                else:                                   # refresh pass of row 2 only
                    v, m = (cell_state(f - 29, ch, ch, 1, 4, rnd) if r == 2 else (ch, False))
                txt += v; mask.append(m)
            rows.append((txt, mask))
        stxt, smask = "", []
        for c in range(10):
            s = 17 + c * 1.2
            v, m = cell_state(f if f <= W_REST else W_REST, ON_TIME[c], BOARDING[c], 1, int(s), rnd)
            stxt += v; smask.append(m)
        lamp = ".35" if f == 0 else ("1" if (f % 2 == 1 or f >= W_REST) else ".25")
        frames.append(frame_svg(f, rows, (stxt, smask), lamp, rnd=rnd))
    return sprite(frames, W_FRAMES)


def done_sprite():
    rnd = random.Random(11)
    frames = []
    for f in range(D_FRAMES):
        rows = []
        for r in range(4):
            txt, mask = "", []
            for c, ch in enumerate(ROWS[r]):
                v, m = cell_state(f, ch, ch, 1 + r, 4 + r + (c * 3 % 3), rnd)
                txt += v; mask.append(m)
            rows.append((txt, mask))
        stxt, smask = "", []
        for c in range(10):
            v, m = cell_state(f, BOARDING[c], ON_TIME[c], 1, 5 + c % 4, rnd)
            stxt += v; smask.append(m)
        lit = f in (9, 10)
        frames.append(frame_svg(f, rows, (stxt, smask), "1" if lit else (".6" if f < 9 else ".35"),
                                status_fill="#fff3c4" if lit else AMBER, rnd=rnd))
    return sprite(frames, D_FRAMES)


# status tile (narrow windows): one 8-cell row, shown in the right gutter when the board and clock do not fit
T8_ON, T8_BD = "ON TIME".center(8), "BOARDING"
TH, TF_W, TF_D = 34, 10, 11


def tile_base():
    tiles = "".join(f"<use href='#t' x='{4 + PITCH * c}' y='4'/>" for c in range(8))
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 160 34'>"
            "<defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='.5' stop-color='#26231c'/><stop offset='.5' stop-color='#1b1914'/></linearGradient>"
            "<g id='t'><rect width='17' height='26' rx='2' fill='url(#g)'/><path d='M0 13h17' stroke='#050403' stroke-width='1.3'/></g></defs>"
            "<rect x='.5' y='.5' width='159' height='33' rx='4' fill='#0b0a08' stroke='#3b362c'/>" + tiles + "</svg>")


def tile_frame(k, txt, mask, fill, rnd):
    y0 = k * TH
    xs = " ".join(f"{12.5 + PITCH * c:g}" for c in range(8))
    flap = "".join(f"M{4 + PITCH * c} 4h17v13h-17z" for c, m in enumerate(mask) if m and rnd.random() < .5)
    return (f"<g transform='translate(0 {y0})'><text x='{xs}' y='23' fill='{fill}'>{txt.replace(' ', '&#160;')}</text>"
            + (f"<path d='{flap}' fill='#2e2a22'/>" if flap else "") + "</g>")


def tile_sprite(n, frames):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 160 {TH * n}'><style>text{{font:700 19px {MONO};text-anchor:middle}}</style>"
            + "".join(frames) + "</svg>")


def tile_work_sprite():
    rnd = random.Random(5)
    fr = []
    for f in range(TF_W):
        t, m = "", []
        for c in range(8):
            v, fl = cell_state(f, T8_ON[c], T8_BD[c], 1, 2 + c, rnd)
            t += v; m.append(fl)
        fr.append(tile_frame(f, t, m, AMBER, rnd))
    return tile_sprite(TF_W, fr)


def tile_done_sprite():
    rnd = random.Random(6)
    fr = []
    for f in range(TF_D):
        t, m = "", []
        for c in range(8):
            v, fl = cell_state(f, T8_BD[c], T8_ON[c], 1, 4 + c % 4 + 1, rnd)
            t += v; m.append(fl)
        fr.append(tile_frame(f, t, m, "#fff3c4" if f == 9 else AMBER, rnd))
    return tile_sprite(TF_D, fr)


# idle event: now and then one destination row re-flips to a new city (frame 0 transparent, last frame = original row)
CITIES = ["KYOTO   C1", "BERLIN  D3", "CAIRO   E8"]
EV_FRAMES = 13


def event_sprite():
    rnd = random.Random(21)
    y = ROW_Y[2]
    fr = []
    seq = [None] + [("r", 1)] * 3 + [CITIES[1]] + [("r", 2)] * 3 + [CITIES[2]] + [("r", 0)] * 3 + [CITIES[0]]
    for k, item in enumerate(seq):
        g = f"<g transform='translate(0 {k * FH})'>"
        if item is not None:
            if isinstance(item, tuple):
                txt = "".join(rnd.choice(ALPHA) if ch != " " else " " for ch in CITIES[item[1]])
                flap = "".join(f"M{6 + PITCH * c} {y}h17v13h-17z" for c in range(10) if txt[c] != " " and rnd.random() < .5)
            else:
                txt, flap = item, ""
            g += "".join(f"<use href='#t' x='{6 + PITCH * c}' y='{y}'/>" for c in range(10))
            g += f"<text x='{XS}' y='{y + 19}' fill='{CREAM}'>{txt.replace(' ', '&#160;')}</text>"
            if flap:
                g += f"<path d='{flap}' fill='#2e2a22'/>"
        fr.append(g + "</g>")
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 " + str(FH * EV_FRAMES) + "'><defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'>"
            "<stop offset='.5' stop-color='#26231c'/><stop offset='.5' stop-color='#1b1914'/></linearGradient>"
            "<g id='t'><rect width='17' height='26' rx='2' fill='url(#g)'/><path d='M0 13h17' stroke='#050403' stroke-width='1.3'/></g></defs>"
            f"<style>text{{font:700 19px {MONO};text-anchor:middle}}</style>" + "".join(fr) + "</svg>")


def event_keyframes():
    T = 150.0
    pts = [(0, 0)]
    for e, t0 in enumerate((45, 90, 135)):
        base = 1 + 4 * e
        for j in range(3):
            pts.append((t0 + .14 * j, base + j))
        pts.append((t0 + .5, base + 3))
    out = []
    for t, k in pts:
        out.append(f"{100 * t / T:.3f}%{{background-position:0 {pct(k, EV_FRAMES)},0 calc(var(--dp-k)*100%),0 0}}")
    out.append(f"to{{background-position:0 0,0 calc(var(--dp-k)*100%),0 0}}")
    return "@keyframes dp-idle{" + "".join(out) + "}"


# ---------------------------------------------------------------- station clock (face + second-hand sprite)
CLK_H, CLK_FRAMES = 232, 21


def clock_face(working):
    ticks = (f"<circle cx='80' cy='80' r='62' fill='none' stroke='{CREAM}' stroke-width='9' stroke-dasharray='.8 {2 * 3.14159 * 62 / 12 - .8:.3f}' transform='rotate(-.25 80 80)'/>"
             f"<circle cx='80' cy='80' r='64' fill='none' stroke='{CREAM}' stroke-width='5' stroke-dasharray='1.2 {2 * 3.14159 * 64 / 60 - 1.2:.3f}' transform='rotate(-.3 80 80)'/>")
    pip = f"<circle cx='80' cy='128' r='3.4' fill='{AMBER}' fill-opacity='{'1' if working else '.35'}'/>"
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 160 232'>"
            f"<style>text{{font:700 11px {MONO};letter-spacing:.22em;text-anchor:middle}}.big{{font-size:38px;letter-spacing:0}}</style>"
            f"<circle cx='80' cy='80' r='72' fill='#0b0a08' stroke='{CREAM}' stroke-opacity='.85' stroke-width='4'/>" + ticks +
            f"<path d='M80 80V42' transform='rotate(290 80 80)' stroke='{CREAM}' stroke-width='6'/>"
            f"<path d='M80 80V24' transform='rotate(246 80 80)' stroke='{CREAM}' stroke-width='4.2'/>"
            f"<circle cx='80' cy='80' r='4' fill='{AMBER}'/>" + pip +
            "<rect x='.5' y='168.5' width='159' height='62' rx='4' fill='#0b0a08' stroke='#3b362c'/>"
            f"<text x='54' y='186' fill='{CREAM}' fill-opacity='.8'>PLATFORM</text>"
            f"<text class='big' x='130' y='214' fill='{AMBER}'>4</text>"
            f"<path d='M16 206h46m-8-7l8 7-8 7' stroke='{CREAM}' stroke-opacity='.8' stroke-width='3' fill='none'/></svg>")


def clock_hand():
    uses = "".join(f"<use href='#h' transform='translate(0 {k * CLK_H}) rotate({k * 18} 80 80)'/>" for k in range(CLK_FRAMES))
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 160 {CLK_H * CLK_FRAMES}'><defs><g id='h'><path d='M80 98V34' stroke='{AMBER}' stroke-width='2'/>"
            f"<circle cx='80' cy='30' r='7' fill='{AMBER}'/></g></defs>" + uses + "</svg>")


# ---------------------------------------------------------------- theme
colors = {
    "canvas": "#0d0c0a", "chrome": "#12100d", "toolbar": "#12100d", "toolbarForeground": "#efe6cf",
    "toolbarBorder": "#2b2720", "toolbarControl": "#1d1a15", "toolbarControlForeground": "#efe6cf",
    "toolbarControlHover": "#2a261e", "surface": "#17150f", "surfaceRaised": "#1f1c15",
    "surfaceOverlay": "#1b1913", "text": "#f2e9d2", "textMuted": "#b8ad93", "border": "#34302a",
    "input": "#4a443a", "focus": "#ffb000", "accent": "#ffb000", "accentForeground": "#17110a",
    "secondary": "#26231c", "secondaryForeground": "#efe6cf", "muted": "#1d1a14",
    "mutedForeground": "#b3a88f", "placeholder": "#8f8571", "secondaryLabel": "#b8ad93",
    "iconMuted": "#a99f87", "error": "#ff7a66", "errorForeground": "#ffb4a6", "errorSurface": "#3a1a16",
    "warning": "#ffb000", "warningForeground": "#ffd27a", "warningSurface": "#3b2c0c",
    "update": "#9fdca0", "updateForeground": "#d7f5d6", "updateSurface": "#16301b",
    "accentSurface": "#2d2310", "accentSurfaceForeground": "#ffd27a", "messageSurface": "#ece2c8",
    "messageForeground": "#1b1710", "messageAction": "#2a2418", "messageActionForeground": "#ece2c8",
    "messageActionHover": "#3b3220", "codeBackground": "#14120e", "codeForeground": "#eadfc4",
    "searchMatchBackground": "#5a4308", "searchMatchForeground": "#ffecc0",
    "searchMatchActiveBackground": "#ffb000", "searchMatchActiveForeground": "#17110a",
    "sidebar": "#0a0908", "sidebarForeground": "#ece2c8", "sidebarMutedForeground": "#aaa088",
    "sidebarControlSurface": "#1a1812", "sidebarRowHover": "#1c1a14", "sidebarRowActive": "#25211a",
    "sidebarRowSelected": "#2a2518", "sidebarBorder": "#2b2720", "terminalBackground": "#0a0908",
    "terminalForeground": "#e8dec6", "terminalCursor": "#ffb000", "terminalSelection": "#5a4308",
    "terminalScrollbar": "#34302a", "terminalScrollbarHover": "#5a5242",
}

A = "rgba(255,176,0,"
CWD = "var(--chat-content-max-width,46rem)"
G = f"(100% - {CWD})/2"
BUSY = ('body:has([data-timeline-row-kind="working"])',
        'body:has([data-thread-item] [aria-busy="true"][aria-current]:not([aria-current="false"]))')


def busy(sel):
    return ",".join(f"{b} {sel}" for b in BUSY)


def not_busy_sel(sel):
    return sel


def gutter_w(maxw, gap=76, minw=130):
    """Width of a gutter layer: 0 unless the gutter can hold minw px at 'gap' px from the reading column."""
    return f"min({maxw}px,clamp(0px,({G} - {gap + minw}px)*1000,{G} - {gap}px))"


SPLIT = "linear-gradient(transparent calc(50% - .5px),rgba(0,0,0,.8) calc(50% - .5px) calc(50% + .5px),transparent calc(50% + .5px))"
DOTS = lambda a: f"radial-gradient(circle,{A}{a}) 1.2px,transparent 1.7px)"
SCAN = "repeating-linear-gradient(rgba(242,233,210,.016) 0 1px,transparent 1px 4px)"
VIG = "radial-gradient(ellipse at 50% 35%,transparent 45%,rgba(0,0,0,.45))"


def garble(word):
    r = random.Random(3)
    steps, n = [], 8
    for i in range(n):
        s = "".join(ch if r.random() < i / n else r.choice("ABCDEGHKLMNOPRSTUWXYZ0123456789") for ch in word)
        steps.append(s)
    return "@keyframes dp-board{" + "".join(f"{i * 6}%{{content:\"{s}\"}}" for i, s in enumerate(steps)) + f"{n * 6}%,to{{content:\"{word}\"}}}}"


NOTCH = ("radial-gradient(circle 6px at 0 50%,#0000 97%,#000) 0 0/51% 100% no-repeat,"
         "radial-gradient(circle 6px at 100% 50%,#0000 97%,#000) 100% 0/51% 100% no-repeat")

pct = lambda k, n: f"{100 * k / (n - 1):.4f}%"
CONV = '[data-workspace-area="conversation"]'
BW = gutter_w(240)
CWID = gutter_w(150, 112, 130)
TW = gutter_w(112, 20, 100)
BOARD_REST_W = pct(W_REST, W_FRAMES)
LONG = "transition:border-color .2s,box-shadow .25s"
FOCUS = f"outline:2px solid {AMBER}!important;outline-offset:2px"

css = (
    ":root{--dp-base:" + data_uri(board_base()) + ";--dp-w:" + data_uri(working_sprite()) + ";--dp-d:" + data_uri(done_sprite())
    + ";--dp-ch:" + data_uri(clock_hand()) + ";--dp-cf:" + data_uri(clock_face(False)) + ";--dp-cfw:" + data_uri(clock_face(True))
    + ";--dp-e:" + data_uri(event_sprite()) + ";--dp-tb:" + data_uri(tile_base()) + ";--dp-tw:" + data_uri(tile_work_sprite()) + ";--dp-td:" + data_uri(tile_done_sprite()) + "}"
    "@property --dp-k{syntax:'<number>';inherits:false;initial-value:1}"
    f"body{{font-family:{SANS}!important}}"
    f"code,pre,kbd,samp{{font-family:{MONOF}}}"
    # ---- concourse: scanlines + vignette on the conversation; the board and clock are gutter pseudo-elements.
    # position:relative is forced on the conversation area only so the pseudo-elements can anchor to it (percentages in
    # their widths then measure the real gutter); the app's own conversation area is already a positioned flex column.
    f"{CONV}{{position:relative;background:{SCAN},{VIG},#0d0c0a!important}}"
    f"{CONV}::before,{CONV}::after{{content:\"\";position:absolute;top:24px;pointer-events:none;z-index:0;background-repeat:no-repeat}}"
    # board (left gutter): idle = a one-shot 'done' re-announce; working = hard rattle, hold BOARDING, rare one-row refresh
    f"{CONV}::before{{left:16px;width:{BW};aspect-ratio:200/212;--dp-k:1;background-image:var(--dp-e),var(--dp-d),var(--dp-base);"
    f"background-size:100% {EV_FRAMES * 100}%,100% {D_FRAMES * 100}%,100% 100%;background-position:0 0,0 calc(var(--dp-k)*100%),0 0;"
    f"transition:--dp-k 1.7s steps({D_FRAMES - 1});animation:dp-idle 150s step-end infinite}}"
    + event_keyframes()
    + busy(CONV + "::before") + f"{{--dp-k:0;transition:none;background-image:var(--dp-w),var(--dp-base);background-size:100% {W_FRAMES * 100}%,100% 100%;"
    f"animation:dp-work 4.8s steps({W_REST}) 1 forwards,dp-refresh 18s step-end 5s infinite}}"
    f"@keyframes dp-work{{from{{background-position:0 0,0 0}}to{{background-position:0 {BOARD_REST_W},0 0}}}}"
    "@keyframes dp-refresh{0%,86%{background-position:0 " + BOARD_REST_W + ",0 0}"
    + "".join(f"{88 + 1.5 * i:g}%{{background-position:0 {pct(k, W_FRAMES)},0 0}}" for i, k in enumerate(W_FLIP))
    + f"95.5%,100%{{background-position:0 {BOARD_REST_W},0 0}}}}"
    # clock + platform sign (right gutter): second hand ticks every 3s; the departure lamp lights while working
    f"{CONV}::after{{right:32px;width:{CWID};aspect-ratio:160/232;background-image:var(--dp-ch),var(--dp-cf);"
    f"background-size:100% {CLK_FRAMES * 100}%,100% 100%;background-position:0 0,0 0;animation:dp-tick 60s steps({CLK_FRAMES - 1}) infinite}}"
    "@keyframes dp-tick{to{background-position:0 100%,0 0}}"
    + busy(CONV + "::after") + "{background-image:var(--dp-ch),var(--dp-cfw)}"
    # narrow windows: no room for the board or clock, so the right gutter carries a one-row status tile (ON TIME / BOARDING)
    f"@media (max-width:1439px){{{CONV}::after{{right:12px;width:{TW};aspect-ratio:160/34;--dp-k:1;background-image:var(--dp-td),var(--dp-tb);"
    f"background-size:100% {TF_D * 100}%,100% 100%;background-position:0 calc(var(--dp-k)*100%),0 0;transition:--dp-k 1.2s steps({TF_D - 1});animation:none}}"
    + busy(CONV + "::after") + f"{{--dp-k:0;transition:none;background-image:var(--dp-tw),var(--dp-tb);background-size:100% {TF_W * 100}%,100% 100%;"
    f"animation:dp-tile 1.1s steps({TF_W - 1}) 1 forwards}}"
    f"@keyframes dp-tile{{from{{background-position:0 0,0 0}}to{{background-position:0 100%,0 0}}}}}}"
    # ---- header: runway lights march while a turn runs; a one-shot amber flash on the rule when it ends
    f"[data-chat-header]{{background-color:#100e0b!important;background-image:{DOTS('.3')};background-size:14px 5px;background-repeat:repeat-x;background-position:0 100%;"
    f"border-bottom:1px solid #2b2720!important;font-family:{MONOF}!important;letter-spacing:.05em;text-transform:uppercase;transition:border-bottom-color 1.6s ease-out}}"
    f"[data-chat-header] *{{font-family:{MONOF}!important}}"
    + busy("[data-chat-header]") + f"{{background-image:{DOTS('.7')};border-bottom-color:{A}.5)!important;transition:none;animation:dp-run 1.6s steps(7) infinite}}"
    "@keyframes dp-run{from{background-position:0 100%}to{background-position:14px 100%}}"
    # ---- sidebar
    f"[data-slot=\"sidebar-inner\"]{{background-color:#0a0908!important}}"
    f"[data-slot=\"sidebar\"],[data-slot=\"sidebar\"] *{{font-family:{MONOF}!important;letter-spacing:.015em;font-variant-numeric:tabular-nums}}"
    f"[data-slot=\"project-monogram\"]{{background:{SPLIT},#1d1a14!important;color:{AMBER}!important;border:1px solid #3b362c!important;border-radius:3px!important;font-family:{MONOF};font-weight:700}}"
    f"[data-thread-item]{{position:relative;border-radius:3px!important}}"
    f"[data-thread-item]>*{{padding-bottom:8px!important}}"
    f"[data-thread-item]:hover::before{{content:\"\";position:absolute;left:0;top:5px;bottom:5px;width:3px;background:{A}.6);z-index:1;pointer-events:none}}"
    f"[data-thread-item] [aria-current]:not([aria-current=\"false\"]){{box-shadow:inset 3px 0 0 {AMBER}}}"
    f"[data-thread-item] [aria-busy=\"true\"]{{background-image:{DOTS('.8')};background-size:14px 3px;background-repeat:repeat-x;background-position:0 calc(100% - 1px);animation:dp-run-s 2s steps(7) infinite}}"
    "@keyframes dp-run-s{from{background-position:0 calc(100% - 1px)}to{background-position:14px calc(100% - 1px)}}"
    # ---- the live working row: a flap tile that rattles BOARDING once, then holds
    "[data-timeline-row-kind=\"working\"]::before{content:\"BOARDING\";display:inline-block;margin-right:10px;padding:3px 9px;border-radius:3px;"
    f"font:700 11px {MONOF};letter-spacing:.16em;color:{AMBER};background:{SPLIT},#1d1a14;border:1px solid #3b362c;animation:dp-board 1.2s step-end 1 forwards}}"
    + garble("BOARDING") +
    # ---- tool-call rows: 'gate call' lines
    f"[data-timeline-row-kind=\"work\"]{{font-family:{MONOF};font-size:11.5px;letter-spacing:0;color:#b8ad93}}"
    f"[data-timeline-row-kind=\"work\"]::before{{content:\"CALL\";display:inline-block;margin-right:6px;padding:1px 6px;border-radius:2px;font:700 10px {MONOF};letter-spacing:.14em;color:{AMBER};background:{SPLIT},#1d1a14;border:1px solid #3b362c}}"
    # ---- user messages are boarding passes; the stub shows the seat (message count)
    f"{'.messages-timeline-scroll'}{{counter-reset:dp-seat}}[data-message-role=\"user\"]{{counter-increment:dp-seat}}"
    f"[data-user-message-bubble],[data-user-message-bubble] *{{color:#1b1710!important}}"
    f"[data-user-message-bubble]{{position:relative;background:linear-gradient(90deg,transparent calc(100% - 58px),rgba(27,23,16,.35) 0 calc(100% - 57px),transparent 0),#ece2c8!important;"
    f"padding-right:70px!important;min-height:44px;border-radius:3px!important;-webkit-mask:{NOTCH};mask:{NOTCH}}}"
    f"[data-user-message-bubble]::after{{content:counter(dp-seat) \"A\";position:absolute;right:12px;top:50%;transform:translateY(-50%);font:700 12px {MONOF};letter-spacing:.1em;color:#6f6244}}"
    # ---- assistant prose
    f".chat-markdown :is(h1,h2,h3){{font-family:{MONOF};text-transform:uppercase;letter-spacing:.1em;color:{AMBER}}}.chat-markdown :is(h1,h2,h3) code{{text-transform:none;letter-spacing:0}}"
    f".chat-markdown :is(h1,h2){{display:inline-block;background:{SPLIT},#1d1a14;padding:.2em .6em;border-radius:3px;border:1px solid #3b362c}}"
    f".chat-markdown h3{{font-size:.95em;border-bottom:1px dashed {A}.45);padding-bottom:.15em}}"
    f".chat-markdown :not(pre)>code{{background:{SPLIT},#26231c;color:{CREAM};padding:.1em .4em;border-radius:3px;border:1px solid #3b362c}}"
    f".chat-markdown a{{color:#ffd27a!important;text-decoration-style:dotted;text-underline-offset:3px}}"
    f".chat-markdown blockquote{{border-left:3px solid {A}.6)!important;color:#cfc4a8}}.chat-markdown hr{{border:0;border-top:1px dashed {A}.4)}}"
    f".chat-markdown li::marker{{color:{AMBER};font-family:{MONOF}}}"
    f".chat-markdown table{{border-collapse:collapse;border:1px solid #3b362c}}"
    f".chat-markdown th{{font-family:{MONOF};font-size:.78em;text-transform:uppercase;letter-spacing:.14em;color:{AMBER};background:{SPLIT},#1d1a14;border:1px solid #3b362c;padding:.4em .8em;text-align:left}}"
    f".chat-markdown td{{border:1px solid #2f2b23;padding:.35em .8em;font-variant-numeric:tabular-nums}}.chat-markdown tr:nth-child(even) td{{background:rgba(242,233,210,.03)}}"
    f".chat-markdown-codeblock{{background-color:#13110d!important;background-image:{DOTS('.35')};background-size:14px 6px;background-repeat:repeat-x;background-position:0 0;border:1px solid #2f2b23!important;border-top:1px dashed {A}.5)!important;border-radius:3px!important}}"
    # ---- composer: the check-in desk; amber edge on focus (its own ring, not doubled by a global outline)
    f"[data-slot=\"composer-host\"]{{background-color:#14120e!important;border:1px solid #3a352b!important;border-radius:4px!important;font-family:{MONOF};{LONG}}}"
    f".composer-tiptap{{font-family:{SANS}!important;outline:none!important}}.composer-tiptap:focus-visible{{outline:none!important}}"
    f"[data-slot=\"composer-host\"]:focus-within{{border-color:{AMBER}!important;box-shadow:0 0 0 3px {A}.14)}}"
    f"[data-slot=\"composer-host\"] [data-slot=\"select-trigger\"]{{background:{SPLIT},#1d1a14!important;border:1px solid #3b362c!important;border-radius:3px!important;font-family:{MONOF};font-size:11px;letter-spacing:.1em;text-transform:uppercase}}"
    + busy('[data-slot="composer-host"]') + f"{{background-image:{DOTS('.7')};background-size:14px 5px;background-repeat:repeat-x;background-position:0 0;animation:dp-run-t 1.6s steps(7) infinite}}"
    "@keyframes dp-run-t{from{background-position:0 0}to{background-position:14px 0}}"
    # ---- controls: flap-tile buttons, lamp focus rings
    f"[data-slot=\"button\"]{{border-radius:3px!important;transition:box-shadow .15s,transform .1s}}"
    f"[data-slot=\"button\"]:not(:has(>svg:only-child)){{background-image:{SPLIT}}}"
    f"[data-slot=\"button\"]:hover{{box-shadow:0 0 0 1px {A}.4)}}[data-slot=\"button\"]:active{{transform:translateY(1px);box-shadow:none}}"
    f"[data-slot=\"button\"]:focus-visible,[data-slot=\"select-trigger\"]:focus-visible,[data-slot=\"switch\"]:focus-visible{{{FOCUS}}}"
    f"[data-slot=\"input\"],[data-slot=\"select-trigger\"]{{background-color:#14120e!important;border:1px solid #4a443a!important;border-radius:3px!important;{LONG}}}"
    f"[data-slot=\"input\"]:hover,[data-slot=\"select-trigger\"]:hover{{border-color:#6b6350!important}}"
    f"[data-slot=\"input\"]:focus-visible{{border-color:{AMBER}!important;box-shadow:0 0 0 3px {A}.18);outline:none!important}}"
    f"[data-slot=\"switch\"]{{border-radius:3px!important;background-color:#26231c}}[data-slot=\"switch\"][aria-checked=\"true\"]{{background-color:{AMBER}}}"
    # ---- popups
    f"[data-slot=\"dialog-popup\"],[data-slot=\"popover-popup\"],[data-slot=\"menu-popup\"]{{background-color:#17150f!important;border:1px solid #4a443a!important;border-radius:4px!important;box-shadow:inset 0 2px 0 {AMBER},0 12px 40px rgba(0,0,0,.6)!important}}"
    f"[data-slot=\"menu-popup\"] [role=\"menuitem\"],[data-slot=\"menu-popup\"] [role=\"option\"]{{border-radius:2px;font-family:{MONOF};font-size:12.5px}}"
    f"[data-slot=\"menu-popup\"] [role=\"menuitem\"]:hover,[data-slot=\"menu-popup\"] [role=\"option\"]:hover{{background:{A}.14)!important;color:#ffe3a3!important}}"
    f"[data-slot=\"tooltip-popup\"]{{background:#1f1c15!important;color:{CREAM}!important;border:1px solid #4a443a!important;border-radius:3px!important;font-family:{MONOF};font-size:12px}}"
    # ---- panels
    f"[data-thread-details-card]{{background-color:#17150f!important;border:1px solid #3b362c!important;border-top:2px solid {AMBER}!important;border-radius:4px!important;font-family:{MONOF}}}"
    f"[data-thread-terminal-drawer]{{background-color:#0a0908!important;border-top:2px solid {AMBER}!important}}"
    f"[data-settings-page-scroll]{{background:{SCAN},#0d0c0a!important}}[data-settings-page-scroll] :is(h1,h2,h3){{font-family:{MONOF};text-transform:uppercase;letter-spacing:.12em}}"
    "svg.lucide{stroke-width:1.75}"
    "::selection{background:rgba(255,176,0,.38);color:#fff6dc}"
    "::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-track,[data-slot=\"scroll-area-scrollbar\"]{background:#0a0908!important}"
    "::-webkit-scrollbar-thumb,[data-slot=\"scroll-area-thumb\"]{background:#3a352b!important;border-radius:2px!important}"
    "::-webkit-scrollbar-thumb:hover,[data-slot=\"scroll-area-thumb\"]:hover{background:#ffb000!important}"
    # ---- reduced motion: freeze every layer on a good-looking still (board ON TIME at rest / BOARDING while working)
    "@media (prefers-reduced-motion:reduce){"
    f"{CONV}::before,{CONV}::after{{animation:none!important}}"
    f"{CONV}::before{{transition:none!important;background-position:0 0,0 100%,0 0!important}}"
    + busy(CONV + "::before") + f"{{background-position:0 {BOARD_REST_W},0 0!important}}"
    f"{CONV}::after{{transition:none!important}}"
    f"@media (max-width:1439px){{{CONV}::after{{background-position:0 100%,0 0!important}}"
    + busy(CONV + "::after") + f"{{background-position:0 100%,0 0!important}}}}"
    f"[data-chat-header],[data-thread-item] [aria-busy],[data-timeline-row-kind]::before,[data-slot=\"composer-host\"]{{transition:none!important;animation:none!important}}"
    "}"
)

theme = {"version": 1, "id": "departures", "name": "Departures", "appearance": "dark", "accent": AMBER, "canvas": "#0d0c0a",
         "colors": colors, "css": css}
with open(os.path.join(HERE, "..", "departures.json"), "w") as fh:
    json.dump(theme, fh, ensure_ascii=False)
print("css chars:", len(css))
svgdir = os.path.join(HERE, "..", "assets", "svg")
os.makedirs(svgdir, exist_ok=True)
for f in os.listdir(svgdir):
    os.remove(os.path.join(svgdir, f))
for n, s in (("board-base", board_base()), ("board-work-sprite", working_sprite()), ("board-done-sprite", done_sprite()),
             ("clock-face", clock_face(False)), ("clock-face-working", clock_face(True)), ("clock-hand-sprite", clock_hand()),
             ("tile-base", tile_base()), ("tile-work-sprite", tile_work_sprite()), ("tile-done-sprite", tile_done_sprite()), ("board-event-sprite", event_sprite())):
    open(os.path.join(svgdir, f"{n}.svg"), "w").write(s)
    print(n, len(data_uri(s)))
