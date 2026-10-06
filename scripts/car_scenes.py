"""Animated SVG scenes built around the real car cut-out (assets/car/*.webp, see make_car.py).

The webp files are embedded as data URIs so the SVGs stay self-contained: GitHub only lets an
<img> SVG load images that are inlined.
"""
import base64, json, math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
CAR_DIR = os.path.join(HERE, "..", "assets", "car")
SANS = "'Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
INK, SOFT = "#4f3f7e", "#8a7bb0"


def uri(name):
    with open(os.path.join(CAR_DIR, name), "rb") as f:
        return "data:image/webp;base64," + base64.b64encode(f.read()).decode()


def meta():
    with open(os.path.join(CAR_DIR, "car.json")) as f:
        return json.load(f)


def car_markup(width, spin=True, spin_dur=0.3):
    """The car at `width` px (origin = its top-left). Returns (markup, height, wheel_bottom_y)."""
    m = meta()
    big = m["sizes"]["car"]
    k = width / big["w"]
    h = big["h"] * k
    parts = [f'<image href="{uri("car.webp")}" x="0" y="0" width="{width:.1f}" height="{h:.1f}"/>']
    if spin:
        for name in ("front", "rear"):
            w = m["wheels"][name]
            half = w["px"] * k / 2
            parts.append(
                f'<g transform="translate({w["cx"] * k:.1f} {w["cy"] * k:.1f})"><g>'
                f'<animateTransform attributeName="transform" type="rotate" from="0" to="-360" dur="{spin_dur}s" repeatCount="indefinite"/>'
                f'<image href="{uri(f"wheel-{name}.webp")}" x="{-half:.1f}" y="{-half:.1f}" width="{half * 2:.1f}" height="{half * 2:.1f}"/>'
                f'</g></g>')
    return "".join(parts), h


