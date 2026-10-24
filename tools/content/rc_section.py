"""Lab 2, part 1 (first-order RC): one circuit for the whole part, R = 10 kOhm + C = 100 nF (104), 2 Vpp,
fc = 1/(2 pi R C) = 159 Hz, instead of the Hanoi 47k + 47k + 0.1 uF circuit. Order: do (Exercises 1-2) -> see what
happens -> why (voltage divider, why 0.707) -> measure exactly (Exercise 3) -> Task 1.
Every idea in the speaker notes is also on the slide (lecturer, 24/10/2026).
- slide plan (old Hanoi step slide), breadboard photo, high-pass slide, theory slides: our circuit, short text
- the two tables: rows 10 Hz, 100 Hz, 200 Hz, 1 kHz, 10 kHz (the frequencies of Exercises 1-2)
- the two "What do you notice?" slides: what to see + Vout/Vin graph with the table points
- new slides: "What you see on the oscilloscope", "Why the output falls – a voltage divider", "Why 0.707?"
- the Hanoi oscilloscope photo "For the first circuit" (1 Hz / 10 Hz, other circuit) is removed
Run after practice_slides.py: "Why 0.707?" goes right after the cut-off slide, before Exercise 3. Running again
gives the same slides."""
import copy, io, math, re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

DECK = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab2/HCM Electronic Circuit Lab 2.pptx'
FIG = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/'
R, C = 10e3, 100e-9
FC = 1 / (2 * math.pi * R * C)
ROWS = [10, 100, 200, 1000, 10000]
MARK = 'RC Section'                 # shapes added by this script (removed and added again on every run)
MODEL = 'Devices and components for this session'
BAR = '1st order RC circuits'
DARK = RGBColor(0x22, 0x22, 0x22)
fmt = lambda f: f'{f / 1000:g} kHz' if f >= 1000 else f'{f:g} Hz'
gain = {'lp': lambda f: 1 / np.sqrt(1 + (f / FC) ** 2), 'hp': lambda f: (f / FC) / np.sqrt(1 + (f / FC) ** 2)}
xc = lambda f: 1 / (2 * math.pi * f * C)
ohm = lambda r: f'{r / 1000:.3g} kΩ' if r >= 1000 else f'{r:.3g} Ω'

# ---------------------------------------------------------------- slide text (notes = the same ideas, spoken)
PLAN = ['We build RC circuits and test them with the function generator and the oscilloscope.',
        '1. Exercise 1: R then C – change the frequency, watch Vout.',
        '2. Exercise 2: swap R and C.',
        '3. Why does Vout change? Why 0.707?',
        '4. Exercise 3: measure the cut-off frequency fc.',
        '5. Task 1: the same with the R and C on your card.']
NOTICE = {
 'lp': ['**Low frequency** (10 Hz): Vout ≈ Vin. The signal **passes**.',
        '**High frequency** (10 kHz): Vout is almost 0. The signal is **blocked**.',
        f'**In between**, Vout falls. It falls around one frequency: the **cut-off frequency fc** (here about {FC:.0f} Hz).',
        '→ This circuit is a **low-pass filter**: it passes low frequencies.',
        'Why? See the next slides.'],
 'hp': ['**Low frequency** (10 Hz): Vout is almost 0. The signal is **blocked**.',
        '**High frequency** (10 kHz): Vout ≈ Vin. The signal **passes**.',
        f'**Same R and C → same fc** (about {FC:.0f} Hz).',
        '**Why?** The same voltage divider, but now Vout is on R. Low f: XC is big, C takes most of Vin, little is left for R. '
        'High f: XC is small, R takes almost all of Vin.',
        '→ This circuit is a **high-pass filter**: it passes high frequencies.'],
}
SCOPE = ['**CH1** (yellow) = Vin. **CH2** (blue) = Vout across C. Vin is 2 Vpp at every frequency.',
         '**10 Hz**: Vout is as big as Vin.',
         f'**{FC:.0f} Hz (fc)**: Vout is smaller, and it comes a little later than Vin.',
         '**1 kHz**: Vout is very small.',
         'At each frequency, turn the time base (s/div) so that you see 2–3 waves.']
DIVIDER = ['**Lab 1:** in a voltage divider, the bigger resistor takes the bigger part of the voltage.',
           'The RC filter is a divider too: **R on top, C at the bottom**. Vout is the voltage on C.',
           'C acts like a resistor that **changes with frequency**: XC = 1 / (2πfC).',
           '**Low frequency:** XC is much bigger than R → C takes almost all of Vin → **Vout ≈ Vin**.',
           '**High frequency:** XC is much smaller than R → C takes almost nothing → **Vout ≈ 0**.']
