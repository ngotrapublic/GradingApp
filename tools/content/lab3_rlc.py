"""Lecturer, 29/10/2026: Lab 2 is too long for the real pace (the instrument lesson moved in from Lab 1) and Lab 3 is
short, so the inductor + series RLC part and the RLC marked task move from Lab 2 to the start of Lab 3. Nobody has had
Lab 2 yet. Marks (still 50 in total): Lab 1 12, Lab 2 12, Lab 3 16, Lab 4 10.
  Lab 2 (12) = one individual task, the RC design: R, C -> fc = 1/(2 pi R C) within 5 % (half 12 %) = 6, and fc shown on
          the oscilloscope (lecturer, at the tick) = 6.
  Lab 3 (16) = Task 1 (team) band-pass RLC: f0 3, BW 3, graph + conclusion 2; Task 2 (individual) amplifier from a scope
          screen: gain 2, R2/R1 2, Vout 2, phase 2. One trainer lets only 2 students work at a time, so the team builds
          ONE amplifier and each member puts in their own R1 and R2 in turn.
decks(): moves the slides "Inductors" ... "Filters in real life" and the two "Task 2 (team)" slides from Lab 2 to Lab 3
         (after "Devices"; the task slides before the amplifier task), renames Task 2 -> Task 1 and Exercise 5 -> A in
         them, and rewrites title, overview, devices, divider, task and "What to submit" slides of Lab 2 and Lab 3, and
         the word reviews (Lab 3: words from Lab 2 without RLC; Lab 4: words from Lab 3 with RLC).
keys():  moves the RLC questions, keys and card lines from Lab 2 to Lab 3 in courses/SE009/keys.json.
Run after the other Lab 2-4 scripts (lab2_*.py, lab4_review.py), before notes_cleanup.py and subscripts.py; do not run the
Lab 2 RLC scripts (rlc_slides, rlc_table, instrument_slides, lab2_task2, lab2_demo) or gen_keys.py + lab2_team.py
again without running this after them. Safe to run again."""
import copy, json, re, sys
from pptx import Presentation
from lab2_instruments import copy_slide
from lab4_review import set_para, title as title_of
import practice_slides as ps

HCM = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM'
DECK = {n: f'{HCM}/Lab{n}/HCM Electronic Circuit Lab {n}.pptx' for n in (2, 3, 4)}
KEYS = f'{HCM}/GradingApp/courses/SE009/keys.json'
NAME = 'From Lab 2: RLC'
TEMPLATE = 'Lab3_RLC_data_template.xlsx'

MOVED = [('Task 2', 'Task 1'), ('Exercise 5', 'Exercise A'), ('Lab2_RLC_data_template.xlsx', TEMPLATE),
         ('Lab 2 card', 'Lab 3 card'), ('Lab 2 –', 'Lab 3 –')]
CARD_BOX = {'Task 1: type, target fc': 'Task 2: the oscilloscope screen', 'Task 1: the oscilloscope screen': 'Task 2: the oscilloscope screen'}     # "Your card shows" box (after Task 2 -> 1)


def texts(s):
    return [sh.text_frame.text.strip() for sh in s.shapes if sh.has_text_frame]


def find(p, test, start=0):
    return next(i for i, s in enumerate(p.slides) if i >= start and test(s))


def replace_in(s, pairs, notes=True):
    """Replace phrases in every paragraph (runs merged when a phrase is split over runs) and in the notes."""
    n = 0
    frames = [sh.text_frame for sh in s.shapes if sh.has_text_frame]
    frames += [c.text_frame for sh in s.shapes if sh.has_table for row in sh.table.rows for c in row.cells]
    for tf in frames:
        for para in tf.paragraphs:
            t = para.text; new = t
            for a, b in pairs: new = new.replace(a, b)
            if new == t:
                continue
            done = False
            for r in para.runs:                            # phrase inside one run: keep the formatting
                rt = r.text
                for a, b in pairs: rt = rt.replace(a, b)
                if rt != r.text: r.text = rt; done = True
            if para.text != new:                           # split over runs
                para.runs[0].text = new
                for r in para.runs[1:]: r._r.getparent().remove(r._r)
            n += 1
    if notes and s.has_notes_slide:
        nt = s.notes_slide.notes_text_frame; t = nt.text
        for a, b in pairs: t = t.replace(a, b)
        if t != nt.text: nt.text = t; n += 1
    return n


