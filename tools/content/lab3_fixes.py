"""Lab 3: the photo of "Connect the rest of the circuit" was the Hanoi build with its own ±6 V supply (lecturer,
24/10/2026: not right for HCM, where the ±6 V comes from the PB-503A). It is replaced by the wiring diagram
fig/p3_wiring.png (fig_practice.py), fitted into the same box. Also: the supply slide and Exercise 1 (voltage
follower) come before the inverting amplifier; no decoupling slides / capacitors (the PB-503A supply is clean).
Run after practice_slides.py. Safe to run again."""
import copy, io, re
from PIL import Image
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx import Presentation
from pptx.util import Emu

DECK = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab3/HCM Electronic Circuit Lab 3.pptx'
CLIP = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/p3_clip.png'
LIMITS = [
    ('Clipping – the output has a limit',
     ['The output of the LM358 cannot go higher than its supply (**+6 V**) or lower than **−6 V**. In fact it stops a little before.',
      'If the input is too big, the top and the bottom of the output wave are cut **flat**. This is called **clipping**.',
      'A clipped wave is wrong: it is not a copy of the input any more. Then make the input smaller.'],
     CLIP,
     'The output of the LM358 cannot go higher than its supply, plus 6 volts, or lower than minus 6 volts. In fact it stops a little before.\n'
     'If the input is too big, the top and the bottom of the output wave are cut flat. This is called clipping.\n'
     'A clipped wave is wrong: it is not a copy of the input any more. Then make the input smaller.'),
    ('Use low (audio) frequencies',
     ['The LM358 is not fast. With a big gain it works well only at **low frequencies**.',
      'In this lab, use **100 Hz – 2 kHz**.'],
     None,
     'The LM358 is not fast. With a big gain it works well only at low frequencies.\nIn this lab, use 100 hertz to 2 kilohertz.')]
FIG = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/p3_wiring.png'
NAME = 'Lab3 wiring'


