import itertools, random

def tm(i):
    """Variant index 0..23 -> (team 1..6, member 1..4). Member 4 exists only for a team of 4."""
    return (i // 3 + 1, i % 3 + 1) if i < 18 else (i - 17, 4)

E24 = [1.0,1.1,1.2,1.3,1.5,1.6,1.8,2.0,2.2,2.4,2.7,3.0,3.3,3.6,3.9,4.3,4.7,5.1,5.6,6.2,6.8,7.5,8.2,9.1]
e24 = [v * 10 ** d for d in range(1, 6) for v in E24]
STD = [220, 330, 470, 680, 1000, 1500, 2200, 3300, 4700, 6800, 10000, 15000, 22000]   # kit values
def nonstd(x): return min(abs(x / v - 1) for v in e24) > 0.03     # not sold as a single resistor
cands = {}
for a_, b_ in itertools.combinations_with_replacement(STD, 2):
    for val, t in ((a_ + b_, '+'), (a_ * b_ / (a_ + b_), '//')):
        if nonstd(val) and round(val) not in cands: cands[round(val)] = (val, t, a_, b_)
cl = list(cands.values())
def make_class(seed):
    """Circuit: 5 V -> (R_A // R_B) -> node X -> R_C -> R_D -> 0 V. Each value used at most 3 times per class."""
    random.seed(seed); count = {}; out = []; seen = set()
    big = [x for x in cl if 1500 <= x[0] <= 15000]; small = [x for x in cl if 500 <= x[0] <= 5000]
    while len(out) < 24:
        A, B = random.sample(big, 2); C, D = random.sample(small, 2)
        key = tuple(round(x[0]) for x in (A, B, C, D))
        if len(set(key)) < 4 or key in seen or any(count.get(v, 0) >= 3 for v in key): continue
        Rp = A[0] * B[0] / (A[0] + B[0]); R = Rp + C[0] + D[0]; I = 5 / R
        if not 0.5e-3 < I < 2.0e-3: continue
        seen.add(key)
        for v in key: count[v] = count.get(v, 0) + 1
        VX = I * (C[0] + D[0]); IA = (5 - VX) / A[0]
        out.append(dict(A=A, B=B, C=C, D=D, Req=R, I=I, IA=IA, VX=VX))
    return out
D1 = {}
for cls, seed in ((1, 11), (2, 23), (3, 37)):
    for i, d in enumerate(make_class(seed), 1): D1[cls * 100 + i] = d
fmt=lambda r: f'{r/1000:g} kΩ' if r>=1000 else f'{r:g} Ω'

# ---------------- Lab 2 ----------------
import math
L2, C2 = 1e-3, 22e-9 + 2.2e-9
F0 = 1 / (2 * math.pi * math.sqrt(L2 * C2)); Z0 = math.sqrt(L2 / C2)
QSET = [1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
TYPES = ['Low-pass (output across C)', 'High-pass (output across L)', 'Band-pass (output across R)']
RC = [(r, c) for r in (1000, 2200, 4700) for c in (10e-9, 22e-9, 47e-9)]
D2 = {}
for cls in (1, 2, 3):
    rot = (cls - 1) * 2  # different Q order per class
    for i in range(24):
        team, member = tm(i); team -= 1
        Q = QSET[(team + rot + (3 if member == 4 else 0)) % 6]
        t = member - 1 if member <= 3 else team % 3
        k = 1 - 1 / (2 * Q * Q)
        if t == 0: fmax, third = F0 * math.sqrt(k), Q / math.sqrt(1 - 1 / (4 * Q * Q))
        elif t == 1: fmax, third = F0 / math.sqrt(k), Q / math.sqrt(1 - 1 / (4 * Q * Q))
        else: fmax, third = F0, F0 / Q
        r, c = RC[(i + 3 * cls + (1 if member == 4 else 0)) % 9]
        D2[cls * 100 + i + 1] = dict(team=team + 1, member=member, type=t, Q=Q, Rtot=Z0 / Q, fmax=fmax, third=third,
                                    rc_r=r, rc_c=c, fc=1 / (2 * math.pi * r * c), rc_kind=('Low-pass', 'High-pass')[i % 2])

# ---------------- Lab 4 ----------------
def _g1(f):
    zf = 30e3 / math.sqrt(1 + (2 * math.pi * f * 30e3 * 1e-9) ** 2)
    return zf / 2.2e3
D4 = {}
for cls in (1, 2, 3):
    for i in range(24):
        team, member = tm(i)
        val = [10 * _g1(1e3), 10 * _g1(1e3) * 4.7 / 2.2, 10 * _g1(5e3), 10 * _g1(5e3) * 4.7 / 2.2][member - 1]
        D4[cls * 100 + i + 1] = dict(team=team, member=member, vpp=val)

# ---------------- Lab 3 ----------------
PAIRS = [(220, 1200), (1200, 47000), (3900, 4700)]
VIN = {0: [0.3, 0.4, 0.6, 0.8, 1.0, 1.2], 1: [0.05, 0.06, 0.08, 0.10, 0.12, 0.15], 2: [1.0, 1.5, 2.0, 3.0, 4.0, 5.0]}
FREQ = [200, 300, 500, 700, 1000, 1500, 2000]
D3 = {}
for cls in (1, 2, 3):
    for i in range(24):
        team, member = tm(i); team -= 1
        m = member - 1 if member <= 3 else team % 3          # member 4: same pair types, other Vin / f
        r1, r2 = PAIRS[m]
        vin = VIN[m][(team + 2 * cls + (3 if member == 4 else 0)) % 6]
        f = FREQ[(team * 3 + m + cls + (4 if member == 4 else 0)) % 7]
        g3 = r2 / r1
        D3[cls * 100 + i + 1] = dict(team=team + 1, member=member, r1=r1, r2=r2, gain=g3, vin=vin, f=f, vout=vin * g3)
