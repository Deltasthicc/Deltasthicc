#!/usr/bin/env python3
"""Contribution Grand Prix: turns a year of GitHub contributions into an animated F1 circuit.

Every one of the last 364 days becomes a tiny segment of the track, coloured by that day's
activity. A car laps the circuit, sectors get timed, and months become a tyre strategy bar.

Usage:
  GITHUB_TOKEN=... python scripts/grand_prix.py --user Deltasthicc --out assets/grand-prix.svg
  python scripts/grand_prix.py --sample --out preview.svg      (synthetic data, for previews)
  python scripts/grand_prix.py --json days.json --out x.svg    ([["YYYY-MM-DD", count], ...])
"""
import argparse, datetime as dt, json, math, os, random, sys, urllib.request

# ---------------------------------------------------------------- data
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch_days(user, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": user}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "grand-prix-profile"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def sample_days():
    random.seed(7)
    end = dt.date.today()
    out = []
    for i in range(364):
        d = end - dt.timedelta(days=363 - i)
        burst = 1.0 + 2.5 * math.exp(-((i - 280) ** 2) / 900) + 2 * math.exp(-((i - 340) ** 2) / 500)
        c = int(max(0, random.gauss(2.2, 2.6)) * burst) if random.random() < 0.55 else 0
        out.append((d.isoformat(), c))
    return out


def prepare(days):
    days = sorted(days)[-364:]
    while len(days) < 364:  # pad the start if the account is young
        first = dt.date.fromisoformat(days[0][0])
        days.insert(0, ((first - dt.timedelta(days=1)).isoformat(), 0))
    counts = [c for _, c in days]
    nz = sorted(c for c in counts if c)
    def q(p):
        return nz[min(len(nz) - 1, int(len(nz) * p))] if nz else 1
    t1, t2, t3 = q(0.25), q(0.5), q(0.8)
    def level(c):
        return 0 if c == 0 else 1 if c <= t1 else 2 if c <= t2 else 3 if c <= t3 else 4
    return days, [level(c) for c in counts]


# ---------------------------------------------------------------- geometry
CTRL = [(70, 270), (36, 190), (62, 100), (140, 62), (215, 92), (262, 150), (330, 112), (385, 52),
        (470, 58), (512, 128), (482, 205), (410, 226), (372, 282), (290, 318), (200, 300), (140, 322)]


def catmull(points, per=60):
    n, out = len(points), []
    for i in range(n):
        p0, p1, p2, p3 = (points[(i + k) % n] for k in (-1, 0, 1, 2))
        for s in range(per):
            t = s / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    return out


def resample(poly, n):
    pts = poly + [poly[0]]
    dist = [0.0]
    for a, b in zip(pts, pts[1:]):
        dist.append(dist[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total, out, j = dist[-1], [], 0
    for k in range(n + 1):
        target = total * k / n
        while dist[j + 1] < target:
            j += 1
        f = (target - dist[j]) / (dist[j + 1] - dist[j] or 1)
        out.append((pts[j][0] + f * (pts[j + 1][0] - pts[j][0]), pts[j][1] + f * (pts[j + 1][1] - pts[j][1])))
    return out, total


# ---------------------------------------------------------------- render
LEVEL = ["#e6e0f3", "#d9c9f7", "#bda0f0", "#f4a3c4", "#e5709f"]
INK, SOFT = "#4f3f7e", "#8a7bb0"
MONTHS = "JFMAMJJASOND"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def render(user, days, levels):
    N = 364
    pts, track_len = resample(catmull(CTRL), N)
    ox, oy = 28, 52  # track offset inside the card
    P = [(x + ox, y + oy) for x, y in pts]
    counts = [c for _, c in days]
    total, best = sum(counts), max(counts)
    best_day = days[counts.index(best)][0]
    active = sum(1 for c in counts if c)
    streak, i = 0, len(counts) - 1
    if counts[i] == 0:  # today may still be empty
        i -= 1
    while i >= 0 and counts[i] > 0:
        streak += 1
        i -= 1

    dur = 18
    d_path = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in P[:-1]) + " Z"

    svg = []
    a = svg.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="430" viewBox="0 0 900 430" role="img" '
      f'aria-label="Contribution Grand Prix for {user}: {total} contributions in the last year">')
    a(f'''<defs>
<linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6f1ff"/><stop offset=".55" stop-color="#fff0f6"/><stop offset="1" stop-color="#eefaf4"/></linearGradient>
<clipPath id="cc"><rect width="900" height="430" rx="26"/></clipPath>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<pattern id="chk" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="3" height="3" fill="#4f3f7e"/><rect x="3" y="3" width="3" height="3" fill="#4f3f7e"/></pattern>
</defs>
<style>
text{{font-family:'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace}}
.h{{font-family:'Segoe UI',system-ui,-apple-system,Arial,sans-serif}}
.pop{{animation:pop .9s cubic-bezier(.2,.9,.3,1.2) both;transform-box:fill-box;transform-origin:left center}}
@keyframes pop{{from{{transform:scaleX(0);opacity:0}}to{{transform:scaleX(1);opacity:1}}}}
.rad{{opacity:0;animation:rad {dur}s linear infinite}}
@keyframes rad{{0%{{opacity:0}}3%,30%{{opacity:1}}33%,100%{{opacity:0}}}}
.drs{{animation:drs 2.4s ease-in-out infinite}}@keyframes drs{{0%,100%{{opacity:.25}}50%{{opacity:.9}}}}
</style>
<g clip-path="url(#cc)"><rect width="900" height="430" fill="url(#card)"/>
<circle cx="90" cy="400" r="120" fill="#e4d6ff" opacity=".5"/><circle cx="820" cy="30" r="110" fill="#ffd6e6" opacity=".5"/>''')

    # title
    a(f'<text class="h" x="32" y="40" font-size="20" font-weight="700" fill="{INK}" letter-spacing="3">CONTRIBUTION GRAND PRIX</text>')
    a(f'<text x="32" y="58" font-size="11" fill="{SOFT}" letter-spacing="2">SEASON: LAST 52 WEEKS  |  DRIVER: @{esc(user)}</text>')
    # start lights: they light one by one, then all go out together ("lights out and away we go")
    for i in range(5):
        cx = 500 + i * 20
        on = 0.01 + i * 0.012
        a(f'<circle cx="{cx}" cy="36" r="7" fill="#f4a3c4" opacity=".25"/>'
          f'<circle cx="{cx}" cy="36" r="7" fill="#e5709f" opacity="0"><animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" '
          f'keyTimes="0;{on:.3f};0.09;1" values="0;1;0;0" calcMode="discrete"/>'
          f'</circle>')
    # track bed
    a(f'<path d="{d_path}" fill="none" stroke="#fff" stroke-width="20" stroke-linejoin="round" opacity=".95"/>')
    a(f'<path d="{d_path}" fill="none" stroke="#d6c9ee" stroke-width="16" stroke-linejoin="round" opacity=".6"/>')
    # day segments
    for i in range(N):
        (x1, y1), (x2, y2) = P[i], P[i + 1]
        date, c = days[i]
        a(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{LEVEL[levels[i]]}" stroke-width="10" '
          f'stroke-linecap="butt"><title>{date}: {c} contribution{"s" if c != 1 else ""}</title></line>')
    # start / finish
    (sx, sy), (nx, ny) = P[0], P[3]
    ang = math.degrees(math.atan2(ny - sy, nx - sx))
    a(f'<g transform="translate({sx:.1f} {sy:.1f}) rotate({ang:.1f})"><rect x="-2" y="-9" width="4" height="18" fill="url(#chk)"/></g>')
    # sectors
    sec = [sum(counts[0:121]), sum(counts[121:242]), sum(counts[242:364])]
    bestsec = sec.index(max(sec))
    cx0 = sum(x for x, _ in P) / len(P); cy0 = sum(y for _, y in P) / len(P)
    for k in range(3):
        i = int(N * (k + 0.5) / 3)
        x, y = P[i]
        vx, vy = x - cx0, y - cy0
        m = math.hypot(vx, vy) or 1
        lx, ly = x + vx / m * 34, y + vy / m * 24
        col = "#c9a6ff" if k == bestsec else "#bfe8d6"
        a(f'<g><rect x="{lx - 33:.1f}" y="{ly - 11:.1f}" width="66" height="22" rx="11" fill="{col}" opacity=".9"/>'
          f'<text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle" font-size="11" fill="{INK}" font-weight="700">S{k + 1} {sec[k]}</text></g>')
    # DRS glow + car (with trail)
    a(f'<path class="drs" d="{d_path}" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="40 {track_len:.0f}" opacity=".6" filter="url(#glow)">'
      f'<animate attributeName="stroke-dashoffset" from="0" to="-{track_len + 40:.0f}" dur="{dur}s" repeatCount="indefinite"/></path>')
    for lag, r, op in ((0.55, 3, .25), (0.35, 3.6, .45), (0.18, 4.2, .7)):
        a(f'<circle r="{r}" fill="#f19cbc" opacity="{op}"><animateMotion dur="{dur}s" repeatCount="indefinite" begin="-{lag}s" path="{d_path}"/></circle>')
    a(f'<g><animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto" path="{d_path}"/>'
      '<rect x="-9" y="-3.2" width="18" height="6.4" rx="3" fill="#e5709f" stroke="#fff" stroke-width="1.2"/>'
      '<rect x="-10.5" y="-5.5" width="3" height="11" rx="1" fill="#4f3f7e"/><rect x="6" y="-4.6" width="2.6" height="9.2" rx="1" fill="#4f3f7e"/>'
      '<circle cx="-1" cy="0" r="2" fill="#fff"/></g>')

    # legend under track
    lx = 36
    a(f'<text x="{lx}" y="412" font-size="10" fill="{SOFT}">QUIET</text>')
    for i, c in enumerate(LEVEL):
        a(f'<rect x="{lx + 40 + i * 16}" y="403" width="12" height="12" rx="3" fill="{c}"/>')
    a(f'<text x="{lx + 40 + 5 * 16 + 4}" y="412" font-size="10" fill="{SOFT}">PUSH</text>')
    a(f'<text x="{lx + 190}" y="412" font-size="10" fill="{SOFT}">Each segment is one day. Hover for details.</text>')

    # telemetry panel
    px = 600
    a(f'<rect x="{px}" y="76" width="276" height="338" rx="18" fill="#fff" opacity=".7"/>')
    stats = [("LAPS (COMMITS)", f"{total}"), ("FASTEST DAY", f"{best}"), ("ACTIVE DAYS", f"{active}"), ("CURRENT STINT", f"{streak}d")]
    for i, (lab, val) in enumerate(stats):
        x, y = px + 18 + (i % 2) * 130, 104 + (i // 2) * 62
        a(f'<text x="{x}" y="{y}" font-size="9" fill="{SOFT}" letter-spacing="1">{lab}</text>'
          f'<text class="h" x="{x}" y="{y + 30}" font-size="30" font-weight="700" fill="{INK}">{val}</text>')
    a(f'<text x="{px + 18}" y="236" font-size="9" fill="{SOFT}" letter-spacing="1">FASTEST DAY SET ON {best_day}</text>')

    # tyre strategy by month
    end = dt.date.fromisoformat(days[-1][0])
    buckets = {}
    for (d, c) in days:
        dd = dt.date.fromisoformat(d)
        buckets[(dd.year, dd.month)] = buckets.get((dd.year, dd.month), 0) + c
    keys = sorted(buckets)[-12:]
    mx = max(buckets[k] for k in keys) or 1
    a(f'<text x="{px + 18}" y="266" font-size="9" fill="{SOFT}" letter-spacing="1">TYRE STRATEGY (MONTH BY MONTH)</text>')
    bw = 240 / len(keys)
    for i, k in enumerate(keys):
        r = buckets[k] / mx
        col, letter = (("#f4a3c4", "S") if r > 0.55 else ("#fbe3a1", "M") if r > 0.2 else ("#ece8f5", "H"))
        if buckets[k] == 0:
            col, letter = "#f1eef7", "-"
        x = px + 18 + i * bw
        a(f'<g><rect class="pop" style="animation-delay:{i * 0.07:.2f}s" x="{x:.1f}" y="274" width="{bw - 3:.1f}" height="30" rx="7" fill="{col}" stroke="#d6c9ee" stroke-width="1"/>'
          f'<text x="{x + (bw - 3) / 2:.1f}" y="293" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}">{letter}</text>'
          f'<text x="{x + (bw - 3) / 2:.1f}" y="320" text-anchor="middle" font-size="9" fill="{SOFT}">{MONTHS[k[1] - 1]}</text>'
          f'<title>{k[0]}-{k[1]:02d}: {buckets[k]} contributions</title></g>')
    a(f'<text x="{px + 18}" y="342" font-size="9" fill="{SOFT}">S = soft (push)  M = medium  H = hard (chill)</text>')

    # race radio
    radio = ["RADIO: LIGHTS OUT AND AWAY WE GO", "RADIO: PUSH PUSH PUSH, YOU ARE PURPLE IN S%d" % (bestsec + 1), "RADIO: BOX BOX, SWITCHING TO SOFTS"]
    for i, msg in enumerate(radio):
        a(f'<text class="rad" style="animation-delay:{i * dur / 3:.1f}s" x="{px + 18}" y="380" font-size="10.5" fill="{INK}" font-weight="700">{msg}</text>')
    a(f'<text x="{px + 18}" y="400" font-size="9" fill="{SOFT}">Updated {end.isoformat()} by GitHub Actions</text>')
    a('</g></svg>')
    return "\n".join(svg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GH_USER", "Deltasthicc"))
    ap.add_argument("--out", default="assets/grand-prix.svg")
    ap.add_argument("--sample", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.sample:
        days = sample_days()
    elif a.json:
        with open(a.json, encoding="utf-8") as f:
            days = [tuple(x) for x in json.load(f)]
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("Set GITHUB_TOKEN (in Actions it is provided automatically).")
        days = fetch_days(a.user, token)
    days, levels = prepare(days)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(render(a.user, days, levels))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
