#!/usr/bin/env python3
"""Regenerate ScreenMagnifier.app's icon: draws a magnifier-glass PNG with
Pillow, then builds Contents/Resources/ScreenMagnifier.icns via `sips`/`iconutil`.

Usage (from the repo root, with the .venv set up):
    ./.venv/bin/python make-icon.py

Requires: Pillow (in requirements.txt) and macOS command-line tools
(`sips`, `iconutil`). The icon is rendered at 4x supersampling then downscaled
for smooth, anti-aliased edges. Colored rounded-square background so it stays
visible on both light and dark Docks.
"""
import os
import shutil
import subprocess
import tempfile
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.abspath(__file__))
ICNS = os.path.join(REPO, "ScreenMagnifier.app", "Contents", "Resources", "ScreenMagnifier.icns")

S = 1024          # final master size
SS = 4            # supersample factor
N = S * SS


def sc(v):
    return int(v * SS)


def draw_master():
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded-square background, subtle vertical blue gradient.
    margin, radius = 40, 220
    top, bot = (90, 160, 225), (44, 100, 180)
    grad = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(N):
        t = y / (N - 1)
        gd.line([(0, y), (N, y)], fill=(
            int(top[0] + (bot[0] - top[0]) * t),
            int(top[1] + (bot[1] - top[1]) * t),
            int(top[2] + (bot[2] - top[2]) * t), 255))
    mask = Image.new("L", (N, N), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [sc(margin), sc(margin), N - sc(margin), N - sc(margin)],
        radius=sc(radius), fill=255)
    img.paste(grad, (0, 0), mask)

    white = (248, 248, 255, 255)

    # Handle first, so the lens ring overlaps its top end.
    hx0, hy0, hx1, hy1, hw = 600, 600, 790, 790, 120
    d.line([(sc(hx0), sc(hy0)), (sc(hx1), sc(hy1))], fill=white, width=sc(hw))
    for cx, cy in ((hx0, hy0), (hx1, hy1)):
        rr = hw / 2
        d.ellipse([sc(cx - rr), sc(cy - rr), sc(cx + rr), sc(cy + rr)], fill=white)

    # Lens: white ring, translucent glass, highlight streak.
    cx, cy, r_out, ring = 430, 400, 250, 72
    r_in = r_out - ring
    d.ellipse([sc(cx - r_out), sc(cy - r_out), sc(cx + r_out), sc(cy + r_out)], fill=white)
    d.ellipse([sc(cx - r_in), sc(cy - r_in), sc(cx + r_in), sc(cy + r_in)],
              fill=(220, 238, 255, 235))
    d.ellipse([sc(cx - r_in + 40), sc(cy - r_in + 40),
               sc(cx - r_in + 130), sc(cy - r_in + 210)], fill=(255, 255, 255, 150))

    return img.resize((S, S), Image.LANCZOS)


def build_icns(master):
    tmp = tempfile.mkdtemp()
    try:
        src = os.path.join(tmp, "icon_1024.png")
        master.save(src)
        iconset = os.path.join(tmp, "Magnifier.iconset")
        os.makedirs(iconset)
        for sz in (16, 32, 128, 256, 512):
            for name, px in ((f"icon_{sz}x{sz}.png", sz), (f"icon_{sz}x{sz}@2x.png", sz * 2)):
                subprocess.run(["sips", "-z", str(px), str(px), src,
                                "--out", os.path.join(iconset, name)],
                               check=True, stdout=subprocess.DEVNULL)
        os.makedirs(os.path.dirname(ICNS), exist_ok=True)
        subprocess.run(["iconutil", "-c", "icns", iconset, "-o", ICNS], check=True)
        print("wrote", ICNS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    build_icns(draw_master())
