#!/usr/bin/env python3
"""Builds the static animated SVGs used by the profile README (header, typing intro, divider, project cards).

Everything is self-hosted pure SVG (CSS + SMIL animation), so no third-party service can break it.
Edit the TYPING / CARDS lists below, then run:  python scripts/build_assets.py
"""
import math, os, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
SANS = "'Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
INK, SOFT = "#4f3f7e", "#8a7bb0"


def write(name, svg):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", name, f"({len(svg) // 1024 + 1} KB)")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------ header
def header():
    W, H = 1000, 300
    rnd = random.Random(11)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Shashwat Rajan">']
    s.append(f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e4d6ff"/><stop offset=".5" stop-color="#ffd9e8"/><stop offset="1" stop-color="#fff0d6"/></linearGradient>
<linearGradient id="w1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cdb8f5" stop-opacity=".75"/><stop offset="1" stop-color="#cdb8f5" stop-opacity=".25"/></linearGradient>
<linearGradient id="w2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7b9d0" stop-opacity=".7"/><stop offset="1" stop-color="#f7b9d0" stop-opacity=".25"/></linearGradient>
<linearGradient id="w3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".85"/><stop offset="1" stop-color="#fff0d6" stop-opacity=".7"/></linearGradient>
<clipPath id="rc"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<filter id="soft"><feGaussianBlur stdDeviation="14"/></filter>
</defs>
<style>
.f1{{animation:fl 9s ease-in-out infinite}}.f2{{animation:fl 12s ease-in-out -3s infinite}}.f3{{animation:fl 14s ease-in-out -6s infinite}}.f4{{animation:fl 10s ease-in-out -2s infinite}}
@keyframes fl{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(18px,-16px)}}}}
.tw{{animation:tw 3s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15;transform:scale(.6)}}50%{{opacity:1;transform:scale(1.15)}}}}
.wv1{{animation:wv 16s linear infinite}}.wv2{{animation:wv 11s linear infinite}}.wv3{{animation:wv 7s linear infinite}}
@keyframes wv{{to{{transform:translateX(-500px)}}}}
.in1{{animation:inn 1.1s cubic-bezier(.2,.8,.2,1) both}}.in2{{animation:inn 1.1s .25s cubic-bezier(.2,.8,.2,1) both}}.in3{{animation:inn 1.1s .5s cubic-bezier(.2,.8,.2,1) both}}
@keyframes inn{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
.star{{transform-box:fill-box;transform-origin:center}}
.bob{{animation:bob 2.2s ease-in-out infinite}}@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}
</style>
<g clip-path="url(#rc)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>''')
    # blurred blobs
    blobs = [(130, 70, 120, "#cdb8f5", "f1"), (860, 60, 140, "#f7b9d0", "f2"), (620, 230, 110, "#a9dcc4", "f3"), (330, 250, 90, "#f8d49b", "f4")]
    for x, y, r, c, cls in blobs:
        s.append(f'<g class="{cls}"><circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity=".55" filter="url(#soft)"/></g>')
    # stars
    for i in range(30):
        x, y = rnd.uniform(20, W - 20), rnd.uniform(14, 190)
        r = rnd.choice([2.2, 3, 3.8, 5])
        col = rnd.choice(["#ffffff", "#ffffff", "#fff6c9", "#f7b9d0"])
        d = rnd.uniform(0, 3)
        path = f"M{x:.1f} {y - r:.1f} Q{x:.1f} {y:.1f} {x + r:.1f} {y:.1f} Q{x:.1f} {y:.1f} {x:.1f} {y + r:.1f} Q{x:.1f} {y:.1f} {x - r:.1f} {y:.1f} Q{x:.1f} {y:.1f} {x:.1f} {y - r:.1f}Z"
        s.append(f'<path class="tw star" style="animation-delay:-{d:.2f}s;animation-duration:{rnd.uniform(2.2, 4.2):.1f}s" d="{path}" fill="{col}"/>')

    # waves: 4 periods of 500px so a 500px shift loops seamlessly
    def wave(y0, amp, phase, cls, fill):
        pts = []
        for k in range(0, 2001, 20):
            pts.append((k - 500, y0 + amp * math.sin((k / 500) * 2 * math.pi + phase)))
        d = "M" + " L".join(f"{x:.0f} {y:.1f}" for x, y in pts) + f" L{pts[-1][0]:.0f} {H + 40} L{pts[0][0]:.0f} {H + 40} Z"
        return f'<g class="{cls}"><path d="{d}" fill="url(#{fill})"/></g>'
    s.append(wave(232, 14, 0.0, "wv1", "w1"))
    s.append(wave(248, 12, 1.6, "wv2", "w2"))
    s.append(wave(266, 9, 3.2, "wv3", "w3"))

    # tiny pastel racer cruising across the front wave
    s.append('<g><animateTransform attributeName="transform" type="translate" values="-60 0;1060 0" dur="13s" repeatCount="indefinite"/>'
             '<g transform="translate(0 276)"><g class="bob">'
             '<rect x="-14" y="-5" width="28" height="9" rx="4.5" fill="#e5709f" stroke="#fff" stroke-width="1.6"/>'
             '<rect x="-17" y="-8" width="5" height="15" rx="1.5" fill="#4f3f7e"/><rect x="9" y="-7" width="4" height="13" rx="1.5" fill="#4f3f7e"/>'
             '<circle cx="-1" cy="-0.5" r="3" fill="#fff"/><circle cx="-9" cy="6" r="3.2" fill="#4f3f7e"/><circle cx="9" cy="6" r="3.2" fill="#4f3f7e"/>'
             '<path d="M-20 -1 h-18 M-20 3 h-26" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".7"/>'
             '</g></g></g>')

    # text
    s.append(f'<g class="in1"><text x="500" y="112" text-anchor="middle" font-family="{SANS}" font-size="15" letter-spacing="7" fill="{SOFT}" font-weight="600">HELLO WORLD, I AM</text></g>')
    s.append(f'<g class="in2"><text x="500" y="176" text-anchor="middle" font-family="{SANS}" font-size="68" font-weight="800" fill="#ffffff" opacity=".85" transform="translate(2 3)">Shashwat Rajan</text>'
             f'<text x="500" y="176" text-anchor="middle" font-family="{SANS}" font-size="68" font-weight="800" fill="{INK}">Shashwat Rajan</text></g>')
    s.append(f'<g class="in3"><text x="500" y="212" text-anchor="middle" font-family="{SANS}" font-size="18" fill="{INK}" opacity=".85">AI &amp; Data Science  ·  LLM agents  ·  Simulators  ·  Search</text></g>')
    s.append('</g></svg>')
    write("header.svg", "\n".join(s))


