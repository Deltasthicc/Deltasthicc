#!/usr/bin/env python3
"""Turns a side-on F1 photo into the animated-car assets used by the profile.

Source photo: "McLaren MP4-26" by Gil Abrantes, CC BY 2.0
  https://commons.wikimedia.org/wiki/File:McLaren_MP4-26.jpg
This script cuts out the car (rembg), cleans the edge, exports it at two sizes, and cuts the two
wheel discs out separately so they can be rotated on top of the static car.

  pip install "rembg[cpu]" pillow numpy
  python scripts/make_car.py --src McLaren_MP4-26.jpg --out assets/car
  (or pass --cutout an_existing_rembg_output.png to skip the background-removal step)
"""
import argparse, json, os
import numpy as np
from PIL import Image, ImageFilter

# Hub centres and disc radius, measured on the cropped cut-out (1991x606 px).
HUBS = {"front": (420, 437), "rear": (1768, 474)}
DISC_R = 118


def cut(src):
    from rembg import remove, new_session
    im = Image.open(src).convert("RGB")
    im.thumbnail((2200, 2200), Image.LANCZOS)
    return remove(im, session=new_session("isnet-general-use"), alpha_matting=True,
                  alpha_matting_foreground_threshold=240, alpha_matting_background_threshold=15,
                  alpha_matting_erode_size=8)


def clean(rgba):
    """Drop thin stray fragments (cables, matting fuzz) and firm up the edge."""
    a = np.asarray(rgba.getchannel("A"), dtype=np.float32) / 255
    core = Image.fromarray(((a > 0.5) * 255).astype(np.uint8))
    core = core.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9))   # opening
    keep = core.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(1.5))
    a = a * (np.asarray(keep, dtype=np.float32) / 255)
    a = np.clip((a - 0.12) / 0.7, 0, 1)
    a = a * a * (3 - 2 * a)
    out = rgba.copy()
    out.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    return out


def disc(car, cx, cy, r, blur_deg=5):
    """Round crop of one wheel with a feathered rim, lightly motion-blurred by averaging rotations."""
    box = (cx - r, cy - r, cx + r, cy + r)
    tile = car.crop(box)
    yy, xx = np.mgrid[0:2 * r, 0:2 * r]
    d = np.hypot(xx - r + 0.5, yy - r + 0.5)
    feather = np.clip((r - d) / 12, 0, 1)
    acc = np.zeros((2 * r, 2 * r, 4), np.float32)
    angles = (-blur_deg, 0, blur_deg)
    for ang in angles:
        t = np.asarray(tile.rotate(ang, resample=Image.BICUBIC), dtype=np.float32)
        pm = t[..., :3] * (t[..., 3:4] / 255)          # premultiply so transparent pixels don't tint
        acc[..., :3] += pm
        acc[..., 3] += t[..., 3]
    acc /= len(angles)
    rgb = np.where(acc[..., 3:4] > 0, acc[..., :3] / np.maximum(acc[..., 3:4] / 255, 1e-4), 0)
    out = np.dstack([np.clip(rgb, 0, 255), acc[..., 3] * feather]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def save(im, path, q=88):
    im.save(path, "WEBP", quality=q, method=6, alpha_quality=100)
    print(f"{path}  {im.size[0]}x{im.size[1]}  {os.path.getsize(path) // 1024} KB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src")
    ap.add_argument("--cutout")
    ap.add_argument("--out", default="assets/car")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    raw = Image.open(a.cutout).convert("RGBA") if a.cutout else cut(a.src)
    bbox = raw.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    car = clean(raw.crop(bbox))
    print("cropped", car.size)

    meta = {"source": "Gil Abrantes, 'McLaren MP4-26', CC BY 2.0", "sizes": {}}
    for name, width in (("car", 1000), ("car-sm", 380)):
        s = width / car.size[0]
        im = car.resize((width, round(car.size[1] * s)), Image.LANCZOS)
        save(im, os.path.join(a.out, name + ".webp"))
        meta["sizes"][name] = {"w": im.size[0], "h": im.size[1], "scale": s}
    s = 1000 / car.size[0]
    meta["wheels"] = {}
    for name, (cx, cy) in HUBS.items():
        d = disc(car, cx, cy, DISC_R)
        d = d.resize((round(d.size[0] * s),) * 2, Image.LANCZOS)
        save(d, os.path.join(a.out, f"wheel-{name}.webp"), q=90)
        meta["wheels"][name] = {"cx": cx * s, "cy": cy * s, "r": DISC_R * s, "px": d.size[0]}
    with open(os.path.join(a.out, "car.json"), "w") as f:
        json.dump(meta, f, indent=1)


if __name__ == "__main__":
    main()
