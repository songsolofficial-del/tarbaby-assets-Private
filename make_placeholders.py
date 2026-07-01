#!/usr/bin/env python3
"""Generate simple DEMO frames so the pipeline runs before you draw real art.
Replace these with your own exported PNG frames. Delete this file anytime."""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
SKIN = (232, 193, 122, 255)   # #e8c17a  (matches palettes.json keys)
SHADE = (212, 169, 95, 255)   # #d4a95f
LINE = (60, 50, 40, 255)


def blank():
    return Image.new("RGBA", (64, 64), (0, 0, 0, 0))


def baby(eyes_open=True):
    im = blank(); d = ImageDraw.Draw(im)
    d.ellipse([20, 20, 44, 46], fill=SKIN, outline=LINE)      # head
    d.ellipse([22, 40, 42, 58], fill=SKIN, outline=LINE)      # body
    d.rectangle([28, 42, 36, 46], fill=SHADE)                 # shade
    if eyes_open:
        d.point([(28, 30), (36, 30)], fill=LINE)
    else:
        d.line([27, 30, 29, 30], fill=LINE); d.line([35, 30, 37, 30], fill=LINE)
    return im


def hat():
    im = blank(); d = ImageDraw.Draw(im)
    d.polygon([(32, 8), (24, 24), (40, 24)], fill=(240, 196, 25, 255), outline=LINE)
    d.point([(32, 10)], fill=(255, 255, 255, 255))
    return im


def bg():
    im = Image.new("RGBA", (64, 64), (40, 44, 90, 255)); d = ImageDraw.Draw(im)
    for x, y in [(10, 12), (52, 18), (20, 48), (48, 50), (32, 8)]:
        d.point([(x, y)], fill=(255, 255, 255, 255))
    return im


def save(folder, frames):
    p = os.path.join(SRC, folder); os.makedirs(p, exist_ok=True)
    for i, fr in enumerate(frames):
        fr.save(os.path.join(p, f"frame_{i:03d}.png"))


save("body_base-baby", [baby(True), baby(True), baby(False)])  # blink loop
save("hat_star", [hat()])
save("bg_night", [bg()])
print("Demo frames written to src/. Run:  python build.py")