def set_box(sh, lines):
    """Lines of a text box, one per paragraph; the formatting of the paragraph at the same place is kept (the last one
    is cloned when there are more lines). '**x**' = bold."""
    tf = sh.text_frame; paras = list(tf.paragraphs)
    while len(paras) < len(lines):
        paras[-1]._p.addnext(copy.deepcopy(paras[-1]._p)); paras = list(tf.paragraphs)
    for para in paras[len(lines):]:
        para._p.getparent().remove(para._p)
    for para, line in zip(tf.paragraphs, lines):
        if not line:
            for r in para.runs: r._r.getparent().remove(r._r)
        elif para.runs:
            set_para(para, line)
        else:
            para.add_run().text = line


def styled_box(sh, lines):
    """Lines of a box with a heading style (0, like its first paragraph) and a bullet style (1, like its second)."""
    tf = sh.text_frame; tpl = [copy.deepcopy(tf.paragraphs[0]._p), copy.deepcopy(tf.paragraphs[1]._p)]
    body = tf.paragraphs[0]._p.getparent()
    for para in list(tf.paragraphs): body.remove(para._p)
    for text, kind in lines:
        el = copy.deepcopy(tpl[kind]); body.append(el)
    for para, (text, kind) in zip(tf.paragraphs, lines):
        set_para(para, text)


def box(s, start):
    return next(sh for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip().startswith(start))


def table_rows(tbl, rows):
    """Set the rows of a table (rows are cloned / removed; the formatting of row 1 is used for new rows)."""
    tr = tbl._tbl.tr_lst
    while len(tbl._tbl.tr_lst) < len(rows):
        tbl._tbl.tr_lst[-2].addnext(copy.deepcopy(tbl._tbl.tr_lst[-2]))
    for x in tbl._tbl.tr_lst[len(rows):]:
        tbl._tbl.remove(x)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            para = tbl.cell(i, j).text_frame.paragraphs[0]
            for extra in tbl.cell(i, j).text_frame.paragraphs[1:]: extra._p.getparent().remove(extra._p)
            if para.runs: set_para(para, v)
            else: para.add_run().text = v


def move_rlc(p2, p3):
    """Copy the RLC slides into Lab 3 and delete them from Lab 2. Only when Lab 2 still has them."""
    s2 = list(p2.slides)
    a = find(p2, lambda s: 'Inductors' in texts(s))
    b = find(p2, lambda s: title_of(s) == 'Filters in real life')
    tasks = [i for i, s in enumerate(s2) if title_of(s).startswith('Task 2 (team)')]
    lst3 = p3.slides._sldIdLst
    for sid, sl in reversed(list(zip(list(lst3), list(p3.slides)))):
        if sl._element.cSld.get('name') == NAME:
            p3.part.drop_rel(sid.rId); lst3.remove(sid)
    layout = next(l for l in p3.slide_layouts if l.name == 'Blank')
    new = []
    for i in list(range(a, b + 1)) + tasks:
        s = copy_slide(p3, s2[i], layout)
        s._element.cSld.set('name', NAME)
        if s2[i]._element.get('show') == '0': s._element.set('show', '0')
        s.notes_slide.notes_text_frame.text = s2[i].notes_slide.notes_text_frame.text if s2[i].has_notes_slide else ''
        new.append(s)
    lesson, task = new[:b - a + 1], new[b - a + 1:]
    sids = {id(s): lst3[list(p3.slides).index(s)] for s in new}
    for s in new: lst3.remove(sids[id(s)])
    at = find(p3, lambda s: title_of(s) == 'Devices and components for this session') + 1
    for k, s in enumerate(lesson): lst3.insert(at + k, sids[id(s)])
    at = find(p3, lambda s: title_of(s).startswith(('Lab 3 exercise – find R1', 'Task 2 (individual) – find R1')))
    for k, s in enumerate(task): lst3.insert(at + k, sids[id(s)])
    lst2 = p2.slides._sldIdLst
    for i in sorted(list(range(a, b + 1)) + tasks, reverse=True):
        sid = lst2[i]; p2.part.drop_rel(sid.rId); lst2.remove(sid)
    p2.part.rename_slide_parts([x.rId for x in lst2])
    p3.part.rename_slide_parts([x.rId for x in lst3])
    return len(new)