# ------------------------------------------------------------------ header
def header():
    W, H = 1000, 320
    rnd = random.Random(11)
    CW = 410                                   # car width in the header
    car, ch = car_markup(CW)
    road_y, wheel_line = 262, 294
    car_y = wheel_line - ch + 2
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Shashwat Rajan, with a McLaren F1 car driving past">']
    s.append(f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e4d6ff"/><stop offset=".5" stop-color="#ffd9e8"/><stop offset="1" stop-color="#fff0d6"/></linearGradient>
<linearGradient id="w1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cdb8f5" stop-opacity=".8"/><stop offset="1" stop-color="#cdb8f5" stop-opacity=".3"/></linearGradient>
<linearGradient id="w2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7b9d0" stop-opacity=".8"/><stop offset="1" stop-color="#f7b9d0" stop-opacity=".3"/></linearGradient>
<linearGradient id="w3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".9"/><stop offset="1" stop-color="#fff0d6" stop-opacity=".75"/></linearGradient>
<linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9a9dc"/><stop offset="1" stop-color="#a392c9"/></linearGradient>
<linearGradient id="sl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity=".85"/></linearGradient>
<linearGradient id="tr" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="rc"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<filter id="soft"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="shadow" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
<style>
.f1{{animation:fl 9s ease-in-out infinite}}.f2{{animation:fl 12s ease-in-out -3s infinite}}.f3{{animation:fl 14s ease-in-out -6s infinite}}.f4{{animation:fl 10s ease-in-out -2s infinite}}
@keyframes fl{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(18px,-16px)}}}}
.tw{{animation:tw 3s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15;transform:scale(.6)}}50%{{opacity:1;transform:scale(1.15)}}}}
.star{{transform-box:fill-box;transform-origin:center}}
.wv1{{animation:wr 26s linear infinite}}.wv2{{animation:wr 15s linear infinite}}.wv3{{animation:wr 8s linear infinite}}
@keyframes wr{{to{{transform:translateX(500px)}}}}
.curb{{animation:cb .3s linear infinite}}@keyframes cb{{to{{transform:translateX(60px)}}}}
.dash{{animation:ds .5s linear infinite}}@keyframes ds{{to{{transform:translateX(100px)}}}}
.sp{{animation:sp linear infinite}}@keyframes sp{{from{{transform:translateX(-300px)}}to{{transform:translateX(1300px)}}}}
.in1{{animation:inn 1.1s cubic-bezier(.2,.8,.2,1) both}}.in2{{animation:inn 1.1s .25s cubic-bezier(.2,.8,.2,1) both}}.in3{{animation:inn 1.1s .5s cubic-bezier(.2,.8,.2,1) both}}
@keyframes inn{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
</style>
<g clip-path="url(#rc)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>''')
    for x, y, r, c, cls in [(130, 70, 120, "#cdb8f5", "f1"), (860, 60, 140, "#f7b9d0", "f2"), (620, 200, 110, "#ffffff", "f3"), (330, 220, 90, "#f8d49b", "f4")]:
        s.append(f'<g class="{cls}"><circle cx="{x}" cy="{y}" r="{r}" fill="{c}" opacity=".55" filter="url(#soft)"/></g>')
    for i in range(30):
        x, y = rnd.uniform(20, W - 20), rnd.uniform(14, 150)
        r = rnd.choice([2.2, 3, 3.8, 5])
        col = rnd.choice(["#ffffff", "#ffffff", "#fff6c9", "#f7b9d0"])
        d = rnd.uniform(0, 3)
        p = f"M{x:.1f} {y - r:.1f} Q{x:.1f} {y:.1f} {x + r:.1f} {y:.1f} Q{x:.1f} {y:.1f} {x:.1f} {y + r:.1f} Q{x:.1f} {y:.1f} {x - r:.1f} {y:.1f} Q{x:.1f} {y:.1f} {x:.1f} {y - r:.1f}Z"
        s.append(f'<path class="tw star" style="animation-delay:-{d:.2f}s;animation-duration:{rnd.uniform(2.2, 4.2):.1f}s" d="{p}" fill="{col}"/>')

    def wave(y0, amp, phase, cls, fill):          # 500px period; scrolls right (the car drives left)
        pts = [(k - 500, y0 + amp * math.sin((k / 500) * 2 * math.pi + phase)) for k in range(0, 2001, 20)]
        d = "M" + " L".join(f"{x:.0f} {y:.1f}" for x, y in pts) + f" L{pts[-1][0]:.0f} {H + 40} L{pts[0][0]:.0f} {H + 40} Z"
        return f'<g class="{cls}"><path d="{d}" fill="url(#{fill})"/></g>'
    s += [wave(206, 13, 0.0, "wv1", "w1"), wave(226, 11, 1.6, "wv2", "w2"), wave(244, 8, 3.2, "wv3", "w3")]

    # road: asphalt, scrolling kerb and centre dashes
    s.append(f'<rect x="0" y="{road_y}" width="{W}" height="{H - road_y}" fill="url(#road)"/>')
    s.append(f'<g class="curb">' + "".join(f'<rect x="{-60 + i * 60}" y="{road_y}" width="30" height="7" fill="#f7b9d0"/><rect x="{-30 + i * 60}" y="{road_y}" width="30" height="7" fill="#fff"/>' for i in range(20)) + '</g>')
    s.append(f'<g class="dash">' + "".join(f'<rect x="{-100 + i * 100}" y="{road_y + 44}" width="50" height="4" rx="2" fill="#fff" opacity=".85"/>' for i in range(13)) + '</g>')
    s.append(f'<rect x="0" y="{H - 8}" width="{W}" height="8" fill="#fff" opacity=".35"/>')

    # title
    s.append(f'<g class="in1"><text x="500" y="62" text-anchor="middle" font-family="{SANS}" font-size="15" letter-spacing="7" fill="{SOFT}" font-weight="600">HELLO WORLD, I AM</text></g>')
    s.append(f'<g class="in2"><text x="500" y="128" text-anchor="middle" font-family="{SANS}" font-size="68" font-weight="800" fill="#ffffff" opacity=".85" transform="translate(2 3)">Shashwat Rajan</text>'
             f'<text x="500" y="128" text-anchor="middle" font-family="{SANS}" font-size="68" font-weight="800" fill="{INK}">Shashwat Rajan</text></g>')
    s.append(f'<g class="in3"><text x="500" y="162" text-anchor="middle" font-family="{SANS}" font-size="18" fill="{INK}" opacity=".85">AI &amp; Data Science  ·  LLM agents  ·  Simulators  ·  Search</text></g>')

    # speed lines (the world rushing past, rightwards)
    for i in range(16):
        y = rnd.uniform(196, 300)
        ln = rnd.uniform(70, 230)
        sec = rnd.uniform(0.9, 1.7)
        s.append(f'<rect class="sp" style="animation-duration:{sec:.2f}s;animation-delay:-{rnd.uniform(0, 1.7):.2f}s" x="0" y="{y:.1f}" width="{ln:.0f}" height="{rnd.choice([1.5, 2, 2.5])}" rx="1" fill="url(#sl)" opacity="{rnd.uniform(.45, .9):.2f}"/>')

    # the car: drives in from the right, cruises, then floors it off to the left
    cx_mid = CW / 2
    s.append(f'<g transform="translate(0 {car_y:.1f})"><g>'
             '<animateTransform attributeName="transform" type="translate" dur="12s" repeatCount="indefinite" calcMode="spline" '
             'keyTimes="0;0.22;0.62;0.80;1" values="1120 0;560 0;520 0;-480 0;-480 0" '
             'keySplines=".1 .7 .3 1;0 0 1 1;.75 0 .9 .35;0 0 1 1"/>'
             f'<ellipse cx="{cx_mid:.0f}" cy="{ch - 2:.0f}" rx="{CW * .47:.0f}" ry="7" fill="#4f3f7e" opacity=".28" filter="url(#shadow)"/>'
             f'<rect x="{CW - 8}" y="{ch * .3:.0f}" width="190" height="{ch * .5:.0f}" rx="30" fill="url(#tr)"/>'
             '<g><animateTransform attributeName="transform" type="translate" dur="0.14s" repeatCount="indefinite" values="0 0;0 -1.1;0 0;0 .8;0 0"/>'
             + car + '</g></g></g>')
    s.append('</g></svg>')
    return "\n".join(s)


# ------------------------------------------------------------------ divider
def divider():
    W, H = 1000, 56
    base, amp = 42, 4
    f = lambda x: base + amp * math.sin(x / 1000 * 2 * math.pi * 6)
    line = "M" + " L".join(f"{x} {f(x):.1f}" for x in range(0, W + 1, 10))
    drive = "M" + " L".join(f"{x} {f(x):.1f}" for x in range(1120, -121, -10))
    CW = 92
    m = meta()["sizes"]["car-sm"]
    ch = m["h"] * CW / m["w"]
    img = f'<image href="{uri("car-sm.webp")}" x="{-CW / 2:.1f}" y="{-ch + 4:.1f}" width="{CW}" height="{ch:.1f}"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="presentation">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#cdb8f5" stop-opacity="0"/><stop offset=".2" stop-color="#cdb8f5"/><stop offset=".5" stop-color="#f7b9d0"/><stop offset=".8" stop-color="#a9dcc4"/><stop offset="1" stop-color="#a9dcc4" stop-opacity="0"/></linearGradient>
<linearGradient id="t" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<style>.fl{{animation:fl 1.4s linear infinite}}@keyframes fl{{to{{stroke-dashoffset:-48}}}}</style>
<path d="{line}" fill="none" stroke="url(#g)" stroke-width="3" stroke-linecap="round" stroke-dasharray="14 10" class="fl"/>
<g><animateMotion dur="9s" repeatCount="indefinite" rotate="auto-reverse" path="{drive}"/>
<rect x="{CW / 2 - 4:.0f}" y="-18" width="70" height="10" rx="5" fill="url(#t)"/>{img}</g>
</svg>'''


# ------------------------------------------------------------------ footer
def footer():
    W, H = 1000, 230
    rnd = random.Random(5)
    CW, road_y, wheel_line = 300, 150, 196
    car, ch = car_markup(CW, spin_dur=0.32)
    car_y = wheel_line - ch + 2
    T = 9.0
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="A McLaren F1 car crossing the finish line">']
    s.append(f'''<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e4d6ff"/><stop offset=".5" stop-color="#ffd9e8"/><stop offset="1" stop-color="#fff0d6"/></linearGradient>
<linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9a9dc"/><stop offset="1" stop-color="#a392c9"/></linearGradient>
<linearGradient id="tr" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<pattern id="chk" width="12" height="12" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#4f3f7e"/><rect x="6" y="6" width="6" height="6" fill="#4f3f7e"/><rect x="6" width="6" height="6" fill="#fff"/><rect y="6" width="6" height="6" fill="#fff"/></pattern>
<clipPath id="rc"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<filter id="shadow" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="soft"><feGaussianBlur stdDeviation="14"/></filter>
</defs>
<style>
.dash{{animation:ds .55s linear infinite}}@keyframes ds{{to{{transform:translateX(100px)}}}}
.cf{{opacity:0;animation:cf {T}s ease-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes cf{{0%,24%{{opacity:0;transform:translate(0,0) rotate(0)}}26%{{opacity:1}}56%{{opacity:0;transform:translate(var(--dx),var(--dy)) rotate(var(--r))}}100%{{opacity:0}}}}
.msg{{opacity:0;animation:msg {T}s ease-in-out infinite}}
@keyframes msg{{0%,28%{{opacity:0;transform:translateY(10px)}}38%,82%{{opacity:1;transform:none}}92%,100%{{opacity:0;transform:translateY(-6px)}}}}
.fa{{animation:fa 9s ease-in-out infinite}}@keyframes fa{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(18px,-12px)}}}}
</style>
<g clip-path="url(#rc)"><rect width="{W}" height="{H}" fill="url(#bg)"/>
<g class="fa"><circle cx="150" cy="40" r="110" fill="#cdb8f5" opacity=".5" filter="url(#soft)"/></g>
<g class="fa" style="animation-delay:-4s"><circle cx="860" cy="30" r="120" fill="#f7b9d0" opacity=".5" filter="url(#soft)"/></g>''')
    s.append(f'<g class="msg"><text x="500" y="62" text-anchor="middle" font-family="{SANS}" font-size="13" letter-spacing="6" fill="{SOFT}" font-weight="600">CHEQUERED FLAG</text>'
             f'<text x="500" y="104" text-anchor="middle" font-family="{SANS}" font-size="34" font-weight="800" fill="{INK}">Thanks for stopping by</text></g>')
    s.append(f'<rect y="{road_y}" width="{W}" height="{H - road_y}" fill="url(#road)"/>')
    s.append('<g class="dash">' + "".join(f'<rect x="{-100 + i * 100}" y="{road_y + 40}" width="50" height="4" rx="2" fill="#fff" opacity=".85"/>' for i in range(13)) + '</g>')
    s.append(f'<rect x="478" y="{road_y}" width="24" height="{H - road_y}" fill="url(#chk)"/>')
    s.append(f'<rect x="0" y="{road_y}" width="{W}" height="6" fill="#fff" opacity=".55"/>')
    cols = ["#f7b9d0", "#cdb8f5", "#a9dcc4", "#f8d49b", "#ffffff", "#c9e7f5"]
    for i in range(34):
        dx, dy, r = rnd.uniform(-260, 260), rnd.uniform(-130, 40), rnd.uniform(-300, 300)
        x = 490 + rnd.uniform(-14, 14)
        s.append(f'<rect class="cf" style="--dx:{dx:.0f}px;--dy:{dy:.0f}px;--r:{r:.0f}deg;animation-delay:{rnd.uniform(0, .5):.2f}s" x="{x:.0f}" y="{road_y - 6}" width="{rnd.choice([6, 8, 10])}" height="{rnd.choice([4, 6])}" rx="1.5" fill="{rnd.choice(cols)}"/>')
    # one pass per loop; crosses the line at ~28% of the cycle
    s.append(f'<g transform="translate(0 {car_y:.1f})"><g>'
             f'<animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" calcMode="spline" '
             f'keyTimes="0;0.5;1" values="1100 0;-420 0;-420 0" keySplines="0 0 1 1;0 0 1 1"/>'
             f'<ellipse cx="{CW / 2:.0f}" cy="{ch - 2:.0f}" rx="{CW * .47:.0f}" ry="6" fill="#4f3f7e" opacity=".28" filter="url(#shadow)"/>'
             f'<rect x="{CW - 6}" y="{ch * .3:.0f}" width="150" height="{ch * .5:.0f}" rx="24" fill="url(#tr)"/>'
             '<g><animateTransform attributeName="transform" type="translate" dur="0.14s" repeatCount="indefinite" values="0 0;0 -1;0 0;0 .7;0 0"/>'
             + car + '</g></g></g>')
    s.append('</g></svg>')
    return "\n".join(s)
