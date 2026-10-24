"""Figures for the practice exercises of Labs 2-3 (practice_slides.py). Values are demo values, not on any card:
RC 10 kOhm + 100 nF, RLC 1 mH + 100 nF + 100 Ohm, voltage follower. Writes fig/p2_*.png, fig/p3_*.png."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import schemdraw, schemdraw.elements as elm

schemdraw.config(fontsize=16, lw=2)
F = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/'


def rc(name, first, second, l1, l2, out):
    with schemdraw.Drawing(file=F + name, dpi=200, show=False) as d:
        elm.SourceSin().up().length(3).label('Function\ngenerator', loc='bottom', ofst=0.3)
        elm.Dot().label('CH1', loc='left', ofst=0.15)
        first().right().length(3.5).label(l1)
        top = d.here; elm.Dot()
        second().down().length(3).label(l2, loc='bottom')
        elm.Line().left(3.5)
        elm.Line().at(top).right(2); elm.Dot(open=True).label(f'CH2\n({out})', loc='right')
        elm.Line().at((3.5, 0)).right(2); elm.Dot(open=True)
        elm.Ground().at((0, 0))


rc('p2_lp.png', elm.Resistor, elm.Capacitor, 'R = 10 kΩ', 'C = 100 nF\n(104)', 'across C')
rc('p2_hp.png', elm.Capacitor, elm.Resistor, 'C = 100 nF (104)', 'R = 10 kΩ', 'across R')

with schemdraw.Drawing(file=F + 'p2_rlc.png', dpi=200, show=False) as d:
    elm.SourceSin().up().length(3).label('Function\ngenerator', loc='bottom', ofst=0.3)
    elm.Dot().label('CH1', loc='left', ofst=0.15)
    elm.Inductor2(loops=3).right().length(3).label('L = 1 mH')
    elm.Capacitor().right().length(3).label('C = 100 nF\n(104)')
    top = d.here; elm.Dot()
    elm.Resistor().down().length(3).label('R = 100 Ω', loc='bottom')
    elm.Line().left(6)
    elm.Line().at(top).right(2); elm.Dot(open=True).label('CH2\n(across R)', loc='right')
    elm.Line().at((6, 0)).right(2); elm.Dot(open=True)
    elm.Ground().at((0, 0))

with schemdraw.Drawing(file=F + 'p3_follower.png', dpi=200, show=False) as d:
    op = elm.Opamp(leads=True)
    elm.Label().at(op.in1).label('2', loc='top', ofst=(0.25, 0.05))
    elm.Label().at(op.in2).label('3', loc='bottom', ofst=(0.25, -0.05))
    elm.Label().at(op.out).label('1', loc='top', ofst=(-0.25, 0.05))
    elm.Line().at(op.out).right(1); out = d.here; elm.Dot()
    elm.Line().right(1); elm.Dot(open=True).label('Vout\n(CH1)', loc='right')
    elm.Line().at(out).up(1.6)
    elm.Line().tox(op.in1).to((op.in1[0] - 0.6, out[1] + 1.6))
    elm.Line().toy(op.in1)
    elm.Line().tox(op.in1)
    elm.Line().at(op.in2).left(1.2); elm.Dot().label('Vin\n(CH2)', loc='top')
    elm.SourceSin().down().length(2.2).label('Function\ngenerator', loc='bottom', ofst=0.3)
    elm.Ground()

# clipping: what the output looks like when the input is too big (no numbers: the students read their own)
t = np.linspace(0, 2, 600); v = 1.35 * np.sin(2 * np.pi * t)
fig, ax = plt.subplots(figsize=(5.2, 3.4), dpi=170)
ax.plot(t, np.clip(v, -1.0, 0.85), color='#1f77b4', lw=2.5, label='output (CH1)')
ax.plot(t, v, color='#999', lw=1.2, ls='--', label='what it should be')
ax.axhline(0, color='#555', lw=0.8); ax.set_yticks([]); ax.set_xticks([])
ax.annotate('flat top = clipping', (0.25, 0.85), (0.55, 1.25), arrowprops=dict(arrowstyle='->', color='#c0392b'), color='#c0392b', fontsize=12)
ax.set_ylim(-1.6, 1.6); ax.legend(loc='lower right', fontsize=9, frameon=False)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.set_xlabel('time'); fig.tight_layout(); fig.savefig(F + 'p3_clip.png'); plt.close(fig)

# capacitor code: the rule and one example (the students read the other codes themselves)
fig, ax = plt.subplots(figsize=(5.2, 3.2), dpi=170); ax.axis('off')
ax.text(0.5, 0.92, 'Reading a capacitor code', ha='center', fontsize=15, weight='bold')
for x, (ch, c) in zip((0.30, 0.42, 0.54), (('1', '#1f77b4'), ('0', '#1f77b4'), ('3', '#c0392b'))):
    ax.text(x, 0.62, ch, ha='center', fontsize=40, weight='bold', color=c, family='DejaVu Sans Mono')
ax.text(0.36, 0.42, 'first 2 digits', ha='center', fontsize=11, color='#1f77b4')
ax.text(0.62, 0.42, 'number of zeros', ha='left', fontsize=11, color='#c0392b')
ax.text(0.5, 0.2, '10 000 pF = 10 nF', ha='center', fontsize=16)
ax.text(0.5, 0.04, 'The value is in pF.  1 nF = 1000 pF', ha='center', fontsize=11, color='#555')
fig.savefig(F + 'p2_capcode.png'); plt.close(fig)
print('ok')
