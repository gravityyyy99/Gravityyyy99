#!/usr/bin/env python3
"""
Render the profile README as a stack of animated SVG cards into cards/.

Every card is shown through <img>, so it only uses what GitHub allows there: an inline
<style> with CSS keyframes, SMIL, and fonts embedded as base64 WOFF data URIs.
Data comes from data/contributions.json and data/repos.json (scripts/fetch_data.py).
STATIC=1 renders every card at its end state (for screenshots).
"""
import base64, datetime, json, os, re, textwrap
from html import escape, unescape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")
STATIC = bool(os.environ.get("STATIC"))
os.makedirs(OUT, exist_ok=True)

# ---- tokens ------------------------------------------------------------------
PAPER, PAPER2, INK, SOFT, MUTED, RULE = "#f4f1ea", "#e8e4da", "#15151a", "#3b3b44", "#7a7a84", "#d9d4c7"
TEAL, CORAL, AMBER, VIOLET = "#0d9488", "#ff5a4e", "#ffb81c", "#6d4aff"
INK_SOFT_ART = "#22222a"
DARK, DARK2 = "#0f1115", "#171a21"
W = 880
SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, sans-serif"
MONO = "'Geist Mono', ui-monospace, Menlo, monospace"
GAP = 12
FONT_FILES = {"serif": ("Instrument Serif", "serif-400.woff", 400), "sans": ("Geist", "geist-400.woff", 400),
              "sansb": ("Geist", "geist-600.woff", 600), "mono": ("Geist Mono", "geistmono-400.woff", 400)}

CSS = """
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translate(4px,-4px)}}
@keyframes tilein{0%{opacity:0;transform:translateY(90px) scale(.6) rotate(-9deg)}55%{opacity:1;transform:translateY(-10px) scale(1.05) rotate(2deg)}75%{transform:translateY(3px) scale(.98) rotate(-.8deg)}100%{opacity:1;transform:none}}
@keyframes sheen{0%{transform:translateX(-300px) skewX(-20deg)}22%,100%{transform:translateX(460px) skewX(-20deg)}}
@keyframes ring{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.6)}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes reveal{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes wipe{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.r{opacity:0;transform-box:fill-box;animation:rise .8s cubic-bezier(.2,.7,.2,1) both}
.f{opacity:0;animation:fade .5s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.cur{animation:blink 1s steps(1) infinite}
.nu{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.ti{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:tilein .9s cubic-bezier(.2,.8,.2,1) both}
.sh{animation:sheen 5s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1s ease-out both}
.dr{stroke-dasharray:var(--l);stroke-dashoffset:var(--l);animation:draw 1.4s ease-out both}
.ty{animation:reveal .7s steps(26) both}
.wp{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:wipe .6s steps(18) both}
@media (prefers-reduced-motion: reduce){.r,.f,.g,.p,.live,.cur,.nu,.ti,.rg,.dr,.wp,.ty{animation:none!important;opacity:1!important;transform:none!important;stroke-dashoffset:0!important;clip-path:none!important}.sh,.rg{display:none}}
"""
if STATIC:
    CSS += ".r,.f,.g,.p,.live,.cur,.nu,.ti,.dr,.wp,.ty{animation:none!important;opacity:1!important;transform:none!important;stroke-dashoffset:0!important;clip-path:none!important}.sh,.rg{display:none}"


_SUB = {}


def subset_b64(fn, chars):
    key = (fn, chars)
    if key not in _SUB:
        from fontTools import subset
        import io
        o = subset.Options()
        o.flavor, o.layout_features, o.notdef_outline = "woff", ["kern", "liga"], True
        f = subset.load_font(os.path.join(FONTS, fn), o)
        sb = subset.Subsetter(o)
        sb.populate(text=chars)
        sb.subset(f)
        buf = io.BytesIO()
        f.flavor = "woff"
        f.save(buf)
        _SUB[key] = base64.b64encode(buf.getvalue()).decode()
    return _SUB[key]


def fontcss(keys, chars):
    out = []
    for k in keys:
        fam, fn, wt = FONT_FILES[k]
        out.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};src:url(data:font/woff;base64,{subset_b64(fn, chars)}) format('woff')}}")
    return "".join(out)