WHY707 = ['fc = 1 / (2πRC) is the frequency where **XC = R**.',
          '**Two equal resistors** share Vin half and half: **0.5 × Vin** each.',
          '**R and C are different:** the voltage on C is 90° behind the voltage on R. '
          'They add like the two sides of a right triangle: **Vin² = VR² + VC²**.',
          'At fc, VR = VC. So Vin² = 2 × VC², and **VC = Vin / √2 = 0.707 × Vin**.',
          '**Meaning:** power ∝ V², and 0.707² = 0.5. At fc the output has **half of the power** (−3 dB). '
          'We use this point as the border between "passes" and "blocked".']
CUTOFF_LP = ['The cut-off frequency (the same formula for low-pass and high-pass):',
             '**fc = 1 / (2πRC)**',
             'At fc, XC = R, and Vout = 0.707 × Vin (next slide: why).',
             f'Our circuit: R = 10 kΩ, C = 100 nF. Calculate fc. Do you get about {FC:.0f} Hz?']
CUTOFF_HP = ['**The same formula** for the high-pass filter: fc = 1 / (2πRC).',
             'Same R and C → **same fc**.',
             'Look at your second table: where is Vout close to 0.707 × Vin?']


def spoken(lines):
    return '\n'.join(re.sub(r'\*\*', '', l) for l in lines)


# ---------------------------------------------------------------- figures
def notice_graph(kind):
    f = np.logspace(0, 5, 400); g = gain[kind]
    fig, ax = plt.subplots(figsize=(6.0, 4.4), dpi=170)
    ax.semilogx(f, g(f), color='#1f77b4', lw=2.5)
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


def scope_figure():
    """Three oscilloscope screens of the low-pass filter: 10 Hz, fc, 1 kHz. CH1 yellow = Vin, CH2 blue = Vout."""
    fig, axs = plt.subplots(3, 1, figsize=(5.6, 6.6), dpi=170)
    for ax, f in zip(axs, (10, FC, 1000)):
        g = 1 / math.sqrt(1 + (f / FC) ** 2); ph = -math.atan(f / FC)
        t = np.linspace(0, 2.5 / f, 500)
        ax.set_facecolor('black')
        for k in range(1, 10): ax.axvline(k / 10 * t[-1], color='#333', lw=0.6)
        for k in (-0.75, -0.5, -0.25, 0.25, 0.5, 0.75): ax.axhline(k * 1.6, color='#333', lw=0.6)
        ax.axhline(0, color='#555', lw=0.8)
        ax.plot(t, np.sin(2 * np.pi * f * t), color='#f5d000', lw=2)
        ax.plot(t, g * np.sin(2 * np.pi * f * t + ph), color='#38b6ff', lw=2)
        ax.set_xlim(0, t[-1]); ax.set_ylim(-1.6, 1.6); ax.set_xticks([]); ax.set_yticks([])
        name = f'{f:.0f} Hz (fc)' if f == FC else fmt(f)
        ax.text(0.01, 0.97, name, transform=ax.transAxes, color='white', fontsize=12, weight='bold', va='top')
        ax.text(0.99, 0.97, f'CH1 2.00 Vpp\nCH2 {2 * g:.2f} Vpp', transform=ax.transAxes, color='white', fontsize=9,
                ha='right', va='top', family='DejaVu Sans Mono')
    fig.tight_layout(h_pad=0.6); path = FIG + 'p2_rc_scope.png'; fig.savefig(path); plt.close(fig)
    return path