def lab2(p):
    s = p.slides[0]
    replace_in(s, [('RC and RLC circuits', 'RC filters')])
    s.notes_slide.notes_text_frame.text = s.notes_slide.notes_text_frame.text.replace('RC and RLC circuits', 'RC filters')
    ov = p.slides[find(p, lambda s: title_of(s) == 'Lab 2 overview')]
    boxes = sorted([sh for sh in ov.shapes if sh.has_text_frame and sh.name in ('TextBox 14', 'TextBox 16', 'TextBox 18', 'TextBox 20')],
                   key=lambda x: x.left)
    for sh, lines in zip(boxes, [['', '**Instruments**', 'Oscilloscope', 'Function generator', 'Exercises A–D'],
                                 ['', '**RC filters**', '1st-order low-pass and high-pass', 'Cut-off frequency fc', 'Exercises 1–3'],
                                 ['', '**Capacitors**', 'Combining capacitors', 'Measuring capacitance', 'Exercise 4'],
                                 ['', '**Lab 2 task (end of the lab)**', 'Design an RC filter for a target fc (individual)', 'Build it and show fc on the oscilloscope']]):
        set_box(sh, lines)
    ov.notes_slide.notes_text_frame.text = ('Today has 4 parts: the oscilloscope and the function generator with Exercises A to D, '
        'RC filters with Exercises 1 to 3, capacitors with Exercise 4, and at the end of the lab the Lab 2 task: you design '
        'an RC filter for a target f c, build it and show f c on the oscilloscope.\n' + ov.notes_slide.notes_text_frame.text.split('\n')[-1])
    dev = p.slides[find(p, lambda s: title_of(s) == 'Devices and components for this session')]
    set_box(box(dev, 'For each team'), ['For each team:', 'Oscilloscope, function generator, 1X BNC cable, two 10X probes',
                                        'Digital multimeter, PB-503A trainer (breadboard), jumper wires', 'For each student (Lab 2 task):',
                                        '1 resistor + 1 capacitor that you choose (parts box)'])
    dev.notes_slide.notes_text_frame.text = ('Each team uses the oscilloscope, function generator, multimeter and PB-503A.\n'
        'The Lab 2 task is individual: each student takes one resistor and one capacitor from the parts box.')
    # the divider of the old Task 2 becomes the divider of the Lab 2 task, before it
    task = find(p, lambda s: title_of(s).startswith(('Task 1 (individual) – RC', 'Lab 2 task (individual) – RC')))
    div = [i for i, s in enumerate(p.slides) if any(t.startswith(('Lab 2 exercise', 'Lab 2 task\n')) for t in texts(s))]
    if div:
        d = p.slides[div[0]]
        set_box(box(d, 'Lab 2'), ['Lab 2 task', 'RC cut-off frequency (individual)'])
        d.notes_slide.notes_text_frame.text = 'Now the Lab 2 task: 12 points.'
        lst = p.slides._sldIdLst; sid = lst[div[0]]
        if div[0] != task - 1:
            lst.remove(sid); lst.insert(find(p, lambda s: title_of(s).startswith(('Task 1 (individual) – RC', 'Lab 2 task (individual)'))), sid)
    t = p.slides[find(p, lambda s: title_of(s).startswith(('Task 1 (individual) – RC', 'Lab 2 task (individual)')))]
    replace_in(t, [('Task 1 (individual) – RC cut-off frequency', 'Lab 2 task (individual) – RC cut-off frequency')], notes=False)
    set_box(box(t, 'Your card gives'), [
        'Your card gives the filter type (low-pass or high-pass) and a target cut-off frequency fc.',
        'Choose R (220 Ω … 22 kΩ) and C (10, 22 or 47 nF) so that fc = 1 / (2πRC) is as close as possible to the target.',
        'Measure R and C with the multimeter. Build the filter. Function generator: sine, 2 Vpp, High-Z. CH1 = Vin, CH2 = Vout.',
        'Change the frequency until Vout = 0.707 × Vin. This frequency is your measured fc.',
        'Work in turns: two members build, the third calculates. One student uses the oscilloscope at a time.',
        'Submit the R and C you chose (the printed values). Show the lecturer fc on the oscilloscope.'])
    t.notes_slide.notes_text_frame.text = (
        'The Lab 2 task is individual: 12 points. Your card gives the filter type and a target cut-off frequency.\n'
        'Choose R and C so that 1 over 2 pi R C is as close as possible to the target.\n'
        'Measure R and C. Build the filter. Function generator: sine, 2 volts peak to peak, High-Z. CH1 is V in, CH2 is V out.\n'
        'Change the frequency until V out is 0.707 times V in. That is your measured f c.\n'
        'Work in turns: two members build, the third calculates. One student uses the oscilloscope at a time.\n'
        'Submit the R and C you chose, the printed values. Then show me f c on the oscilloscope.')
    w = p.slides[find(p, lambda s: title_of(s) == 'Lab 2 – What to submit')]
    tbl = next(sh.table for sh in w.shapes if sh.has_table)
    table_rows(tbl, [['Value to submit (student page)', 'Unit', 'Marks'],
                     ['The R (Ω) and C (nF) you chose. Marks: fc = 1/(2πRC) within ±5 % of the target (half: ±12 %)', 'Ω, nF', '6'],
                     ['fc on the oscilloscope: show the lecturer Vout = 0.707 × Vin at your fc (at your table, at the tick)', '–', '6'],
                     ['Total', '', '12']])
    w.notes_slide.notes_text_frame.text = ('Type R and C on the student page, under your card, and add one photo of your circuit.\n'
        'Then call me for the tick: show me V out = 0.707 × V in at your f c on the oscilloscope. After the tick, tidy your table. '
        'The next slide shows how.')


