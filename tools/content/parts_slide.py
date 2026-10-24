"""Lab 1: slide "Parts: use up or give back" right after "Find your table".
Rule (lecturer, 2026-10-24): only resistors are used up; every other part goes back to its bag.
Run after bench_map_slide.py; running again replaces the slide."""
import copy, io, re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

DECK = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab1/HCM Electronic Circuit Lab 1.pptx'
TITLE = 'Parts: use up or give back'
AFTER = 'Find your table'
DARK, GREEN, FILL, LINE = RGBColor(0x22, 0x22, 0x22), RGBColor(0x54, 0x9E, 0x39), RGBColor(0xF3, 0xF7, 0xF0), RGBColor(0xB7, 0xCF, 0xA8)
RED, RED_FILL, RED_LINE = RGBColor(0xB0, 0x3A, 0x2E), RGBColor(0xFB, 0xEE, 0xEC), RGBColor(0xE3, 0xB4, 0xAE)

USE_UP = ['**Resistors** you used in your circuit → the bin.']
GIVE_BACK = ['**Capacitors** – read the code on the part (104, 223, 222, 1 µF…) and put it in the bag with that value.',
             '**1 mH inductor** – it looks like a resistor! Keep it apart from the resistors and check it before you give it back.',
             '**LM358, microphone** (with its jumpers), **LED**, **470 µF**.']
RULES = ['**Not used?** It goes back to its bag – even a resistor.',
         '**Straighten the legs** before you give a part back.',
         '**Broken part?** Put it in the bin and tell the lecturer.']


def para_runs(p, text, size, color=DARK):
    for part in re.split(r'(\*\*.*?\*\*)', text):
        if part:
            r = p.add_run(); r.text = part.strip('*'); r.font.size = Pt(size); r.font.name = 'Arial'
            r.font.bold = part.startswith('**'); r.font.color.rgb = color


def box(s, x, y, w, h, head, items, color, fill, line):
    sh = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.06; sh.fill.solid(); sh.fill.fore_color.rgb = fill; sh.line.color.rgb = line; sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True; tf.vertical_anchor = 1                     # top
    tf.margin_left = tf.margin_right = Inches(0.2); tf.margin_top = Inches(0.15)
    p = tf.paragraphs[0]; para_runs(p, head, 26, color); p.space_after = Pt(10)
    for t in items:
        p = tf.add_paragraph(); para_runs(p, '•  ' + t, 20); p.space_after = Pt(8)


def run():
    import sys
    if '--force' not in sys.argv:           # Lab 1 was edited by hand on 24/10/2026: running this would undo it
        raise SystemExit('Lab 1 is edited by hand since 24/10/2026 - not changed (add --force to run anyway)')
    p = Presentation(DECK); lst = p.slides._sldIdLst
    for sid, sl in reversed(list(zip(list(lst), list(p.slides)))):
        if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == TITLE for sh in sl.shapes):
            p.part.drop_rel(sid.rId); lst.remove(sid)
    p.part.rename_slide_parts([x.rId for x in lst])
    slides = list(p.slides)
    model = next(s for s in slides if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == AFTER for sh in s.shapes))
    s = p.slides.add_slide(model.slide_layout)
    for sh in model.shapes:
        if sh.name == 'Title Bar':
            s.shapes._spTree.append(copy.deepcopy(sh._element)); bar = s.shapes[-1]
            bar.text_frame.paragraphs[0].runs[0].text = TITLE
            for r in bar.text_frame.paragraphs[0].runs[1:]: r._r.getparent().remove(r._r)
        elif sh.name.startswith('Logo'):
            s.shapes.add_picture(io.BytesIO(sh.image.blob), sh.left, sh.top, sh.width, sh.height)
    box(s, 0.55, 1.3, 4.0, 3.7, 'Use up', USE_UP, RED, RED_FILL, RED_LINE)
    box(s, 4.8, 1.3, 8.0, 3.7, 'Give back – to the right bag', GIVE_BACK, GREEN, FILL, LINE)
    tb = s.shapes.add_textbox(Inches(0.55), Inches(5.2), Inches(12.2), Inches(1.6)); tf = tb.text_frame; tf.word_wrap = True
    for i, t in enumerate(RULES):
        q = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); para_runs(q, t, 20); q.space_after = Pt(6)
    s.notes_slide.notes_text_frame.text = (
        'Every table has a parts box with small bags. Each bag has one value on its label.\n'
        'Only resistors are used up. A resistor you used in your circuit goes into the bin.\n'
        'Every other part goes back to its bag: capacitors, the 1 mH inductor, the LM358, the microphone, the LED and the big 470 microfarad capacitors.\n'
        'For a capacitor, read the code on it, for example 104 or 223, and find the bag with that value.\n'
        'Be careful with the 1 mH inductor: it looks like a resistor. Keep it apart from your resistors and check it before you give it back.\n'
        'A part you did not use goes back to its bag, even a resistor. Straighten the legs first. A broken part goes into the bin, and you tell me.')
    sid = lst[-1]; lst.remove(sid); lst.insert(slides.index(model) + 1, sid)
    p.save(DECK)
    print('Lab 1:', len(p.slides), 'slides; parts slide at', [i + 1 for i, x in enumerate(p.slides)
          if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == TITLE for sh in x.shapes)])


if __name__ == '__main__':
    run()
