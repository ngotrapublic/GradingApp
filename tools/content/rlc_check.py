"""Lab 2 Task 2 (RLC): will real parts and the real measurement give marks close to the answer keys?

AC analysis of the series RLC (the same equations a SPICE .ac run solves) with:
  - part tolerances: L +/-10 %, each C +/-5 % (or 10 %), resistors +/-1 %
  - inductor wire resistance R_L (DC) and core/AC loss at ~32 kHz, given as the inductor's own quality factor Q_L
  - 10X probe load (10 MOhm // 15 pF) on Vin and Vout; Vin is measured at the filter input, so the generator's
    50 Ohm output does not change Vout/Vin
  - the student's R: the closest value made from 47, 47, 100, 100, 220 Ohm to (R_total - R_L), as on the slides
  - the student's sweep: the 9 frequencies of the card + 2 extra points around the highest reading
Prints, per filter type and Q, the share of simulated circuits whose answers are within 10 % (full marks) of the key.

    python rlc_check.py
"""
import itertools, math, random

L0, C0 = 1e-3, 22e-9 + 2.2e-9
F0 = 1 / (2 * math.pi * math.sqrt(L0 * C0)); Z0 = math.sqrt(L0 / C0)
QS = (1.5, 1.75, 2.0, 2.25, 2.5, 3.0)
CARD = [round(F0 * m / 1e3, 1) * 1e3 for m in (0.25, 0.5, 0.7, 0.85, 1, 1.15, 1.4, 2, 4)]
PROBE = lambda w: 1 / (1 / 10e6 + 1j * w * 15e-12)


def r_choices():
    """Every value the student can make from 47, 47, 100, 100, 220 Ohm: one resistor, two or three in series,
    two in parallel, two in parallel plus one in series."""
    parts = [47, 47, 100, 100, 220]; out = set()
    for k in (1, 2, 3):
        for c in itertools.combinations(parts, k):
            out.add(sum(c))
    for a, b in itertools.combinations(parts, 2):
        out.add(a * b / (a + b))
        for c in parts:
            out.add(a * b / (a + b) + c)
    return sorted(out)


R_OPTIONS = r_choices()


def keys(kind, Q):
    k = math.sqrt(1 - 1 / (2 * Q * Q)); peak = Q / math.sqrt(1 - 1 / (4 * Q * Q))
    if kind == 'LP': return Z0 / Q, F0 * k, peak
    if kind == 'HP': return Z0 / Q, F0 / k, peak
    return Z0 / Q, F0, F0 / Q                                    # band-pass: last value is BW


def gain(kind, f, R, L, C, RL, QL):
    w = 2 * math.pi * f
    zl = RL + 1j * w * L + (w * L / QL if QL else 0)            # wire resistance + loss at this frequency
    zc = 1 / (1j * w * C); zr = R
    out = {'LP': zc, 'HP': zl, 'BP': zr}[kind]
    zo = out * PROBE(w) / (out + PROBE(w))                       # probe across the output part
    rest = zr + zl + zc - out
    return abs(zo / (zo + rest))


def one(kind, Q, tolC, RL_dc, QL, rng):
    L = L0 * rng.uniform(0.9, 1.1); C = (22e-9 * rng.uniform(1 - tolC, 1 + tolC) + 2.2e-9 * rng.uniform(1 - tolC, 1 + tolC))
    RL = RL_dc * rng.uniform(0.9, 1.1)
    target = Z0 / Q - RL                                         # the student measures R_L and builds R = R_total - R_L
    R = min(R_OPTIONS, key=lambda x: abs(x - target)) * rng.uniform(0.99, 1.01)
    Rtot = R + RL                                                # measured with the ohmmeter (DC)
    g = lambda f: gain(kind, f, R, L, C, RL, QL)
    pts = {f: g(f) for f in CARD}
    i = CARD.index(max(pts, key=pts.get))
    for j in (i - 1, i + 1):                                     # 2 extra points around the highest reading
        if 0 <= j < len(CARD):
            fx = (CARD[i] + CARD[j]) / 2; pts[fx] = g(fx)
    fmax = max(pts, key=pts.get); peak = pts[fmax]
    if kind == 'BP':                                             # f_L, f_H found by turning the frequency knob
        lim = 0.707 * max(g(f) for f in [F0 * (0.8 + k / 500) for k in range(200)])
        lo, hi = F0 / 3, F0
        for _ in range(40): mid = (lo + hi) / 2; lo, hi = (mid, hi) if g(mid) < lim else (lo, mid)
        fl = lo; lo, hi = F0, 3 * F0
        for _ in range(40): mid = (lo + hi) / 2; lo, hi = (lo, mid) if g(mid) < lim else (mid, hi)
        last = hi - fl
    else:
        last = peak
    return Rtot, fmax, last


def run(tolC=0.05, RL_dc=15, QL=30, n=2000, seed=1):
    rng = random.Random(seed); rows = []
    for kind in ('LP', 'HP', 'BP'):
        for Q in QS:
            k = keys(kind, Q); ok = [0, 0, 0]
            for _ in range(n):
                got = one(kind, Q, tolC, RL_dc, QL, rng)
                for i in range(3):
                    ok[i] += abs(got[i] / k[i] - 1) <= 0.10
            rows.append((kind, Q, *(100 * x / n for x in ok)))
    return rows


if __name__ == '__main__':
    print(f'f0 = {F0:.0f} Hz, Z0 = {Z0:.1f} Ohm. R values the student can make: {len(R_OPTIONS)}')
    for title, kw in [('Ideal inductor (no loss), C +/-5 %', dict(RL_dc=15, QL=None)),
                      ('Inductor Q_L = 50 at 32 kHz, C +/-5 %', dict(RL_dc=15, QL=50)),
                      ('Inductor Q_L = 30 at 32 kHz, C +/-5 %', dict(RL_dc=15, QL=30)),
                      ('Inductor Q_L = 20 at 32 kHz, C +/-10 %', dict(RL_dc=15, QL=20, tolC=0.10))]:
        print(f'\n{title}   (% of circuits within 10 % of the key: R_total | f_max | peak or BW)')
        for kind, Q, a, b, c in run(**kw):
            print(f'  {kind}  Q={Q:<4}  {a:5.0f}  {b:5.0f}  {c:5.0f}')
