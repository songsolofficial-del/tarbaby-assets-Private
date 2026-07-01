#!/usr/bin/env python3
"""
Drop an item image in, get a baby-ready animated asset out.

    python3 fit_item.py <image> <category_name> [options]

Example:
    python3 fit_item.py ~/Downloads/crown.png hat_crown --width 44 --y 8

What it does (the whole manual hat process, automated):
  1. isolate the main item (drops stray floating bits like sparkles)
  2. crop, downscale to target width (crisp)
  3. reduce colors to shed anti-aliasing fuzz
  4. recolor the darkest tone to pure black  -> matches the baby outline
  5. drop onto a 128x128 canvas, centered, at the given y
  6. expand into 16 breathing frames synced to the baby idle

Options:
  --width N     item width in px on the 128 canvas (default 46)
  --y N         top y position on the canvas (default 20; smaller = higher)
  --colors N    palette size after cleanup (default 6)
  --keep-all    keep every piece (don't drop detached bits like sparkles)
  --no-breathe  output a single static frame only
"""
import sys, os, glob, math, argparse
import numpy as np
from PIL import Image
try:
    from scipy import ndimage
    HAVE_SCIPY = True
except ImportError:
    HAVE_SCIPY = False

CANVAS = 128

def isolate_main(img):
    a = np.array(img); al = a[:, :, 3]
    if not HAVE_SCIPY:
        return img
    lbl, n = ndimage.label(al > 60)
    if n <= 1:
        return img
    biggest = max(range(1, n + 1), key=lambda i: int(np.sum(lbl == i)))
    mask = lbl == biggest
    a[~mask] = (0, 0, 0, 0)
    return Image.fromarray(a, 'RGBA')

def clean_and_snap(small, k):
    """Quantize to k colors, map the darkest to pure black."""
    a = np.array(small).astype(int)
    op = a[:, :, 3] > 110
    rgb = Image.fromarray(np.array(small)[:, :, :3])
    q = rgb.quantize(colors=max(2, k), method=Image.MEDIANCUT).convert('RGB')
    qa = np.array(q)
    # darkest palette color -> black
    pal = qa[op]
    if len(pal):
        lum = pal[:, 0].astype(int) + pal[:, 1] + pal[:, 2]
        darkest = tuple(pal[np.argmin(lum)])
        d = np.all(qa == np.array(darkest), axis=-1)
        qa[d] = (0, 0, 0)
    out = np.zeros((a.shape[0], a.shape[1], 4), dtype=np.uint8)
    out[:, :, :3] = qa
    out[:, :, 3] = np.where(op, 255, 0)
    return Image.fromarray(out, 'RGBA')

def bob_offsets(n=16, amp=2):
    return [int(round(-amp * (0.5 - 0.5 * math.cos(2 * math.pi * i / n)))) for i in range(n)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image'); ap.add_argument('name')
    ap.add_argument('--width', type=int, default=46)
    ap.add_argument('--y', type=int, default=20)
    ap.add_argument('--colors', type=int, default=6)
    ap.add_argument('--keep-all', action='store_true')
    ap.add_argument('--no-breathe', action='store_true')
    args = ap.parse_args()

    img = Image.open(args.image).convert('RGBA')
    if not args.keep_all:
        img = isolate_main(img)
    al = np.array(img)[:, :, 3]
    ys, xs = np.where(al > 30)
    crop = img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    th = max(1, round(crop.height * args.width / crop.width))
    small = crop.resize((args.width, th), Image.LANCZOS)
    clean = clean_and_snap(small, args.colors)

    canvas = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.alpha_composite(clean, (CANVAS // 2 - clean.width // 2, args.y))

    folder = os.path.join('src', args.name)
    os.makedirs(folder, exist_ok=True)
    for f in glob.glob(folder + '/*.png'):
        os.remove(f)

    if args.no_breathe:
        canvas.save(os.path.join(folder, 'frame_000.png'))
        print(f'OK - {folder}/frame_000.png ({clean.size[0]}x{clean.size[1]} @ y{args.y})')
    else:
        for i, dy in enumerate(bob_offsets()):
            o = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
            o.alpha_composite(canvas, (0, dy))
            o.save(os.path.join(folder, f'frame_{i:03d}.png'))
        print(f'OK - {folder}: 16 breathing frames ({clean.size[0]}x{clean.size[1]} @ y{args.y})')
    print('Next: python3 build.py  ->  commit  ->  push')

if __name__ == '__main__':
    main()
