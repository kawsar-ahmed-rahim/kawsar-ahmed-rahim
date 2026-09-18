#!/usr/bin/env python3
from pathlib import Path
import html

rows = [
    ("OS", "Windows / Linux"),
    ("Host", "Dhaka, Bangladesh"),
    ("Role", "Full Stack Web Developer"),
    ("Frontend", "React · Tailwind CSS · Bootstrap"),
    ("Backend", "Node.js · Express · Python · Django · DRF"),
    ("Tools", "Git · GitHub · VS Code · Postman"),
    ("Deploy", "Vercel · Netlify"),
    ("Portfolio", "spectacular-macaron-597a89.netlify.app"),
    ("GitHub", "github.com/kawsar-ahmed-rahim"),
]
W, H = 760, 430
lines = []
for i, (k, v) in enumerate(rows):
    y = 75 + i*34
    delay = i*.08
    lines.append(f'<text x="34" y="{y}" class="key" style="animation-delay:{delay:.2f}s">{html.escape(k)}</text>')
    lines.append(f'<text x="170" y="{y}" class="value" style="animation-delay:{delay:.2f}s">{html.escape(v)}</text>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.bg{{fill:#0d0d0d;stroke:#333;stroke-width:1.2}}
.key{{fill:#00BFFF;font:600 17px monospace;opacity:0;animation:fade .55s ease forwards}}
.value{{fill:#c9c9c9;font:15px monospace;opacity:0;animation:fade .55s ease forwards}}
.title{{fill:#eee;font:600 14px monospace}} .dim{{fill:#777;font:12px monospace}}
@keyframes fade{{from{{opacity:0;transform:translateX(-7px)}}to{{opacity:1;transform:translateX(0)}}}}
</style>
<rect class="bg" x=".6" y=".6" width="{W-1.2}" height="{H-1.2}" rx="14"/>
<circle cx="20" cy="20" r="6" fill="#ff5f57"/><circle cx="40" cy="20" r="6" fill="#febc2e"/><circle cx="60" cy="20" r="6" fill="#28c840"/>
<text x="82" y="24" class="title">The Cipher Stack</text>
<text x="{W-30}" y="24" text-anchor="end" class="dim">neofetch://rahim</text>
<line x1="28" y1="43" x2="{W-28}" y2="43" stroke="#252525"/>
{''.join(lines)}
<text x="34" y="{H-22}" class="dim">status: building · shipping · learning</text>
</svg>"""
Path("info-card.svg").write_text(svg, encoding="utf-8")
print("Saved info-card.svg")
