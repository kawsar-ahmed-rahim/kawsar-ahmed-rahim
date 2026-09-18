#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

DATA, OUT = Path("data/contributions.json"), Path("contrib-heatmap.svg")
COLORS = ["#161b22","#3b2f10","#6f5517","#a17c20","#D4AF37"]
CELL, GAP, LEFT, TOP = 12, 4, 40, 48

def main():
    if not DATA.exists(): raise SystemExit("Run fetch_contributions.py first.")
    p = json.loads(DATA.read_text(encoding="utf-8"))
    days = {x["date"]:x for x in p["days"]}
    dates = sorted(days)
    if not dates: raise SystemExit("No contribution data.")
    start, end = date.fromisoformat(dates[0]), date.fromisoformat(dates[-1])
    start = date.fromordinal(start.toordinal() - (start.weekday()+1)%7)
    weeks = ((end-start).days//7)+1
    W, H = LEFT + weeks*(CELL+GAP) + 20, TOP + 7*(CELL+GAP) + 38
    rects=[]; cur=start
    while cur <= end:
        col=(cur-start).days//7; row=(cur.weekday()+1)%7
        d=days.get(cur.isoformat(),{"count":0,"level":0})
        x=LEFT+col*(CELL+GAP); y=TOP+row*(CELL+GAP)
        rects.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{COLORS[min(4,int(d["level"]))]}"><title>{cur}: {d["count"]} contributions</title></rect>')
        cur=date.fromordinal(cur.toordinal()+1)
    m=p["metrics"]
    legend="".join(f'<rect x="{LEFT+28+i*18}" y="{H-18}" width="12" height="12" rx="2" fill="{c}"/>' for i,c in enumerate(COLORS))
    svg=f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>.bg{{fill:#0d0d0d;stroke:#333;stroke-width:1.2}}.title{{fill:#eee;font:600 13px monospace}}.meta{{fill:#D4AF37;font:12px monospace}}.day{{fill:#777;font:10px monospace}}</style>
<rect class="bg" x=".6" y=".6" width="{W-1.2}" height="{H-1.2}" rx="14"/>
<text x="20" y="25" class="title">Contribution Activity</text>
<text x="{W-20}" y="25" text-anchor="end" class="meta">{m["total_contributions"]} total · {m["current_streak"]} day streak · best {m["best_day"]["count"]}</text>
<text x="18" y="{TOP+10}" class="day">Sun</text><text x="18" y="{TOP+2*(CELL+GAP)+10}" class="day">Tue</text>
<text x="18" y="{TOP+4*(CELL+GAP)+10}" class="day">Thu</text><text x="18" y="{TOP+6*(CELL+GAP)+10}" class="day">Sat</text>
{''.join(rects)}
<text x="{LEFT}" y="{H-8}" class="day">less</text>{legend}<text x="{LEFT+28+len(COLORS)*18+4}" y="{H-8}" class="day">more</text>
</svg>"""
    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved {OUT}")

if __name__ == "__main__":
    main()
