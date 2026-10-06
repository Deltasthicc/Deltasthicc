#!/usr/bin/env python3
"""Builds the static animated SVGs used by the profile README (header, typing intro, divider, project cards).

Everything is self-hosted pure SVG (CSS + SMIL animation), so no third-party service can break it.
Edit the TYPING / CARDS lists below, then run:  python scripts/build_assets.py
"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import car_scenes

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
    write("header.svg", car_scenes.header())
    write("divider.svg", car_scenes.divider())
    write("footer.svg", car_scenes.footer())
    typing()
    cards()
