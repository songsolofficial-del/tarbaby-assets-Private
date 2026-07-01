#!/usr/bin/env python3
"""
Make an item (hat, hair, top, prop...) breathe in sync with the baby.

Draw ONE static frame aligned on the template, save as:
    src/<category>_<name>/frame_000.png   (128x128, transparent)
Then run:
    python3 breathe_item.py src/hat_star

It expands frame_000.png into 16 frames using the SAME vertical bob as the
baby's idle, so the item stays glued to the head while breathing.
"""
import sys, os, glob, math
from PIL import Image

def bob_offsets(n=16, amp=2):
    # identical curve to the baby's breathing idle
    return [int(round(-amp*(0.5-0.5*math.cos(2*math.pi*i/n)))) for i in range(n)]

def shift_v(img, dy):
    out = Image.new('RGBA', img.size, (0,0,0,0))
    out.alpha_composite(img, (0, dy))
    return out

def main():
    if len(sys.argv) < 2:
        print("usage: python3 breathe_item.py src/<category>_<name>")
        sys.exit(1)
    folder = sys.argv[1].rstrip('/')
    src = os.path.join(folder, 'frame_000.png')
    if not os.path.exists(src):
        print(f"! {src} not found. Put your static item there first.")
        sys.exit(1)
    base = Image.open(src).convert('RGBA')
    if base.size != (128,128):
        print(f"! frame_000.png is {base.size}, expected (128,128). Fix canvas first.")
        sys.exit(1)
    # clear any old frames except the source
    for f in glob.glob(os.path.join(folder,'frame_*.png')):
        if os.path.basename(f) != 'frame_000.png':
            os.remove(f)
    offs = bob_offsets(16, 2)
    for i, dy in enumerate(offs):
        shift_v(base, dy).save(os.path.join(folder, f'frame_{i:03d}.png'))
    print(f"OK - {folder}: 16 breathing frames written (offsets {offs})")

if __name__ == '__main__':
    main()
