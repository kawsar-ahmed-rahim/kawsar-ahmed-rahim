#!/usr/bin/env python3

import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "kawsar-ahmed-rahim"

URL = f"https://github.com/users/{USERNAME}/contributions"

OUT = Path("data/contributions.json")


def parse_contributions():
    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
            "Referer": f"https://github.com/{USERNAME}",
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # ------------------------------------------
    # Find contribution days
    # ------------------------------------------

    cells = soup.select(
        ".js-calendar-graph-table "
        ".ContributionCalendar-day"
    )

    if not cells:
        raise RuntimeError(
            "GitHub contribution cells were not found."
        )

    # ------------------------------------------
    # Build tooltip lookup
    #
    # Each contribution day has an id.
    # Each tooltip has a matching "for" attribute.
    # ------------------------------------------

    tooltips = {}

    for tooltip in soup.select("tool-tip[for]"):
        tooltip_for = tooltip.get("for")

        if tooltip_for:
            tooltips[tooltip_for] = tooltip

    print(
        f"Found {len(cells)} contribution days."
    )

    print(
        f"Found {len(tooltips)} contribution tooltips."
    )

    days = []

    # ------------------------------------------
    # Read contribution days
    # ------------------------------------------

    for cell in cells:

        contribution_date = cell.get("data-date")

        if not contribution_date:
            continue

        cell_id = cell.get("id")

        level = int(
            cell.get(
                "data-level",
                "0",
            )
        )

        count = 0

        # --------------------------------------
        # Get count from matching tooltip
        # --------------------------------------

        tooltip = tooltips.get(cell_id)

        if tooltip:

            text = tooltip.get_text(
                " ",
                strip=True,
            )

            match = re.search(
                r"(\d[\d,]*)\s+contribution",
                text,
                re.IGNORECASE,
            )

            if match:

                count = int(
                    match.group(1).replace(
                        ",",
                        "",
                    )
                )

        days.append(
            {
                "date": contribution_date,
                "count": count,
                "level": level,
            }
        )

    if not days:
        raise RuntimeError(
            "No contribution data found."
        )

    return days


def calculate_metrics(days):

    ordered = sorted(
        days,
        key=lambda item: item["date"],
    )

    # ------------------------------------------
    # Total contributions
    # ------------------------------------------

    total = sum(
        item["count"]
        for item in ordered
    )

    # ------------------------------------------
    # Contribution map
    # ------------------------------------------

    contribution_map = {
        date.fromisoformat(item["date"]): item["count"]
        for item in ordered
    }

    # ------------------------------------------
    # Longest streak
    # ------------------------------------------

    longest_streak = 0
    current_run = 0
    previous_day = None

    for item in ordered:

        current_day = date.fromisoformat(
            item["date"]
        )

        if item["count"] > 0:

            if (
                previous_day is not None
                and current_day
                == previous_day + timedelta(days=1)
            ):
                current_run += 1
            else:
                current_run = 1

            longest_streak = max(
                longest_streak,
                current_run,
            )

        else:
            current_run = 0

        previous_day = current_day

    # ------------------------------------------
    # Current streak
    # ------------------------------------------

    latest_day = max(
        contribution_map.keys()
    )

    current_streak = 0
    current_day = latest_day

    while contribution_map.get(
        current_day,
        0,
    ) > 0:

        current_streak += 1

        current_day -= timedelta(
            days=1
        )

    # ------------------------------------------
    # Best day
    # ------------------------------------------

    best_day = max(
        ordered,
        key=lambda item: item["count"],
    )

    return {
        "total_contributions": total,

        "current_streak": current_streak,

        "longest_streak": longest_streak,

        "best_day": {
            "date": best_day["date"],
            "count": best_day["count"],
        },
    }


def main():

    print(
        "Fetching GitHub contributions..."
    )

    days = parse_contributions()

    metrics = calculate_metrics(
        days
    )

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "username": USERNAME,

        "source": URL,

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "metrics": metrics,

        "days": days,
    }

    OUT.write_text(
        json.dumps(
            output,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()

    print(
        "=============================="
    )

    print(
        "Contribution statistics"
    )

    print(
        "=============================="
    )

    print(
        f"Total contributions: "
        f"{metrics['total_contributions']}"
    )

    print(
        f"Current streak: "
        f"{metrics['current_streak']}"
    )

    print(
        f"Longest streak: "
        f"{metrics['longest_streak']}"
    )

    print(
        f"Best day: "
        f"{metrics['best_day']['date']} "
        f"({metrics['best_day']['count']} contributions)"
    )

    print(
        "=============================="
    )

    print(
        f"Saved: {OUT}"
    )


if __name__ == "__main__":
    main()