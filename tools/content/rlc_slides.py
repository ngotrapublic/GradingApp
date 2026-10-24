"""Lab 2: series RLC. Low-pass and high-pass are explained in detail in the RC part, so here they are one line each on
"Series RLC – one circuit, three filters" (lecturer, 24/10/2026); band-pass is the main topic, kept short: "only the
middle passes", bandwidth, measuring BW (inserted after that slide; Exercise 6 comes first: practice, then theory).
Plus "Filters in real life" before the Hanoi slides "Where are RLC circuits used?".
Run after align_web.py; running again replaces the slides.   Figures: fig_rlc_theory.py."""
import copy, io, re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn

DECK = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab2/HCM Electronic Circuit Lab 2.pptx'
FIG = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig'
AFTER = 'Series RLC – one circuit, three filters'
GREEN, DARK, BOXFILL, BOXLINE = RGBColor(0x3F, 0x7A, 0x2A), RGBColor(0x22, 0x22, 0x22), RGBColor(0xF3, 0xF7, 0xF0), RGBColor(0xB7, 0xCF, 0xA8)


def add_runs(par, text, size):
    """'**bold**' and '_{sub}' markup -> runs (subscripts as real subscripts)."""
    for chunk in re.split(r'(\*\*.*?\*\*)', text):                 # bold parts may contain subscripts
        bold = chunk.startswith('**'); chunk = chunk[2:-2] if bold else chunk
        for part in re.split(r'(_\{.*?\})', chunk):
            if not part:
                continue
            r = par.add_run(); r.font.size = Pt(size); r.font.name = 'Arial'; r.font.color.rgb = DARK; r.font.bold = bold
            if part.startswith('_{'):
                r.text = part[2:-1]; r._r.get_or_add_rPr().set('baseline', '-25000')
            else:
                r.text = part


