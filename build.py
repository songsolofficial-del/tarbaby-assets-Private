#!/usr/bin/env python3
"""
STAR BABY asset build pipeline.
src/<category>_<name>/frame_*.png  ->  dist/{sheets,meta,thumbs}/ + dist/manifest.json

No Aseprite needed. Runs anywhere Python + Pillow run (local, or GitHub Actions).
Draw frames in any pixel tool, export as PNG sequence, drop in src/, run this.
"""
import json, os, glob, sys
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DIST = os.path.join(ROOT, "dist")
CFG = json.load(open(os.path.join(ROOT, "config.json")))
PALETTES = json.load(open(os.path.join(ROOT, "palettes", "palettes.json")))

CANVAS = tuple(CFG["canvas"])
ANCHOR = CFG["anchor"]
FPS = CFG["fps"]
SCALES = CFG["scales"]
LAYERS = CFG["layers"]
CDN = CFG["cdnBase"].rstrip("/")
VARIANTS = CFG.get("variants", {})
ITEM_META = CFG.get("itemMeta", {})   # per-item shop price: {id: {starCost: N}}

for sub in ("sheets", "meta", "thumbs"):
    os.makedirs(os.path.join(DIST, sub), exist_ok=True)


def load_frames(folder):
    files = sorted(glob.glob(os.path.join(folder, "frame_*.png")))
    if not files:  # allow single static png too
        files = sorted(glob.glob(os.path.join(folder, "*.png")))
    frames = []
    for f in files:
        im = Image.open(f).convert("RGBA")
        if im.size != CANVAS:
            # pad/crop to canvas, aligned top-left, so anchor stays valid
            canv = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
            canv.paste(im, (0, 0))
            im = canv
            print(f"  ! {os.path.basename(f)} was {im.size}, padded to {CANVAS}")
        frames.append(im)
    return frames


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def recolor(im, mapping):
    src = {hex_to_rgb(k): hex_to_rgb(v) for k, v in mapping.items()}
    out = im.copy()
    px = out.load()
    w, h = out.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in src:
                nr, ng, nb = src[(r, g, b)]
                px[x, y] = (nr, ng, nb, a)
    return out


def make_sheet(frames):
    n = len(frames)
    sheet = Image.new("RGBA", (CANVAS[0] * n, CANVAS[1]), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i * CANVAS[0], 0))
    return sheet


def export(item_id, category, frames):
    """Write sheets (@2x/@3x), thumb, meta for one item id. Returns meta dict."""
    sheet = make_sheet(frames)
    n = len(frames)
    for s in SCALES:
        scaled = sheet.resize((sheet.width * s, sheet.height * s), Image.NEAREST)
        scaled.save(os.path.join(DIST, "sheets", f"{item_id}@{s}x.png"))
    # thumbnail = first frame @2x
    thumb = frames[0].resize((CANVAS[0] * 2, CANVAS[1] * 2), Image.NEAREST)
    thumb.save(os.path.join(DIST, "thumbs", f"{item_id}.png"))
    meta = {
        "id": item_id,
        "category": category,
        "layer": LAYERS.get(category, 99),
        "canvas": list(CANVAS),
        "anchor": ANCHOR,
        "fps": FPS,
        "frames": n,
        "sheet": f"{CDN}/sheets/{item_id}@3x.png",
        "sheet2x": f"{CDN}/sheets/{item_id}@2x.png",
        "thumb": f"{CDN}/thumbs/{item_id}.png",
    }
    # shop price (star cost). Structure is always present; values fill in later.
    price = ITEM_META.get(item_id, {}).get("starCost", None)
    if item_id == "body_base-baby":
        price = 0            # default baby is free, not a shop item
        meta["shop"] = False
    else:
        meta["shop"] = True
    meta["starCost"] = price
    json.dump(meta, open(os.path.join(DIST, "meta", f"{item_id}.json"), "w"),
              ensure_ascii=False, indent=2)
    return meta


def main():
    manifest = {"version": "auto", "canvas": list(CANVAS), "anchor": ANCHOR,
                "fps": FPS, "cdnBase": CDN, "items": []}
    folders = sorted(d for d in glob.glob(os.path.join(SRC, "*")) if os.path.isdir(d))
    if not folders:
        print("src/ is empty. Add a folder like src/hat_star/ with frame_000.png inside.")
        return
    for folder in folders:
        base = os.path.basename(folder)          # e.g. body_base-baby
        category = base.split("_", 1)[0]         # body
        frames = load_frames(folder)
        if not frames:
            print(f"- skip {base} (no png)")
            continue
        print(f"+ {base}  ({len(frames)} frame{'s' if len(frames)>1 else ''})")
        manifest["items"].append(export(base, category, frames))
        # palette variants (auto color mass-production)
        for var in VARIANTS.get(base, []):
            if var not in PALETTES:
                print(f"  ! palette '{var}' not found, skip")
                continue
            vframes = [recolor(fr, PALETTES[var]) for fr in frames]
            vid = f"{base}_{var}"
            print(f"    -> variant {vid}")
            manifest["items"].append(export(vid, category, vframes))

    manifest["items"].sort(key=lambda m: (m["layer"], m["id"]))
    json.dump(manifest, open(os.path.join(DIST, "manifest.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"\nDONE - {len(manifest['items'])} assets -> dist/manifest.json")


if __name__ == "__main__":
    main()