def lab3(p):
    s = p.slides[0]
    replace_in(s, [('Operational amplifiers', 'Series RLC filters'), ('RLC filters and op-amps', 'Series RLC filters')])
    s.notes_slide.notes_text_frame.text = 'Welcome to Lab 3. Today we measure a series RLC filter and build an inverting amplifier.'
    words = p.slides[find(p, lambda s: title_of(s) == 'Review – words from Lab 2')]
    replace_in(words, [(a, b) for a, b in WORDS2], notes=False)
    ov = p.slides[find(p, lambda s: title_of(s) == 'Lab 3 overview')]
    boxes = sorted([sh for sh in ov.shapes if sh.has_text_frame and sh.name in ('TextBox 14', 'TextBox 16', 'TextBox 18', 'TextBox 20')],
                   key=lambda x: x.left)
    for sh, lines in zip(boxes, [['', '**Series RLC**', 'Inductors', 'Resonance f0, band-pass, bandwidth BW', 'Demo by the lecturer'],
                                 ['', '**Op-amp basics**', 'LM358: pins and ratings', '±6 V supply from the PB-503A'],
                                 ['', '**Inverting amplifier**', 'Measure gain and phase', 'Clipping'],
                                 ['', '**Lab 3 tasks (end of the lab)**', 'Task 1: band-pass RLC (team)', 'Task 2: amplifier from a screen (individual)']]):
        set_box(sh, lines)
    set_box(box(ov, 'You will study op-amps'), ['You will study op-amps in detail later. Today you learn just enough to build and measure '
                                               'an inverting amplifier. Each team builds one amplifier; in Task 2 each member puts in their own R1 and R2.'])
    ov.notes_slide.notes_text_frame.text = ('Today: the series RLC filter, op-amp basics, the LM358 chip, how to measure gain and phase, '
        'and the two Lab 3 tasks.\nYou will study op-amps in detail later. Today we learn only what we need to build one. '
        'Each team builds one amplifier. In Task 2, each member puts in their own R1 and R2.')
    dev = p.slides[find(p, lambda s: title_of(s) == 'Devices and components for this session')]
    styled_box(box(dev, 'For each team'), [
        ('For each team:', 0),
        ('PB-503A trainer (breadboard and ±6 V supplies), oscilloscope, function generator, 1X BNC cable, 10X probes, multimeter', 1),
        ('1 inductor 1 mH, the capacitor C and the resistor R on your card (Task 1)', 1),
        (f'Excel file “{TEMPLATE}” (student page) on your laptop', 1),
        ('1 LM358 op-amp (return it at the end – we use it again in Lab 4)', 1),
        ('For each student:', 0),
        ('R1 and R2 for Task 2: take them from the parts box once you know them', 1)])
    dev.notes_slide.notes_text_frame.text = ('Each team gets one inductor, the capacitor and the resistor on the card for Task 1, and one LM358.\n'
        'The LM358 goes back to the parts box at the end. We use it again in Lab 4.\n'
        'Download the Excel template from the student page now. For Task 2, each student takes R1 and R2 from the parts box.')
    d = p.slides[find(p, lambda s: any(t.startswith(('Lab 3 exercise\n', 'Lab 3 tasks\n')) for t in texts(s)))]
    set_box(box(d, 'Lab 3'), ['Lab 3 tasks', 'Task 1: RLC filter (team)', 'Task 2: from a screen to the circuit (individual)'])
    d.notes_slide.notes_text_frame.text = 'Now the Lab 3 tasks: 16 points. Task 1 is team work. Task 2 is your own.'
    t = p.slides[find(p, lambda s: title_of(s).startswith(('Lab 3 exercise – find R1', 'Task 2 (individual) – find R1')))]
    replace_in(t, [('Lab 3 exercise – find R1 and R2', 'Task 2 (individual) – find R1 and R2'),
                   ('Build the amplifier with the ±6 V supply of the PB-503A.',
                    'Your team builds one amplifier (±6 V from the PB-503A). In turn, each member puts in their own R1 and R2.')], notes=False)
    for para in box(t, 'Your card shows').text_frame.paragraphs:
        if para.text.startswith('Submit your values'):
            set_para(para, 'Submit your values on the student page. Then show the lecturer your screen.')
    nt = t.notes_slide.notes_text_frame
    nt.text = nt.text.replace('Build it, set', 'Your team builds one amplifier. In turn, each member puts in their own R1 and R2, sets') \
                     .replace('Build it, ', 'Your team builds one amplifier. In turn, each member puts in their own R1 and R2, ')
    nt.text = nt.text.replace('and make your screen look like', 'and makes the screen look like')
    w = p.slides[find(p, lambda s: title_of(s) == 'Lab 3 – What to submit')]
    tbl = next(sh.table for sh in w.shapes if sh.has_table)
    table_rows(tbl, [['Value to submit (student page)', 'Unit', 'Marks'],
                     ['Task 1 (team): peak frequency f0', 'kHz', '3'],
                     ['Task 1 (team): BW = fH − fL (full ±20 %, half ±35 %)', 'kHz', '3'],
                     ['Task 1: graph + conclusion (one screenshot)', '–', '2'],
                     ['Task 2: gain read from the screen on your card', '–', '2'],
                     ['Task 2: R2 / R1 of your resistors (printed values)', '–', '2'],
                     ['Task 2: measured Vout,pp', 'V', '2'],
                     ['Task 2: measured phase shift', 'degrees', '2'],
                     ['Total', '', '16']])
    for row in tbl.rows: row.height = 365760                     # 0.4 in: the table ends above the text below it
    w.notes_slide.notes_text_frame.text = (
        'Task 1 values are the same for the whole team. Use kilohertz for f 0 and BW. Add one screenshot of your team\'s RLC graph.\n'
        'Task 2 is your own: gain and R2 over R1 have no unit, V out in volts, the phase in degrees.\n'
        'Then call me for the tick. I check your Task 2 screen on the oscilloscope. After the tick: the LM358 back to the '
        'parts box, then tidy your table. The next slide shows how.')