def svg(name, h, body, fonts=("serif", "sans", "sansb", "mono"), left=0, right=0, w=W, defs=""):
    H = h + GAP
    chars = "".join(sorted(set(unescape("".join(re.findall(r">([^<]*)<", body))) + " 0123456789.,%+-")))
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w + left + right:.2f}" height="{H}" viewBox="0 0 {w + left + right:.2f} {H}">'
         f'<defs>{defs}<style>{fontcss(fonts, chars)}{CSS}</style></defs>'
         f'<g transform="translate({left} 0)">{body}</g></svg>')
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(s)
    print(f"{name}: {len(s)//1024} KB")


def t(x, y, s, size=14, fill=INK, font=SANS, cls="", delay=0.0, anchor="start", extra=""):
    c = f' class="{cls}" style="animation-delay:{delay:.2f}s"' if cls else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{c} {extra}>'
            f'{escape(str(s))}</text>')


def card(w, h, fill=PAPER, rx=22, stroke=RULE, extra=""):
    return f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="{rx}" fill="{fill}" stroke="{stroke}" {extra}/>'


def arrow(x, y, color=INK, delay=0.0, size=14):
    return (f'<g class="nu" style="animation-delay:{delay}s"><path d="M{x} {y + size} L{x + size} {y} M{x + 3} {y} H{x + size} V{y + size - 3}" '
            f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>')


def countup(x, y, final, size, fill, delay, font=SERIF, suffix="", anchor="start", steps=18, dur=1.3):
    """Count-up with SMIL: one text per value, shown for a few ms (CSS cannot change text)."""
    if STATIC:
        return t(x, y, f"{final:,}{suffix}", size, fill, font, anchor=anchor)
    out = []
    for i in range(steps + 1):
        v = round(final * (1 - (1 - i / steps) ** 3))
        begin = delay + dur * i / steps
        last = i == steps
        d = "" if last else f' dur="{dur / steps:.3f}s" fill="remove"'
        out.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" visibility="hidden">'
                   f'{v:,}{suffix}<set attributeName="visibility" to="visible" begin="{begin:.3f}s"{d}'
                   f'{" fill=%sfreeze%s" % (chr(34), chr(34)) if last else ""}/></text>')
    return "".join(out)


def load(name, default=None):
    p = os.path.join(ROOT, "data", name)
    return json.load(open(p)) if os.path.exists(p) else default


C = load("contributions.json")
REPOS = load("repos.json", [])


# ================================ HERO =========================================
def hero(portrait=None, dark=False, out="hero.svg"):
    h = 410
    b = [card(W, h)]
    b.append(f'<rect x="43" y="41" width="10" height="10" rx="3" fill="{TEAL}" class="live"/>')
    b.append(t(62, 50, "OPEN TO WORK  /  BHUBANESWAR, INDIA", 11.5, MUTED, MONO, "ty", 0.2, extra='letter-spacing="1.6"'))
    grad = (f'<linearGradient id="sg" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="300" y2="0" gradientTransform="translate(-260 0)">'
            f'<stop offset="0" stop-color="{INK}"/><stop offset=".42" stop-color="{INK}"/><stop offset=".5" stop-color="{TEAL}"/>'
            f'<stop offset=".58" stop-color="{INK}"/><stop offset="1" stop-color="{INK}"/>'
            f'<animateTransform attributeName="gradientTransform" type="translate" values="-260 0;300 0;300 0" keyTimes="0;.4;1" dur="6s" begin="2.2s" repeatCount="indefinite"/></linearGradient>')
    b.append(t(44, 148, "Dibyajyoti", 100, INK, SERIF, "r", 0.3))
    b.append(t(44, 244, "Pradhan", 100, "url(#sg)" if not STATIC else INK, SERIF, "r", 0.6))
    b.append(t(48, 300, "Just a silly coder", 21, SOFT, SANS, "ty", 1.2))
    b.append(t(48, 328, "chasing semicolons.", 21, SOFT, SANS, "ty", 1.9))
    b.append(t(48, 372, "github.com/gravityyyy99", 13.5, INK, MONO, "ty", 2.6))
    b.append(arrow(252, 360, TEAL, 3.4, 11))
    # portrait: fine ASCII drawn straight onto the card (data/portrait.txt, see scripts/make_ascii.py)
    pr = portrait or os.path.join(ROOT, "data", "portrait.txt")
    rows = open(pr).read().split(chr(10)) if os.path.exists(pr) else placeholder_portrait()
    cols = max(len(r) for r in rows)
    ch = 350 / len(rows)
    cw = ch * 0.62
    px, py = 505 + (350 - cols * cw) / 2, 30
    for i, row in enumerate(rows):
        if row.strip():
            b.append(f'<text x="{px:.1f}" y="{py + (i + 1) * ch:.1f}" font-family="{MONO}" font-size="{cw / 0.6:.2f}" fill="{INK_SOFT_ART}" xml:space="preserve" '
                     f'textLength="{len(row) * cw:.1f}" lengthAdjust="spacing" class="ty" style="animation-delay:{0.5 + i * 0.045:.2f}s">{escape(row)}</text>')
    svg(out, h, "".join(b), defs=grad)