# ------------------------------------------------------------------ typing intro
TYPING = [
    "Building LLM agents that call the pit wall",
    "Training with GRPO. Reward design is the fun part",
    "Simulators, search systems and a little hardware",
    "Python and C++, clean maths over brute force",
]


def typing():
    W, H, FS = 820, 64, 22
    CW = FS * 0.6          # monospace advance
    SLOT, T = 6.0, 6.0 * len(TYPING)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(" / ".join(TYPING))}">',
         f'<style>text{{font-family:{MONO};font-size:{FS}px;font-weight:700;fill:#7a62c8}}'
         '.pk{fill:#e5709f}@media(prefers-color-scheme:dark){text{fill:#c5b3f5}.pk{fill:#f7a3c4}}'
         '.cur{animation:b .9s steps(1) infinite}@keyframes b{50%{opacity:0}}</style><defs>']
    for k, line in enumerate(TYPING):
        n = len(line)
        x0 = (W - n * CW) / 2
        s.append(f'<clipPath id="c{k}"><rect x="{x0:.1f}" y="0" width="0" height="{H}">' + anim("width", k, n, CW, SLOT, T) + '</rect></clipPath>')
    s.append('</defs>')
    for k, line in enumerate(TYPING):
        n = len(line)
        x0 = (W - n * CW) / 2
        s.append(f'<g clip-path="url(#c{k})"><text x="{x0:.1f}" y="40" textLength="{n * CW:.1f}" lengthAdjust="spacing" xml:space="preserve">{esc(line)}</text></g>')
        # cursor: follows the typed edge, only exists during this line's slot
        t0 = k * SLOT
        kt = f"0;{t0 / T:.4f};{(t0 + SLOT) / T:.4f};1"
        s.append(f'<g class="cur"><rect class="pk" x="{x0:.1f}" y="14" width="3" height="32" rx="1.5" opacity="0">'
                 + anim("x", k, n, CW, SLOT, T, base=x0)
                 + f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="0;1;0;0"/>'
                 + '</rect></g>')
    s.append('</svg>')
    write("typing.svg", "\n".join(s))


