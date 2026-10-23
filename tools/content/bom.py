import collections, math, runpy, io, contextlib
with contextlib.redirect_stdout(io.StringIO()): g=runpy.run_path(__file__.replace('bom.py','design.py'))
D1=g['D1']
need=collections.defaultdict(lambda: collections.Counter())  # item -> day -> qty
def R(v): return ('R',v)
for d in D1:
    for k in 'ABC': need[R(d[k][2])]['N1']+=1; need[R(d[k][3])]['N1']+=1
need[R(2200)]['N1']+=18; need[R(4700)]['N1']+=18          # cầu chia áp/dòng demo
need[('LED','LED 5mm đỏ')]['N1']+=18
# Day 2: RC warm-up 6R x 3C
for r in [1000,1500,2200,3300,4700,6800]: need[R(r)]['N2']+=3
for c in ['10nF','22nF','47nF']: need[('Cf',c)]['N2']+=6
# RLC: Q -> resistors, each Q x3 (LP/HP/BP)
for rs in [[1000,1000],[1000,330],[1000],[680],[470],[390]]:
    for r in rs: need[R(r)]['N2']+=3
need[R(47)]['N2']+=18; need[R(100)]['N2']+=18   # tinh chỉnh bù R cuộn cảm
need[('L','10mH')]['N2']+=18
need[('Cf','2.2nF')]['N2']+=18
need[('Cc','270pF')]['N2']+=18
# Day 3: per student LM358 + pair; 6 of each pair
for a,b in [(220,1200),(1200,47000),(3900,4700)]:
    need[R(a)]['N3']+=6; need[R(b)]['N3']+=6
need[('IC','LM358 (DIP-8)')]['N3']+=18
need[('Cc','100nF')]['N3']+=36
need[('Ce','470µF 25V')]['N3']+=12
# Day 4: per cluster (6)
for r,q in [(10000,5),(2200,2),(4700,1),(47000,1)]: need[R(r)]['N4']+=6*q
for item,q in [(('Ce','1µF 50V'),1),(('Ce','10µF 25V'),1),(('Ce','470µF 25V'),4),(('Cc','1nF'),1),(('Cc','100nF'),4),(('IC','LM358 (DIP-8)'),1),(('MIC','Electret 6x5mm chân dài'),1),(('Cf','100nF'),2)]:
    need[item]['N4']+=6*q
# Exam tray per team x6
for r,q in [(100,2),(220,3),(330,2),(470,2),(1000,3),(1500,2),(2200,2),(3300,2),(4700,3),(6800,1),(10000,3),(15000,2)]: need[R(r)]['Thi']+=6*q
for c in ['10nF','22nF','33nF','47nF','100nF','220nF','470nF']: need[('Cf',c)]['Thi']+=12
need[('Ce','1µF 50V')]['Thi']+=12
spare={'R':0.5,'LED':0.5,'Cf':0.3,'Cc':0.3,'Ce':0.3,'L':0.2,'IC':0.5,'MIC':0.5}
rows=[]
def name(k):
    t,v=k
    if t=='R': return 'Điện trở '+(f'{v/1000:g}kΩ' if v>=1000 else f'{v:g}Ω')
    return {'LED':'','Cf':'Tụ film (polyester) ','Cc':'Tụ gốm NP0/C0G ' if v in('270pF','1nF') else 'Tụ gốm ','Ce':'Tụ hóa ','L':'Cuộn cảm ','IC':'IC ','MIC':'Micro '}[t]+v
order={'R':0,'Cc':1,'Cf':2,'Ce':3,'L':4,'IC':5,'MIC':6,'LED':7}
for k in sorted(need,key=lambda k:(order[k[0]],k[1] if k[0]=='R' else str(k[1]))):
    c=need[k]; tot=sum(c.values()); st=10 if k[0]=="R" else 5; buy=math.ceil(tot*(1+spare[k[0]])/st)*st
    rows.append((name(k),c['N1'],c['N2'],c['N3'],c['N4'],c['Thi'],tot,f"{int(spare[k[0]]*100)}%",buy))
for r in rows: print(r)
import json; json.dump(rows,open(__file__.replace('bom.py','bom.json'),'w'),ensure_ascii=False)
