#!/usr/bin/env python3
"""Renders the real F1 car (assets/car/*.webp) as looping GIFs for places that cannot show the animated SVGs.

  python scripts/make_gif.py            -> assets/car/car-drive.gif   (car on a pastel road, 800x240)
                                           assets/car/car-spin.gif    (car only, transparent background)

Every layer scrolls an exact whole number of its own period per loop, so the loop is seamless.
Needs only Pillow and numpy. Car photo credit: see assets/car/CREDITS.md.
"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
CAR = os.path.join(HERE, "..", "assets", "car")
S = 2                                    # supersample factor, then Lanczos down for smooth edges


def load():
    meta = json.load(open(os.path.join(CAR, "car.json")))
    car = Image.open(os.path.join(CAR, "car.webp")).convert("RGBA")
    wheels = {k: Image.open(os.path.join(CAR, f"wheel-{k}.webp")).convert("RGBA") for k in ("front", "rear")}
    return meta, car, wheels


def car_frame(car, wheels, meta, width, spin_deg):
    """The car at `width` px with both wheel discs rotated by spin_deg. Returns (image, wheel_bottom_y)."""
    k = width / car.size[0]
    base = car.resize((width, round(car.size[1] * k)), Image.LANCZOS)
    for name, w in meta["wheels"].items():
        px = max(2, round(w["px"] * k))
        d = wheels[name].resize((px, px), Image.LANCZOS).rotate(spin_deg, resample=Image.BICUBIC)
        base.alpha_composite(d, (round(w["cx"] * k - px / 2), round(w["cy"] * k - px / 2)))
    return base


def gradient(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (xx / w) * 0.5 + (yy / h) * 0.5
    stops = [(0.0, (228, 214, 255)), (0.5, (255, 217, 232)), (1.0, (255, 240, 214))]
    out = np.zeros((h, w, 3), np.float32)
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1)
        f = ((t - t0) / (t1 - t0))[m][:, None]
        out[m] = np.array(c0) * (1 - f) + np.array(c1) * f
    return Image.fromarray(out.astype(np.uint8), "RGB").convert("RGBA")


def palette(frames, n=255):
    """One shared palette from a mosaic of sample frames (keeps the GIF small and flicker-free)."""
    pick = [frames[i] for i in range(0, len(frames), max(1, len(frames) // 6))][:6]
    w, h = pick[0].size
    mosaic = Image.new("RGB", (w, h * len(pick)))
    for i, f in enumerate(pick):
        mosaic.paste(f.convert("RGB"), (0, i * h))
    return mosaic.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)


# ------------------------------------------------------------------ scene GIF
def drive(meta, car, wheels, out, W=800, H=240, N=50, delay=40):
    rnd = random.Random(3)
    road_y = 158
    CW = 430
    car_x = 175
    # static layers (drawn once at 2x)
    bg = gradient(W * S, H * S)
    blobs = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blobs)
    for x, y, r, c in [(110, 50, 95, (205, 184, 245, 150)), (690, 40, 110, (247, 185, 208, 150)), (520, 150, 80, (255, 255, 255, 110))]:
        bd.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    bg.alpha_composite(blobs.filter(ImageFilter.GaussianBlur(28 * S)))
    stars = [(rnd.uniform(20, W - 20), rnd.uniform(10, 105), rnd.choice([2, 3, 4]), rnd.random()) for _ in range(16)]
    road = Image.new("RGBA", (W * S, (H - road_y) * S))
    rd = np.linspace(0, 1, road.size[1])[:, None, None]
    road = Image.fromarray((np.array([185, 169, 220]) * (1 - rd) + np.array([163, 146, 201]) * rd).astype(np.uint8).repeat(road.size[0], 1), "RGB").convert("RGBA")
    shadow = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sw = CW * 0.47
    sd.ellipse([(car_x + CW / 2 - sw) * S, 201 * S, (car_x + CW / 2 + sw) * S, 213 * S], fill=(79, 63, 126, 95))
    shadow = shadow.filter(ImageFilter.GaussianBlur(4 * S))
    lines = [(rnd.uniform(168, 232), rnd.uniform(60, 190), rnd.uniform(0, 800), rnd.choice([1.5, 2, 2.5]), rnd.choice([1, 2])) for _ in range(14)]

    def wave(layer, y0, amp, period, shift, phase, color):
        d = ImageDraw.Draw(layer)
        pts = [(x * S, (y0 + amp * math.sin(2 * math.pi * (x - shift) / period + phase)) * S) for x in range(-8, W + 9, 4)]
        d.polygon(pts + [((W + 8) * S, H * S), (-8 * S, H * S)], fill=color)

    frames = []
    for f in range(N):
        t = f / N
        im = bg.copy()
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        for x, y, r, ph in stars:                                   # twinkle: one full cycle per loop
            a = int(255 * (0.25 + 0.75 * (0.5 + 0.5 * math.sin(2 * math.pi * (t + ph)))))
            od.polygon([(x * S, (y - r) * S), ((x + r * .3) * S, (y - r * .3) * S), ((x + r) * S, y * S), ((x + r * .3) * S, (y + r * .3) * S),
                        (x * S, (y + r) * S), ((x - r * .3) * S, (y + r * .3) * S), ((x - r) * S, y * S), ((x - r * .3) * S, (y - r * .3) * S)], fill=(255, 255, 255, a))
        im.alpha_composite(ov)
        for y0, amp, per, ph, col in ((118, 9, 200, 0.0, (205, 184, 245, 215)), (134, 8, 300, 1.6, (247, 185, 208, 215)), (147, 6, 400, 3.2, (255, 255, 255, 235))):
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            wave(lay, y0, amp, per, per * t, ph, col)               # one period per loop => seamless
            im.alpha_composite(lay)
        r2 = road.copy()
        im.alpha_composite(r2, (0, road_y * S))
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        sh = 600 * t                                               # 10 kerb periods, 6 dash periods
        for i in range(-2, W // 30 + 3):
            x = i * 30 + sh % 60
            od.rectangle([x * S, road_y * S, (x + 30) * S, (road_y + 8) * S], fill=(247, 185, 208, 255) if i % 2 == 0 else (255, 255, 255, 255))
        for i in range(-2, W // 100 + 3):
            x = i * 100 + sh % 100
            od.rounded_rectangle([x * S, (road_y + 46) * S, (x + 50) * S, (road_y + 50) * S], radius=2 * S, fill=(255, 255, 255, 215))
        im.alpha_composite(ov)
        im.alpha_composite(shadow)
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        for y, ln, x0, hgt, k in lines:                            # speed lines rush rightwards
            L = ln * 1.6
            x = -L + (x0 + t * k * (W + L)) % (W + L)
            od.rounded_rectangle([x * S, y * S, (x + L) * S, (y + hgt) * S], radius=S, fill=(255, 255, 255, 150))
        im.alpha_composite(ov)
        bob = math.sin(2 * math.pi * 8 * t) * 0.9
        cf = car_frame(car, wheels, meta, CW * S, -360 * 4 * t)     # 4 wheel revolutions per loop
        im.alpha_composite(cf, (car_x * S, round((204 - cf.size[1] / S + bob) * S)))
        frames.append(im.resize((W, H), Image.LANCZOS).convert("RGB"))
    pal = palette(frames)
    pf = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    pf[0].save(out, save_all=True, append_images=pf[1:], duration=delay, loop=0, optimize=False, disposal=1)
    print(out, os.path.getsize(out) // 1024, "KB,", N, "frames")


# ------------------------------------------------------------------ transparent car-only GIF
def spin(meta, car, wheels, out, CW=460, N=24, delay=40):
    pad = 10
    frames = []
    for f in range(N):
        t = f / N
        cf = car_frame(car, wheels, meta, CW * S, -360 * 2 * t)   # 2 revolutions per loop
        canvas = Image.new("RGBA", (cf.size[0] + pad * 2 * S, cf.size[1] + pad * 2 * S), (0, 0, 0, 0))
        canvas.alpha_composite(cf, (pad * S, pad * S))
        frames.append(canvas.resize((canvas.size[0] // S, canvas.size[1] // S), Image.LANCZOS))
    flat = []
    for fr in frames:                                              # palette must ignore the transparent area
        bg = Image.new("RGB", fr.size, (255, 255, 255))
        bg.paste(fr.convert("RGB"), mask=fr.getchannel("A").point(lambda a: 255 if a > 127 else 0))
        flat.append(bg)
    pal = palette(flat)
    pf = []
    for fr, fl in zip(frames, flat):
        p = fl.quantize(palette=pal, dither=Image.Dither.NONE)
        p.paste(255, mask=fr.getchannel("A").point(lambda a: 255 if a <= 127 else 0))
        pf.append(p)
    pf[0].save(out, save_all=True, append_images=pf[1:], duration=delay, loop=0, transparency=255, disposal=2, optimize=False)
    print(out, os.path.getsize(out) // 1024, "KB,", N, "frames,", frames[0].size)


if __name__ == "__main__":
    meta, car, wheels = load()
    drive(meta, car, wheels, os.path.join(CAR, "car-drive.gif"))
    spin(meta, car, wheels, os.path.join(CAR, "car-spin.gif"))
