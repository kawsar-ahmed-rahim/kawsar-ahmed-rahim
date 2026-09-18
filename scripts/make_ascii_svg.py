#!/usr/bin/env python3
from pathlib import Path
import html
import numpy as np
from PIL import Image, ImageOps

SOURCE = Path("source-prepped.png")
OUTPUT = Path("hxni-ascii.svg")
RAMP = " .`:-=+*cs#%@"
GOLD, BG = "#D4AF37", "#0d0d0d"
WIDTH, FONT_SIZE, LINE_HEIGHT = 92, 7.0, 7.5

def main():
    if not SOURCE.exists():
        raise SystemExit("source-prepped.png not found. Run prep_photo.py first.")
    img = Image.open(SOURCE).convert("L")
    height = max(1, round(WIDTH * img.height / img.width * 0.50))
    img = ImageOps.fit(img, (WIDTH, height), method=Image.Resampling.LANCZOS)
    px = np.asarray(img, dtype=np.float32)
    rows = ["".join(RAMP[int(v/255*(len(RAMP)-1))] for v in row) for row in px]
    pad = 14
    card_w = WIDTH * FONT_SIZE * 0.60 + pad*2
    card_h = height * LINE_HEIGHT + 46
    clips, groups = [], []
    for i, row in enumerate(rows):
        y = 35 + (i+1)*LINE_HEIGHT
        safe = html.escape(row).replace(" ", "&#160;")
        cid = f"l{i}"
        clips.append(f'<clipPath id="{cid}"><rect x="0" y="{y-LINE_HEIGHT+1:.1f}" width="{card_w}" height="{LINE_HEIGHT+2:.1f}"/></clipPath>')
        groups.append(f'<g clip-path="url(#{cid})"><text x="{pad}" y="{y:.1f}" class="ascii" style="animation-delay:{i*0.018:.2f}s">{safe}</text></g>')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{card_w:.0f}" height="{card_h:.0f}" viewBox="0 0 {card_w:.0f} {card_h:.0f}">
<style>
.card{{fill:{BG};stroke:#333;stroke-width:1.2}}
.ascii{{fill:{GOLD};font-family:monospace;font-size:{FONT_SIZE}px;letter-spacing:.15px;opacity:0;animation:fin .7s ease-out forwards}}
@keyframes fin{{from{{opacity:0;transform:translateY(2px)}}to{{opacity:1;transform:translateY(0)}}}}
</style>
<defs>{''.join(clips)}</defs>
<rect class="card" x=".6" y=".6" width="{card_w-1.2:.0f}" height="{card_h-1.2:.0f}" rx="14"/>
<circle cx="20" cy="18" r="5" fill="#ff5f57"/><circle cx="36" cy="18" r="5" fill="#febc2e"/><circle cx="52" cy="18" r="5" fill="#28c840"/>
<text x="{card_w/2:.0f}" y="21" text-anchor="middle" fill="#888" font-family="monospace" font-size="8">THE CIPHER STACK // PORTRAIT</text>
{''.join(groups)}
</svg>"""
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Saved {OUTPUT}")

if __name__ == "__main__":
    main()
