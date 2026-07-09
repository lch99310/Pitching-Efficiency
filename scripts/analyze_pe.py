"""
analyze_pe.py -- compute Outs Per Effort (OPE) and print the validation report.

OPE = 100 * outs / (pitches + 4 * TB)

Reads the raw CSVs in ../data (as produced by fetch_pe_data.py) and writes
../data/pe_computed.csv (the 2023-2025 sample with OPE and friends). Run from
the repo root or the scripts/ folder:

    python3 scripts/analyze_pe.py
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

W = 4  # pitches charged per base allowed

AL = {"Baltimore Orioles","Boston Red Sox","New York Yankees","Tampa Bay Rays",
      "Toronto Blue Jays","Chicago White Sox","Cleveland Guardians","Detroit Tigers",
      "Kansas City Royals","Minnesota Twins","Houston Astros","Los Angeles Angels",
      "Athletics","Oakland Athletics","Seattle Mariners","Texas Rangers"}


def load_main():
    df = pd.read_csv(os.path.join(DATA, "pe_data_2023_2024_2025.csv"))
    df["IP"] = pd.to_numeric(df["inningsPitched"], errors="coerce")
    for c in ["era", "ops", "whip"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[df["IP"] >= 50].copy()
    df["role"] = np.where(df["gamesStarted"] / df["gamesPitched"] >= 0.5, "SP", "RP")
    df["OPE"] = 100 * df["outs"] / (df["numberOfPitches"] + W * df["totalBases"])
    df["lg"] = np.where(df["team"].isin(AL), "AL", "NL")
    const = {}
    for s, g in df.groupby("season"):
        lgERA = 9 * g["earnedRuns"].sum() / g["IP"].sum()
        const[s] = lgERA - (13*g["homeRuns"].sum() + 3*(g["baseOnBalls"].sum()
                    + g["hitBatsmen"].sum()) - 2*g["strikeOuts"].sum()) / g["IP"].sum()
    df["FIP"] = (13*df["homeRuns"] + 3*(df["baseOnBalls"]+df["hitBatsmen"])
                 - 2*df["strikeOuts"]) / df["IP"] + df["season"].map(const)
    df["K9"] = df["strikeOuts"]*9/df["IP"]
    df["BB9"] = df["baseOnBalls"]*9/df["IP"]
    df["HR9"] = df["homeRuns"]*9/df["IP"]
    return df


def main():
    df = load_main()
    print("N pitcher-seasons (IP>=50):", len(df))
    print("OPE percentiles:",
          {int(q*100): round(df.OPE.quantile(q), 1) for q in (.1,.25,.5,.75,.9)})
    print("r(OPE, IP) =", round(df.OPE.corr(df.IP), 3), "(workload independence)")
    print("Correlations with OPE:")
    for m, c in [("ERA","era"),("FIP","FIP"),("OPS","ops"),("WHIP","whip"),
                 ("HR/9","HR9"),("BB/9","BB9"),("K/9","K9")]:
        print(f"  {m:5}: {df.OPE.corr(df[c]):+.2f}")
    df.to_csv(os.path.join(DATA, "pe_computed.csv"), index=False)
    print("wrote data/pe_computed.csv")


if __name__ == "__main__":
    main()