def run():
    p = Presentation(DECK)
    s = next(s for s in p.slides if any(sh.has_text_frame and 'Connect the rest of the circuit' in sh.text_frame.text for sh in s.shapes))
    pics = [sh for sh in s.shapes if sh.shape_type == 13 and (sh.name == NAME or sh.width > Emu(914400 * 4))]
    old = max(pics, key=lambda sh: sh.width * sh.height)
    x, y, w, h = old.left, old.top, old.width, old.height
    old._element.getparent().remove(old._element)
    iw, ih = Image.open(FIG).size; k = min(w / iw, h / ih); pw, ph = int(iw * k), int(ih * k)
    pic = s.shapes.add_picture(FIG, x + (w - pw) // 2, y + (h - ph) // 2, pw, ph); pic.name = NAME
    # the easy circuit first (lecturer, 24/10/2026): supply, then Exercise 1 (voltage follower, no R1 R2) and its answer,
    # then "We will now construct an inverting amplifier ..." and the amplifier slides
    title = lambda x: ' '.join(sh.text_frame.text.strip() for sh in x.shapes if sh.name == 'Title Bar')
    text = lambda x: '\n'.join(sh.text_frame.text for sh in x.shapes if sh.has_text_frame)
    supply = next(x for x in p.slides if title(x) == 'Supplying the op-amp from the PB-503A')
    ex1 = [x for x in p.slides if any(sh.name == 'Practice Exercise' for sh in x.shapes) and
           ('Exercise 1:' in text(x) or 'Exercise 1 – answer' in text(x))]
    intro = next(x for x in p.slides if 'We will now construct an inverting amplifier' in text(x))
    lst = p.slides._sldIdLst
    sids = [lst[list(p.slides).index(x)] for x in [supply] + ex1]
    for sid in sids: lst.remove(sid)
    at = list(p.slides).index(intro)
    for k, sid in enumerate(sids): lst.insert(at + k, sid)
    # no decoupling in Lab 3 (lecturer, 24/10/2026: the PB-503A supply is clean; the Hanoi board had a home-made ±6 V)
    gone = []
    for sid, x in reversed(list(zip(list(lst), list(p.slides)))):
        if title(x) == 'Decoupling the supply rails' or 'We filter it at the DC supply' in text(x):
            gone.append(title(x) or text(x)[:30]); p.part.drop_rel(sid.rId); lst.remove(sid)
    p.part.rename_slide_parts([x.rId for x in lst])
    dev = next(x for x in p.slides if title(x) == 'Devices and components for this session')
    for sh in dev.shapes:
        if sh.has_text_frame:
            for para in list(sh.text_frame.paragraphs):
                if para.text.startswith('470 µF capacitors') or para.text.startswith('100 nF capacitors'):
                    para._p.getparent().remove(para._p)
    if gone: print('Lab 3: removed', gone)
    # "LM358 limits you will meet" (3 ideas, many numbers) -> one idea per slide, simple words (lecturer, 24/10/2026)
    # only while the old slide is still there; practice slides (Exercise 3) share the title bar: never touch them
    olds = [x for x in p.slides if title(x) in ('LM358 limits you will meet',) + tuple(t for t, *_ in LIMITS)
            and not any(sh.name == 'Practice Exercise' for sh in x.shapes)]
    if any(title(x) == 'LM358 limits you will meet' for x in olds):
        model = olds[0]; at = list(p.slides).index(olds[0])
        bar = copy.deepcopy(next(sh._element for sh in model.shapes if sh.name == 'Title Bar'))
        logo = next(sh for sh in model.shapes if sh.name.startswith('Logo') or (sh.shape_type == 13 and sh.left == 0 and sh.top == 0))
        logo_blob, logo_box = logo.image.blob, (logo.left, logo.top, logo.width, logo.height)
        callout = next((copy.deepcopy(sh._element) for x in olds for sh in x.shapes if sh.name == 'Key word callout'), None)
        new = []
        for t, lines, fig, say in LIMITS:
            x = p.slides.add_slide(model.slide_layout)
            x.shapes._spTree.append(copy.deepcopy(bar)); b = x.shapes[-1]
            b.text_frame.paragraphs[0].runs[0].text = t
            for r in b.text_frame.paragraphs[0].runs[1:]: r._r.getparent().remove(r._r)
            x.shapes.add_picture(io.BytesIO(logo_blob), *logo_box).name = 'Logo'
            tb = x.shapes.add_textbox(Inches(0.6), Inches(1.4), Inches(6.6 if fig else 12.0), Inches(5.2)); tf = tb.text_frame; tf.word_wrap = True
            for k, line in enumerate(lines):
                para = tf.paragraphs[0] if k == 0 else tf.add_paragraph(); para.space_after = Pt(14)
                for part in re.split(r'(\*\*.*?\*\*)', line):
                    if part:
                        r = para.add_run(); r.text = part.strip('*'); r.font.size = Pt(22); r.font.name = 'Arial'
                        r.font.bold = part.startswith('**'); r.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
            if fig:
                iw, ih = Image.open(fig).size; w = Inches(5.6); h = int(w * ih / iw)
                x.shapes.add_picture(fig, Inches(7.4), Inches(1.4), w, h)
            if t.startswith('Clipping') and callout is not None:
                x.shapes._spTree.append(copy.deepcopy(callout))
            x.notes_slide.notes_text_frame.text = say
            new.append(x)
        for x in olds:
            sid = lst[list(p.slides).index(x)]; p.part.drop_rel(sid.rId); lst.remove(sid)
        p.part.rename_slide_parts([x.rId for x in lst])
        sids = [lst[list(p.slides).index(x)] for x in new]
        for sid in sids: lst.remove(sid)
        for k, sid in enumerate(sids): lst.insert(at + k, sid)
    p.save(DECK); print('Lab 3: wiring diagram on slide', list(p.slides).index(s) + 1,
                        '| supply + Exercise 1 at', [list(p.slides).index(x) + 1 for x in [supply] + ex1], 'before', list(p.slides).index(intro) + 1)


if __name__ == '__main__':
    run()
