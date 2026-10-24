"""Lab 2, Task 2 is a band-pass filter for every team (lecturer, 24/10/2026; keys: lab2_team.lab2_bandpass).
Rewrites the Task 2 slides made by build_d2.py / align_web.py: design and build, measure and plot, what to submit.
Paragraph text is replaced (the first run keeps its format). Run after align_web.py, before subscripts.py. Safe to run again."""
from pptx import Presentation

DECK = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab2/HCM Electronic Circuit Lab 2.pptx'


def slide(p, title):
    return next(s for s in p.slides if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == title for sh in s.shapes))


def paragraphs(s):
    for sh in s.shapes:
        if sh.has_text_frame:
            yield from sh.text_frame.paragraphs
        if sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    yield from c.text_frame.paragraphs


def set_text(para, text):
    """The first run keeps its format, but not bold; no bullet."""
    rs = para.runs
    rs[0].text = text; rs[0].font.bold = False
    for r in rs[1:]:
        r._r.getparent().remove(r._r)
    pPr = para._p.pPr
    if pPr is not None:
        for tag in ('buChar', 'buAutoNum'):
            el = pPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}' + tag)
            if el is not None and para._p.getparent().tag.endswith('txBody') and 'tc' in para._p.getparent().getparent().tag:
                pPr.remove(el)


def drop(para):
    para._p.getparent().remove(para._p)


def run():
    p = Presentation(DECK)
    s = slide(p, 'Task 2 (team) – design and build')
    for para in list(paragraphs(s)):
        t = para.text
        if t.startswith('Your card gives the filter type') or t.startswith('Every team builds'):
            set_text(para, 'Every team builds a band-pass filter: the output is across R. Your card gives the quality factor Q. '
                           'L = 1 mH, C = 22 nF ∥ 2.2 nF.')
        elif t == 'Filter type':
            drop(para)
        elif t in ('RC warm-up: type, R, C', 'Task 1: type, R, C'):
            set_text(para, 'Task 1: type, R, C')
    s = slide(p, 'Task 2 (team) – measure and plot')
    for para in list(paragraphs(s)):
        t = para.text
        if t.startswith('Low-pass or high-pass:'):
            drop(para)
        elif t.startswith('Band-pass: find') or t.startswith('Find fL and fH'):
            set_text(para, 'Find fL and fH where Vout/Vin = 0.707 × highest value. BW = fH − fL (kHz).')
    s = slide(p, 'Lab 2 – What to submit')
    for sh in s.shapes:
        if sh.has_table:
            for row in sh.table.rows:
                c0, c1 = row.cells[0], row.cells[1]
                if 'low-pass / high-pass' in c0.text or c0.text.startswith('Task 2: bandwidth BW'):
                    set_text(c0.text_frame.paragraphs[0], 'Task 2: bandwidth BW = fH − fL   (full marks within ±20 %, half within ±35 %)')
                    for para in c0.text_frame.paragraphs[1:]: drop(para)
                    set_text(c1.text_frame.paragraphs[0], 'kHz')
                    for para in c1.text_frame.paragraphs[1:]: drop(para)
    p.save(DECK); print('Lab 2: Task 2 slides = band-pass')


if __name__ == '__main__':
    run()
