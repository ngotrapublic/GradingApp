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
    Q = 4.0; share = 0.15                                  # example only (no variant has Q = 4); 15 % of R_total is the coil wire
    y = H('BP', Q, Rl_share=share); top = y.max(); lim = 0.707 * top
    fl = F0 * (math.sqrt(1 + 1 / (4 * Q * Q)) - 1 / (2 * Q)); fh = F0 * (math.sqrt(1 + 1 / (4 * Q * Q)) + 1 / (2 * Q))
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=150)
    y = H('BP', Q, f=(fz := np.linspace(15e3, 62e3, 800)), Rl_share=share)
    ax.plot(fz, y, color=G, lw=2.4)
    ax.axhline(top, color='#bbb', lw=1, ls='--'); ax.text(61.5e3, top + 0.02, f'highest = {top:.2f}', color='#666', fontsize=11, ha='right')
    ax.axhline(lim, color=OR, lw=1.3, ls='--'); ax.text(61.5e3, lim + 0.02, f'0.707 × highest = {lim:.2f}', color=OR, fontsize=11, ha='right')
    for x, t, dx in ((fl, '$f_L$', -1.2e3), (fh, '$f_H$', 1.2e3)):
        ax.plot([x, x], [0, lim], color=OR, lw=1.2, ls=':'); ax.plot([x], [lim], 'o', color=OR, ms=7)
        ax.text(x + dx, lim + 0.05, t, color=OR, ha='right' if dx < 0 else 'left', fontsize=13, weight='bold')
    ax.plot([F0, F0], [0, top], color='#bbb', lw=1, ls=':')
    ax.annotate('', (fl, lim * 0.45), (fh, lim * 0.45), arrowprops=dict(arrowstyle='<->', color=BL, lw=1.6))
    ax.text(math.sqrt(fl * fh), lim * 0.5, 'BW', color=BL, ha='center', va='bottom', weight='bold')
    ax.text(22.8e3, 1.0, f'Example: Q = 4\n$f_L$ ≈ {fl/1e3:.1f} kHz\n$f_H$ ≈ {fh/1e3:.1f} kHz\nBW ≈ {(fh-fl)/1e3:.1f} kHz = $f_0$ / Q',
            ha='center', va='top', fontsize=11, color='#333', bbox=dict(boxstyle='round', fc='#f3f7f0', ec='#b7cfa8'))
    ax.set_xlim(15e3, 62e3); ax.set_ylim(0, 1.05); ax.set_xlabel('Frequency (kHz)'); ax.set_ylabel('$V_{out}$ / $V_{in}$')
    ax.set_xticks([20e3, F0, 40e3, 50e3, 60e3]); ax.set_xticklabels(['20', '$f_0$ = 32.4', '40', '50', '60'])
    ax.grid(True, color='#e5e5e5'); [ax.spines[k].set_visible(False) for k in ('top', 'right')]
    fig.tight_layout(); fig.savefig(f'{OUT}/rlc_bp_bw.png'); plt.close(fig)


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


lp_hp('LP', 'rlc_lp_curve'); lp_hp('HP', 'rlc_hp_curve'); xlxc(); bp_bw(); bp_q(); three()
print('figures written to', OUT)