def triangle_figure():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.4, 3.4), dpi=170, gridspec_kw=dict(width_ratios=[1, 1.15]))
    for ax in (a, b): ax.set_aspect('equal'); ax.axis('off')
    a.set_title('Two equal resistors', fontsize=11)
    a.annotate('', (0.5, 0), (0, 0), arrowprops=dict(arrowstyle='->', lw=2.5, color='#1f77b4'))
    a.annotate('', (1, 0), (0.5, 0), arrowprops=dict(arrowstyle='->', lw=2.5, color='#C2410C'))
    a.text(0.25, 0.07, '0.5 Vin', ha='center', color='#1f77b4'); a.text(0.75, 0.07, '0.5 Vin', ha='center', color='#C2410C')
    a.text(0.5, -0.15, 'in one line: 0.5 + 0.5 = 1', ha='center', fontsize=10, color='#444')
    a.set_xlim(-0.05, 1.05); a.set_ylim(-0.3, 0.8)
    b.set_title('R and C at fc', fontsize=11)
    s = 1 / math.sqrt(2)
    b.annotate('', (s, 0), (0, 0), arrowprops=dict(arrowstyle='->', lw=2.5, color='#1f77b4'))
    b.annotate('', (s, s), (s, 0), arrowprops=dict(arrowstyle='->', lw=2.5, color='#C2410C'))
    b.annotate('', (s, s), (0, 0), arrowprops=dict(arrowstyle='->', lw=2.5, color='#222'))
    b.plot([s - 0.06, s - 0.06, s], [0, 0.06, 0.06], color='#444', lw=1)
    b.text(s / 2, -0.09, 'VR = 0.707 Vin', ha='center', color='#1f77b4', fontsize=10)
    b.text(s + 0.04, s / 2, 'VC = 0.707 Vin', ha='left', va='center', color='#C2410C', fontsize=10)
    b.text(s / 2 - 0.08, s / 2 + 0.07, 'Vin', ha='right', color='#222', fontsize=11, weight='bold')
    b.text(s / 2, -0.25, '90° apart: 0.707² + 0.707² = 1', ha='center', fontsize=10, color='#444')
    b.set_xlim(-0.05, 1.25); b.set_ylim(-0.3, 0.8)
    fig.tight_layout(); path = FIG + 'p2_rc_0707.png'; fig.savefig(path); plt.close(fig)
    return path


# ---------------------------------------------------------------- slide helpers
def text_of(s):
    return '\n'.join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)


def find(p, snippet, required=True):
    hits = [s for s in p.slides if snippet in text_of(s)]
    if not required and not hits:
        return None
    assert len(hits) == 1, (snippet, len(hits))
    return hits[0]


def add_runs(para, text, size=16, color=DARK):
    for part in re.split(r'(\*\*.*?\*\*)', text):
        if part:
            r = para.add_run(); r.text = part.strip('*'); r.font.size = Pt(size); r.font.name = 'Rockwell'
            r.font.bold = part.startswith('**'); r.font.color.rgb = color


def textbox(s, x, y, w, h, lines, size=16, gap=10):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tb.name = MARK
    tf = tb.text_frame; tf.word_wrap = True
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); add_runs(para, line, size); para.space_after = Pt(gap)
    return tb


def picture(s, path, x, y, w, h, top=False):
    iw, ih = Image.open(path).size; k = min(w / iw, h / ih)
    pw, ph = iw * k, ih * k
    pic = s.shapes.add_picture(path, Inches(x + (w - pw) / 2), Inches(y if top else y + (h - ph) / 2), Inches(pw), Inches(ph))
    pic.name = MARK
    return pic


def clear(s):
    for sh in list(s.shapes):
        if (sh.name.startswith(MARK) and sh.name != MARK + ' fig') or sh.name.startswith('RC Notice'):   # RC Notice: older version
            sh._element.getparent().remove(sh._element)


def swap_pictures(s, paths):
    """Replace the big pictures of a slide (left to right) by our figures, fitted into the same boxes."""
    old = sorted([sh for sh in s.shapes if sh.shape_type == 13 and sh.width > Inches(2.2) and not sh.name.startswith('Logo')
                  and (not sh.name.startswith(MARK) or sh.name == MARK + ' fig')], key=lambda sh: sh.left)
    assert len(old) == len(paths), (len(old), paths)
    for sh, path in zip(old, paths):
        box = [Emu(v).inches for v in (sh.left, sh.top, sh.width, sh.height)]
        sh._element.getparent().remove(sh._element)
        picture(s, path, *box).name = MARK + ' fig'


def new_slide(p, model, title):
    s = p.slides.add_slide(model.slide_layout)
    for sh in model.shapes:
        if sh.name == 'Title Bar':
            s.shapes._spTree.append(copy.deepcopy(sh._element)); bar = s.shapes[-1]
            bar.text_frame.paragraphs[0].runs[0].text = title
            for r in bar.text_frame.paragraphs[0].runs[1:]: r._r.getparent().remove(r._r)
            bar.name = MARK + ' bar'
        elif sh.name.startswith('Logo'):
            s.shapes.add_picture(io.BytesIO(sh.image.blob), sh.left, sh.top, sh.width, sh.height).name = MARK + ' logo'
    return s


def place_after(p, slide, ref):
    lst = p.slides._sldIdLst; slides = list(p.slides)
    sid = lst[slides.index(slide)]; lst.remove(sid)
    lst.insert(list(p.slides).index(ref) + 1, sid)


