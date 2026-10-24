"""Lab 2: series RLC. Low-pass and high-pass are explained in detail in the RC part, so here they are one line each on
"Series RLC – one circuit, three filters" (lecturer, 24/10/2026); band-pass is the main topic: three slides (why only a
band passes, bandwidth, measuring BW), inserted after that slide.
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
    ('Band-pass RLC – why only a band passes', [
        'The output is the voltage across **R**: V_{out} = I × R. When the current I is big, V_{out} is big. When I is small, V_{out} is small.',
        'L and C both resist AC current. This "AC resistance" is called **reactance**: X_{C} for the capacitor, X_{L} for the inductor. It is measured in ohms (Ω).',
        '**Below f_{0}** (low frequency): X_{C} = 1/(2πfC) is very big. The capacitor blocks the current, so V_{out} is small.',
        '**Above f_{0}** (high frequency): X_{L} = 2πfL is very big. The inductor blocks the current, so V_{out} is small.',
        '**At f_{0}**: X_{L} and X_{C} are equal (about 203 Ω). They work in opposite directions, so together they become zero. '
        'Now only R limits the current. The current is the biggest, so V_{out} is the biggest.',
        'The highest V_{out}/V_{in} is a little **below 1**: the coil wire has a small resistance R_{L}, and part of the voltage is lost there.',
        'So the circuit lets a **band** of frequencies around f_{0} pass. It blocks lower and higher frequencies. That is why it is called **band-pass**.'],
     [('rlc_xlxc.png', 7.25, 1.2, 5.7), ('d2_bp.png', 8.6, 5.05, 3.0)],
     'The output is the voltage across R: Vout = I times R. When the current is big, Vout is big. When the current is small, Vout is small.\n'
     'L and C both resist AC current. This AC resistance is called reactance: X C for the capacitor, X L for the inductor. It is measured in ohms.\n'
     'Below f0, at low frequency, X C is very big. The capacitor blocks the current, so Vout is small.\n'
     'Above f0, at high frequency, X L is very big. The inductor blocks the current, so Vout is small.\n'
     'At f0, X L and X C are equal, about 203 ohms. They work in opposite directions, so together they become zero. '
     'Now only R limits the current. The current is the biggest, so Vout is the biggest. Look at the graph: the two lines cross at f0.\n'
     'The highest Vout over Vin is a little below 1: the coil wire has a small resistance R L, and part of the voltage is lost there.\n'
     'So the circuit lets a band of frequencies around f0 pass. It blocks lower and higher frequencies. That is why it is called band-pass.'),
    ('Band-pass – bandwidth (BW)', [
        'The band has two edges: **f_{L}** (the low edge) and **f_{H}** (the high edge).',
        'At each edge, V_{out}/V_{in} is **0.707 × the highest value**. This is the same -3 dB rule as for the RC filters: '
        'the output still has 70% of its highest value.',
        'The **bandwidth** is the width of the band: **BW = f_{H} − f_{L}** (in kHz).',
        'In theory, **BW = f_{0} / Q = R_{total} / (2πL)**. A bigger R gives a wider band. A smaller R gives a narrow, sharp band (lower graph).',
        'Note: f_{0} is **not** exactly in the middle of f_{L} and f_{H}. The correct rule is **f_{0} = √(f_{L} × f_{H})**.'],
     [('rlc_bp_bw.png', 8.3, 1.12, 4.45), ('rlc_bp_q.png', 8.3, 4.08, 4.45)],
     'The band has two edges: f L, the low edge, and f H, the high edge.\n'
     'At each edge, Vout over Vin is 0.707 times the highest value. This is the same minus 3 dB rule as for the RC filters: '
     'the output still has 70 percent of its highest value.\n'
     'The bandwidth is the width of the band: BW = f H minus f L, in kilohertz.\n'
     'In theory, BW = f0 over Q, or R total over 2 pi L. A bigger R gives a wider band. A smaller R gives a narrow, sharp band: look at the lower graph.\n'
     'Note: f0 is not exactly in the middle of f L and f H. The correct rule is: f0 is the square root of f L times f H.'),
    ('Band-pass – measuring BW step by step', [
        '1.  Set the function generator near **f_{0}** (about 32.4 kHz). Turn the frequency knob slowly. Find the frequency where V_{out}/V_{in} is the **highest**. Write this value down (for example 0.80).',
        '2.  Calculate the **target**: target = 0.707 × the highest value (for example 0.707 × 0.80 = 0.57).',
        '3.  Turn the frequency **down** (below f_{0}) until V_{out}/V_{in} is equal to the target. This frequency is **f_{L}**.',
        '4.  Turn the frequency **up** (above f_{0}) until V_{out}/V_{in} is equal to the target again. This frequency is **f_{H}**.',
        '5.  Calculate **BW = f_{H} − f_{L}**. Check your result: √(f_{L} × f_{H}) should be close to f_{0}.'],
     [],
     'Now how to measure the bandwidth at your table. There are five steps.\n'
     'One: set the generator near f0, about 32.4 kilohertz. Turn the knob slowly and find the highest Vout over Vin. Write it down.\n'
     'Two: calculate the target: 0.707 times the highest value.\n'
     'Three: turn the frequency down until Vout over Vin is equal to the target. This frequency is f L.\n'
     'Four: turn the frequency up, past f0, until the ratio is equal to the target again. This frequency is f H.\n'
     'Five: calculate BW = f H minus f L. Check that the square root of f L times f H is close to f0.\n'
     'Common mistakes. Do not use 0.707 times Vin: use 0.707 times the highest Vout over Vin. '
     'Do not read Vin only once: near f0 it changes, so read CH1 and CH2 again at f L and at f H. '
     'Do not take f L and f H from the 9 frequencies on your card: they are too far apart. Turn the knob to find them.'),
]
MISTAKES = ['Do not use 0.707 × V_{in}. Use 0.707 × the **highest V_{out}/V_{in}**.',
            'Do not read V_{in} only once. Near f_{0}, V_{in} changes. Read **CH1 and CH2 again** at f_{L} and at f_{H}.',
            'Do not take f_{L} and f_{H} from the 9 frequencies on your card. They are too far apart. **Turn the knob** to find them.']
OLD = {'Low-pass RLC – output across C', 'High-pass RLC – output across L'}     # removed 24/10/2026
THREE = ['The circuit has L = 1 mH and C = 22 nF ∥ 2.2 nF. The same current flows through R, L and C. The type of filter depends on where you measure the output.',
         'If you measure the output across **C**, you get a **low-pass** filter. If you measure it across **L**, you get a **high-pass** filter. '
         'They work like the RC filters you built before.',
         'One difference: near f_{0}, the output of these two filters can be **bigger than the input**. The highest point is at f_{max}. '
         'In Task 2, the low-pass and high-pass teams measure f_{max} and the highest V_{out}/V_{in}.',
         'If you measure the output across **R**, you get a **band-pass** filter: only frequencies near f_{0} can pass. '
         'This filter is new for you, so the next slides explain it step by step.',
         'Always put the output part at the **ground side**. Then both probe grounds are connected to the same point.']
THREE_SAY = ('The circuit has L = 1 millihenry and C = 22 nanofarad parallel 2.2 nanofarad. The same current flows through R, L and C. '
             'The type of filter depends on where you measure the output.\n'
             'If you measure the output across C, you get a low-pass filter. If you measure it across L, you get a high-pass filter. '
             'They work like the RC filters you built before.\n'
             'One difference: near f0, the output of these two filters can be bigger than the input. The highest point is at f max. '
             'In Task 2, the low-pass and high-pass teams measure f max and the highest Vout over Vin.\n'
             'If you measure the output across R, you get a band-pass filter: only frequencies near f0 can pass. '
             'This filter is new for you, so the next slides explain it step by step.\n'
             'Always put the output part at the ground side. Then both probe grounds are connected to the same point.')
def run():
    p = Presentation(DECK)
    titles = {t for t, *_ in SLIDES} | OLD
    lst = p.slides._sldIdLst
    for sid, sl in reversed(list(zip(list(lst), list(p.slides)))):          # an earlier run: remove, then add again
        if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() in titles for sh in sl.shapes):
            p.part.drop_rel(sid.rId); lst.remove(sid)
    p.part.rename_slide_parts([x.rId for x in lst])
    slides = list(p.slides)
    model = next(s for s in slides if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == AFTER for sh in s.shapes))
    at = slides.index(model) + 1
    tb = next(sh for sh in model.shapes if sh.has_text_frame and 'Where you take the output' in sh.text_frame.text)
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
            text_box(s, 0.55, 1.2, 6.5 if figs[0][1] < 8 else 7.4, 5.8, paras, size=15)
        else:
            text_box(s, 0.55, 1.2, 7.3, 5.8, paras, size=16)
            text_box(s, 8.2, 1.3, 4.6, 4.2, ['•  ' + m for m in MISTAKES], size=15, box=True, title='Common mistakes')
        for name, x, y, w in figs:
            pic(s, name, x, y, w)
        s.notes_slide.notes_text_frame.text = note
        sid = lst[-1]; lst.remove(sid); lst.insert(at + k, sid)
    p.save(DECK)
    print('Lab 2:', len(p.slides), 'slides; RLC theory slides at', [i + 1 for i, s in enumerate(p.slides)
          if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() in titles for sh in s.shapes)])


if __name__ == '__main__':
    run()
