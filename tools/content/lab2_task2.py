"""Lab 2 (lecturer, 24/10/2026): Task 1 is a design (target fc on the card; keys: lab2_team.lab2_task1_design) and Task 2
measures a band-pass filter with the team's C and R, like Exercises 6-7 (keys: lab2_team.lab2_task2_measure). Rewrites the slides made by build_d2.py / align_web.py:
Task 1, devices, Task 2 design and build, measure and plot, what to submit.
Paragraph text is replaced (the first run keeps its format). Run after align_web.py, before subscripts.py. Safe to run again."""
from pptx import Presentation

DECK = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab2/HCM Electronic Circuit Lab 2.pptx'


TASK1 = ['Your card gives the filter type (low-pass or high-pass) and a target cut-off frequency fc.',
         'Choose R (220 Ω … 22 kΩ) and C (10, 22 or 47 nF) so that fc = 1 / (2πRC) is as close as possible to the target.',
         'Measure R and C with the multimeter. Calculate fc again with these values.',
         'Build the filter. Function generator: sine, 2 Vpp, High-Z. CH1 = Vin, CH2 = Vout.',
         'Change the frequency until Vout = 0.707 × Vin. This frequency is your measured fc.',
         'Submit the R and C you chose (the printed values). Show the lecturer fc on the oscilloscope.']


BUILD = ['Every team builds a band-pass filter, the same circuit as in Exercise 6. Your card gives C and R. L = 1 mH.',
         'Take the 1 mH inductor, the capacitor C and the resistor R on your card.',
         'Build the filter: generator → L → C → R → ground. The output (CH2) is across R, at the ground side.',
         'Function generator: sine, 2 Vpp, High-Z. CH1 = Vin, CH2 = Vout.',
         'Before you measure, calculate f0 = 1 / (2π√(LC)) and BW = R / (2πL).']


def slide(p, *titles):
    return next(s for s in p.slides if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() in titles for sh in s.shapes))


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
    # Task 1 is a design (option A): target fc on the card, the student chooses R and C
    s = slide(p, 'Task 1 (individual) – RC cut-off frequency')
    for sh in s.shapes:
        if sh.has_text_frame and len(sh.text_frame.paragraphs) == 6 and 'cut-off' in sh.text_frame.text:
            for para, t in zip(sh.text_frame.paragraphs, TASK1):
                set_text(para, t)
    s = slide(p, 'Devices and components for this session')
    for para in paragraphs(s):
        if para.text.startswith('Task 1, each student'):
            set_text(para, 'Task 1, each student: 1 resistor + 1 capacitor that you choose (parts box)')
    s = slide(p, 'Lab 2 – What to submit')
    for sh in s.shapes:
        if sh.has_table:
            for row in sh.table.rows:
                c0 = row.cells[0]
                if c0.text.startswith('Task 1 (individual)'):
                    set_text(row.cells[1].text_frame.paragraphs[0], 'Ω, nF')
                    set_text(c0.text_frame.paragraphs[0], 'Task 1 (individual): the R (Ω) and C (nF) you chose. Marks: fc = 1/(2πRC) within ±5 % of the target (half: ±12 %)')
    # Task 2 = measure a band-pass filter with the team's C and R (lab2_team.lab2_task2_measure)
    s = slide(p, 'Task 2 (team) – design and build', 'Task 2 (team) – build the filter')
    for sh in s.shapes:
        if sh.name == 'Title Bar':
            set_text(sh.text_frame.paragraphs[0], 'Task 2 (team) – build the filter')
        elif sh.has_text_frame and sh.text_frame.paragraphs[0].text.startswith('Every team builds'):
            paras = list(sh.text_frame.paragraphs)
            for para, t in zip(paras, BUILD):
                set_text(para, t)
            for para in paras[len(BUILD):]:
                drop(para)
    for para in list(paragraphs(s)):
        if para.text in ('Q', 'C and R (Task 2)'):
            set_text(para, 'C and R (Task 2)')
    s = slide(p, 'Task 2 (team) – measure and plot')
    for para in list(paragraphs(s)):
        t = para.text
        if t.startswith('Low-pass or high-pass:'):
            drop(para)
        elif t.startswith('Band-pass: find') or t.startswith('Find fL and fH'):
            set_text(para, 'Find fL and fH where Vout/Vin = 0.707 × the peak value. BW = fH − fL (kHz).')
        elif t.startswith('To find f'):
            set_text(para, 'To find f0, fL and fH, use the method of Exercise 7 (turn the knob slowly).')
        elif t.startswith('Find the highest') or t.startswith('Find the peak'):
            set_text(para, 'Find the peak: the highest Vout / Vin. Add at most 2 points near it. The peak frequency is f0 (kHz).')
    s = slide(p, 'Lab 2 – What to submit')
    for sh in s.shapes:
        if not sh.has_table:
            continue
        for row in list(sh.table.rows):
            c0, c1, c2 = row.cells[0], row.cells[1], row.cells[2]
            t = c0.text
            if 'Task 1' in t and 'individual' in t:
                set_text(row.cells[1].text_frame.paragraphs[0], 'Ω, nF')
                set_text(c0.text_frame.paragraphs[0], 'Task 1 (individual): the R (Ω) and C (nF) you chose. Marks: fc = 1/(2πRC) within ±5 % of the target (half: ±12 %)')
            elif t.startswith('Task 2: measured R') or t.startswith('Task 2: peak frequency'):
                set_text(c0.text_frame.paragraphs[0], 'Task 2: peak frequency f0'); set_text(c1.text_frame.paragraphs[0], 'kHz')
                set_text(c2.text_frame.paragraphs[0], '4')
            elif t.startswith('Task 2: frequency of maximum output') or t.startswith('Task 2: bandwidth'):
                set_text(c0.text_frame.paragraphs[0], 'Task 2: bandwidth BW = fH − fL   (full marks within ±20 %, half within ±35 %)')
                set_text(c1.text_frame.paragraphs[0], 'kHz'); set_text(c2.text_frame.paragraphs[0], '5')
        bw = [r for r in sh.table.rows if r.cells[0].text.startswith('Task 2: bandwidth')]
        for r in bw[1:]:                                   # the old BW row: the max-output row became the BW row
            r._tr.getparent().remove(r._tr)
    s = slide(p, 'Devices and components for this session')
    for para in list(paragraphs(s)):
        if para.text.startswith('Task 2, each team'):
            set_text(para, 'Task 2, each team: 1 inductor 1 mH, the capacitor C and the resistor R on your card')
        elif para.text.startswith('Resistors 47'):
            drop(para)
    s = slide(p, 'Real components at 32 kHz', 'Real components')
    for sh in s.shapes:
        if sh.name == 'Title Bar':
            set_text(sh.text_frame.paragraphs[0], 'Real components')
    for para in list(paragraphs(s)):
        if para.text.startswith('The inductor wire has'):
            set_text(para, 'The inductor wire has a small resistance (RL). It makes BW a little bigger than R / (2πL).')
        elif para.text.startswith('Parts are not exact'):
            set_text(para, 'Parts are not exact: L is ±10%, C is ±5%. Your f0 can be a few % away from the theory.')
    p.save(DECK); print('Lab 2: Task 2 slides = band-pass')


if __name__ == '__main__':
    run()
