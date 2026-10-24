"""Lab 3: the photo of "Connect the rest of the circuit" was the Hanoi build with its own ±6 V supply (lecturer,
24/10/2026: not right for HCM, where the ±6 V comes from the PB-503A). It is replaced by the wiring diagram
fig/p3_wiring.png (fig_practice.py), fitted into the same box. Also: the supply slide and Exercise 1 (voltage
follower) come before the inverting amplifier; no decoupling slides / capacitors (the PB-503A supply is clean).
Run after practice_slides.py. Safe to run again."""
from PIL import Image
from pptx import Presentation
from pptx.util import Emu

DECK = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab3/HCM Electronic Circuit Lab 3.pptx'
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
    p.save(DECK); print('Lab 3: wiring diagram on slide', list(p.slides).index(s) + 1,
                        '| supply + Exercise 1 at', [list(p.slides).index(x) + 1 for x in [supply] + ex1], 'before', list(p.slides).index(intro) + 1)


if __name__ == '__main__':
    run()