def anim(attr, k, n, CW, SLOT, T, base=0.0):
    """Discrete-step typing then erasing for line k inside the global T-second loop."""
    t0 = k * SLOT
    type_s, hold_end, erase_s = 2.4, 4.9, 0.7
    kt, vals = [0.0], [base if attr == "x" else 0.0]
    for j in range(1, n + 1):
        kt.append((t0 + 0.4 + (j - 1) * type_s / n) / T)
        vals.append(base + j * CW if attr == "x" else j * CW)
    for j in range(1, n + 1):
        kt.append((t0 + hold_end + (j - 1) * erase_s / n) / T)
        vals.append(base + (n - j) * CW if attr == "x" else (n - j) * CW)
    # the cursor must sit at x0 (not 0) outside the slot; width must be 0
    return (f'<animate attributeName="{attr}" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="{";".join(f"{v:.5f}" for v in kt)}" values="{";".join(f"{v:.1f}" for v in vals)}"/>')


# ------------------------------------------------------------------ divider
def divider():
    W, H = 1000, 28
    pts = []
    for x in range(0, W + 1, 10):
        pts.append((x, 14 + 5 * math.sin(x / 1000 * 2 * math.pi * 6)))
    d = "M" + " L".join(f"{x} {y:.1f}" for x, y in pts)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="presentation">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#cdb8f5" stop-opacity="0"/><stop offset=".2" stop-color="#cdb8f5"/><stop offset=".5" stop-color="#f7b9d0"/><stop offset=".8" stop-color="#a9dcc4"/><stop offset="1" stop-color="#a9dcc4" stop-opacity="0"/></linearGradient></defs>
