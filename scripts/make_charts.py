"""
make_charts.py -- generate all figures for the Outs Per Effort (OPE) article.
Run after analyze_pe.py:   python3 scripts/make_charts.py
Writes PNGs to ../charts.
"""
import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

from analyze_pe import load_main, DATA, W

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "charts")
os.makedirs(OUT, exist_ok=True)

# ---- palette (dataviz validated) ----
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e5e4e0"
BLUE, ORANGE, RED, AQUA, VIOLET, YELLOW, BLUE_D = (
    "#2a78d6", "#eb6834", "#e34948", "#1baf7a", "#4a3aa7", "#eda100", "#184f95")

mpl.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "font.family": "DejaVu Sans", "font.size": 12,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.titlecolor": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 1,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 15, "axes.titleweight": "bold", "axes.labelsize": 12.5,
    "figure.dpi": 140,
})
def style(ax): ax.set_axisbelow(True); ax.tick_params(length=0)
_tier_cmap = mpl.colors.LinearSegmentedColormap.from_list("t", ["#b7d3f6", "#184f95"])
def cmap_step(i, n=6): return _tier_cmap(i/(n-1))
def trend(ax, x, y, color):
    b, a = np.polyfit(x, y, 1); xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, a + b*xs, color=color, lw=2.5, zorder=5)

df = load_main()
sp, rp = df[df.role == "SP"], df[df.role == "RP"]

# ===== 1. OPE vs IP =====
fig, ax = plt.subplots(figsize=(8.6, 5.6))
ax.scatter(rp.IP, rp.OPE, s=26, color=ORANGE, alpha=.55, edgecolor="none", label="Reliever")
ax.scatter(sp.IP, sp.OPE, s=26, color=BLUE, alpha=.55, edgecolor="none", label="Starter")
b, a = np.polyfit(df.IP, df.OPE, 1); xs = np.linspace(df.IP.min(), df.IP.max(), 50)
ax.plot(xs, a + b*xs, color=INK, lw=2.5, zorder=5)
ax.text(0.97, 0.06, f"r = {df.OPE.corr(df.IP):+.02f}", transform=ax.transAxes, ha="right",
        fontsize=15, fontweight="bold", bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=GRID))
ax.set_xlabel("Innings Pitched (workload)"); ax.set_ylabel("Outs Per Effort (OPE)")
ax.set_title("OPE is blind to workload — starters and relievers judged alike")
ax.legend(frameon=False, loc="upper left")
style(ax); fig.tight_layout(); fig.savefig(f"{OUT}/1_ope_vs_ip.png"); plt.close()

# ===== 2. why w=4 =====
ws = np.arange(0, 12.05, 0.25); base = 100*df.outs/(df.numberOfPitches+4*df.totalBases)
corr_ip = [(100*df.outs/(df.numberOfPitches+w*df.totalBases)).corr(df.IP) for w in ws]
spear = [(100*df.outs/(df.numberOfPitches+w*df.totalBases)).corr(base, method="spearman") for w in ws]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2))
ax1.axhline(0, color=INK2, lw=1, ls=(0, (4, 3)))
ax1.plot(ws, corr_ip, color=BLUE, lw=2.8); ax1.axvline(4, color=RED, lw=2, ls=(0, (3, 2)))
ax1.scatter([4], [np.interp(4, ws, corr_ip)], color=RED, s=70, zorder=6)
ax1.annotate("w = 4\nworkload-neutral", xy=(4, np.interp(4, ws, corr_ip)), xytext=(5.3, 0.075),
             color=RED, fontweight="bold", fontsize=11.5, arrowprops=dict(arrowstyle="-", color=RED, lw=1.4))
ax1.set_xlabel("weight w  (pitches charged per base allowed)")
ax1.set_ylabel("correlation of OPE with innings pitched")
ax1.set_title("Why 4?  It is where workload bias vanishes"); style(ax1)
ax2.plot(ws, spear, color=AQUA, lw=2.8); ax2.axvspan(2, 6, color=AQUA, alpha=.10)
ax2.axvline(4, color=RED, lw=2, ls=(0, (3, 2))); ax2.set_ylim(0.6, 1.01)
ax2.set_xlabel("weight w"); ax2.set_ylabel("rank agreement with w=4 (Spearman)")
ax2.set_title("Rankings barely move for w = 2–6 (robust)"); style(ax2)
fig.tight_layout(); fig.savefig(f"{OUT}/2_why_w4.png"); plt.close()