def set_notes(s, text):
    s.notes_slide.notes_text_frame.text = text


# ---------------------------------------------------------------- build
def run():
    lp, hp = FIG + 'p2_lp.png', FIG + 'p2_hp.png'
    p = Presentation(DECK); lst = p.slides._sldIdLst
    # remove the slides this script made before, and the Hanoi photo slide
    for sid, sl in reversed(list(zip(list(lst), list(p.slides)))):
        if any(sh.name == MARK + ' bar' for sh in sl.shapes) or 'For the first circuit' in text_of(sl):
            p.part.drop_rel(sid.rId); lst.remove(sid)
    p.part.rename_slide_parts([x.rId for x in lst])
    model = next(s for s in p.slides if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == MODEL for sh in s.shapes))

    # plan (the old Hanoi step slide)
    s = find(p, 'We now construct RC circuits') if find(p, 'We now construct RC circuits', False) else find(p, PLAN[0])
    for sh in list(s.shapes):
        if sh.has_text_frame and 'RC circuits' in sh.text_frame.text and sh.width < Inches(6):
            sh._element.getparent().remove(sh._element)
    clear(s); textbox(s, 0.47, 1.5, 5.0, 5.5, PLAN, gap=12)
    swap_pictures(s, [lp])
    set_notes(s, spoken(PLAN))

    # breadboard photo
    s = find(p, 'Example of breadboard circuit')
    clear(s); textbox(s, 0.47, 2.3, 3.2, 1.5, ['The output (CH2) is across the capacitor.'])
    set_notes(s, 'Here is an example on the breadboard. The output (CH2) is across the capacitor.')

    # the two tables
    tables = [s for s in p.slides if any(sh.has_table and sh.table.cell(0, 0).text.startswith('Generated frequency') for sh in s.shapes)]
    assert len(tables) == 2
    for s, kind in zip(tables, ('lp', 'hp')):
        t = next(sh for sh in s.shapes if sh.has_table).table
        put(t.cell(0, 0), ['Generated frequency at function generator (2 V', 'peak-to-peak', ')'])
        put(t.cell(0, 1), ['Observation (oscilloscope waveform, the frequency and V', 'peak-to-peak',
                           ' of the signal across C)' if kind == 'lp' else ' of the signal across R)'])
        for i, f in enumerate(ROWS, 1):
            put(t.cell(i, 0), [fmt(f)])
        clear(s); line = f'Fill in what you see on CH2 (Vout across {"C" if kind == "lp" else "R"}) at each frequency.'
        textbox(s, 0.69, 1.2, 10, 0.5, [line])
        set_notes(s, line)

    # "What do you notice?" + graphs
    notice = [s for s in p.slides if any(sh.has_text_frame and sh.text_frame.text.strip() == 'What do you notice?' for sh in s.shapes)]
    assert len(notice) == 2
    for s, kind in zip(notice, ('lp', 'hp')):
        clear(s); textbox(s, 0.47, 2.1, 6.2, 4.8, NOTICE[kind])
        picture(s, notice_graph(kind), 6.9, 1.45, 6.1, 4.6, top=True)
        set_notes(s, 'What do you notice?\n' + spoken(NOTICE[kind]))

    # new: oscilloscope screens and the voltage divider, right after the low-pass "What do you notice?"
    s1 = new_slide(p, model, 'What you see on the oscilloscope')
    textbox(s1, 0.5, 1.4, 6.6, 5.6, SCOPE, gap=12); picture(s1, scope_figure(), 7.3, 1.1, 5.7, 6.0, top=True)
    set_notes(s1, spoken(SCOPE))
    s2 = new_slide(p, model, 'Why the output falls – a voltage divider')
    textbox(s2, 0.5, 1.4, 6.4, 5.6, DIVIDER, gap=12)
    rows = [('f', 'XC (C = 100 nF)', 'R', 'Who takes most of Vin?')] + [
        (fmt(f), ohm(xc(f)), '10 kΩ', ('C → Vout big' if xc(f) > R else 'R → Vout small') if f not in (10, 10000)
         else ('C → Vout ≈ Vin' if f == 10 else 'R → Vout ≈ 0')) for f in (10, 100, 1000, 10000)]
    tb = s2.shapes.add_table(len(rows), 4, Inches(7.1), Inches(1.4), Inches(5.9), Inches(2.4)); tb.name = MARK
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            cell = tb.table.cell(i, j); cell.text = ''
            add_runs(cell.text_frame.paragraphs[0], f'**{v}**' if i == 0 else v, 13, RGBColor(0xFF, 0xFF, 0xFF) if i == 0 else DARK)
    picture(s2, lp, 7.6, 4.2, 4.9, 2.7)
    set_notes(s2, spoken(DIVIDER) + '\nThe table shows XC at 10 Hz, 100 Hz, 1 kHz and 10 kHz, compared with R = 10 kΩ.')
    place_after(p, s2, notice[0]); place_after(p, s1, notice[0])          # order: notice, scope, divider

    # high-pass slide (old Hanoi circuit picture)
    s = find(p, 'Now do the same thing as before')
    for sh in list(s.shapes):
        if sh.shape_type == 9 or (sh.has_text_frame and sh.text_frame.text.strip() == 'Output signal'):
            sh._element.getparent().remove(sh._element)
    clear(s); textbox(s, 0.47, 2.5, 5.0, 1.5, ['R and C are swapped. The output (CH2) is now across R.'])
    swap_pictures(s, [hp])
    set_notes(s, 'Now do the same thing for this circuit. R and C are swapped. The output (CH2) is now across R.')

    # theory slides: our circuits
    for s in p.slides:
        t = text_of(s)
        if 'Low pass filter:' in t and any(sh.name == 'Key word callout' for sh in s.shapes):     # low-pass / high-pass circuits
            swap_pictures(s, [lp, hp])
        elif 'Low pass filter:' in t:                                                          # the two response curves
            clear(s); line = 'Both curves change at the cut-off frequency fc.'
            textbox(s, 7.2, 6.88, 5.6, 0.45, [line], size=14)
            set_notes(s, 'Low-pass: lower frequency gives a higher output. High-pass: higher frequency gives a higher output.\n' + line)
    s = find(p, 'analyse these circuits')
    clear(s); hint = 'Hint: the impedance of C is ZC = 1 / (jωC). Write Vout / Vin for both circuits.'
    textbox(s, 1.6, 2.3, 10.5, 0.45, [hint], size=14)
    swap_pictures(s, [lp, hp])
    set_notes(s, 'Use your circuit theory to analyse these two circuits and find the formula for the output voltage. '
                 'Solve it on paper or on the board.\n' + hint)

    # cut-off slides: the Hanoi text box (with a formula object and 47k + 47k) -> plain text with our circuit
    cut = [s for s in p.slides if any(sh.name.startswith(MARK + ' cutoff') for sh in s.shapes) or
           b'You should also know the formula' in __import__('lxml.etree', fromlist=['x']).tostring(s._element)]
    assert len(cut) == 2, len(cut)
    for s, kind in zip(cut, ('lp', 'hp')):
        for ac in s._element.findall('.//{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent'):
            ac.getparent().remove(ac)
        clear(s)
        lines = CUTOFF_LP if kind == 'lp' else CUTOFF_HP
        textbox(s, 0.47, 1.5, 6.2, 4.4, lines, gap=14).name = MARK + ' cutoff'
        swap_pictures(s, [lp if kind == 'lp' else hp])
        callout = 'New word: Cut-off frequency (fc). Cut-off frequency (fc) means: where Vout = 0.707 × Vin. Say it with me: Cut-off frequency (fc).'
        set_notes(s, spoken(lines) + ('\n' + callout if kind == 'lp' else ''))

    # new: why 0.707, right after the low-pass cut-off slide (before Exercise 3)
    s3 = new_slide(p, model, 'Why 0.707?')
    textbox(s3, 0.5, 1.4, 6.5, 5.7, WHY707, gap=12); picture(s3, triangle_figure(), 7.2, 1.6, 5.9, 3.8, top=True)
    set_notes(s3, spoken(WHY707))
    place_after(p, s3, cut[0])

    p.save(DECK)
    idx = lambda s: list(p.slides).index(s) + 1
    print('Lab 2 RC part:', ', '.join(f'{idx(s)} {n}' for s, n in [(tables[0], 'table LP'), (notice[0], 'notice LP'), (s1, 'scope'),
          (s2, 'divider'), (tables[1], 'table HP'), (notice[1], 'notice HP'), (cut[0], 'cut-off'), (s3, '0.707'), (cut[1], 'cut-off HP')]),
          '|', len(p.slides), 'slides')


def put(cell, runs):
    """Write the cell text into its existing runs (keeps the table style): first runs get the text, the rest are emptied."""
    rs = [r for para in cell.text_frame.paragraphs for r in para.runs]
    for r, t in zip(rs, runs + [''] * (len(rs) - len(runs))):
        r.text = t


if __name__ == '__main__':
    run()
