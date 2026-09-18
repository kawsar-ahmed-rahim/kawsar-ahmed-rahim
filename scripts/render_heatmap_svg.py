#!/usr/bin/env python3

import json
from datetime import date
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")

COLORS = [
    "#161b22",
    "#3b2f10",
    "#6f5517",
    "#a17c20",
    "#D4AF37",
]

CELL = 12
GAP = 4
LEFT = 40
TOP = 230


def format_date(value):
    d = date.fromisoformat(value)
    return d.strftime("%b %d, %Y")


def main():

    if not DATA.exists():
        raise SystemExit("Run fetch_contributions.py first.")

    data = json.loads(DATA.read_text(encoding="utf-8"))

    days = {
        item["date"]: item
        for item in data["days"]
    }

    dates = sorted(days)

    if not dates:
        raise SystemExit("No contribution data.")

    start = date.fromisoformat(dates[0])
    end = date.fromisoformat(dates[-1])

    # Start heatmap on Sunday
    start = date.fromordinal(
        start.toordinal() - (start.weekday() + 1) % 7
    )

    weeks = ((end - start).days // 7) + 1

    heatmap_width = LEFT + weeks * (CELL + GAP) + 20
    heatmap_height = TOP + 7 * (CELL + GAP) + 38

    W = max(700, heatmap_width)
    H = heatmap_height

    # --------------------------------------------------
    # HEATMAP CELLS
    # --------------------------------------------------

    rects = []

    current = start

    while current <= end:

        column = (current - start).days // 7
        row = (current.weekday() + 1) % 7

        item = days.get(
            current.isoformat(),
            {"count": 0, "level": 0}
        )

        level = min(4, int(item["level"]))

        x = LEFT + column * (CELL + GAP)
        y = TOP + row * (CELL + GAP)

        rects.append(
            f"""
            <rect
                x="{x}"
                y="{y}"
                width="{CELL}"
                height="{CELL}"
                rx="2"
                fill="{COLORS[level]}"
            >
                <title>
                    {current}: {item["count"]} contributions
                </title>
            </rect>
            """
        )

        current = date.fromordinal(
            current.toordinal() + 1
        )

    metrics = data["metrics"]

    total = metrics["total_contributions"]
    current_streak = metrics["current_streak"]
    longest_streak = metrics["longest_streak"]

    first_date = format_date(dates[0])
    last_date = format_date(dates[-1])

    # --------------------------------------------------
    # SVG
    # --------------------------------------------------

    svg = f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{W}"
    height="{H}"
    viewBox="0 0 {W} {H}"
>

<style>

    .background {{
        fill: #0d0d0d;
        stroke: #333333;
        stroke-width: 1.2;
    }}

    .title {{
        fill: #eeeeee;
        font-family: monospace;
        font-size: 18px;
        font-weight: 700;
    }}

    .subtitle {{
        fill: #888888;
        font-family: monospace;
        font-size: 11px;
    }}

    .number {{
        fill: #111111;
        font-family: monospace;
        font-size: 28px;
        font-weight: 700;
    }}

    .label {{
        fill: #D4AF37;
        font-family: monospace;
        font-size: 13px;
        font-weight: 700;
    }}

    .date {{
        fill: #666666;
        font-family: monospace;
        font-size: 10px;
    }}

    .day {{
        fill: #777777;
        font-family: monospace;
        font-size: 10px;
    }}

    .stat-card {{
        fill: #ffffff;
        stroke: #dddddd;
        stroke-width: 1;
    }}

    .divider {{
        stroke: #dddddd;
        stroke-width: 1;
    }}

</style>


<!-- Main background -->

<rect
    class="background"
    x="0.6"
    y="0.6"
    width="{W - 1.2}"
    height="{H - 1.2}"
    rx="14"
/>


<!-- Title -->

<text
    x="20"
    y="30"
    class="title"
>
    Contribution Activity
</text>


<text
    x="20"
    y="49"
    class="subtitle"
>
    GitHub contribution history
</text>


<!-- ========================================== -->
<!-- STATISTICS CARDS -->
<!-- ========================================== -->

<rect
    class="stat-card"
    x="20"
    y="70"
    width="{(W - 40) / 3}"
    height="120"
    rx="8"
/>


<rect
    class="stat-card"
    x="{20 + (W - 40) / 3}"
    y="70"
    width="{(W - 40) / 3}"
    height="120"
    rx="8"
/>


<rect
    class="stat-card"
    x="{20 + 2 * (W - 40) / 3}"
    y="70"
    width="{(W - 40) / 3}"
    height="120"
    rx="8"
/>


<!-- Dividers -->

<line
    class="divider"
    x1="{20 + (W - 40) / 3}"
    y1="70"
    x2="{20 + (W - 40) / 3}"
    y2="190"
/>

<line
    class="divider"
    x1="{20 + 2 * (W - 40) / 3}"
    y1="70"
    x2="{20 + 2 * (W - 40) / 3}"
    y2="190"
/>


<!-- Total Contributions -->

<text
    x="{20 + (W - 40) / 6}"
    y="112"
    text-anchor="middle"
    class="number"
>
    {total}
</text>

<text
    x="{20 + (W - 40) / 6}"
    y="137"
    text-anchor="middle"
    class="label"
>
    Total Contributions
</text>

<text
    x="{20 + (W - 40) / 6}"
    y="160"
    text-anchor="middle"
    class="date"
>
    {first_date} - Present
</text>


<!-- Current Streak -->

<text
    x="{20 + (W - 40) / 2}"
    y="112"
    text-anchor="middle"
    class="number"
>
    {current_streak}
</text>

<text
    x="{20 + (W - 40) / 2}"
    y="137"
    text-anchor="middle"
    class="label"
>
    Current Streak
</text>

<text
    x="{20 + (W - 40) / 2}"
    y="160"
    text-anchor="middle"
    class="date"
>
    consecutive days
</text>


<!-- Longest Streak -->

<text
    x="{20 + 5 * (W - 40) / 6}"
    y="112"
    text-anchor="middle"
    class="number"
>
    {longest_streak}
</text>

<text
    x="{20 + 5 * (W - 40) / 6}"
    y="137"
    text-anchor="middle"
    class="label"
>
    Longest Streak
</text>

<text
    x="{20 + 5 * (W - 40) / 6}"
    y="160"
    text-anchor="middle"
    class="date"
>
    consecutive days
</text>


<!-- ========================================== -->
<!-- HEATMAP -->
<!-- ========================================== -->

<text
    x="20"
    y="215"
    class="subtitle"
>
    Daily contributions
</text>


<!-- Day labels -->

<text x="18" y="{TOP + 10}" class="day">
    Sun
</text>

<text
    x="18"
    y="{TOP + 2 * (CELL + GAP) + 10}"
    class="day"
>
    Tue
</text>

<text
    x="18"
    y="{TOP + 4 * (CELL + GAP) + 10}"
    class="day"
>
    Thu
</text>

<text
    x="18"
    y="{TOP + 6 * (CELL + GAP) + 10}"
    class="day"
>
    Sat
</text>


{''.join(rects)}


<!-- Legend -->

<text
    x="{LEFT}"
    y="{H - 8}"
    class="day"
>
    less
</text>

{''.join(
    f'<rect x="{LEFT + 28 + i * 18}" '
    f'y="{H - 18}" '
    f'width="12" height="12" rx="2" fill="{color}"/>'
    for i, color in enumerate(COLORS)
)}

<text
    x="{LEFT + 28 + len(COLORS) * 18 + 4}"
    y="{H - 8}"
    class="day"
>
    more
</text>

</svg>
"""

    OUT.write_text(
        svg,
        encoding="utf-8"
    )

    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()