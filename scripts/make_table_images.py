"""
make_table_images.py -- render the article's data tables as PNG images, so they
survive the FanGraphs Community (WordPress) editor, which strips <table> tags.
Writes t01..t06 into ../charts.  Run:  python3 scripts/make_table_images.py
"""
import os
import matplotlib as mpl
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "charts")
SURF, INK, INK2, HEAD, ROW = "#fcfcfb", "#0b0b0b", "#52514e", "#184f95", "#eef4fc"
mpl.rcParams.update({"figure.facecolor": SURF, "savefig.facecolor": SURF,
                     "font.family": "DejaVu Sans"})


def render(headers, rows, fname, colw=None, title=None):
    n, m = len(rows) + 1, len(headers)
    fig_w = sum(colw) if colw else 1.6 * m
    fig, ax = plt.subplots(figsize=(fig_w, 0.52 * n + (0.5 if title else 0.15)))
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=headers, cellLoc="center", loc="center",
                   colWidths=[w / fig_w for w in colw] if colw else None)
    tbl.auto_set_font_size(False); tbl.set_fontsize(12); tbl.scale(1, 1.5)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#d7d7d3")
        if r == 0:
            cell.set_facecolor(HEAD); cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor(ROW if r % 2 else "white")
            cell.set_text_props(color=INK)
        if c == 0 and r > 0:
            cell.set_text_props(color=INK, fontweight="bold")
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", color=INK, pad=10)
    fig.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, fname), dpi=150, bbox_inches="tight")
    plt.close()
    print("wrote", fname)


# T1 tiers
render(["Tier", "OPE", "Meaning"],
       [["Elite", "≥ 15.0", "top 10% — Cy Young class"],
        ["Good", "14.2 – 15.0", "top 25% — dependable starter / high-leverage reliever"],
        ["Average", "≈ 13.4", "the league median"],
        ["Below average", "12.7 – 13.4", "back-of-rotation / middle relief"],
        ["Struggling", "< 12.2", "bottom 10%"]],
       "t01_tiers.png", colw=[2.6, 2.2, 6.6])

# T2 top 15
render(["#", "Pitcher", "Year", "Team", "Role", "IP", "ERA", "OPE"],
       [["1", "Emmanuel Clase", "2024", "CLE", "RP", "74.1", "0.61", "18.8"],
        ["2", "Raisel Iglesias", "2024", "ATL", "RP", "69.1", "1.95", "17.9"],
        ["3", "Adrian Morejón", "2025", "SD", "RP", "73.2", "2.08", "17.7"],
        ["4", "Tyler Rogers", "2025", "NYM", "RP", "77.1", "1.98", "17.5"],
        ["5", "Aroldis Chapman", "2025", "BOS", "RP", "61.1", "1.17", "17.0"],
        ["6", "Ryan Helsley", "2024", "STL", "RP", "66.1", "2.04", "16.7"],
        ["7", "Brusdar Graterol", "2023", "LAD", "RP", "67.1", "1.20", "16.7"],
        ["8", "Tyler Holton", "2024", "DET", "RP", "94.1", "2.19", "16.6"],
        ["…", "", "", "", "", "", "", ""],
        ["13", "Trevor Rogers", "2025", "BAL", "SP", "109.2", "1.81", "16.2"]],
       "t02_top15.png", colw=[0.8, 3.3, 1.2, 1.3, 1.2, 1.2, 1.2, 1.2])

# T3 top SP
render(["#", "Pitcher", "Year", "Team", "IP", "ERA", "OPE"],
       [["1", "Trevor Rogers", "2025", "BAL", "109.2", "1.81", "16.2"],
        ["2", "Cristopher Sánchez", "2025", "PHI", "202.0", "2.50", "15.7"],
        ["3", "Nathan Eovaldi", "2025", "TEX", "130.0", "1.73", "15.7"],
        ["4", "Bryan Woo", "2024", "SEA", "121.1", "2.89", "15.6"],
        ["5", "Tarik Skubal", "2025", "DET", "195.1", "2.21", "15.6"],
        ["6", "Framber Valdez", "2024", "HOU", "176.1", "2.91", "15.5"]],
       "t03_topsp.png", colw=[0.8, 3.6, 1.3, 1.4, 1.3, 1.3, 1.3])

# T4 Glasnow / Morton
render(["Pitcher", "Year", "ERA", "OPE", "Tier"],
       [["Tyler Glasnow", "2024", "3.49", "15.0", "Elite"],
        ["Charlie Morton", "2023", "3.64", "13.1", "Below average"]],
       "t04_glasnow_morton.png", colw=[3.0, 1.4, 1.4, 1.4, 2.6])

# T5 Price / Verlander
render(["2012 AL", "ERA", "IP", "K", "WHIP", "OPE"],
       [["David Price (winner)", "2.56", "211.0", "205", "1.10", "14.69"],
        ["Justin Verlander", "2.64", "238.1", "239", "1.06", "14.47"]],
       "t05_price_verlander.png", colw=[4.2, 1.3, 1.4, 1.2, 1.4, 1.4])

# T6 legends OPE+
render(["Pitcher", "Career OPE+", "Span"],
       [["Mariano Rivera", "117", "1995–2013"],
        ["Greg Maddux", "115 (±6)", "1988–2008"],
        ["Clayton Kershaw", "114", "2008–2025"],
        ["Pedro Martínez", "111", "1993–2009"],
        ["Justin Verlander", "104", "2006–2025"]],
       "t06_legends.png", colw=[3.4, 2.4, 2.4])

print("done")