# ===== 3. results by OPE tier (staircase) =====
bins = [0, 12.2, 12.7, 13.4, 14.2, 15.0, 99]
labs = ["<12.2", "12.2–12.7", "12.7–13.4", "13.4–14.2", "14.2–15.0", "≥15.0"]
d3 = df.copy(); d3["tier"] = pd.cut(d3.OPE, bins=bins, labels=labs)
g3 = d3.groupby("tier", observed=True).agg(ERA=("era", "mean"), OPS=("ops", "mean"))
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.8, 5.4))
x = np.arange(len(labs))
for ax, col, ylab, fmt in [(ax1, "ERA", "average ERA", "{:.2f}"),
                           (ax2, "OPS", "average opponent OPS", "{:.3f}")]:
    vals = g3[col].values
    ax.bar(x, vals, color=[cmap_step(i) for i in range(len(x))], width=0.72, zorder=3)
    for xi, v in zip(x, vals):
        ax.text(xi, v + (max(vals)*0.012), fmt.format(v), ha="center", va="bottom",
                fontsize=11, fontweight="bold", color=INK)
    ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=9.5, rotation=0)
    ax.set_xlabel("OPE tier"); ax.set_ylabel(ylab)
    ax.set_title(f"Climb an OPE tier, {col} drops"); style(ax); ax.grid(axis="x", visible=False)
fig.suptitle("Every step up in OPE means better results", fontsize=15, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.96]); fig.savefig(f"{OUT}/3_ope_vs_results.png"); plt.close()

# ===== 4. correlation bars =====
mets = [("OPS", "ops"), ("WHIP", "whip"), ("ERA", "era"), ("FIP", "FIP"),
        ("HR/9", "HR9"), ("BB/9", "BB9"), ("K/9", "K9")]
vals = [df.OPE.corr(df[c]) for _, c in mets]
fig, ax = plt.subplots(figsize=(9, 5.4)); y = np.arange(len(vals))[::-1]
ax.barh(y, vals, color=[RED if v < 0 else BLUE for v in vals], height=0.62, zorder=3)
for yi, v in zip(y, vals):
    ax.text(v + (0.02 if v > 0 else -0.02), yi, f"{v:+.2f}", va="center",
            ha="left" if v > 0 else "right", fontsize=11.5, fontweight="bold", color=INK2)
ax.axvline(0, color=INK2, lw=1.2); ax.set_yticks(y); ax.set_yticklabels([m for m, _ in mets])
ax.set_xlim(-1, 0.5); ax.set_xlabel("correlation with OPE")
ax.set_title("What OPE captures — and what it does not")
ax.text(0.30, 0.13, "weak K/9 tie:\nOPE is not just strikeouts", transform=ax.transAxes,
        fontsize=10.5, color=INK2, ha="center")
style(ax); ax.grid(axis="y", visible=False)
fig.tight_layout(); fig.savefig(f"{OUT}/4_correlations.png"); plt.close()

# ===== 5. distribution + tiers =====
q50, q75, q90 = df.OPE.quantile(.5), df.OPE.quantile(.75), df.OPE.quantile(.9)
fig, ax = plt.subplots(figsize=(9.4, 5.4))
ax.hist(df.OPE, bins=34, color="#9ec5f4", edgecolor=SURF, linewidth=1.2, zorder=3)
ymax = ax.get_ylim()[1]
for xv, lab, c, yf in [(q50, "Average · 50th", INK2, 0.62), (q75, "Good · 75th", BLUE, 0.78),
                       (q90, "Elite · 90th", BLUE_D, 0.94)]:
    ax.axvline(xv, color=c, lw=2, ls=(0, (3, 2)))
    ax.annotate(f"{lab}  ({xv:.1f})", xy=(xv, ymax*yf), xytext=(xv+0.55, ymax*yf),
                color=c, fontsize=10.5, fontweight="bold", va="center",
                arrowprops=dict(arrowstyle="-", color=c, lw=1))
ax.set_xlabel("Outs Per Effort"); ax.set_ylabel("pitcher-seasons")
ax.set_title("The OPE scale (MLB 2023–2025, IP ≥ 50)")
style(ax); ax.grid(axis="x", visible=False)
fig.tight_layout(); fig.savefig(f"{OUT}/5_distribution.png"); plt.close()

