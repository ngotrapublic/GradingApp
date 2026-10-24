"""Frequency-response figures for the Lab 2 RLC theory slides (low-pass, high-pass, band-pass, X_L / X_C)."""
import math, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig'
L, C = 1e-3, 24.2e-9
F0 = 1 / (2 * math.pi * math.sqrt(L * C)); Z0 = math.sqrt(L / C)
f = np.logspace(math.log10(4e3), math.log10(260e3), 1200)
G, OR, BL, GR = '#3f7a2a', '#c77c00', '#1f5fa8', '#888888'
plt.rcParams.update({'font.size': 13, 'font.family': 'DejaVu Sans'})


def H(kind, Q, f=f, Rl_share=0.0):
    Rt = Z0 / Q; w = 2 * np.pi * f
    zl, zc = 1j * w * L, 1 / (1j * w * C)
    z = Rt + zl + zc
    return np.abs({'LP': zc, 'HP': zl, 'BP': Rt * (1 - Rl_share)}[kind] / z)


def axes(ax, ylab='$V_{out}$ / $V_{in}$'):
    ax.set_xscale('log'); ax.set_xlabel('Frequency (kHz)'); ax.set_ylabel(ylab)
    ax.set_xticks([5e3, 10e3, 20e3, 32.35e3, 50e3, 100e3, 200e3]); ax.set_xticklabels(['5', '10', '20', '$f_0$\n32.4', '50', '100', '200'])
    ax.grid(True, which='both', color='#e5e5e5'); ax.set_xlim(f[0], f[-1])
    for s in ('top', 'right'): ax.spines[s].set_visible(False)


def lp_hp(kind, name):
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=150)
    for Q, c in ((0.71, GR), (1.5, BL), (3.0, G)):
        ax.plot(f, H(kind, Q), color=c, lw=2.2, label=f'Q = {Q:g}')
    Q = 3.0; k = math.sqrt(1 - 1 / (2 * Q * Q)); fm = F0 * k if kind == 'LP' else F0 / k; pk = Q / math.sqrt(1 - 1 / (4 * Q * Q))
    ax.plot([fm], [pk], 'o', color=OR, ms=8, zorder=5)
    ax.annotate('highest $V_{out}$/$V_{in}$\nat $f_{max}$', (fm, pk), xytext=(fm * (0.33 if kind == 'LP' else 3.2), pk * (0.92 if kind == 'LP' else 0.62)), color=OR,
                arrowprops=dict(arrowstyle='->', color=OR), ha='center')
    ax.axhline(1, color='#bbb', lw=1, ls='--'); ax.text(f[0] * 1.05 if kind == 'LP' else f[-1] / 1.05, 1.05, '$V_{out}$ = $V_{in}$', color='#888',
                                                        ha='left' if kind == 'LP' else 'right', fontsize=11)
    axes(ax); ax.set_ylim(0, 3.4); ax.legend(loc='upper right' if kind == 'LP' else 'upper left', frameon=False)
    fig.tight_layout(); fig.savefig(f'{OUT}/{name}.png'); plt.close(fig)


def xlxc():
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=150)
    w = 2 * np.pi * f
    ax.plot(f, w * L, color=BL, lw=2.4, label='$X_L$ = 2πfL  (grows with f)')
    ax.plot(f, 1 / (w * C), color=OR, lw=2.4, label='$X_C$ = 1 / (2πfC)  (falls with f)')
    ax.plot([F0], [Z0], 'o', color=G, ms=9, zorder=5)
    ax.annotate(f'$f_0$: $X_L$ = $X_C$ = $Z_0$ ≈ {Z0:.0f} Ω\nthey cancel → current is maximum', (F0, Z0), xytext=(4.6e3, 3000), color=G,
                arrowprops=dict(arrowstyle='->', color=G))
    ax.text(5e3, 38, 'C blocks (small current)', color=OR, fontsize=12); ax.text(240e3, 38, 'L blocks (small current)', color=BL, fontsize=12, ha='right')
    axes(ax, 'Reactance (Ω)'); ax.set_yscale('log'); ax.set_ylim(30, 8000); ax.legend(loc='lower center', bbox_to_anchor=(0.5, 0.12), frameon=False, fontsize=11)
    fig.tight_layout(); fig.savefig(f'{OUT}/rlc_xlxc.png'); plt.close(fig)


def bp_bw():
    """Bandwidth, as simple as possible: the peak, the 0.707 × peak line, f_L, f_H and the BW arrow."""
    Q = 4.0; share = 0.15                                  # example only (no variant has Q = 4); 15 % of R_total is the coil wire
    fz = np.linspace(18e3, 52e3, 800); y = H('BP', Q, f=fz, Rl_share=share); top = y.max(); lim = 0.707 * top
    fl = F0 * (math.sqrt(1 + 1 / (4 * Q * Q)) - 1 / (2 * Q)); fh = F0 * (math.sqrt(1 + 1 / (4 * Q * Q)) + 1 / (2 * Q))
    fig, ax = plt.subplots(figsize=(7.0, 4.6), dpi=150)
    ax.fill_between(fz, 0, y, where=(fz >= fl) & (fz <= fh), color=G, alpha=0.12)
    ax.plot(fz, y, color=G, lw=3)
    ax.axhline(top, color='#999', lw=1.2, ls='--'); ax.text(51.5e3, top + 0.025, 'peak', color='#555', fontsize=14, ha='right')
    ax.axhline(lim, color=OR, lw=1.5, ls='--'); ax.text(51.5e3, lim + 0.025, '0.707 × peak', color=OR, fontsize=14, ha='right')
    for x, t, dx in ((fl, '$f_L$', -0.6e3), (fh, '$f_H$', 0.6e3)):
        ax.plot([x, x], [0, lim], color=OR, lw=1.3, ls=':'); ax.plot([x], [lim], 'o', color=OR, ms=9)
        ax.text(x + dx, lim + 0.06, t, color=OR, ha='right' if dx < 0 else 'left', fontsize=17, weight='bold')
    ax.annotate('', (fl, 0.2), (fh, 0.2), arrowprops=dict(arrowstyle='<->', color=BL, lw=2))
    ax.text(F0, 0.24, 'BW = $f_H$ − $f_L$', color=BL, ha='center', va='bottom', fontsize=15, weight='bold')
    ax.set_xlim(fz[0], fz[-1]); ax.set_ylim(0, 1.0); ax.set_xlabel('frequency', fontsize=13); ax.set_ylabel('$V_{out}$ / $V_{in}$', fontsize=13)
    ax.set_xticks([F0]); ax.set_xticklabels(['$f_0$']); ax.set_yticks([0, 0.5, 1.0])
    for k in ('top', 'right'): ax.spines[k].set_visible(False)
    fig.tight_layout(); fig.savefig(f'{OUT}/rlc_bp_bw.png'); plt.close(fig)


