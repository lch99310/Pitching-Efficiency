import pandas as pd, numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os

OUT = 'charts'
os.makedirs(OUT, exist_ok=True)

# ---- palette (dataviz validated) ----
SURF   = '#fcfcfb'
INK    = '#0b0b0b'
INK2   = '#52514e'
GRID   = '#e5e4e0'
BLUE   = '#2a78d6'   # SP
ORANGE = '#eb6834'   # RP
RED    = '#e34948'
AQUA   = '#1baf7a'
BLUE_D = '#184f95'

mpl.rcParams.update({
    'figure.facecolor': SURF, 'axes.facecolor': SURF, 'savefig.facecolor': SURF,
    'font.family': 'DejaVu Sans', 'font.size': 12,
    'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'text.color': INK,
    'xtick.color': INK2, 'ytick.color': INK2, 'axes.titlecolor': INK,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 1,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.titlesize': 15, 'axes.titleweight': 'bold', 'axes.labelsize': 12.5,
    'figure.dpi': 140,
})

def style(ax):
    ax.set_axisbelow(True)
    ax.tick_params(length=0)

# ---- data ----
df = pd.read_csv('pe_computed.csv')
sp = df[df.role=='SP']; rp = df[df.role=='RP']

def trend(ax, x, y, color):
    b,a = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, a+b*xs, color=color, lw=2.5, zorder=5)

# ========== 1. PE vs IP (workload fairness) ==========
fig, ax = plt.subplots(figsize=(8.6,5.6))
ax.scatter(rp.IP, rp.PE, s=26, color=ORANGE, alpha=.55, edgecolor='none', label='Reliever')
ax.scatter(sp.IP, sp.PE, s=26, color=BLUE,   alpha=.55, edgecolor='none', label='Starter')
b,a = np.polyfit(df.IP, df.PE, 1)
xs=np.linspace(df.IP.min(),df.IP.max(),50)
ax.plot(xs, a+b*xs, color=INK, lw=2.5, zorder=5)
r = df.PE.corr(df.IP)
ax.text(0.97,0.06,f'r = {r:+.02f}', transform=ax.transAxes, ha='right',
        fontsize=15, fontweight='bold', color=INK,
        bbox=dict(boxstyle='round,pad=0.4', fc='white', ec=GRID))
ax.set_xlabel('Innings Pitched (workload)'); ax.set_ylabel('Pitching Efficiency (PE)')
ax.set_title('PE is blind to workload — starters and relievers judged alike')
ax.legend(frameon=False, loc='upper left', fontsize=12)
style(ax); fig.tight_layout(); fig.savefig(f'{OUT}/1_pe_vs_ip.png'); plt.close()

# ========== 2. Why w=4 ==========
ws = np.arange(0, 12.05, 0.25)
corr_ip=[]; spear=[]
base = 100*df.outs/(df.numberOfPitches+4*df.totalBases)
for w in ws:
    pe = 100*df.outs/(df.numberOfPitches+w*df.totalBases)
    corr_ip.append(pe.corr(df.IP))
    spear.append(pe.corr(base, method='spearman'))
fig, (ax1,ax2) = plt.subplots(1,2, figsize=(12.5,5.2))
ax1.axhline(0, color=INK2, lw=1, ls=(0,(4,3)))
ax1.plot(ws, corr_ip, color=BLUE, lw=2.8)
ax1.axvline(4, color=RED, lw=2, ls=(0,(3,2)))
ax1.scatter([4],[np.interp(4,ws,corr_ip)], color=RED, s=70, zorder=6)
ax1.annotate('w = 4\nworkload-neutral', xy=(4, np.interp(4,ws,corr_ip)),
             xytext=(5.3, 0.075), color=RED, fontweight='bold', fontsize=11.5,
             arrowprops=dict(arrowstyle='-', color=RED, lw=1.4))
ax1.set_xlabel('weight w  (pitches charged per base allowed)')
ax1.set_ylabel('correlation of PE with innings pitched')
ax1.set_title('Why 4?  It is where workload bias vanishes')
style(ax1)
ax2.plot(ws, spear, color=AQUA, lw=2.8)
ax2.axvspan(2,6, color=AQUA, alpha=.10)
ax2.axvline(4, color=RED, lw=2, ls=(0,(3,2)))
ax2.set_ylim(0.6,1.01)
ax2.set_xlabel('weight w'); ax2.set_ylabel('rank agreement with w=4 (Spearman)')
ax2.set_title('Rankings barely move for w = 2–6 (robust)')
style(ax2)
fig.tight_layout(); fig.savefig(f'{OUT}/2_why_w4.png'); plt.close()