# ===== 6. team OPE =====
d6 = df.copy(); d6["team_n"] = d6["team"].replace({"Oakland Athletics": "Athletics"})
tm = d6.groupby("team_n").OPE.mean().sort_values()
fig, ax = plt.subplots(figsize=(9, 8.4))
norm = (tm.values - tm.values.min()) / (tm.values.max() - tm.values.min())
cmap = mpl.colors.LinearSegmentedColormap.from_list("b", ["#cde2fb", BLUE_D])
ax.barh(np.arange(len(tm)), tm.values, color=[cmap(n) for n in norm], height=0.72, zorder=3)
ax.set_yticks(np.arange(len(tm))); ax.set_yticklabels(tm.index, fontsize=9.5)
ax.set_xlim(tm.values.min()-0.4, tm.values.max()+0.2)
ax.set_xlabel("team average OPE"); ax.set_title("Staff efficiency by team (2023–2025 pooled)")
style(ax); ax.grid(axis="y", visible=False)
fig.tight_layout(); fig.savefig(f"{OUT}/6_team_ope.png"); plt.close()

# ===== 7. Cy Young scorecard (dumbbell: winner OPE vs league OPE leader) =====
winners = [(2023,"AL","Gerrit Cole"),(2023,"NL","Blake Snell"),(2024,"AL","Tarik Skubal"),
           (2024,"NL","Chris Sale"),(2025,"AL","Tarik Skubal"),(2025,"NL","Paul Skenes")]
rows = []
for yr, lg, win in winners:
    pool = df[(df.season==yr)&(df.lg==lg)&(df.role=="SP")&(df.IP>=120)].sort_values("OPE", ascending=False)
    leader = pool.iloc[0]
    w = pool[pool.player_name==win].iloc[0]
    rows.append(dict(label=f"{yr} {lg}  {win}", win_ope=w.OPE, lead_ope=leader.OPE,
                     leader=leader.player_name, gap=leader.OPE-w.OPE))
sc = pd.DataFrame(rows).sort_values("gap")
fig, ax = plt.subplots(figsize=(10.5, 5.6)); yv = np.arange(len(sc))
for i, r in enumerate(sc.itertuples()):
    ax.plot([r.win_ope, r.lead_ope], [i, i], color=GRID, lw=3, zorder=1)
    ax.scatter(r.lead_ope, i, s=70, color=INK2, zorder=3)
    big = r.gap > 0.5
    ax.scatter(r.win_ope, i, s=110, color=RED if big else AQUA, zorder=4)
    if r.leader != r.label.split("  ")[1]:
        ax.text(r.lead_ope+0.05, i, r.leader, va="center", fontsize=9, color=INK2)
ax.set_yticks(yv); ax.set_yticklabels(sc.label, fontsize=10.5)
ax.set_xlabel("Outs Per Effort")
ax.set_title("Cy Young winners vs their league's OPE leader")
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([],[],marker="o",color="w",markerfacecolor=AQUA,markersize=10,label="winner ≈ OPE elite"),
                   Line2D([],[],marker="o",color="w",markerfacecolor=RED,markersize=10,label="winner well below OPE leader"),
                   Line2D([],[],marker="o",color="w",markerfacecolor=INK2,markersize=9,label="that year's league OPE leader")],
          frameon=False, loc="lower left", fontsize=9.5)
style(ax); ax.grid(axis="y", visible=False)
fig.tight_layout(); fig.savefig(f"{OUT}/7_cy_young.png"); plt.close()

# ===== 8. legends career trajectory (era-adjusted OPE+) =====
base = pd.read_csv(os.path.join(DATA, "pe_league_baseline.csv"))
base["lgOPE"] = 100*base["lg_outs"]/(base["lg_pitches"]+W*base["lg_totalBases"])
lgmap = dict(zip(base.season, base.lgOPE))
L = pd.read_csv(os.path.join(DATA, "pe_legends.csv"))
L["IP"] = pd.to_numeric(L["inningsPitched"], errors="coerce")
L["numberOfPitches"] = pd.to_numeric(L["numberOfPitches"], errors="coerce")
def dedupe(g):
    if g["team"].isna().any(): return g[g["team"].isna()].iloc[0]
    return g.sort_values("IP", ascending=False).iloc[0]