def minis():
    """Small response shapes for "Filters in real life": low-pass, high-pass, band-pass (no numbers)."""
    for kind, Q, c in (('LP', 0.71, OR), ('HP', 0.71, BL), ('BP', 2.0, G)):
        fig, ax = plt.subplots(figsize=(3.0, 1.3), dpi=170)
        ax.plot(f, H(kind, Q), color=c, lw=3.5); ax.set_xscale('log'); ax.set_xlim(f[0], f[-1]); ax.set_ylim(0, 1.15)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel('frequency', fontsize=10, color='#666')
        for k in ('top', 'right'): ax.spines[k].set_visible(False)
        fig.tight_layout(pad=0.2); fig.savefig(f'{OUT}/rlc_mini_{kind}.png'); plt.close(fig)


def icons():
    """Material Symbols (Rounded, filled; Apache 2.0) for "Filters in real life", in the colour of each filter.
    Needs the font in _build/material_symbols (see poster_icons.py); the PNGs are kept in fig/icons."""
    import os
    from PIL import Image, ImageDraw, ImageFont
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_build', 'material_symbols')
    if not os.path.exists(os.path.join(src, 'MaterialSymbolsRounded.ttf')):
        print('font not found: icons not rendered again'); return
    cp = dict(l.split() for l in open(os.path.join(src, 'MaterialSymbolsRounded.codepoints')))
    font = ImageFont.truetype(os.path.join(src, 'MaterialSymbolsRounded.ttf'), 230)
    axes_ = {a['name'].decode() if isinstance(a['name'], bytes) else a['name']: a for a in font.get_variation_axes()}
    want = {'Fill': 1, 'Weight': 500, 'Grade': 0, 'Optical size': 48}
    font.set_variation_by_axes([want.get(n, a['default']) for n, a in axes_.items()])
    for kind, names, c in (('LP', ('speaker', 'power', 'memory'), OR), ('HP', ('volume_up', 'mic', 'block'), BL),
                           ('BP', ('radio', 'wifi', 'equalizer'), G)):
        rgb = tuple(int(c[k:k + 2], 16) for k in (1, 3, 5)) + (255,)
        for name in names:
            ch = chr(int(cp[name], 16)); im = Image.new('RGBA', (256, 256), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            l, t, r, b = d.textbbox((0, 0), ch, font=font)
            d.text(((256 - (r - l)) / 2 - l, (256 - (b - t)) / 2 - t), ch, font=font, fill=rgb)
            im.save(f'{OUT}/icons/life_{kind}_{name}.png')


def bp_q():
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=150)
    for Q, c in ((1.5, GR), (3.0, BL), (6.0, G)):
        ax.plot(f, H('BP', Q), color=c, lw=2.2, label=f'Q = {Q:g}   (BW = $f_0$/Q ≈ {F0 / Q / 1e3:.0f} kHz)')
    axes(ax); ax.set_ylim(0, 1.1); ax.legend(loc='upper right', frameon=False, fontsize=11)
    ax.text(4.5e3, 0.55, 'bigger Q →\nnarrower band', color='#333', fontsize=12)
    fig.tight_layout(); fig.savefig(f'{OUT}/rlc_bp_q.png'); plt.close(fig)



def three():
    """The three filters of one RLC circuit on one graph: low-pass, band-pass (the middle), high-pass."""
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=150)
    ax.axvspan(F0 / 1.6, F0 * 1.6, color=G, alpha=0.10)
    ax.plot(f, H('LP', 0.71), color=OR, lw=2.6, label='across C: low-pass')
    ax.plot(f, H('BP', 2.0), color=G, lw=3.0, label='across R: band-pass')
    ax.plot(f, H('HP', 0.71), color=BL, lw=2.6, label='across L: high-pass')
    axes(ax); ax.set_ylim(0, 1.15); ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.17), ncol=3, frameon=False, fontsize=10)
    ax.text(F0, 0.08, 'the middle', color=G, ha='center', fontsize=12, weight='bold')
    ax.text(5e3, 0.08, 'low', color=OR, fontsize=12); ax.text(250e3, 0.08, 'high', color=BL, fontsize=12, ha='right')
    fig.tight_layout(); fig.savefig(f'{OUT}/rlc_three.png'); plt.close(fig)


lp_hp('LP', 'rlc_lp_curve'); lp_hp('HP', 'rlc_hp_curve'); xlxc(); bp_bw(); bp_q(); three(); minis(); icons()
print('figures written to', OUT)