def placeholder_portrait():
    """Soft silhouette until a real portrait.txt exists (run scripts/make_ascii.py photo.jpg)."""
    rows, ramp = [], " .:-=+*#%@"
    R, Cc = 46, 62
    for y in range(R):
        s = ""
        for x in range(Cc):
            dx, dy = (x - Cc / 2) / (Cc * 0.2), (y - R * 0.34) / (R * 0.27)
            head = dx * dx + dy * dy < 1
            sx, sy = (x - Cc / 2) / (Cc * 0.42), (y - R * 1.02) / (R * 0.5)
            body = sx * sx + sy * sy < 1
            v = 0.0
            if head:
                v = 0.55 + 0.4 * (1 - min(1, dx * dx + dy * dy))
            elif body:
                v = 0.35 + 0.2 * (1 - min(1, sx * sx + sy * sy))
            s += ramp[int(v * (len(ramp) - 1))] if v else " "
        rows.append(s.rstrip())
    return rows


# ================================ TERMINAL =====================================
def terminal():
    K, S, F, N, CM, ST, G = "#ff7b72", "#a5d6ff", "#d2a8ff", "#e6edf3", "#7d8590", "#7ee787", "#ffa657"
    L = [
        [("~/dibya", ST), (" $ ", CM), ("whoami", N)],
        [("> Dibyajyoti Pradhan", N), ("   // aka Dibya, aka gravityyyy99", CM)],
        [("~/dibya", ST), (" $ ", CM), ("cat about.js", N)],
        [("class ", K), ("Dibya ", G), ("extends ", K), ("Engineer ", G), ("{", N)],
        [("  stack ", F), ("= [", N), ("'React'", S), (", ", N), ("'MongoDB'", S), (", ", N), ("'SQL'", S), (", ", N), ("'Firebase'", S), ("];", N)],
        [("  bugs ", F), ("= [];  ", N), ("// O(n) in the morning, O(n log n) after coffee", CM)],
        [("  async ", K), ("build", F), ("(idea) {", N)],
        [("    while ", K), ("(!idea.shipped) { ", N), ("code", F), ("(); ", N), ("debug", F), ("(); ", N), ("coffee", F), ("(); }  ", N), ("// infinite loop, by design", CM)],
        [("    return ", K), ("deploy", F), ("(idea);  ", N), ("// works on my machine, and on Render", CM)],
        [("  }", N)],
        [("  get ", K), ("hobbies", F), ("() { ", N), ("return ", K), ("['photography', 'cinematography', 'game QA']", S), ("; }", N)],
        [("}", N)],
        [("~/dibya", ST), (" $ ", CM), ("git status", N)],
        [("On branch ", N), ("main", ST), (": 99 problems, but a segfault ain't one", CM)],
        [("~/dibya", ST), (" $ ", CM), ("./hire --me", N)],
        [("   # 404: sleep not found", CM)],
    ]
    lh, top = 21, 62
    h = top + len(L) * lh + 30
    b = [card(W, h, DARK, 18, "#2a2f3a")]
    b.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="40" rx="18" fill="{DARK2}"/><rect x="0.5" y="24" width="{W - 1}" height="17" fill="{DARK2}"/>')
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        b.append(f'<circle cx="{28 + i * 20}" cy="21" r="6" fill="{c}" class="p" style="animation-delay:{i * .1}s"/>')
    b.append(t(W / 2, 25, "dibya@portfolio: ~/about.js", 12, CM, MONO, anchor="middle"))
    for i, segs in enumerate(L):
        d = 0.5 + i * 0.32
        sp = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in segs)
        b.append(f'<text x="28" y="{top + i * lh}" font-family="{MONO}" font-size="13" xml:space="preserve" class="f" style="animation-delay:{d:.2f}s">{sp}</text>')
    b.append(f'<rect x="28" y="{top + len(L) * lh - 12}" width="8" height="15" fill="{TEAL}" class="cur"/>')
    svg("terminal.svg", h, "".join(b), fonts=("mono",))