# ========== 3. PE vs ERA and OPS-against ==========
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(12.8,5.6))
for ax,(col,lab) in zip((ax1,ax2), [('era','ERA'),('ops','OPS against')]):
    ax.scatter(rp.PE, rp[col], s=24, color=ORANGE, alpha=.5, edgecolor='none', label='Reliever')
    ax.scatter(sp.PE, sp[col], s=24, color=BLUE,   alpha=.5, edgecolor='none', label='Starter')
    trend(ax, df.PE, df[col], INK)
    r=df.PE.corr(df[col])
    ax.text(0.04,0.06,f'r = {r:+.02f}', transform=ax.transAxes, fontsize=14,
            fontweight='bold', bbox=dict(boxstyle='round,pad=0.35',fc='white',ec=GRID))
    ax.set_xlabel('Pitching Efficiency'); ax.set_ylabel(lab)
    ax.set_title(f'Higher PE  →  lower {lab}')
    style(ax)
ax1.legend(frameon=False, loc='upper right', fontsize=11)
fig.tight_layout(); fig.savefig(f'{OUT}/3_pe_vs_era_ops.png'); plt.close()

# ========== 4. correlation bars ==========
mets=[('OPS','ops'),('WHIP','whip'),('ERA','era'),('FIP','FIP'),
      ('HR/9','HR9'),('BB/9','BB9'),('K/9','K9')]
vals=[df.PE.corr(df[c]) for _,c in mets]
labs=[m for m,_ in mets]
fig,ax=plt.subplots(figsize=(9,5.4))
colors=[RED if v<0 else BLUE for v in vals]
y=np.arange(len(vals))[::-1]
ax.barh(y, vals, color=colors, height=0.62, zorder=3)
for yi,v in zip(y,vals):
    ax.text(v+(0.02 if v>0 else -0.02), yi, f'{v:+.2f}',
            va='center', ha='left' if v>0 else 'right', fontsize=11.5, fontweight='bold', color=INK2)
ax.axvline(0, color=INK2, lw=1.2)
ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=12.5)
ax.set_xlim(-1,0.5); ax.set_xlabel('correlation with PE')
ax.set_title('What PE captures — and what it does not')
ax.text(0.30,0.14,'weak K/9 tie:\nPE is not just strikeouts', transform=ax.transAxes,
        fontsize=10.5, color=INK2, ha='center')
style(ax); ax.grid(axis='y', visible=False)
fig.tight_layout(); fig.savefig(f'{OUT}/4_correlations.png'); plt.close()

# ========== 5. distribution + tiers ==========
q10,q25,q50,q75,q90 = [df.PE.quantile(q) for q in (.1,.25,.5,.75,.9)]
fig,ax=plt.subplots(figsize=(9.4,5.4))
ax.hist(df.PE, bins=34, color='#9ec5f4', edgecolor=SURF, linewidth=1.2, zorder=3)
ymax = ax.get_ylim()[1]
for xv,lab,c,yf in [(q50,'Average · 50th',INK2,0.62),(q75,'Good · 75th',BLUE,0.78),(q90,'Elite · 90th',BLUE_D,0.94)]:
    ax.axvline(xv, color=c, lw=2, ls=(0,(3,2)))
    ax.annotate(f'{lab}  ({xv:.1f})', xy=(xv, ymax*yf), xytext=(xv+0.55, ymax*yf),
                color=c, fontsize=10.5, fontweight='bold', va='center',
                arrowprops=dict(arrowstyle='-', color=c, lw=1))
ax.set_xlabel('Pitching Efficiency'); ax.set_ylabel('pitcher-seasons')
ax.set_title('The PE scale (MLB 2023–2025, IP ≥ 50)')
style(ax); ax.grid(axis='x', visible=False)
fig.tight_layout(); fig.savefig(f'{OUT}/5_distribution.png'); plt.close()

# ========== 6. team PE ==========
df['team_n'] = df['team'].replace({'Oakland Athletics':'Athletics'})
tm=df.groupby('team_n').PE.mean().sort_values()
# merge duplicate Athletics naming
fig,ax=plt.subplots(figsize=(9,8.4))
norm=(tm.values-tm.values.min())/(tm.values.max()-tm.values.min())
cmap=mpl.colors.LinearSegmentedColormap.from_list('b',['#cde2fb',BLUE_D])
ax.barh(np.arange(len(tm)), tm.values, color=[cmap(n) for n in norm], height=0.72, zorder=3)
ax.set_yticks(np.arange(len(tm))); ax.set_yticklabels(tm.index, fontsize=9.5)
ax.set_xlim(tm.values.min()-0.4, tm.values.max()+0.2)
ax.set_xlabel('team average PE'); ax.set_title('Staff efficiency by team (2023–2025 pooled)')
style(ax); ax.grid(axis='y', visible=False)
fig.tight_layout(); fig.savefig(f'{OUT}/6_team_pe.png'); plt.close()

print('charts written to', OUT)
print(os.listdir(OUT))
print(f'tiers: q10={q10:.1f} q25={q25:.1f} q50={q50:.1f} q75={q75:.1f} q90={q90:.1f}')
