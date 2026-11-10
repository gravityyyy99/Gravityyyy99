#!/usr/bin/env python3
"""Turn a front-facing portrait (plain coloured background) into data/portrait.txt for the hero card.
Usage: python scripts/make_ascii.py photo.png [cols] [x0,y0,x1,y1 crop box]"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps

src = sys.argv[1]
cols = int(sys.argv[2]) if len(sys.argv) > 2 else 76
box = tuple(int(v) for v in sys.argv[3].split(",")) if len(sys.argv) > 3 else None
CELL = 0.62  # char width / char height as drawn by render_cards.py
DARKMODE = os.environ.get("MODE") == "dark"  # busy photo: no cut-out, dense = bright, for a dark panel
RAMP = " .,:;-=+*#%@"  # sparse -> dense; dense = dark (ink on the light hero panel)

im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
if box:
    im = im.crop(box)
rgb = np.asarray(im).astype(float)
# background = median colour of the top strip; subject = anything far from it
bg = np.median(rgb[: max(8, rgb.shape[0] // 12)].reshape(-1, 3), axis=0)
dist = np.sqrt(((rgb - bg) ** 2).sum(2))
mask = Image.fromarray((np.ones(dist.shape) * 255).astype('uint8')) if DARKMODE else Image.fromarray((dist > 38).astype("uint8") * 255).filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.GaussianBlur(1.5))
mask = np.asarray(mask) > 128

import cv2
gray = Image.fromarray(cv2.createCLAHE(clipLimit=3.0, tileGridSize=(6, 6)).apply(np.asarray(ImageOps.autocontrast(im.convert('L'), cutoff=1))))
g = np.asarray(gray).astype(float) / 255
sub = g[mask]
lo, hi = np.percentile(sub, 3), np.percentile(sub, 97)
g = np.clip((g - lo) / (hi - lo + 1e-6), 0, 1) ** 2.0  # darken mids so facial features carry density

rows = round(cols * (im.height / im.width) * CELL)
gs = np.asarray(Image.fromarray((g * 255).astype("uint8")).resize((cols, rows), Image.LANCZOS)).astype(float) / 255
ms = np.asarray(Image.fromarray((mask * 255).astype("uint8")).resize((cols, rows), Image.LANCZOS)) > 110
lines = []
for y in range(rows):
    line = "".join(RAMP[max(0 if DARKMODE else 1, min(len(RAMP) - 1, int((gs[y, x] if DARKMODE else 1 - gs[y, x]) * len(RAMP))))] if ms[y, x] else " " for x in range(cols))
    lines.append(line.rstrip())
out = os.environ.get("OUT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "portrait.txt")
open(out, "w").write("\n".join(lines))
print(rows, "rows ->", out)
