#!/usr/bin/env python3
from __future__ import annotations
import json, re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup

USERNAME = "kawsar-ahmed-rahim"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")
LEVELS = {"ContributionCalendar-day-L1":1,"ContributionCalendar-day-L2":2,
          "ContributionCalendar-day-L3":3,"ContributionCalendar-day-L4":4}

def parse():
    r = requests.get(URL, headers={"User-Agent":"cipher-stack-profile/1.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        d = cell.get("data-date")
        if not d: continue
        m = re.search(r"([\d,]+)\s+contribution", cell.get_text(" ", strip=True))
        count = int(m.group(1).replace(",","")) if m else 0
        level = next((LEVELS[c] for c in cell.get("class",[]) if c in LEVELS), 0)
        days.append({"date":d,"count":count,"level":level})
    if not days:
        raise RuntimeError("No contribution cells found; GitHub may have changed its HTML.")
    return days

def metrics(days):
    ordered = sorted(days, key=lambda x:x["date"])
    total = sum(x["count"] for x in ordered)
    best = max(ordered, key=lambda x:(x["count"],x["date"]))
    longest = run = 0
    for x in ordered:
        run = run+1 if x["count"] else 0
        longest = max(longest, run)
    bydate = {date.fromisoformat(x["date"]):x["count"] for x in ordered}
    cur = date.today()
    if bydate.get(cur,0) == 0: cur -= timedelta(days=1)
    streak = 0
    while bydate.get(cur,0) > 0:
        streak += 1
        cur -= timedelta(days=1)
    return {"total_contributions":total,"current_streak":streak,
            "longest_streak":longest,"best_day":{"date":best["date"],"count":best["count"]}}

def main():
    days = parse()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"username":USERNAME,"source":URL,
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "metrics":metrics(days),"days":days}, indent=2), encoding="utf-8")
    print(json.dumps(metrics(days), indent=2))

if __name__ == "__main__":
    main()
