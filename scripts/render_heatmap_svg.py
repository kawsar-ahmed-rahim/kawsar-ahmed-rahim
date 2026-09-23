#!/usr/bin/env python3
"""
scripts/render_heatmap_svg.py

Reads data/contributions.json (produced by scripts/fetch_contributions.py)
and renders the combined overview + streak-ring + compact mosaic card to
contrib-heatmap.svg at the repo root.
"""

import json
from datetime import date, timedelta
from pathlib import Path

IN = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")

# Theme (matches the rest of the README)
BG = "#0d0d0d"
BORDER = "#262626"
ACCENT = "#00BFFF"
TEXT = "#ffffff"
MUTED = "#8b8b8b"

LEVEL_COLORS = ["#161b22", "#0a3d62", "#1477b3", "#00a8e8", "#00d9ff"]


def build_mosaic(days, x0, y0, cell=10, gap=3):
    first_date = date.fromisoformat(days[0]["date"])
    first_sunday_offset = (first_date.weekday() + 1) % 7
    grid_start = first_date - timedelta(days=first_sunday_offset)

    squares = []
    row_labels = {0: "Sun", 2: "Tue", 4: "Thu", 6: "Sat"}
    for row, label in row_labels.items():
        ly = y0 + row * (cell + gap) + cell - 2
        squares.append(f'<text x="{x0 - 8}" y="{ly}" text-anchor="end" '
                        f'font-size="9" fill="{MUTED}" font-family="JetBrains Mono, monospace">{label}</text>')

    by_date = {date.fromisoformat(d["date"]): d["level"] for d in days}
    end_date = date.fromisoformat(days[-1]["date"])
    cursor = grid_start
    week = 0
    while cursor <= end_date:
        for row in range(7):
            day = cursor + timedelta(days=row)
            if day > end_date:
                continue
            level = by_date.get(day, 0)
            cx = x0 + week * (cell + gap)
            cy = y0 + row * (cell + gap)
            squares.append(
                f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="2" '
                f'fill="{LEVEL_COLORS[min(level, 4)]}" />'
            )
        cursor += timedelta(days=7)
        week += 1

    return "\n".join(squares), 7 * (cell + gap)


def ring_badge(cx, cy, r, value, label, sublabel):
    circumference = 2 * 3.14159265 * r
    return f'''
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BORDER}" stroke-width="4"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{ACCENT}" stroke-width="4"
  stroke-linecap="round" stroke-dasharray="{circumference}" stroke-dashoffset="{circumference * 0.15}"
  transform="rotate(-90 {cx} {cy})"/>
<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="18" font-weight="700"
  fill="{TEXT}" font-family="JetBrains Mono, monospace">{value}</text>
<text x="{cx}" y="{cy + 14}" text-anchor="middle" font-size="8" fill="{MUTED}"
  font-family="JetBrains Mono, monospace">{sublabel}</text>
<text x="{cx}" y="{cy + r + 18}" text-anchor="middle" font-size="10" font-weight="600"
  fill="{ACCENT}" font-family="JetBrains Mono, monospace">{label}</text>
'''


def render_svg(days, metrics):
    width = 780
    mosaic, mosaic_h = build_mosaic(days, x0=60, y0=170)
    height = 170 + mosaic_h + 40

    badges = "".join([
        ring_badge(150, 90, 40, f'{metrics["total_contributions"]:,}', "CONTRIBUTIONS", "TOTAL"),
        ring_badge(390, 90, 40, metrics["current_streak"], "CURRENT STREAK", "DAYS"),
        ring_badge(630, 90, 40, metrics["longest_streak"], "LONGEST STREAK", "DAYS MAX"),
    ])

    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
  xmlns="http://www.w3.org/2000/svg" font-family="JetBrains Mono, monospace">
<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{BG}" stroke="{BORDER}"/>
<text x="30" y="34" font-size="14" font-weight="700" fill="{ACCENT}">● GITHUB ACTIVITY</text>
{badges}
<line x1="30" y1="140" x2="{width - 30}" y2="140" stroke="{BORDER}"/>
<text x="30" y="162" font-size="11" fill="{MUTED}">Daily contributions</text>
{mosaic}
</svg>'''


def main():
    payload = json.loads(IN.read_text(encoding="utf-8"))
    days = sorted(payload["days"], key=lambda d: d["date"])
    metrics = payload["metrics"]

    svg = render_svg(days, metrics)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Total: {metrics['total_contributions']}  "
          f"Current streak: {metrics['current_streak']}  "
          f"Longest streak: {metrics['longest_streak']}")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()