<style>.fl{{animation:fl 3.2s linear infinite}}@keyframes fl{{to{{stroke-dashoffset:-48}}}}
.sp{{transform-box:fill-box;transform-origin:center;animation:sp 6s linear infinite}}@keyframes sp{{to{{transform:rotate(360deg)}}}}
.pu{{animation:pu 2.4s ease-in-out infinite}}@keyframes pu{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}</style>
<path d="{d}" fill="none" stroke="url(#g)" stroke-width="3" stroke-linecap="round" stroke-dasharray="14 10" class="fl"/>
<g class="sp"><path d="M500 3 Q500 14 511 14 Q500 14 500 25 Q500 14 489 14 Q500 14 500 3Z" fill="#f7b9d0" stroke="#fff" stroke-width="1.5"/></g>
<circle class="pu" cx="468" cy="14" r="2.6" fill="#cdb8f5"/><circle class="pu" style="animation-delay:-1.2s" cx="532" cy="14" r="2.6" fill="#a9dcc4"/>
</svg>'''
    write("divider.svg", svg)


# ------------------------------------------------------------------ project cards
# (file, repo, mono, display name, tagline, tags, language, (bg1, bg2), accent)
CARDS = [
    ("card-f1", "F1_Simulator_OpenENV", "F1", "F1 Strategist", "LLM race strategist trained with GRPO on F1 strategy",
     ["OpenEnv", "GRPO", "Qwen3"], "Jupyter Notebook", ("#ece3ff", "#ffe0ec"), "#e5709f"),
    ("card-lexshift", "LexShift", "LS", "LexShift", "Good-law-aware search over Supreme Court judgments",
     ["Information retrieval", "Law", "Python"], "Python", ("#dff5ea", "#dbeefa"), "#5fae8e"),
    ("card-prism", "PRISM", "PR", "PRISM", "Explainable competency-gap platform in 11 languages",
     ["SIH 2026", "Explainable", "Python"], "Python", ("#fff0d9", "#ffe0ec"), "#e0a23f"),
    ("card-snu", "snu-scheduler", "SB", "SNU Bid Planner", "Reserve-aware bid planner and timetable builder",
     ["OR-Tools", "CP-SAT", "Scheduling"], "HTML", ("#dbeefa", "#ece3ff"), "#6aa6d0"),
    ("card-ghostmate", "ghost-mate", "GM", "Ghost Mate", "Autonomous CoreXY chess robot on a Raspberry Pi",
     ["Teensy 4.1", "Hardware", "Python"], "Python", ("#ffe0ec", "#ece3ff"), "#c27bd6"),
    ("card-opstwin", "opstwin-recovery", "OT", "OpsTwin Recovery Arena", "OpenEnv arena for incident-response agents",
     ["OpenEnv", "RL", "Multi-agent"], "Python", ("#dff5ea", "#fff0d9"), "#e08a5f"),
]
LANG = {"Python": "#9b86e8", "HTML": "#f19cbc", "Jupyter Notebook": "#f0a26b"}


def cards():
    for fid, repo, mono, name, tag, tags, lang, (c1, c2), acc in CARDS:
        W, H = 430, 190
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(name)}: {esc(tag)}">']
        s.append(f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>
<linearGradient id="ic" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{acc}" stop-opacity=".95"/><stop offset="1" stop-color="{acc}" stop-opacity=".6"/></linearGradient>
<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="cl"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="22"/></clipPath>
<filter id="bl"><feGaussianBlur stdDeviation="12"/></filter>
</defs>
<style>
.fa{{animation:fa 8s ease-in-out infinite}}.fb{{animation:fa 11s ease-in-out -4s infinite}}
@keyframes fa{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(14px,-10px)}}}}
.sh{{animation:sh 6.5s ease-in-out infinite}}@keyframes sh{{0%,55%{{transform:translateX(-200px)}}100%{{transform:translateX(640px)}}}}
.ic{{animation:ic 3.4s ease-in-out infinite}}@keyframes ic{{0%,100%{{transform:translateY(0) rotate(0)}}50%{{transform:translateY(-3px) rotate(-3deg)}}}}
.ar{{animation:ar 1.6s ease-in-out infinite}}@keyframes ar{{0%,100%{{transform:translateX(0)}}50%{{transform:translateX(5px)}}}}
.pl{{animation:pl 3s ease-in-out infinite}}@keyframes pl{{0%,100%{{opacity:.85}}50%{{opacity:1}}}}
.in{{animation:inn .9s cubic-bezier(.2,.8,.2,1) both}}@keyframes inn{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22.5" fill="url(#bg)" stroke="#fff" stroke-opacity=".9"/>
<g clip-path="url(#cl)">
<g class="fa"><circle cx="360" cy="30" r="62" fill="{acc}" opacity=".22" filter="url(#bl)"/></g>
<g class="fb"><circle cx="60" cy="176" r="56" fill="#fff" opacity=".5" filter="url(#bl)"/></g>''')
        # icon
        s.append(f'<g class="ic" style="transform-box:fill-box;transform-origin:center"><rect x="24" y="22" width="48" height="48" rx="15" fill="url(#ic)" stroke="#fff" stroke-width="2"/>'
                 f'<text x="48" y="53" text-anchor="middle" font-family="{SANS}" font-size="19" font-weight="800" fill="#fff">{mono}</text></g>')
        s.append(f'<g class="in"><text x="86" y="43" font-family="{SANS}" font-size="20" font-weight="800" fill="{INK}">{esc(name)}</text>'
                 f'<text x="86" y="62" font-family="{MONO}" font-size="11" fill="{SOFT}">{esc(repo)}</text></g>')
        s.append(f'<g class="in" style="animation-delay:.15s"><text x="24" y="104" font-family="{SANS}" font-size="13.5" fill="{INK}" opacity=".9">{esc(tag)}</text></g>')
        # pills
        x = 24
        for i, t in enumerate(tags):
            w = len(t) * 6.6 + 20
            s.append(f'<g class="pl" style="animation-delay:-{i * .7:.1f}s"><rect x="{x:.1f}" y="120" width="{w:.1f}" height="24" rx="12" fill="#fff" opacity=".75" stroke="{acc}" stroke-opacity=".35"/>'
                     f'<text x="{x + w / 2:.1f}" y="136" text-anchor="middle" font-family="{SANS}" font-size="11.5" font-weight="600" fill="{INK}">{esc(t)}</text></g>')
            x += w + 8
        # footer
        s.append(f'<circle cx="31" cy="166" r="5" fill="{LANG.get(lang, "#bbb")}"/><text x="42" y="170" font-family="{SANS}" font-size="12" fill="{SOFT}">{esc(lang)}</text>')
        s.append(f'<g class="ar"><text x="{W - 24}" y="170" text-anchor="end" font-family="{SANS}" font-size="13" font-weight="700" fill="{acc}">view repo  →</text></g>')
        s.append(f'<g transform="skewX(-18)"><rect class="sh" x="0" y="0" width="90" height="{H}" fill="url(#sh)"/></g>')
        s.append('</g></svg>')
        write(fid + ".svg", "\n".join(s))


if __name__ == "__main__":
    header()
    typing()
    divider()
    cards()
