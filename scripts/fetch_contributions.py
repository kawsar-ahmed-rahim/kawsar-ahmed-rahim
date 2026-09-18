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
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    cells = soup.select(
        "td.ContributionCalendar-day[data-date]"
    )

    if not cells:
        raise RuntimeError(
            "GitHub contribution cells were not found."
        )

    days = []

    # ------------------------------------------
    # Build tooltip lookup
    # ------------------------------------------

    tooltips = {}

    for tooltip in soup.select("tool-tip"):

        text = tooltip.get_text(
            " ",
            strip=True
        )

        if text:
            tooltips[id(tooltip)] = text

    # ------------------------------------------
    # Read every contribution day
    # ------------------------------------------

    for cell in cells:

        contribution_date = cell.get(
            "data-date"
        )

        if not contribution_date:
            continue

        # GitHub currently provides data-level
        # directly on the calendar cell.

        level = int(
            cell.get(
                "data-level",
                "0"
            )
        )

        count = 0

        # --------------------------------------
        # Check aria-label
        # --------------------------------------

        aria = cell.get(
            "aria-label",
            ""
        )

        match = re.search(
            r"([\d,]+)\s+contribution",
            aria,
            re.IGNORECASE
        )

        if match:
            count = int(
                match.group(1).replace(",", "")
            )

        # --------------------------------------
        # Check title
        # --------------------------------------

        if count == 0:

            title = cell.get(
                "title",
                ""
            )

            match = re.search(
                r"([\d,]+)\s+contribution",
                title,
                re.IGNORECASE
            )

            if match:
                count = int(
                    match.group(1).replace(",", "")
                )

        # --------------------------------------
        # Look for nearby tooltip
        # --------------------------------------

        if count == 0:

            parent = cell.parent

            if parent:

                text = parent.get_text(
                    " ",
                    strip=True
                )

                match = re.search(
                    r"([\d,]+)\s+contribution",
                    text,
                    re.IGNORECASE
                )

                if match:
                    count = int(
                        match.group(1).replace(",", "")
                    )

        days.append(
            {
                "date": contribution_date,
                "count": count,
                "level": level
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
        key=lambda item: item["date"]
    )

    total = sum(
        item["count"]
        for item in ordered
    )

    # ------------------------------------------
    # Longest streak
    # ------------------------------------------

    longest_streak = 0
    current_run = 0

    for item in ordered:

        if item["count"] > 0:

            current_run += 1

            longest_streak = max(
                longest_streak,
                current_run
            )

        else:

            current_run = 0

   # ------------------------------------------
# Current streak
# ------------------------------------------

contribution_map = {
    date.fromisoformat(item["date"]): item["count"]
    for item in ordered
}

latest_day = max(contribution_map.keys())

current_streak = 0
current_day = latest_day

while contribution_map.get(current_day, 0) > 0:
    current_streak += 1
    current_day -= timedelta(days=1)

    # If today has no contribution,
    # start checking from yesterday.

    if contribution_map.get(
        current_day,
        0
    ) == 0:

        current_day -= timedelta(
            days=1
        )

    current_streak = 0

    while contribution_map.get(
        current_day,
        0
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
        key=lambda item: item["count"]
    )

    return {
        "total_contributions": total,

        "current_streak": current_streak,

        "longest_streak": longest_streak,

        "best_day": {
            "date": best_day["date"],
            "count": best_day["count"]
        }
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
        exist_ok=True
    )

    output = {
        "username": USERNAME,

        "source": URL,

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "metrics": metrics,

        "days": days
    }

    OUT.write_text(
        json.dumps(
            output,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print(
        "Contribution statistics:"
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

    print()
    print(
        f"Saved: {OUT}"
    )


if __name__ == "__main__":
    main()