#!/usr/bin/env python3
"""
fetch_history.py -- two things the OPE article still needs, in one run.
Standard library only:   python3 fetch_history.py

Writes TWO files; send both back:
  1) pe_finesse.csv          career year-by-year lines for finesse/soft-tossing
                             pitchers (Moyer, Buehrle, Haren, Tyler Rogers).
  2) pe_league_baseline.csv  league-wide pitching TOTALS per season 1988-2026,
                             so OPE can be compared to each era's own average.

Each finesse pitcher's resolved full name is printed so you can confirm the
right person was pulled. If any shows 0 seasons, tell me and I'll fix the ID.
"""
import csv
import json
import time
import urllib.request

FINESSE = {          # MLB people IDs; script prints resolved names to verify
    "Jamie Moyer":   118264,
    "Mark Buehrle":  279824,
    "Dan Haren":     407845,
    "Tyler Rogers":  643511,
}
SEASONS = list(range(1988, 2027))   # league baseline span


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch_finesse():
    rows = []
    for name, pid in FINESSE.items():
        url = (f"https://statsapi.mlb.com/api/v1/people/{pid}"
               f"?hydrate=stats(group=[pitching],type=[yearByYear],gameType=[R])")
        try:
            data = get(url)
        except Exception as e:
            print(f"  !! {name} failed: {e}"); continue
        people = data.get("people", [])
        if not people:
            print(f"  !! {name} ({pid}): no data — ID may be wrong"); continue
        resolved = people[0].get("fullName", "?")
        n = 0
        for blk in people[0].get("stats", []):
            for sp in blk.get("splits", []):
                team = sp.get("team", {}) or {}
                stat = sp.get("stat", {}) or {}
                row = {"player_name": resolved, "mlb_id": pid,
                       "season": sp.get("season"),
                       "team": team.get("abbreviation") or team.get("name")}
                for k, v in stat.items():
                    if not isinstance(v, (dict, list)):
                        row[k] = v
                rows.append(row); n += 1
        print(f"  {name} -> '{resolved}', {n} seasons")
        time.sleep(0.3)
    return rows


def fetch_baseline():
    rows = []
    for yr in SEASONS:
        url = (f"https://statsapi.mlb.com/api/v1/teams/stats?stats=season"
               f"&group=pitching&season={yr}&sportId=1")
        try:
            data = get(url)
        except Exception as e:
            print(f"  !! baseline {yr} failed: {e}"); continue
        outs = pitches = tb = 0
        teams = 0
        for blk in data.get("stats", []):
            for sp in blk.get("splits", []):
                st = sp.get("stat", {}) or {}
                outs += st.get("outs", 0) or 0
                pitches += st.get("numberOfPitches", 0) or 0
                tb += st.get("totalBases", 0) or 0
                teams += 1
        rows.append({"season": yr, "teams": teams, "lg_outs": outs,
                     "lg_pitches": pitches, "lg_totalBases": tb})
        print(f"  baseline {yr}: {teams} teams, pitches={pitches}")
        time.sleep(0.3)
    return rows


def write(path, rows):
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} rows -> {path}")


def main():
    print("Fetching finesse pitchers ...")
    fin = fetch_finesse()
    if fin:
        write("pe_finesse.csv", fin)
    print("\nFetching per-season league baseline ...")
    base = fetch_baseline()
    if base:
        write("pe_league_baseline.csv", base)
    print("\nDone. Send pe_finesse.csv and pe_league_baseline.csv back.")


if __name__ == "__main__":
    main()
