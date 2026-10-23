import math, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

SEQ = [1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 0.1, 0.2, 0.5, 1, 2, 5]
TSEQ = [b * 10 ** e for e in range(-6, -1) for b in (1, 2, 4, 5)]  # scope-like time/div incl 400us


def vfmt(v):
    return f'{v*1000:.1f}mV' if v < 1 else f'{v:.3f}V' if v < 10 else f'{v:.2f}V'


def divfmt(v):
    return f'{v*1000:g}mV' if v < 1 else f'{v:g}V'


def tfmt(t):
    return f'{t*1e6:g}µs' if t < 1e-3 else f'{t*1e3:g}ms'


def ffmt(f):
    return f'{f:.1f}Hz' if f < 1000 else f'{f/1000:.3f}kHz'


def draw(path, vin, vout, f, tag, seed=0):
    """Simulated TBS1000C screen. CH1 (yellow) = output, CH2 (blue) = input. Scales are written as 'per division'
    and the measurement box sits beside the screen, so students read the numbers without guessing."""
    rng = np.random.default_rng(seed)
    vdiv1 = min(v for v in SEQ if vout / v <= 6.2)   # CH1 output
    vdiv2 = min(v for v in SEQ if vin / v <= 6.2)    # CH2 input
    tdiv = min(t for t in TSEQ if 10 * t * f >= 3)
    fig = plt.figure(figsize=(11, 5.6), dpi=130)
    fig.patch.set_facecolor('#e9e9e6')
    ax = fig.add_axes([0.03, 0.17, 0.70, 0.70])
    ax.set_facecolor('black'); ax.set_xlim(-5, 5); ax.set_ylim(-4, 4)
    for sp in ax.spines.values(): sp.set_color('#555')
    ax.set_xticks([]); ax.set_yticks([])
    for x in range(-5, 6): ax.axvline(x, color='#3a3a3a', lw=0.6, ls=(0, (1, 3)))
    for y in range(-4, 5): ax.axhline(y, color='#3a3a3a', lw=0.6, ls=(0, (1, 3)))
    ax.axvline(0, color='#5a5a5a', lw=0.7); ax.axhline(0, color='#5a5a5a', lw=0.7)
    t = np.linspace(-5 * tdiv, 5 * tdiv, 2500)
    ph = rng.uniform(0, 2 * math.pi)
    vi = vin / 2 * np.sin(2 * math.pi * f * t + ph) + rng.normal(0, vin * 0.006 + 0.0008, t.size)
    vo = -vout / 2 * np.sin(2 * math.pi * f * t + ph) + rng.normal(0, vout * 0.004 + 0.002, t.size)
    ax.plot(t / tdiv, vi / vdiv2, color='#25d6e8', lw=1.1)
    ax.plot(t / tdiv, vo / vdiv1, color='#f4e04d', lw=1.1)
    ax.text(-5.15, 0, '1▸', color='#c9b000', fontsize=8, va='center', ha='right')
    ax.text(-5.15, -0.25, '2▸', color='#1597a5', fontsize=8, va='center', ha='right')
    # header
    fig.text(0.03, 0.935, 'Tek', fontsize=11, weight='bold', color='#222')
    fig.text(0.08, 0.935, 'Run', fontsize=10, color='#2a7a2a')
    fig.text(0.13, 0.935, "Trig'd", fontsize=10, color='#222')
    fig.text(0.25, 0.935, 'CH1 (yellow) = output', fontsize=10, color='#8a7a00', weight='bold')
    fig.text(0.47, 0.935, 'CH2 (blue) = input', fontsize=10, color='#1597a5', weight='bold')
    fig.text(0.97, 0.935, tag, fontsize=8, color='#777', ha='right')
    # measurement box beside the screen
    m = lambda v, e=0.01: v * (1 + rng.uniform(-e, e))
    rows = [('CH1', 'Pk-Pk', vfmt(m(vout)), '#f4e04d'), ('CH1', 'Frequency', ffmt(m(f, 0.002)), '#f4e04d'),
            ('CH2', 'Pk-Pk', vfmt(m(vin)), '#25d6e8'), ('CH2', 'Frequency', ffmt(m(f, 0.002)), '#25d6e8')]
    fig.patches.append(Rectangle((0.755, 0.17), 0.215, 0.70, transform=fig.transFigure, color='#2b2b2b'))
    fig.text(0.8625, 0.83, 'Measurements', fontsize=9.5, color='#ddd', ha='center', va='center', weight='bold')
    for i, (ch, name, val, c) in enumerate(rows):
        y0 = 0.73 - i * 0.15
        fig.patches.append(Rectangle((0.765, y0 - 0.025), 0.05, 0.05, transform=fig.transFigure, color=c))
        fig.text(0.79, y0, ch, fontsize=8, ha='center', va='center', weight='bold')
        fig.text(0.825, y0, name, fontsize=9, va='center', color='#ddd')
        fig.text(0.96, y0 - 0.06, val, fontsize=12, va='center', ha='right', color='white', weight='bold')
    # scales: per division (one square of the grid)
    y = 0.085
    fig.patches.append(Rectangle((0.03, y - 0.025), 0.05, 0.05, transform=fig.transFigure, color='#f4e04d'))
    fig.text(0.055, y, 'CH1', fontsize=9, ha='center', va='center', weight='bold')
    fig.text(0.09, y, f'{divfmt(vdiv1)}/div', fontsize=11, va='center')
    fig.patches.append(Rectangle((0.22, y - 0.025), 0.05, 0.05, transform=fig.transFigure, color='#25d6e8'))
    fig.text(0.245, y, 'CH2', fontsize=9, ha='center', va='center', weight='bold')
    fig.text(0.28, y, f'{divfmt(vdiv2)}/div', fontsize=11, va='center')
    fig.text(0.42, y, f'Time {tfmt(tdiv)}/div', fontsize=11, va='center')
    fig.text(0.60, y, 'Trigger: CH2', fontsize=10, va='center', color='#1597a5')
    fig.text(0.755, y, 'div = one square of the grid', fontsize=9, va='center', color='#666')
    fig.savefig(path, facecolor=fig.get_facecolor()); plt.close(fig)
    return dict(vdiv1=vdiv1, vdiv2=vdiv2, tdiv=tdiv)