Ld = pd.DataFrame([dedupe(g) for _, g in L.groupby(["player_name","season"])])
# require realistic pitch counts (pre-1988 pitch data is incomplete)
Ld = Ld[(Ld.IP >= 40) & (Ld.numberOfPitches / Ld.IP >= 13)].copy()
Ld["OPE"] = 100*Ld["outs"]/(Ld["numberOfPitches"]+W*Ld["totalBases"])
Ld["OPEplus"] = 100*Ld["OPE"]/Ld["season"].map(lgmap)   # 100 = league average that season
print("legend era-adjusted OPE+ (mean, sd):")
for pl in ["Greg Maddux","Mariano Rivera","Clayton Kershaw","Pedro Martínez","Justin Verlander"]:
    s = Ld[Ld.player_name == pl]
    print(f"  {pl}: OPE+ {s.OPEplus.mean():.0f} ± {s.OPEplus.std():.0f}  ({int(s.season.min())}-{int(s.season.max())})")
order = ["Mariano Rivera","Greg Maddux","Clayton Kershaw","Pedro Martínez","Justin Verlander"]
cols = {"Greg Maddux":BLUE,"Mariano Rivera":ORANGE,"Clayton Kershaw":AQUA,
        "Pedro Martínez":VIOLET,"Justin Verlander":YELLOW}
fig, ax = plt.subplots(figsize=(11.5, 6.2))
ax.axhline(100, color=INK, lw=1.6, ls=(0,(5,3)), zorder=2)
ax.text(1988, 101, "league average (100)", color=INK, fontsize=9.5, fontweight="bold")
for pl in order:
    s = Ld[Ld.player_name == pl].sort_values("season")
    ax.plot(s.season, s.OPEplus, color=cols[pl], lw=2.4, marker="o", ms=4, zorder=3)
    last = s.iloc[-1]; ax.text(last.season+0.3, last.OPEplus, pl.split()[-1], color=cols[pl], fontweight="bold", fontsize=10, va="center")
ax.set_xlabel("season"); ax.set_ylabel("OPE+  (100 = league average that year)")
ax.set_title("Greatness is consistency: era-adjusted OPE across HOF careers")
ax.set_xlim(1987, 2029); style(ax)
fig.tight_layout(); fig.savefig(f"{OUT}/8_legends.png"); plt.close()

# ===== 9. 2026 leaderboard (SP so far) =====
d26 = pd.read_csv(os.path.join(DATA, "pe_data_2026.csv"))
d26["IP"] = pd.to_numeric(d26["inningsPitched"], errors="coerce")
d26["era"] = pd.to_numeric(d26["era"], errors="coerce")
d26 = d26[d26.IP >= 60].copy()
d26["OPE"] = 100*d26["outs"]/(d26["numberOfPitches"]+W*d26["totalBases"])
d26["role"] = np.where(d26.gamesStarted/d26.gamesPitched >= 0.5, "SP", "RP")
top = d26[d26.role == "SP"].sort_values("OPE", ascending=False).head(12).iloc[::-1]
fig, ax = plt.subplots(figsize=(9.5, 6.2)); yv = np.arange(len(top))
colors = [YELLOW if n == top.iloc[-1].player_name else "#9ec5f4" for n in top.player_name]
ax.barh(yv, top.OPE, color=colors, height=0.72, zorder=3)
for i, r in enumerate(top.itertuples()):
    ax.text(r.OPE-0.1, i, f"{r.OPE:.1f}", va="center", ha="right", fontsize=9.5, fontweight="bold", color=INK)
ax.set_yticks(yv); ax.set_yticklabels([f"{r.player_name} ({r.team.split()[-1]})" for r in top.itertuples()], fontsize=9.5)
ax.set_xlim(12, top.OPE.max()+0.4); ax.set_xlabel("Outs Per Effort (2026 to date, IP ≥ 60)")
ax.set_title("2026 OPE leaderboard — starters, midseason")
style(ax); ax.grid(axis="y", visible=False)
fig.tight_layout(); fig.savefig(f"{OUT}/9_ope_2026.png"); plt.close()

print("wrote 9 charts to", OUT)
print(os.listdir(OUT))
