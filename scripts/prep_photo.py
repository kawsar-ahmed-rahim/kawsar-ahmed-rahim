#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps
from rembg import remove, new_session

def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, default=Path("source-prepped.png"))
    p.add_argument("--size", type=int, default=160)
    a = p.parse_args()
    if not a.input.exists():
        raise SystemExit(f"Input image not found: {a.input}")

    session = new_session("u2net")          # pin the lightweight model
    src = Image.open(a.input).convert("RGBA")
    src.thumbnail((1200, 1200))              # cap resolution before segmentation

    rgba = remove(src, session=session).convert("RGBA")
    bg = Image.new("RGBA", rgba.size, (13, 13, 13, 255))
    bg.alpha_composite(rgba)
    rgb = np.asarray(bg.convert("RGB"))
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l, aa, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    enhanced = cv2.cvtColor(cv2.merge((l, aa, b)), cv2.COLOR_LAB2RGB)
    img = ImageOps.contain(Image.fromarray(enhanced).convert("RGB"),
                           (a.size, a.size), method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (a.size, a.size), (13, 13, 13))
    canvas.paste(img, ((a.size-img.width)//2, (a.size-img.height)//2))
    canvas.save(a.output, "PNG", optimize=True)
    print(f"Saved {a.output}")

if __name__ == "__main__":
    main()