WORDS2 = [   # Lab 3 "words from Lab 2": no RLC words (they are taught in Lab 3 now)
    ('Band-pass', 'Oscilloscope'), ('Passes only frequencies near one value', 'Shows a voltage as a wave on a screen'),
    ('Near f0 only', 'CH1 = Vin, CH2 = Vout'),
    ('Capacitor / inductor', 'Capacitor'), ('C stores charge (unit F) / L is a coil of wire (unit H)', 'Stores charge (unit F)'),
    ('22 nF, 1 mH', '100 nF = code 104'),
    ('Resonance (f0)', 'High-Z'), ('The frequency where the effects of L and C cancel', 'Generator setting for a load with a big resistance'),
    ('f0 ≈ 32 kHz today', 'Our circuits: always High-Z'),
    ('Quality factor (Q)', 'Peak-to-peak (Vpp)'), ('How sharp the peak is. Big Q = narrow, high peak', 'From the lowest to the highest point of a wave'),
    ('Q = 2', 'Measure → Pk-Pk'),
    ('Bandwidth (BW)', 'Probe 1X / 10X'), ('How wide the passed band is', '10X makes the signal 10 times smaller; set it on the oscilloscope'),
    ('BW = fH − fL', '10X probe → 10X setting')]
WORDS3 = [   # Lab 4 "words from Lab 3": three op-amp details give their place to RLC words
    ('Feedback resistor', 'Band-pass'), ('The resistor from the output back to the input', 'Passes only frequencies near one value'),
    ('R2 in the exercise', 'Near f0 only'),
    ('Datasheet', 'Resonance (f0)'), ('The document from the maker with pins and limits', 'The frequency where the effects of L and C cancel'),
    ('Search “LM358 datasheet”', 'f0 = 1 / (2π√(LC))'),
    ('Pins that give power to the IC', 'How wide the passed band is'), ('Pin 8 = +6 V, pin 4 = −6 V', 'BW = fH − fL')]


