#!/usr/bin/env python3
"""
fetch_legends.py  --  Career year-by-year pitching lines for a few legends,
for the Pitching Efficiency (PE) "consistency" case study.

Runs on YOUR machine (no network restrictions). Standard library only:

    python3 fetch_legends.py

Writes ONE file, `pe_legends.csv`, with one row per player-season.
It prints each player's full name as resolved by MLB, so you can confirm
the right person was pulled. Send that single CSV back.
"""

import csv
import json
import time
import urllib.request

# MLB "people" IDs. The script prints the resolved full name for each, so
# if any ID is wrong you'll see it immediately (tell me and I'll fix it).
LEGENDS = {
    "Clayton Kershaw":  477132,
    "Mariano Rivera":   121250,
    "Greg Maddux":      118120,
    "Justin Verlander": 434378,
    "Pedro Martinez":   118377,
}

OUT_FILE = "pe_legends.csv"
ID_COLS = ["player_name", "mlb_id", "season", "team"]


def fetch_person(name, pid):
    url = (
        f"https://statsapi.mlb.com/api/v1/people/{pid}"
        f"?hydrate=stats(group=[pitching],type=[yearByYear],gameType=[R])"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)

    people = data.get("people", [])
    if not people:
        print(f"  !! {name} ({pid}): no data — ID may be wrong")
        return []
    resolved = people[0].get("fullName", "?")
    rows = []
    for blk in people[0].get("stats", []):
        for sp in blk.get("splits", []):
            team = sp.get("team", {}) or {}
            stat = sp.get("stat", {}) or {}
            row = {
                "player_name": resolved,
                "mlb_id": pid,
                "season": sp.get("season"),
                "team": team.get("abbreviation") or team.get("name"),
            }
            for k, v in stat.items():
                if isinstance(v, (dict, list)):
                    continue
                row[k] = v
            rows.append(row)
    print(f"  {name} -> resolved as '{resolved}', {len(rows)} seasons")
    return rows


def main():
    all_rows = []
    for name, pid in LEGENDS.items():
        print(f"Fetching {name} ...")
        try:
            all_rows.extend(fetch_person(name, pid))
        except Exception as e:
            print(f"  !! {name} failed: {e}")
        time.sleep(0.4)

    if not all_rows:
        print("No data fetched. Check your internet connection and try again.")
        return

    cols = list(ID_COLS)
    for row in all_rows:
        for k in row:
            if k not in cols:
                cols.append(k)

    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in all_rows:
            w.writerow(row)

    print(f"\nDone. Wrote {len(all_rows)} rows -> {OUT_FILE}")
    print("Send that single file back.")


if __name__ == "__main__":
    main()
