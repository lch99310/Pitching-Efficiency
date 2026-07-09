#!/usr/bin/env python3
"""
fetch_pe_data.py  --  Pull MLB pitching season stats for Pitching Efficiency (PE).

Runs on YOUR machine (no network restrictions there). Zero dependencies:
uses only the Python standard library. Just run:

    python3 fetch_pe_data.py

It writes ONE file, `pe_data.csv`, containing every pitcher-season for
2023, 2024, 2025 (regular season). Send that single CSV back to me.

Nothing to install, no website logins, no manual merging.
"""

import csv
import json
import sys
import time
import urllib.request

# Seasons: pass years on the command line, e.g.  python3 fetch_pe_data.py 2026
# With no arguments it pulls 2023-2025.
if len(sys.argv) > 1:
    SEASONS = [int(a) for a in sys.argv[1:]]
else:
    SEASONS = [2023, 2024, 2025]
OUT_FILE = "pe_data_%s.csv" % "_".join(str(s) for s in SEASONS)
BASE = "https://statsapi.mlb.com/api/v1/stats"

# We dump EVERY stat field the API returns (so nothing is missed), plus
# player/team identity. These identity columns come first for readability.
ID_COLS = ["season", "player_id", "player_name", "team"]


def fetch_season(season):
    """Return a list of dicts, one per pitcher, for a single season."""
    rows = []
    offset = 0
    limit = 1000
    while True:
        url = (
            f"{BASE}?stats=season&group=pitching&season={season}"
            f"&sportId=1&gameType=R&playerPool=all&limit={limit}&offset={offset}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)

        splits = []
        for blk in data.get("stats", []):
            splits.extend(blk.get("splits", []))

        if not splits:
            break

        for sp in splits:
            player = sp.get("player", {}) or {}
            team = sp.get("team", {}) or {}
            stat = sp.get("stat", {}) or {}
            row = {
                "season": season,
                "player_id": player.get("id"),
                "player_name": player.get("fullName"),
                "team": team.get("abbreviation") or team.get("name"),
            }
            # flatten every stat field the API gives us
            for k, v in stat.items():
                if isinstance(v, (dict, list)):
                    continue  # skip nested objects
                row[k] = v
            rows.append(row)

        if len(splits) < limit:
            break
        offset += limit
        time.sleep(0.4)  # be polite to the API

    print(f"  {season}: {len(rows)} pitcher rows")
    return rows


def main():
    all_rows = []
    for yr in SEASONS:
        print(f"Fetching {yr} ...")
        try:
            all_rows.extend(fetch_season(yr))
        except Exception as e:
            print(f"  !! {yr} failed: {e}")

    if not all_rows:
        print("No data fetched. Check your internet connection and try again.")
        return

    # union of all columns, identity columns first
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

    print(f"\nDone. Wrote {len(all_rows)} rows x {len(cols)} cols -> {OUT_FILE}")
    print("Send that file back.")


if __name__ == "__main__":
    main()
