import pandas as pd, numpy as np
pd.set_option('display.width',200)

df = pd.read_csv('pe_data.csv')
df['IP'] = df['inningsPitched'].astype(float)
for c in ['era','ops','obp','slg','avg','whip']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
# API gives 'outs' directly; verify against IP conversion
df = df[df['IP'] >= 50].copy()

# role: SP if majority of appearances are starts
df['role'] = np.where(df['gamesStarted'] / df['gamesPitched'] >= 0.5, 'SP', 'RP')

# PE 2.0
W = 4
df['PE'] = 100 * df['outs'] / (df['numberOfPitches'] + W * df['totalBases'])

# FIP with per-season constant so league FIP == league ERA
def fip_const(g):
    lgERA = 9*g['earnedRuns'].sum()/g['IP'].sum()
    return lgERA - (13*g['homeRuns'].sum() + 3*(g['baseOnBalls'].sum()+g['hitBatsmen'].sum()) - 2*g['strikeOuts'].sum())/g['IP'].sum()
consts = df.groupby('season').apply(fip_const)
df['cFIP'] = df['season'].map(consts)
df['FIP'] = (13*df['homeRuns'] + 3*(df['baseOnBalls']+df['hitBatsmen']) - 2*df['strikeOuts'])/df['IP'] + df['cFIP']

df['K9']=df['strikeOuts']*9/df['IP']
df['BB9']=df['baseOnBalls']*9/df['IP']
df['HR9']=df['homeRuns']*9/df['IP']
df['OPS']=df['ops']

print("=== N by role/season ==="); print(df.groupby(['season','role']).size())

print("\n=== PE distribution (all) ===")
for q in [0.1,0.25,0.5,0.75,0.9]:
    print(f"  {int(q*100)}th: {df['PE'].quantile(q):.2f}")
print(f"  mean {df['PE'].mean():.2f}  sd {df['PE'].std():.2f}  min {df['PE'].min():.2f} max {df['PE'].max():.2f}")

print("\n=== THE KEY TEST: corr(PE, IP) — should be ~0 for PE2.0 ===")
print(f"  overall Pearson r(PE, IP) = {df['PE'].corr(df['IP']):.3f}")
print(f"  SP only r(PE, IP)         = {df[df.role=='SP']['PE'].corr(df[df.role=='SP']['IP']):.3f}")
print(f"  RP only r(PE, IP)         = {df[df.role=='RP']['PE'].corr(df[df.role=='RP']['IP']):.3f}")
# compare to old PE1.0
df['PE1'] = 100*df['outs']/((1+df['totalBases'])*df['numberOfPitches'])
print(f"  [PE1.0 for contrast] r(PE1, IP) = {df['PE1'].corr(df['IP']):.3f}")
print(f"  mean PE by role: SP {df[df.role=='SP'].PE.mean():.2f}  RP {df[df.role=='RP'].PE.mean():.2f}")
print(f"  mean PE1 by role: SP {df[df.role=='SP'].PE1.mean():.3f}  RP {df[df.role=='RP'].PE1.mean():.3f}")

print("\n=== Correlations of PE with skill metrics (lower ERA/FIP better) ===")
for m in ['ERA','FIP','K9','BB9','HR9','OPS','whip']:
    col = 'era' if m=='ERA' else m
    print(f"  r(PE, {m:4}) = {df['PE'].corr(df[col]):.3f}")

print("\n=== Year-to-year stability (reliability) ===")
p = df.pivot_table(index='player_id', columns='season', values='PE')
for a,b in [(2023,2024),(2024,2025)]:
    sub=p[[a,b]].dropna()
    print(f"  r(PE_{a}, PE_{b}) = {sub[a].corr(sub[b]):.3f}  (n={len(sub)})")
# compare ERA stability
pe_era=df.pivot_table(index='player_id',columns='season',values='era')
for a,b in [(2023,2024),(2024,2025)]:
    sub=pe_era[[a,b]].dropna()
    print(f"  r(ERA_{a},ERA_{b}) = {sub[a].corr(sub[b]):.3f}  (n={len(sub)})")
# SP-only PE stability
for role in ['SP','RP']:
    ps=df[df.role==role].pivot_table(index='player_id',columns='season',values='PE')
    rs=[]
    for a,b in [(2023,2024),(2024,2025)]:
        s=ps[[a,b]].dropna(); rs.append(s[a].corr(s[b]))
    print(f"  {role} PE stability: {rs[0]:.3f}, {rs[1]:.3f}")

print("\n=== w sensitivity: Spearman rank corr of PE(w) vs PE(w=4) ===")
base = 100*df['outs']/(df['numberOfPitches']+4*df['totalBases'])
for w in [0,1,2,3,4,5,6,8,12]:
    pe_w = 100*df['outs']/(df['numberOfPitches']+w*df['totalBases'])
    print(f"  w={w:2}: spearman={pe_w.corr(base,method='spearman'):.4f}   r(PE_w,IP)={pe_w.corr(df['IP']):.3f}")

print("\n=== Top 15 PE (all, IP>=50) ===")
cols=['season','player_name','team','role','IP','numberOfPitches','totalBases','PE','era','FIP']
print(df.sort_values('PE',ascending=False).head(15)[cols].to_string(index=False))

print("\n=== Top 12 PE among SP only ===")
print(df[df.role=='SP'].sort_values('PE',ascending=False).head(12)[cols].to_string(index=False))

print("\n=== Team average PE (2023-2025 pooled, top/bottom 6) ===")
tm=df.groupby('team')['PE'].mean().sort_values(ascending=False)
print(tm.head(6).round(2).to_string()); print('...'); print(tm.tail(6).round(2).to_string())

df.to_csv('pe_computed.csv',index=False)
print("\nsaved pe_computed.csv")
