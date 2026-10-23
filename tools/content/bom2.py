import collections, math, runpy
V=runpy.run_path(__file__.replace('bom2.py','variants.py'))['D1']
need=collections.defaultdict(collections.Counter)
def R(v): return ('R',v)
# ---- tiêu hao, tính cho cả 3 lớp ----
for code, d in V.items():
    if code % 100 > 19: continue        # 18 students + 1 possible 4th member per class
    for k in 'ABCD': need[R(d[k][2])]['N1']+=1; need[R(d[k][3])]['N1']+=1
for r in (2200,4700): need[R(r)]['N1']+=54          # cầu chia áp/dòng
for r in [1000,2200,4700]: need[R(r)]['N2']+=18   # RC khởi động (3 lớp × 6)
for c in ['10nF','22nF','47nF']: need[('Cf',c)]['N2']+=18
need[('Cf','22nF')]['N2']+=54; need[('Cf','2.2nF')]['N2']+=54   # RLC: 22nF // 2.2nF
for r,q in ((47,2),(100,2),(220,1)): need[R(r)]['N2']+=54*q     # ghép R theo Q
for a,b in [(220,1200),(1200,47000),(3900,4700)]:
    need[R(a)]['N3']+=18; need[R(b)]['N3']+=18
need[('Cc','100nF')]['N3']+=108
for r,q in [(10000,5),(2200,2),(4700,1),(47000,1)]: need[R(r)]['N4']+=18*q
need[('Cc','1nF')]['N4']+=18; need[('Cc','100nF')]['N4']+=18*4
for r,q in [(100,2),(220,3),(330,2),(470,2),(1000,3),(1500,2),(2200,2),(3300,2),(4700,3),(6800,1),(10000,3),(15000,2)]: need[R(r)]['Thi']+=18*q
for c in ['10nF','22nF','33nF','47nF','100nF']: need[('Cf',c)]['Thi']+=36   # tụ khay thi: tiêu hao (nhìn giống nhau)
need[('Cf','220nF')]['Thi']+=18
# ---- thu hồi, dùng chung 3 lớp (không nhân 3) ----
need[('L','1mH 0410-102')]['N2']+=54   # tiêu hao: nhìn giống điện trở
need[('IC','LM358L (DIP-8)')]['N3']+=18
need[('Ce','470µF 25V')]['N3']+=12; need[('Ce','470µF 25V')]['N4']+=12
need[('Ce','1µF 50V')]['N4']+=18; need[('Ce','10µF 25V')]['N4']+=18   # tiêu hao: 2 loại lon nhỏ giống nhau
need[('MIC','Electret')]['N4']+=6
need[('LED','LED 5mm')]['N1']+=18
spare={'R':0.15,'LED':0.1,'Cf':0.2,'Cc':0.2,'Ce':0.25,'L':0.1,'IC':0.5,'MIC':0.3}
reuse={'IC','MIC','LED'}   # + tụ 470µF (xử lý riêng)
