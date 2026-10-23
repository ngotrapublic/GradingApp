import itertools, random, collections
E12=[1.0,1.2,1.5,1.8,2.2,2.7,3.3,3.9,4.7,5.6,6.8,8.2]
e12=[v*10**d for d in range(1,6) for v in E12]
STD=[220,330,470,680,1000,1500,2200,3300,4700,6800,10000,15000,22000]
def nonstd(x): return min(abs(x/v-1) for v in e12)>0.03
cands={}
for a,b in itertools.combinations_with_replacement(STD,2):
    for val,t in ((a+b,'+'),(a*b/(a+b),'//')):
        if nonstd(val) and round(val) not in cands: cands[round(val)]=(val,t,a,b)
cl=list(cands.values())
print('candidates',len(cl))
random.seed(11)
used=set(); D1=[]
while len(D1)<18:
    A,B,C=random.sample([x for x in cl if 1500<=x[0]<=15000 and round(x[0]) not in used],2)+[random.choice([x for x in cl if 600<=x[0]<=6000 and round(x[0]) not in used])]
    if len({round(A[0]),round(B[0]),round(C[0])})<3: continue
    Rp=A[0]*B[0]/(A[0]+B[0]); R=Rp+C[0]; I=5/R
    if not 0.5e-3<I<2.5e-3: continue
    used.update({round(A[0]),round(B[0]),round(C[0])})
    VX=I*C[0]; IA=(5-VX)/A[0]
    D1.append(dict(A=A,B=B,C=C,Req=R,I=I,IA=IA,VX=VX))
cnt=collections.Counter()
def f(r): return f'{r/1000:g}k' if r>=1000 else f'{r:g}'
for i,d in enumerate(D1,1):
    for k in 'ABC': cnt[d[k][2]]+=1; cnt[d[k][3]]+=1
    print(f'D1-{i:02d}',' | '.join(f"R{k}={d[k][0]:.0f} ({f(d[k][2])}{d[k][1]}{f(d[k][3])})" for k in 'ABC'),f"Req={d['Req']:.0f} I={d['I']*1e3:.3f}mA IA={d['IA']*1e3:.3f}mA VX={d['VX']:.3f}V")
print(sorted((k,v) for k,v in cnt.items()))