# ================================ SECTION HEADERS ==============================
def section(name, title, sub, color):
    h = 78
    b = [card(W, h)]
    b.append(f'<rect x="28" y="30" width="14" height="14" rx="4" fill="{color}" class="p"/>')
    b.append(t(56, 50, title, 40, INK, SERIF, "r", 0.1))
    b.append(t(W - 28, 46, sub, 12.5, MUTED, MONO, "f", 0.4, anchor="end"))
    svg(name, h, "".join(b), fonts=("serif", "mono"))


# ================================ CONTRIBUTIONS ================================
def heatmap():
    days = C["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7  # Sunday = 0
    grid = [None] * lead + days
    weeks = [grid[i:i + 7] for i in range(0, len(grid), 7)]
    cell, gap = 13, 3
    x0, y0 = (W - len(weeks) * (cell + gap) + gap) / 2, 78
    h = y0 + 7 * (cell + gap) + 52
    nz = sorted(d["count"] for d in days if d["count"])
    q = [nz[int(len(nz) * f)] if nz else 1 for f in (0.25, 0.5, 0.75)]
    pal = ["#e4e2d9", "#a7e3dc", "#4fc9bd", "#119f94", "#0a5f58"]
    b = [card(W, h)]
    b.append(t(28, 42, "Contribution graph", 30, INK, SERIF, "r", 0.1))
    b.append(t(W - 28, 40, f"{C['total']:,} in the last year", 12.5, MUTED, MONO, "f", 0.3, anchor="end"))
    for wi, wk in enumerate(weeks):
        for di, d in enumerate(wk):
            if not d:
                continue
            n = d["count"]
            lvl = 0 if n == 0 else 1 + sum(n > v for v in q)
            b.append(f'<rect x="{x0 + wi * (cell + gap):.1f}" y="{y0 + di * (cell + gap)}" width="{cell}" height="{cell}" rx="3" fill="{pal[lvl]}" class="p" style="animation-delay:{0.3 + wi * 0.035:.2f}s"/>')
    ly = h - 22
    b.append(t(x0, ly + 9, "less", 10.5, MUTED, MONO))
    for i, c in enumerate(pal):
        b.append(f'<rect x="{x0 + 32 + i * 16}" y="{ly}" width="11" height="11" rx="3" fill="{c}"/>')
    b.append(t(x0 + 32 + 5 * 16 + 4, ly + 9, "more", 10.5, MUTED, MONO))
    svg("heatmap.svg", h, "".join(b), fonts=("serif", "mono"))


def activity():
    h = 330
    m = C["monthly"]
    mx = max(1, max(x["total"] for x in m))
    best = max(range(len(m)), key=lambda i: m[i]["total"])
    b = [card(W, h)]
    b.append(t(28, 42, "Month by month", 30, INK, SERIF, "r", 0.1))
    b.append(t(W - 28, 40, "contributions per month", 12.5, MUTED, MONO, "f", 0.3, anchor="end"))
    base, top = 215, 80
    bw, step = 38, (W - 56) / len(m)
    for i, x in enumerate(m):
        bh = max(4, (x["total"] / mx) * (base - top))
        bx = 28 + i * step + (step - bw) / 2
        col = TEAL if i == best else "#c9c4b4"
        d = 0.4 + i * 0.07
        b.append(f'<rect x="{bx:.1f}" y="{base - bh:.1f}" width="{bw}" height="{bh:.1f}" rx="6" fill="{col}" class="g" style="animation-delay:{d:.2f}s"/>')
        label = datetime.date.fromisoformat(x["month"] + "-01").strftime("%b")
        b.append(t(bx + bw / 2, base + 20, label, 11.5, MUTED, MONO, anchor="middle"))
        if i == best:
            b.append(t(bx + bw / 2, base - bh - 10, x["total"], 22, TEAL, SERIF, "p", d + 0.8, anchor="middle"))
    stats = [("total", f"{C['total']:,}", TEAL), ("active days", C["active_days"], CORAL), ("longest streak", f"{C['longest_streak']}d", AMBER),
             ("current streak", f"{C['current_streak']}d", VIOLET),
             ("busiest day", f"{C['best_day']['count']}", INK)]
    sw = (W - 56) / len(stats)
    b.append(f'<line x1="28" y1="256" x2="{W - 28}" y2="256" stroke="{RULE}"/>')
    for i, (lab, val, col) in enumerate(stats):
        x = 28 + i * sw
        b.append(t(x, 296, val, 34, col, SERIF, "r", 1 + i * 0.1))
        b.append(t(x, 316, lab.upper(), 10.5, MUTED, MONO, "f", 1.1 + i * 0.1, extra='letter-spacing="1.2"'))
    svg("activity.svg", h, "".join(b))


# ================================ TILES ========================================
def tile(name, color, tag, num, suffix, label, line2, textcol=INK, delay=0.0):
    w, h = W / 3 - 12, 250
    b = []
    clip = f'<clipPath id="c"><rect x="0" y="0" width="{w}" height="{h}" rx="22"/></clipPath>'
    inner = [f'<rect width="{w}" height="{h}" rx="22" fill="{color}"/>']
    inner.append(f'<g class="sh" style="animation-delay:{delay + 2:.1f}s"><rect x="0" y="-20" width="70" height="{h + 40}" fill="#fff" opacity=".28"/></g>')
    b.append(f'<g class="ti" style="animation-delay:{delay:.2f}s"><g clip-path="url(#c)">{"".join(inner)}</g>')
    b.append(f'<circle cx="{w - 34}" cy="34" r="16" fill="none" stroke="{textcol}" stroke-width="2" class="rg" style="animation-delay:{delay + 1:.1f}s"/>')
    b.append(t(26, 40, tag, 12, textcol, MONO, extra='letter-spacing="2.2" font-weight="600"'))
    b.append(arrow(w - 42, 26, textcol, delay))
    b.append(countup(24, 150, num, 92, textcol, delay + 0.3, SERIF, suffix, dur=1.0, steps=12))
    b.append(t(26, 185, label, 15, textcol, SANS, extra='font-weight="600"'))
    b.append(t(26, 208, line2, 12.5, textcol, SANS, extra='opacity=".78"'))
    b.append("</g>")
    svg(name, h, "".join(b), fonts=("serif", "sansb", "mono"), left=6, right=6, w=w, defs=clip)


def tiles():
    nrepos = 24
    tile("build.svg", TEAL, "BUILD", nrepos, "", "repos and counting", "React, Node, Socket.IO, MongoDB", "#fff", 0.05)
    tile("create.svg", CORAL, "CREATE", 3, " yrs", "Media Club president", "photography, film, game QA", "#fff", 0.2)
    tile("learn.svg", AMBER, "LEARN", 9, "", "certifications earned", "JS, React, GenAI, ML, IoT", INK, 0.35)


# ================================ STACK ========================================
ICONS = os.path.join(ROOT, "icons")


def icon(name, x, y, size, color):
    d = " ".join(re.findall(r' d="([^"]+)"', open(os.path.join(ICONS, name + ".svg"), encoding="utf-8").read()))
    return f'<svg x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" viewBox="0 0 24 24"><path d="{d}" fill="{color}"/></svg>'


STACK_ROWS = [
    [("Languages", [("HTML", "html5", "#E34F26"), ("CSS", "css3", "#1572B6"), ("Tailwind", "tailwindcss", "#06B6D4"), ("JavaScript", "javascript", "#F7DF1E"),
                    ("Java", "openjdk", "#ED8B00"), ("Python", "python", "#3776AB"), ("TypeScript", "typescript", "#3178C6")], "TypeScript: still learning")],
    [("Frontend", [("React", "react", "#61DAFB")], ""),
     ("Databases", [("MongoDB", "mongodb", "#47A248"), ("MySQL", "mysql", "#4479A1"), ("Firebase", "firebase", "#FFCA28")], "Firebase: some"),
     ("Creative tools", [("Premiere", "adobepremierepro", "#9999FF"), ("Photoshop", "adobephotoshop", "#31A8FF"), ("Canva", "canva", "#00C4CC")], "")],
    [("Tools and deployment", [("Git", "git", "#F05032"), ("GitHub", "github", "#181717"), ("Vercel", "vercel", "#000000"),
                               ("Netlify", "netlify", "#00C7B7"), ("Cloudflare", "cloudflare", "#F38020")], "")],
]


def stack():
    tw, th, pitch = 100, 100, 138
    h = 34 + len(STACK_ROWS) * pitch - 14
    b = [card(W, h)]
    k = 0
    for r, row in enumerate(STACK_ROWS):
        y = 38 + r * pitch
        x = 28
        for name, items, note in row:
            b.append(t(x, y, name.upper(), 11, MUTED, MONO, "f", 0.1 + k * 0.03, extra='letter-spacing="1.6"'))
            if note:
                nx = W - 28 if len(row) == 1 else x + len(name) * 8.2 + 14
                b.append(t(nx, y, note, 11, MUTED, MONO, "f", 0.2, anchor="end" if len(row) == 1 else "start"))
            for label, ic, col in items:
                d = 0.15 + k * 0.045
                b.append(f'<g class="p" style="animation-delay:{d:.2f}s"><rect x="{x}" y="{y + 14}" width="{tw}" height="{th}" rx="18" fill="#fbfaf6" stroke="{RULE}"/>'
                         f'{icon(ic, x + (tw - 40) / 2, y + 14 + 18, 40, col)}'
                         f'{t(x + tw / 2, y + 14 + 82, label, 12, SOFT, SANS, anchor="middle", extra="font-weight=%s600%s" % (chr(34), chr(34)))}</g>')
                x += tw + 12
                k += 1
            x += 16
    svg("stack.svg", h, "".join(b))


# ================================ CERTS ========================================
CERTS = [("Namaste JavaScript", "NamasteDev", "Closures, event loop, async JS", TEAL),
         ("React and Redux", "KnowledgeGate", "Scored 98%  |  Sep 2026", VIOLET),
         ("Prompt Engineering with OpenAI", "Columbia+", "Jul 2026", CORAL),
         ("Machine Learning I", "Columbia+", "Jul 2026", AMBER),
         ("Gen AI Engineering Mastermind", "Outskill", "LLMs, prompt design, AI tools", TEAL),
         ("Generative AI Mastermind", "Outskill", "Applied GenAI workflows", VIOLET),
         ("Generative AI Fundamentals", "Databricks", "Exam  |  Oct 2026", CORAL),
         ("AI Skills Passport", "EY and Microsoft", "General + employability", AMBER),
         ("Introduction to IoT", "NPTEL, IIT Kharagpur", "Jul-Oct 2025  |  58%", TEAL)]


def certs():
    cw, ch = (W - 56 - 24) / 3, 92
    h = 64 + 3 * (ch + 12) + 22
    b = [card(W, h)]
    b.append(t(28, 40, "const certifications = [", 14, MUTED, MONO, "f", 0.1))
    b.append(t(W - 28, 40, "// 10 and counting", 13, MUTED, MONO, "f", 0.2, anchor="end"))
    for i, (n, org, sub, col) in enumerate(CERTS):
        x, y = 28 + (i % 3) * (cw + 12), 58 + (i // 3) * (ch + 12)
        d = 0.3 + i * 0.12
        title = textwrap.wrap(n, 26)
        g = [f'<rect x="{x:.1f}" y="{y}" width="{cw:.1f}" height="{ch}" rx="14" fill="#fbfaf6" stroke="{RULE}"/>',
             f'<rect x="{x:.1f}" y="{y + 14}" width="4" height="{ch - 28}" rx="2" fill="{col}"/>']
        for j, ln in enumerate(title[:2]):
            g.append(t(x + 18, y + 28 + j * 18, ln, 14.5, INK, SANS, extra='font-weight="600"'))
        yy = y + 28 + len(title[:2]) * 18
        g.append(t(x + 18, yy + 2, org, 11.5, col if col != AMBER else "#b07d00", MONO))
        g.append(t(x + 18, yy + 20, sub, 11.5, MUTED, SANS))
        b.append(f'<g class="r" style="animation-delay:{d:.2f}s">{"".join(g)}</g>')
    svg("certs.svg", h, "".join(b))


# ================================ JOURNEY ======================================
JOURNEY = [("11-12", "Class 11 and 12", "Prabhujee English School", "Physics, Chem, Maths, CS", TEAL),
           ("2023", "B.Tech CSE", "Gandhi Engineering College", "Where the debugging began", CORAL),
           ("QA", "Game Beta Tester", "UGW, FAU-G, Indus", "Hunting bugs in game builds", AMBER),
           ("23-26", "Media Club President", "PRATIBIMBA, GEC", "Led it 3 years, then passed it on", VIOLET),
           ("2026", "International Photo Win", "Won an international event", "One photo got featured", TEAL),
           ("Oct", "Naukri Young Turks", "Rank 1224, top 3000", "99.69 percentile", CORAL),
           ("Now", "Final-year student", "B.Tech CSE, CGPA 8.21", "Building and learning", AMBER)]


def journey():
    h = 400
    mid = 220
    n = len(JOURNEY)
    step = (W - 200) / (n - 1)
    b = [card(W, h)]
    b.append(t(28, 40, "git log --oneline --graph", 14, MUTED, MONO, "f", 0.1))
    b.append(t(W - 28, 40, "# the story so far", 13, MUTED, MONO, "f", 0.2, anchor="end"))
    L = W - 200
    b.append(f'<line x1="100" y1="{mid}" x2="{W - 100}" y2="{mid}" stroke="{INK}" stroke-width="2.5" stroke-linecap="round" class="dr" style="--l:{L};animation-delay:.3s"/>')
    for i, (when, title, a, c, col) in enumerate(JOURNEY):
        x = 100 + i * step
        d = 0.5 + i * 0.35
        up = i % 2 == 0
        b.append(f'<circle cx="{x:.1f}" cy="{mid}" r="11" fill="{col}" stroke="{PAPER}" stroke-width="4" class="p" style="animation-delay:{d:.2f}s"/>')
        b.append(f'<g class="r" style="animation-delay:{d + 0.15:.2f}s">')
        if up:
            y1, y2 = mid - 24, mid - 70
            b.append(f'<line x1="{x:.1f}" y1="{mid - 12}" x2="{x:.1f}" y2="{mid - 66}" stroke="{col}" stroke-width="2"/>')
            by = mid - 160
        else:
            b.append(f'<line x1="{x:.1f}" y1="{mid + 12}" x2="{x:.1f}" y2="{mid + 50}" stroke="{col}" stroke-width="2"/>')
            by = mid + 58
        b.append(t(x, by + 26, when, 28, col if col != AMBER else "#b07d00", SERIF, anchor="middle"))
        b.append(t(x, by + 48, title, 13.5, INK, SANS, anchor="middle", extra='font-weight="600"'))
        b.append(t(x, by + 66, a, 11, SOFT, SANS, anchor="middle"))
        b.append(t(x, by + 82, c, 11, MUTED, SANS, anchor="middle"))
        b.append("</g>")
    svg("journey.svg", h, "".join(b))


# ================================ REPOS ========================================
LANG = {"JavaScript": "#f1e05a", "TypeScript": "#3178c6", "CSS": "#9b6bff", "Python": "#3572a5", "HTML": "#e34c26"}
ACC = [TEAL, CORAL, AMBER, VIOLET, TEAL, CORAL]


DESC_FALLBACK = {"thestoryteller-website": "Website for The Storyteller, my photography and cinematography brand."}


def repo(i, r):
    w, h = W / 3 - 12, 210
    col = ACC[i % len(ACC)]
    b = [card(w, h)]
    d = 0.2 + (i % 3) * 0.2
    b.append(t(22, 52, "repo", 11, MUTED, MONO, "f", d, extra='letter-spacing="1.6"'))
    b.append(arrow(w - 38, 34, INK, d))
    name = r["name"]
    size = 26 if len(name) <= 16 else 21
    b.append(t(22, 86, name, size, INK, SERIF, "r", d + 0.1))
    desc = r["description"] or DESC_FALLBACK.get(r["name"], "Work in progress.")
    for j, ln in enumerate(textwrap.wrap(desc, 38)[:4]):
        b.append(t(22, 112 + j * 17, ln, 12, SOFT, SANS, "f", d + 0.3 + j * 0.1))
    ly = h - 24
    if r["language"]:
        b.append(f'<circle cx="28" cy="{ly - 4}" r="5" fill="{LANG.get(r["language"], MUTED)}" class="p" style="animation-delay:{d + .6:.1f}s"/>')
        b.append(t(40, ly, r["language"], 11.5, SOFT, MONO))
    b.append(t(w - 22, ly, f"* {r['stars']}", 11.5, SOFT, MONO, anchor="end"))
    svg(f"repo-{i + 1}.svg", h, "".join(b), left=6, right=6, w=w)


# ================================ FOOTER =======================================
def footer():
    h = 136
    b = [card(W, h, DARK, 22, "#2a2f3a")]
    b.append(t(W / 2, 70, "Thanks for stopping by", 58, "#f4f1ea", SERIF, "r", 0.2, anchor="middle"))
    b.append(t(W / 2, 108, "return 0;  // exit code 0: no errors, only features", 14, "#7d8590", MONO, "f", 0.7, anchor="middle"))
    svg("footer.svg", h, "".join(b), fonts=("serif", "mono"))


def live_terminal():
    h = 104
    b = [card(W, h, DARK, 22, "#2a2f3a")]
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        b.append(f'<circle cx="{30 + i * 18}" cy="26" r="5.5" fill="{c}" class="p" style="animation-delay:{i * .1}s"/>')
    b.append(t(30, 72, "$ ssh dibya@live-terminal", 15, "#7ee787", MONO, "ty", 0.4))
    b.append(f'<rect x="252" y="59" width="8" height="15" fill="{TEAL}" class="cur"/>')
    b.append(t(W - 70, 70, "Live Terminal", 40, "#f4f1ea", SERIF, "r", 0.8, anchor="end"))
    b.append(arrow(W - 52, 44, TEAL, 1.0, 20))
    b.append(t(W - 70, 90, "an interactive about-me, in your browser", 11.5, "#7d8590", MONO, "f", 1.1, anchor="end"))
    svg("live-terminal.svg", h, "".join(b), fonts=("serif", "mono"))


SOCIALS = [("linkedin", "LinkedIn", "in/dibyajyotipradhan", "linkedin", "#0A66C2"),
           ("email", "Email", "write to me", "gmail", "#EA4335"),
           ("instagram", "Instagram", "@thestoryteller.raw", "instagram", "#E4405F"),
           ("discord", "Discord", "gravityyyy99", "discord", "#5865F2")]


def socials():
    w, h = W / 4 - 12, 96
    for i, (key, label, handle, ic, col) in enumerate(SOCIALS):
        b = [card(w, h)]
        d = 0.1 + i * 0.12
        b.append(f'<g class="p" style="animation-delay:{d:.2f}s"><circle cx="40" cy="48" r="24" fill="{col}"/>{icon(ic, 28, 36, 24, "#ffffff")}</g>')
        b.append(t(76, 50, label, 25, INK, SERIF, "r", d + 0.1))
        b.append(t(76, 70, handle, 10, MUTED, MONO, "f", d + 0.25))
        b.append(arrow(w - 34, 22, INK, d, 12))
        svg(f"social-{key}.svg", h, "".join(b), left=6, right=6, w=w, fonts=("serif", "mono"))


if __name__ == "__main__":
    hero()
    terminal()
    heatmap()
    activity()
    tiles()
    section("title-stack.svg", "Tech stack", "what I build with", TEAL)
    stack()
    section("title-certs.svg", "Certifications", "keep learning, keep shipping", AMBER)
    certs()
    section("title-journey.svg", "My journey", "the story so far", CORAL)
    journey()
    section("title-code.svg", "What I'm coding", "latest from github", VIOLET)
    for i, r in enumerate(REPOS[:3]):
        repo(i, r)
    live_terminal()
    footer()
    socials()