def lab4(p):
    w = p.slides[find(p, lambda s: title_of(s) == 'Review – words from Lab 3')]
    replace_in(w, WORDS3, notes=False)
    for sh in w.shapes:
        if sh.has_table:
            for row in sh.table.rows:
                c = row.cells[0]
                if c.text.startswith('Supply pins'):
                    set_para(c.text_frame.paragraphs[0], 'Bandwidth (BW)')


def decks():
    p2, p3, p4 = (Presentation(DECK[n]) for n in (2, 3, 4))
    moved = move_rlc(p2, p3) if any(title_of(s).startswith('Task 2 (team)') for s in p2.slides) else 0
    n = sum(replace_in(s, MOVED) for s in p3.slides if s._element.cSld.get('name') == NAME) if moved else 0   # only once
    for s in p3.slides:
        if s._element.cSld.get('name') == NAME:
            for sh in s.shapes:
                if sh.has_text_frame:
                    for para in sh.text_frame.paragraphs:
                        if para.text in CARD_BOX: set_para(para, CARD_BOX[para.text])
    for s in p3.slides:                                     # "Your card shows" box of the Task 1 slide: Task 1 lines first
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.startswith('Your card shows') and 'C and R (Task 1)' in sh.text_frame.text:
                set_box(sh, ['Your card shows', 'Variant number', 'C and R (Task 1)', 'Frequency list (Task 1)', 'Task 2: the oscilloscope screen'])
    lab2(p2); lab3(p3); lab4(p4)
    for n_, p in ((2, p2), (3, p3), (4, p4)): p.save(DECK[n_])
    left2 = [i + 1 for i, s in enumerate(p2.slides) if re.search(r'RLC|Task 2|inductor', ' '.join(texts(s)), re.I)]
    print(f'decks: {moved} slides moved to Lab 3 | {n} texts renamed | Lab 2 {len(p2.slides)} slides, Lab 3 {len(p3.slides)} |'
          f' Lab 2 slides still with RLC / Task 2 / inductor: {left2}')


