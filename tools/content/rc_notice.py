"""Lab 2, RC part: the two observation tables and the two "What do you notice?" slides match practice Exercises 1-2
(R = 10 kOhm, C = 100 nF, 2 Vpp, fc = 1/(2 pi R C) = 159 Hz) instead of the Hanoi 47k + 47k + 0.1 uF circuit.
Tables: rows 10 Hz, 100 Hz, 200 Hz, 1 kHz, 10 kHz. Notice slides: what to see + a Vout/Vin graph with the table points.
Running again gives the same slides. Run after practice_slides.py (or before: it does not move slides)."""
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

DECK = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab2/HCM Electronic Circuit Lab 2.pptx'
FIG = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/'
R, C = 10e3, 100e-9
FC = 1 / (2 * math.pi * R * C)
ROWS = [10, 100, 200, 1000, 10000]
NAME = 'RC Notice'
DARK, RED = RGBColor(0x22, 0x22, 0x22), RGBColor(0xC0, 0x00, 0x00)
fmt = lambda f: f'{f / 1000:g} kHz' if f >= 1000 else f'{f:g} Hz'
gain = {'lp': lambda f: 1 / np.sqrt(1 + (f / FC) ** 2), 'hp': lambda f: (f / FC) / np.sqrt(1 + (f / FC) ** 2)}

TEXT = {
 'lp': ['**Low frequency** (10 Hz): Vout ≈ Vin. The signal **passes**.',
        '**High frequency** (10 kHz): Vout is almost 0. The signal is **blocked**.',
        f'**At fc = 1 / (2πRC) ≈ {FC:.0f} Hz**: Vout = 0.707 × Vin.',
        '**Why?** XC = 1 / (2πfC). Low f: XC is big, C is almost an open circuit. High f: XC is small, C shorts the output to ground.',
        '→ This circuit is a **low-pass filter**.'],
 'hp': ['**Low frequency** (10 Hz): Vout is almost 0. The signal is **blocked**.',
        '**High frequency** (10 kHz): Vout ≈ Vin. The signal **passes**.',
        f'**Same fc ≈ {FC:.0f} Hz**: Vout = 0.707 × Vin.',
        '**Why?** C is now in series. Low f: XC is big, C blocks the signal. High f: XC is small, the signal goes through C to R.',
        '→ This circuit is a **high-pass filter**.'],
}
SAY = {
 'lp': f'What do you notice? At low frequency the output is as big as the input. At high frequency it is almost zero. '
       f'Between them, at about {FC:.0f} hertz, the output is 0.707 times the input: this is the cut-off frequency. '
       'The reason is the capacitor: at high frequency it is almost a short circuit to ground. This is a low-pass filter.',
 'hp': 'What do you notice now? It is the other way round: low frequencies are blocked, high frequencies pass. '
       'The cut-off frequency is the same, because R and C are the same. This is a high-pass filter.',
}


def graph(kind):
    f = np.logspace(0, 5, 400); g = gain[kind]
    fig, ax = plt.subplots(figsize=(6.0, 4.4), dpi=170)
    ax.semilogx(f, g(f), color='#1f77b4', lw=2.5)
    ax.axhline(0.707, color='#999', ls='--', lw=1); ax.text(1.3, 0.735, '0.707', color='#666', fontsize=10)
    ax.axvline(FC, color='#c0392b', ls=':', lw=1.5)
    ax.text(FC * 1.15, 0.05 if kind == 'lp' else 0.12, f'fc ≈ {FC:.0f} Hz', color='#c0392b', fontsize=11)
    for x in ROWS:
        ax.plot(x, g(x), 'o', color='#C2410C', ms=7)
        ax.annotate(f'{g(x):.2f}', (x, g(x)), textcoords='offset points', xytext=(6, 6), fontsize=9, color='#444')
    ax.set_xlim(1, 1e5); ax.set_ylim(0, 1.1)
    ax.set_xticks([1, 10, 100, 1000, 10000, 100000]); ax.set_xticklabels(['1 Hz', '10 Hz', '100 Hz', '1 kHz', '10 kHz', '100 kHz'])
    ax.set_ylabel('Vout / Vin'); ax.set_xlabel('frequency (log scale)')
    ax.set_title(('Low-pass' if kind == 'lp' else 'High-pass') + ': R = 10 kΩ, C = 100 nF', fontsize=12)
    ax.grid(True, which='major', alpha=0.3)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    fig.tight_layout(); path = FIG + f'p2_rc_{kind}_graph.png'; fig.savefig(path); plt.close(fig)
    return path


def put(cell, runs):
    """Write the cell text into its existing runs (keeps the table style): first run gets the text, the rest are emptied."""
    rs = [r for para in cell.text_frame.paragraphs for r in para.runs]
    for r, t in zip(rs, runs + [''] * (len(rs) - len(runs))):
        r.text = t


def add_runs(para, text, size=16):
    import re
    for part in re.split(r'(\*\*.*?\*\*)', text):
        if part:
            r = para.add_run(); r.text = part.strip('*'); r.font.size = Pt(size); r.font.name = 'Rockwell'
            r.font.bold = part.startswith('**'); r.font.color.rgb = DARK


def run():
    p = Presentation(DECK)
    tables = [s for s in p.slides if any(sh.has_table and sh.table.cell(0, 0).text.startswith('Generated frequency') for sh in s.shapes)]
    notice = [s for s in p.slides if any(sh.has_text_frame and sh.text_frame.text.strip() == 'What do you notice?' for sh in s.shapes)]
    assert len(tables) == 2 and len(notice) == 2, (len(tables), len(notice))
    for s, kind in zip(tables, ('lp', 'hp')):
        t = next(sh for sh in s.shapes if sh.has_table).table
        put(t.cell(0, 0), ['Generated frequency at function generator (2 V', 'peak-to-peak', ')'])
        put(t.cell(0, 1), ['Observation (oscilloscope waveform, the frequency and V', 'peak-to-peak',
                           ' of the signal across C)' if kind == 'lp' else ' of the signal across R)'])
        for i, f in enumerate(ROWS, 1):
            put(t.cell(i, 0), [fmt(f)])
    for s, kind in zip(notice, ('lp', 'hp')):
        for sh in list(s.shapes):
            if sh.name.startswith(NAME):
                sh._element.getparent().remove(sh._element)
        tb = s.shapes.add_textbox(Inches(0.47), Inches(2.1), Inches(6.2), Inches(4.6)); tb.name = NAME
        tf = tb.text_frame; tf.word_wrap = True
        for i, line in enumerate(TEXT[kind]):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); add_runs(para, line); para.space_after = Pt(10)
        pic = s.shapes.add_picture(graph(kind), Inches(6.9), Inches(1.45), Inches(6.1)); pic.name = NAME + ' graph'
        s.notes_slide.notes_text_frame.text = SAY[kind]
    p.save(DECK)
    print('Lab 2: tables on slides', [list(p.slides).index(s) + 1 for s in tables], '| notice on', [list(p.slides).index(s) + 1 for s in notice])


if __name__ == '__main__':
    run()