def text_box(slide, x, y, w, h, paras, size=16, box=False, title=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    if box:
        tb.fill.solid(); tb.fill.fore_color.rgb = BOXFILL; tb.line.color.rgb = BOXLINE
        tf.margin_left = tf.margin_right = Inches(0.15); tf.margin_top = Inches(0.1)
    first = True
    if title:
        p = tf.paragraphs[0]; first = False; add_runs(p, f'**{title}**', size + 1); p.space_after = Pt(6)
    for t in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        add_runs(p, t, size); p.space_after = Pt(8)
    return tb


def new_slide(p, model, title):
    s = p.slides.add_slide(model.slide_layout)
    for sh in model.shapes:
        if sh.name == 'Title Bar':
            s.shapes._spTree.append(copy.deepcopy(sh._element))
            bar = s.shapes[-1]; runs = bar.text_frame.paragraphs[0].runs
            runs[0].text = title
            for r in runs[1:]: r._r.getparent().remove(r._r)
        elif sh.name.startswith('Logo'):
            s.shapes.add_picture(io.BytesIO(sh.image.blob), sh.left, sh.top, sh.width, sh.height)
    return s


def pic(slide, name, x, y, w):
    slide.shapes.add_picture(f'{FIG}/{name}', Inches(x), Inches(y), Inches(w))


SLIDES = [
    ('Band-pass RLC – only the middle passes', [
        'A low-pass filter passes the **low** frequencies. A high-pass filter passes the **high** frequencies. '
        'A band-pass filter passes only the **middle**: a band of frequencies around f_{0}.',
        '**Below f_{0}**, the capacitor blocks the current. **Above f_{0}**, the inductor blocks the current.',
        '**At f_{0}**, nothing blocks the current. The current is the biggest, so V_{out} (across R) is the biggest.'],
     [('rlc_three.png', 7.25, 1.3, 5.8)],
     'A low-pass filter passes the low frequencies. A high-pass filter passes the high frequencies. '
     'A band-pass filter passes only the middle: a band of frequencies around f0.\n'
     'Below f0, the capacitor blocks the current. Above f0, the inductor blocks the current.\n'
     'At f0, nothing blocks the current. The current is the biggest, so Vout across R is the biggest.'),
    ('Band-pass – bandwidth (BW)', [
        '**Bandwidth (BW)** tells you how wide the band is.',
        'The two edges are **f_{L}** and **f_{H}**. There, V_{out}/V_{in} = **0.707 × the peak** (-3 dB).',
        '**BW = f_{H} − f_{L}**',
        'A bigger R makes the band wider.'],
     [('rlc_bp_bw.png', 7.1, 1.5, 5.9)],
     'Bandwidth, BW, tells you how wide the band is.\n'
     'The two edges are f L and f H. There, Vout over Vin is 0.707 times the peak: minus 3 dB.\n'
     'BW = f H minus f L.\n'
     'A bigger R makes the band wider.'),
    ('Band-pass – measuring BW step by step', [
        '**Before you start.** Function generator: sine, 2 Vpp, High-Z. Oscilloscope: CH1 = V_{in}, CH2 = V_{out}. '
        'Press **Measure** and show **Pk-Pk** for CH1 and for CH2. Use the table on the next slide.',
        '**1. Find the peak.** On the function generator, press **Display Setup**, then the button next to **Freq** (beside the screen). '
        'Type 32.4 on the number pad and press the button next to **kHz**. Now turn the **round knob** slowly, a little down and a little up. '
        'The **◄ ►** keys choose which digit the knob changes: start with the 1 kHz digit, then use the 0.1 kHz digit. '
        '**What you see:** when you come closer to the peak, the CH2 wave (V_{out}) grows. At the peak it is the **biggest** and almost '
        'as big as the CH1 wave (V_{in}), but a little smaller. After the peak it becomes smaller again. '
        'Stop where the CH2 wave is the biggest compared with CH1. Write f, V_{in} and V_{out} in **row 1**.',
        '**2. Calculate the target:** target = 0.707 × the highest V_{out}/V_{in}. Write it in **row 2**.',
        '**3. Find f_{L}.** Turn the round knob to a **lower** frequency until V_{out}/V_{in} = target. '
        'Read V_{in} and V_{out} again, because V_{in} changes near the peak. Write them in **row 3**.',
        '**4. Find f_{H}.** Turn the round knob to a **higher** frequency, past the peak, until V_{out}/V_{in} = target again. Write them in **row 4**.',
        '**5. Calculate BW = f_{H} − f_{L}.** Write it in **row 5**.'],
     [],
     'Before you start: the function generator gives a sine wave, 2 volts peak-to-peak, High-Z. On the oscilloscope, CH1 is Vin and CH2 is Vout. '
     'Press Measure and show Pk-Pk for CH1 and for CH2. Use the table on the next slide.\n'
     'Step 1, find the peak. On the function generator, press Display Setup, then the button next to Freq. Type 32.4 and press the button next to kHz. '
     'Now turn the round knob slowly, a little down and a little up. The left and right arrow keys choose which digit the knob changes: '
     'start with the 1 kilohertz digit, then use the 0.1 kilohertz digit.\n'
     'What you see: when you come closer to the peak, the CH2 wave, Vout, grows. At the peak it is the biggest and almost as big as the CH1 wave, Vin, '
     'but a little smaller. After the peak it becomes smaller again. Stop where the CH2 wave is the biggest compared with CH1. '
     'Write f, Vin and Vout in row 1.\n'
     'Step 2: calculate the target, 0.707 times the highest Vout over Vin. Write it in row 2.\n'
     'Step 3, find f L. Turn the round knob to a lower frequency until Vout over Vin is equal to the target. '
     'Read Vin and Vout again, because Vin changes near the peak. Write them in row 3.\n'
     'Step 4, find f H. Turn the knob to a higher frequency, past the peak, until the ratio is equal to the target again. Write them in row 4.\n'
     'Step 5: calculate BW = f H minus f L and write it in row 5.'),
]
APPS_TITLE = 'Filters in real life'
APPS = [('Low-pass', 'LP', [('speaker', 'Subwoofer: only the bass'), ('power', 'Power supply: smooth DC'),
                              ('memory', 'Sensor input: less noise')]),
        ('High-pass', 'HP', [('volume_up', 'Tweeter: only the treble'), ('mic', 'Microphone: no wind noise'),
                               ('block', 'Coupling capacitor: blocks DC (Lab 4)')]),
        ('Band-pass', 'BP', [('radio', 'Radio: one station'), ('wifi', 'Wi-Fi: one channel'),
                               ('equalizer', 'Equalizer: bass, middle, treble')])]
APPS_SAY = ('Filters are everywhere.\n'
            'Low-pass: a subwoofer gets only the bass of the music. A power supply filter gives a smooth DC voltage. '
            'A sensor input uses a low-pass filter to get less noise.\n'
            'High-pass: a tweeter gets only the treble. A microphone uses a high-pass filter to remove wind noise. '
            'A coupling capacitor blocks DC: you use one in Lab 4.\n'
            'Band-pass: a radio receives one station. Wi-Fi uses one channel. An equalizer has bands for bass, middle and treble.')
BEFORE_APPS = 'Where are RLC circuits used?'

BW_TABLE_TITLE = 'Band-pass – BW table'
BW_ROWS = [('Step', 'f (kHz)', 'V_{in} (CH1, Vpp)', 'V_{out} (CH2, Vpp)', 'V_{out} / V_{in}'),
           ('1. Peak', '', '', '', ''),
           ('2. Target = 0.707 × peak', '–', '–', '–', ''),
           ('3. f_{L} (below the peak)', '', '', '', ''),
           ('4. f_{H} (above the peak)', '', '', '', ''),
           ('5. BW = f_{H} − f_{L}', '', '–', '–', '–')]
BW_TABLE_SAY = ('Fill in this table step by step: row 1 is the peak, row 2 is the target, row 3 is f L, row 4 is f H, and row 5 is the bandwidth.\n'
                'Common mistakes. Do not use 0.707 times Vin: use 0.707 times the highest Vout over Vin. '
                'Do not read Vin only once: near the peak it changes, so read CH1 and CH2 again at f L and at f H. '
                'Do not take f L and f H from the 9 frequencies on your card: they are too far apart. Turn the knob to find them.')
MISTAKES = ['Do not use 0.707 × V_{in}. Use 0.707 × the **highest V_{out}/V_{in}**.',
            'Do not read V_{in} only once. Near f_{0}, V_{in} changes. Read **CH1 and CH2 again** at f_{L} and at f_{H}.',
            'Do not take f_{L} and f_{H} from the 9 frequencies on your card. They are too far apart. **Turn the knob** to find them.']
OLD = {'Low-pass RLC – output across C', 'High-pass RLC – output across L',     # removed 24/10/2026
       'Band-pass RLC – why only a band passes'}
THREE = ['One RLC circuit (L = 1 mH, C = 22 nF ∥ 2.2 nF) can make three filters. It depends on where you measure the output.',
         'Across **C**: a **low-pass** filter. Across **L**: a **high-pass** filter. They work like the RC filters. '
         'Near f_{0} their output can be bigger than the input (a peak at f_{max}). Low-pass and high-pass teams measure this peak in Task 2.',
         'Across **R**: a **band-pass** filter. It passes only the **middle** frequencies, around f_{0}.',
         'Always put the output part at the **ground side**, so both probe grounds are on the same point.']

THREE_SAY = ('One RLC circuit can make three filters. It depends on where you measure the output.\n'
             'Across C: a low-pass filter. Across L: a high-pass filter. They work like the RC filters. '
             'Near f0 their output can be bigger than the input: a peak at f max. Low-pass and high-pass teams measure this peak in Task 2.\n'
             'Across R: a band-pass filter. It passes only the middle frequencies, around f0.\n'
             'Always put the output part at the ground side, so both probe grounds are on the same point.')

def run():
    p = Presentation(DECK)
    titles = {t for t, *_ in SLIDES} | OLD | {APPS_TITLE, BW_TABLE_TITLE}
    lst = p.slides._sldIdLst
    for sid, sl in reversed(list(zip(list(lst), list(p.slides)))):          # an earlier run: remove, then add again
        if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() in titles for sh in sl.shapes):
            p.part.drop_rel(sid.rId); lst.remove(sid)
    p.part.rename_slide_parts([x.rId for x in lst])
    slides = list(p.slides)
    model = next(s for s in slides if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == AFTER for sh in s.shapes))
    at = slides.index(model) + 1
    tb = next(sh for sh in model.shapes if sh.has_text_frame and any(k in sh.text_frame.text for k in
              ('Where you take the output', 'where you measure the output', 'It depends on where you measure')))
    tf = tb.text_frame
    for para in tf.paragraphs[1:]:
        para._p.getparent().remove(para._p)
    for r in list(tf.paragraphs[0].runs):
        r._r.getparent().remove(r._r)
    for k, t in enumerate(THREE):
        par = tf.paragraphs[0] if k == 0 else tf.add_paragraph(); add_runs(par, t, 15); par.space_after = Pt(6)
    model.notes_slide.notes_text_frame.text = THREE_SAY
    for k, (title, paras, figs, note) in enumerate(t for t in SLIDES if t[0] not in OLD):
        s = new_slide(p, model, title)
        if figs:
            text_box(s, 0.55, 1.2, 6.5 if figs[0][1] < 8 else 7.4, 5.8, paras, size=17)
        else:
            text_box(s, 0.55, 1.15, 12.3, 6.0, paras, size=17)
        for name, x, y, w in figs:
            pic(s, name, x, y, w)
        s.notes_slide.notes_text_frame.text = note
        sid = lst[-1]; lst.remove(sid); lst.insert(at + k, sid)
    # the BW table to fill in, right after the steps
    s = new_slide(p, model, BW_TABLE_TITLE)
    tb = s.shapes.add_table(len(BW_ROWS), 5, Inches(0.5), Inches(1.25), Inches(12.3), Inches(3.4))
    for r, row in enumerate(BW_ROWS):
        for c, v in enumerate(row):
            cell = tb.table.cell(r, c); cell.text = ''
            add_runs(cell.text_frame.paragraphs[0], f'**{v}**' if r == 0 or c == 0 else v, 15)
            if r == 0:
                for run in cell.text_frame.paragraphs[0].runs: run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for c, w in enumerate((3.5, 1.8, 2.3, 2.4, 2.3)):
        tb.table.columns[c].width = Inches(w)
    text_box(s, 0.5, 4.95, 12.3, 2.0, ['•  ' + m for m in MISTAKES], size=15, box=True, title='Common mistakes')
    s.notes_slide.notes_text_frame.text = BW_TABLE_SAY
    steps = next(x for x in p.slides if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == 'Band-pass – measuring BW step by step'
                                              for sh in x.shapes))
    sid = lst[-1]; lst.remove(sid); lst.insert(list(p.slides).index(steps) + 1, sid)

    # "Filters in real life": three columns, each with the response shape and three examples (icon + a few words)
    s = new_slide(p, model, APPS_TITLE)
    for k, (head, kind, items) in enumerate(APPS):
        x = 0.45 + k * 4.2
        text_box(s, x, 1.15, 4.0, 0.5, [f'**{head}**'], size=20)
        pic(s, f'rlc_mini_{kind}.png', x + 0.3, 1.7, 3.3)
        for r, (icon, label) in enumerate(items):
            y = 3.35 + r * 1.2
            s.shapes.add_picture(f'{FIG}/icons/life_{kind}_{icon}.png', Inches(x + 0.1), Inches(y), Inches(0.9), Inches(0.9))
            text_box(s, x + 1.1, y + 0.08, 2.9, 0.9, [label], size=17)
    s.notes_slide.notes_text_frame.text = APPS_SAY
    # before the Hanoi slides "Where are RLC circuits used?"; the lecturer removed them (24/10/2026): then after "Real components"
    ref = next((x for x in p.slides if any(sh.has_text_frame and BEFORE_APPS in sh.text_frame.text for sh in x.shapes)), None)
    after = ref is None
    ref = ref or next(x for x in p.slides if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == 'Real components at 32 kHz'
                                                 for sh in x.shapes))
    sid = lst[-1]; lst.remove(sid); lst.insert(list(p.slides).index(ref) + (1 if after else 0), sid)
    p.save(DECK)
    print('Lab 2:', len(p.slides), 'slides; RLC theory slides at', [i + 1 for i, s in enumerate(p.slides)
          if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() in titles for sh in s.shapes)])


if __name__ == '__main__':
    run()