def keys():
    K = json.load(open(KEYS, encoding='utf-8')); L2, L3 = K['labs']['2'], K['labs']['3']
    if not any(q[0] == 'f0' for q in L2['questions']):
        print('keys: already moved'); return
    for v, V2 in L2['variants'].items():
        V3 = L3['variants'][v]
        fc, f0, bw = V2['keys'][0], V2['keys'][1], V2['keys'][2]
        head = V2['card'][0].replace('LAB 2', 'LAB 3')
        rlc, rc = V2['card'][2:6], V2['card'][1]
        V3['keys'] = V3['keys'][:4] + [f0, bw]
        V3['info'] = V3['info'][:2] + [V2['info'][0]]
        V3['card'] = ([head, rlc[0].replace('RLC (team', 'Task 1 – RLC (team')] + rlc[1:] +
                      ['Task 2 – inverting amplifier (your own): LM358, supply ±6 V. CH2 (blue) = input, CH1 (yellow) = output.',
                       'Find R1 and R2 from the screen. Put them into your team\'s amplifier and make your screen look the same. '
                       'Measure Vout,pp and the phase shift.',
                       'Submit + one screenshot of your team\'s RLC graph on the student page (QR).'])
        V3['figs'] = [V3['figs'][0], V2['figs'][1]]
        V2['keys'] = [fc, 0]
        V2['info'] = [V2['info'][1]]
        V2['card'] = [V2['card'][0], rc.replace('Task 1 – RC cut-off frequency:', 'Lab 2 task – RC cut-off frequency (individual):'),
                      'Submit + one photo of your circuit on the student page (QR).']
        V2['figs'] = [V2['figs'][0]]
    note_rlc = L2['parts'][1]['note']
    L3.update(title='Lab 3 – RLC filter & inverting amplifier', total=16,
              manual=[['graph', 'Task 1: RLC graph + conclusion', [0, 1, 2], 'student']],
              questions=[[q[0], q[1], q[2], 2] + q[4:] for q in L3['questions']] +
                        [['f0', 'f0 (the peak frequency)', 'kHz', 3], ['BW', 'BW = fH − fL', 'kHz', 3, {'full': 0.2, 'half': 0.35}]],
              files=[{'label': ['Excel template for your RLC data', 'File Excel mẫu để ghi số liệu RLC'],
                      'url': f'/courses/SE009/files/{TEMPLATE}'}],
              parts=[{'title': ['Task 1 – band-pass RLC filter (team – one circuit for the whole team)',
                                'Bài 1 – Bộ lọc thông dải RLC (làm nhóm – cả nhóm chung một mạch)'],
                      'cardSlice': [1, 5], 'figs': [1], 'questions': [4, 5], 'files': True, 'note': note_rlc},
                     {'title': ['Task 2 – inverting amplifier from an oscilloscope screen (individual)',
                                'Bài 2 – Mạch khuếch đại đảo từ màn hình osci (cá nhân)'],
                      'cardSlice': [5, 7], 'figs': [0], 'image': True, 'questions': [0, 1, 2, 3],
                      'note': ['Your team builds one LM358 amplifier. In turn, put in your own R1 and R2, set the function generator '
                               'like CH2 on your card and measure. The lecturer checks your screen at the tick.',
                               'Cả nhóm lắp chung một mạch LM358. Lần lượt từng bạn lắp R1, R2 của mình, chỉnh máy phát giống CH2 '
                               'trên đề rồi đo. Giảng viên kiểm tra màn hình osci khi tick.']}],
              photo={'head': ['Task 1 – screenshot of your team\'s RLC graph (required, one only). Not a photo of the circuit.',
                              'Bài 1 – ảnh đồ thị RLC của nhóm (bắt buộc, đúng 1 tấm). Không chụp ảnh mạch.'],
                     'empty': L2['photo']['empty'], 'btn': L2['photo']['btn'],
                     'howto': ['<b>Task 1</b> = team RLC (one shared circuit). <b>Task 2</b> = your own amplifier. Type your values, '
                               'upload <b>one screenshot of the Task 1 RLC graph</b> (not a breadboard photo), then <span class="nowrap">tap <b>Submit.</b></span>',
                               '<b>Bài 1</b> = RLC nhóm (chung một mạch). <b>Bài 2</b> = mạch khuếch đại của bạn. Nhập số, tải <b>đúng một ảnh '
                               'đồ thị RLC Bài 1</b> (không phải ảnh breadboard), rồi <span class="nowrap">bấm <b>Nộp.</b></span>'],
                     'check': ['They will check your Task 2 screen <span class="nowrap">on the <b>oscilloscope</b></span> and your '
                               '<b>RLC graph</b>, then confirm at your table.',
                               'Họ sẽ xem màn hình Bài 2 <span class="nowrap">trên <b>osci</b></span> và <b>đồ thị RLC</b>, rồi xác nhận tại cụm máy.'],
                     'need': L2['photo']['need'], 'capture': False})
    L3['photo']['need'] = ['Upload one screenshot of your Task 1 RLC graph first (not the circuit).',
                           'Hãy tải một ảnh đồ thị RLC Bài 1 trước (không phải ảnh mạch).']
    L2.update(title='Lab 2 – RC filters', total=12,
              manual=[['fc_scope', 'fc on the oscilloscope (Vout = 0.707 × Vin)', [0, 3, 6], 'student']],
              questions=[['Task C', 'C you chose', 'nF', 6, {'full': 0.05, 'half': 0.12, 'calc': 'rc_fc', 'from': 1}],
                         ['Task R', 'R you chose', 'Ω', 0]],
              parts=[{'title': ['Lab 2 task – RC cut-off frequency (individual)', 'Bài lab 2 – Tần số cắt mạch RC (cá nhân)'],
                      'cardSlice': [1, None], 'figs': [0], 'questions': [1, 0],
                      'note': ['Design: choose R and C for the target fc on your card. Submit the R and C you chose (the printed values). '
                               'Marks: 6 when fc = 1/(2πRC) is within ±5 % of the target (half: ±12 %), 6 when you show the lecturer '
                               'Vout = 0.707 × Vin at your fc on the oscilloscope.',
                               'Thiết kế: chọn R và C cho f_c mục tiêu trên đề. Nộp R và C đã chọn (giá trị in trên linh kiện). '
                               'Điểm: 6 khi f_c = 1/(2πRC) lệch ≤ ±5 % so với mục tiêu (nửa điểm: ±12 %), 6 khi cho giảng viên xem '
                               'Vout = 0,707 × Vin tại f_c của bạn trên osci.']}])
    for k in ('files', 'photo'): L2.pop(k, None)
    json.dump(K, open(KEYS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('keys: Lab 2 =', L2['total'], '| Lab 3 =', L3['total'], '| total', sum(L['total'] for L in K['labs'].values()))


if __name__ == '__main__':
    what = sys.argv[1:] or ['decks', 'keys']
    if 'decks' in what: decks()
    if 'keys' in what: keys()
