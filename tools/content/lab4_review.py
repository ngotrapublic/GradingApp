"""Lab 4 (lecturer, 29/10/2026: students are slower than planned; the exam has no decoupling).
1. No decoupling lesson: the slides "Capacitors" (coupling and decoupling) and "Decoupling capacitor" go; the recap line
   "Decouple both supply rails" goes; the overview says "Coupling capacitor". The 0.1 uF capacitors at the op-amp pins in
   "Final circuit version 2" stay (they are in the HN schematics), without the word "decoupling".
2. Exam practice after "Skills checklist for the exam" (not marked, after the Lab 4 marks): Exercise 6 combine
   resistors, Exercise 7 set up the instruments from the default state (as the exam starts), Exercise 8 design an RC
   low-pass filter with the parts on the table. Each has its answer slide (practice_slides.add / answer_slide).
3. One final circuit instead of version 1 + version 2 (see one_final).
4. Review fixes (see review): language, untaught words, HN numbers, the marked measurement (also on the cards).
5. Lab 4 marks are team work: four values, one member submits, the others confirm (lab4_team, lab4_keys).
Run after practice_slides.py (`practice_slides.py 4` removes the practice slides), before subscripts.py. Safe to run again."""
import copy, hashlib, re, unicodedata
import schemdraw, schemdraw.elements as elm
from pptx.oxml.ns import qn
from pptx import Presentation
import practice_slides as ps

DECK = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab4/HCM Electronic Circuit Lab 4.pptx'
NAME = 'Lab 4 exam practice'
AFTER = 'Skills checklist for the exam'
DROP = ('Depending on how you connect it, we have:', 'When you only wants DC signal to go through',
        'Decoupling capacitors in microphone circuit', 'We build a similar circuit today.')
RECAP = 'Decouple both supply rails'

EX = [
    dict(bar='Exam practice', fig='p4_combine.png',
         head='Exercise 6: Combine resistors to get a target value (5 minutes)',
         steps=['Your marks are done. You can take the resistors out of your amplifier.',
                'Make 5 kΩ from two 10 kΩ resistors.',
                'Make 12.2 kΩ from the resistors on your table.',
                'Make about 3.2 kΩ from one 10 kΩ and one 4.7 kΩ resistor.',
                'Calculate each value. Then measure it with the multimeter. Write down both.'],
         ask='How did you connect them? How close is each measured value to the target?',
         answer=['**5 kΩ:** two 10 kΩ in **parallel**: 10 × 10 / (10 + 10) = 5 kΩ.',
                 '**12.2 kΩ:** 10 kΩ and 2.2 kΩ in **series**: 10 + 2.2 = 12.2 kΩ.',
                 '**3.2 kΩ:** 10 kΩ and 4.7 kΩ in **parallel**: 10 × 4.7 / (10 + 4.7) ≈ 3.2 kΩ.',
                 'The measured values are usually within 1–2% of the target. In the exam, write the measured values on your schematic.']),
    dict(bar='Exam practice', fig='inst_gen.png',
         head='Exercise 7: Set up the instruments from the start (5 minutes)',
         steps=['Press Default Setup on the oscilloscope. Set the generator load to 50 Ω (Utility → Output Setup).',
                'Now another member sets everything again, without help.',
                'Generator: High-Z, sine, 3 Vpp, 1 kHz, offset 0 V. Connect it to CH1 with the 1X BNC cable.',
                'Oscilloscope: set CH1 to 1X. Measure the frequency and the Pk-Pk of CH1.',
                'The screen must show 1 kHz and 3 Vpp.'],
         ask='What do you see if you forget High-Z? And if you forget the 1X setting?',
         answer=['The exam starts like step 1: the oscilloscope in its default state and the generator at 50 Ω. Check both first.',
                 '**Generator at 50 Ω:** the real output is **2 times** the number you set: 6 Vpp instead of 3 Vpp.',
                 '**Oscilloscope at 10X (the default) with a 1X cable:** the reading is **10 times too big**: 30 Vpp instead of 3 Vpp.']),
    dict(bar='Exam practice', fig='p4_rc_design.png',
         head='Exercise 8: Design a low-pass filter for fc = 1 kHz (10 minutes)',
         steps=['Use one 100 nF capacitor and the resistors on your table. You can combine resistors.',
                'Choose R so that fc = 1 / (2πRC) is within ±20% of 1 kHz (800 Hz – 1.2 kHz).',
                'Build the filter. Generator: sine, 2 Vpp, High-Z. CH1 = Vin, CH2 = Vout (across C).',
                'Measure Vout at 100 Hz, at your fc and at 10 kHz.'],
         ask='Which R did you choose? Is Vout at your fc close to 0.707 × Vin?',
         answer=['You need R = 1 / (2π × 1 kHz × 100 nF) ≈ **1.6 kΩ**. There is no 1.6 kΩ resistor, so combine two.',
                 '**2.2 kΩ in parallel with 4.7 kΩ ≈ 1.5 kΩ:** fc ≈ 1.06 kHz. **10 kΩ in parallel with 2.2 kΩ ≈ 1.8 kΩ:** fc ≈ 880 Hz. Both are within ±20%.',
                 'At your fc, Vout ≈ 0.707 × Vin (about 1.4 Vpp). At 100 Hz, Vout ≈ Vin. At 10 kHz, Vout is about 10 times smaller.']),
]


def figures():
    schemdraw.config(fontsize=16, lw=2)
    with schemdraw.Drawing(file=ps.FIG + 'p4_combine.png', dpi=200, show=False) as d:
        elm.Label().at((2.25, 1.3)).label('Series: R = R1 + R2')
        elm.Dot(open=True).at((0, 0))
        elm.Resistor().right().length(2.25).label('R1')
        elm.Resistor().right().length(2.25).label('R2')
        elm.Dot(open=True)
        elm.Label().at((2.25, -2.2)).label('Parallel: R = R1 × R2 / (R1 + R2)')
        elm.Dot(open=True).at((0, -4.5))
        elm.Line().right(1); a = d.here
        elm.Line().up(1); elm.Resistor().right().length(2.5).label('R1'); elm.Line().down(1); b = d.here
        elm.Line().at(a).down(1); elm.Resistor().right().length(2.5).label('R2', loc='bottom'); elm.Line().up(1)
        elm.Line().at(b).right(1); elm.Dot(open=True)
    with schemdraw.Drawing(file=ps.FIG + 'p4_rc_design.png', dpi=200, show=False) as d:
        elm.SourceSin().up().length(3).label('Function\ngenerator', loc='bottom', ofst=0.3)
        elm.Dot().label('CH1', loc='left', ofst=0.15)
        elm.Resistor().right().length(3.5).label('R = ?')
        top = d.here; elm.Dot()
        elm.Capacitor().down().length(3).label('C = 100 nF\n(104)', loc='bottom')
        elm.Line().left(3.5)
        elm.Line().at(top).right(2); elm.Dot(open=True).label('CH2\n(across C)', loc='right')
        elm.Line().at((3.5, 0)).right(2); elm.Dot(open=True)
        elm.Ground().at((0, 0))


# 3. One final circuit (lecturer, 29/10/2026): version 1 "dies out after about 1 minute" only with the HN home-made
#    supply (12 V + 2 x 1 MOhm divider as 0 V); on the PB-503A it works. The marks use the version 2 values
#    (4.7 kOhm, 1 nF), so version 1 goes and version 2 becomes "Final circuit". Slides are found by old or new text.
V1 = ('Final circuit (version 1)', 'Final circuit version 1', 'Second, add 0.1 µF capacitors at the voltage supply pins')
# lecturer, 29/10/2026: no 0.1 uF at the op-amp supply pins either; C4 and C5 painted out of the HN schematics (fix_divider.paint)
NOC45 = {'36093e': 'hn_s3_solution_noc45.png', 'f8fba8': 'hn_s3_stage1_noc45.png', 'f73224': 'hn_s3_final2_noc45.png'}
FINAL = {   # old first line -> new lines of the text box ("**x**" = bold)
    'So how do we solve the echo?': [
        '**Before you connect the microphone**',
        'Your voice gives tens to hundreds of mVpp (Exercise 4).',
        'With a gain of 291, the output would need tens of volts. It clips (Lab 3).',
        'The speaker is also very close to the microphone. A loud speaker gives an echo (acoustic feedback).',
        'So we make two changes.'],
    'The resulting circuit is this': [
        '**The final circuit is this**',
        'Disconnect the function generator.',
        'Connect the microphone circuit to stage 1 through the 1 µF capacitor.',
        'Connect the final output to the speaker.'],
    'You will see that the echo is much less': [
        'Speak into the microphone through the rolled paper.',
        'You hear your voice in the speaker, with little echo.',
        'The output signal looks something like this'],
}
FINAL['Before you connect the microphone'] = FINAL['So how do we solve the echo?']     # running again
FINAL_NOTES = {
    'Before you connect the microphone': 'Before you connect the microphone: your voice gives tens to hundreds of millivolts. '
        'With a gain of 291, the output would need tens of volts, so it clips, like in Lab 3. The speaker is also very '
        'close to the microphone. A loud speaker gives an echo. So we make two changes.',
    'The final circuit is this': 'This is the final circuit. Disconnect the function generator. Connect the microphone '
        'circuit to stage 1 through the 1 microfarad capacitor. Connect the final output to the speaker.',
    'Speak into the microphone through': 'Speak into the microphone through the rolled paper. You hear your voice in the '
        'speaker, with little echo. The output signal looks like this.',
}


def set_lines(sh, lines):
    """Replace the text of an HN text box: one paragraph per line with an empty paragraph between (as in HN)."""
    tf = sh.text_frame; paras = tf.paragraphs
    tpl = copy.deepcopy(paras[0]._p)
    for r in tpl.findall(qn('a:r')) + tpl.findall(qn('a:br')): tpl.remove(r)
    body = paras[0]._p.getparent()
    for para in paras: body.remove(para._p)
    for k, line in enumerate(lines):
        if k:
            body.append(copy.deepcopy(tpl))
        p_ = copy.deepcopy(tpl); body.append(p_)
        from pptx.text.text import _Paragraph
        para = _Paragraph(p_, tf)
        for part in re.split(r'(\*\*.*?\*\*)', line):
            if part:
                r = para.add_run(); r.text = part.strip('*'); r.font.bold = part.startswith('**')


def one_final(p):
    gone = drop(p, lambda s: any(v in ps.text_of(s) for v in V1))
    for s in p.slides:
        for sh in s.shapes:
            if not sh.has_text_frame:
                continue
            for r in (r for para in sh.text_frame.paragraphs for r in para.runs):
                if r.text in ('Final circuit version 2', 'Final circuit (version 2)'):
                    r.text = 'Final circuit'
            first = sh.text_frame.paragraphs[0].text
            if first in FINAL:
                set_lines(sh, FINAL[first])
            runs = sh.text_frame.paragraphs[0].runs
            if first.startswith('Third,') and runs:
                runs[0].text = runs[0].text.replace('Third,', 'Second,')
        for pic in [x for x in s.shapes if x.shape_type == 13]:
            part = s.part.related_part(pic._element.blip_rId)
            if hashlib.md5(part.blob).hexdigest()[:6] in NOC45:
                part._blob = open(ps.FIG + NOC45[hashlib.md5(part.blob).hexdigest()[:6]], 'rb').read()
        for key, say in FINAL_NOTES.items():
            if key in ps.text_of(s):
                s.notes_slide.notes_text_frame.text = say
        nt = s.notes_slide.notes_text_frame if s.has_notes_slide else None
        if nt is not None:
            nt.text = nt.text.replace('Fix 3:', 'Fix 2:').replace('Look at the changes: 4.7 kΩ, 1 nF, 100 nF.',
                                                                 'Look at the changes: 4.7 kΩ and 1 nF.')
        if nt is not None and nt.text in ('Final circuit, version 2.', 'This is version 2 of the schematic.'):
            nt.text = {'Final circuit, version 2.': 'The final circuit.',
                       'This is version 2 of the schematic.': 'This is the schematic of the final circuit.'}[nt.text]
    return gone


# 4. Review before class (lecturer, 29/10/2026): language of the HN slides (simple, complete sentences, no "->" chains),
#    words that were not taught, HN numbers that disagree with the exercise answers, and the marked measurement
#    (speaker disconnected: the 8 Ohm speaker loads the LM358 output; generator High-Z: at 50 Ohm the input doubles).
TEXT = {   # whole paragraph -> new paragraph (first run's format kept; "**x**" = bold)
    'Decoupling capacitor': 'Voltage follower',                                    # Lab 3 words: decoupling not taught
    'A capacitor from the supply to GND that removes noise': 'An op-amp circuit with gain 1: the output follows the input',
    '470 µF and 100 nF': 'Pin 1 connected to pin 2',
    'Sends noise on the supply to GND': 'How high or low a sound is',                 # Lab 4 words (hidden slide)
    '470 µF on each rail': 'A higher frequency gives a higher pitch',
    'When you only wants AC signal to go through': 'Use a coupling capacitor when you want only the AC signal to go through.',
    'You connect a coupling capacitor': 'The DC is blocked.',
    'DC signal is blocked': 'It is used in audio circuits and in other circuits that work with AC signals.',
    'This is usually used in audio circuits, or any circuit that process AC signal': '',
    'That means the speaker needs AC signal to generate suitable sound frequency for you':
        'So the speaker needs an AC signal with a frequency that you can hear.',
    'Bigger amplitude -> bigger sound': 'A bigger amplitude gives a louder sound.',
    'Bigger frequency -> higher pitch': 'A higher frequency gives a higher pitch.',
    'Sound creates vibration -> change capacitor value -> generate AC signal':
        'Sound makes a thin plate vibrate. The capacitance changes. This makes a small AC signal.',
    'But with electret or microphone in general': 'A microphone always needs a cover.',
    'You don’t just talk straight to it': 'You do not talk straight into it.',
    'There’s always some shield covering the mic': '',
    'This is to prevent unwanted sound from winds and air movement in general': 'The cover blocks the noise of wind and moving air.',
    'Not any other direction -> unwanted noises': 'Sound from other directions is unwanted noise.',
    'But our electret doesn’t care': 'But our electret hears all directions.',
    'Most microphones only generates mV signals': 'Most microphones give only a few mV.',
    'We always need amplifier circuit for microphones': 'We always need an amplifier for a microphone.',
    'Does that mean we can just connect to the speaker right?': 'Can we connect it directly to the speaker?',
    'But you see how the speaker deteriorate your output?': 'But the speaker makes your output much smaller:',
    'We need to filter it but not losing the gain': 'We filter it out, but keep the gain for the voice.',
    'Solution: Just add a 1 nF capacitor || 30kΩ in the first amplifier':
        '**Solution:** add a 1 nF capacitor in parallel with the 30 kΩ resistor in stage 1.',
    '(or use 2 of 2.2 nF in series to create 1.1 nF)': '(Or use two 2.2 nF capacitors in series: 1.1 nF.)',
    'Build the electret test circuit: bias resistor from +6 V, ground pin to GND.':
        'Build the circuit of the slide before: R1 = 10 kΩ from +6 V, R2 = 10 kΩ to GND, microphone ground pin to GND.',
    'Measurement (electret disconnected, function generator = 10 mVpp sine at the stage-1 input)':
        'Measurement (microphone and speaker disconnected; function generator High-Z, 10 mVpp sine at the stage-1 input)',
}
NOTES = [('1. Build the electret test circuit: bias resistor from +6 V, ground pin to GND.',
          '1. Build the circuit of the slide before: R1 = 10 kΩ from +6 V, R2 = 10 kΩ to GND, microphone ground pin to GND.'),
         ('Disconnect the microphone. Put 10 mVpp from the function generator into stage 1.',
          'Disconnect the microphone and the speaker. Set the function generator to High-Z and put 10 mVpp into stage 1.'),
         ('Microphones usually have a cover to block wind noise.', 'A microphone always needs a cover. You do not talk straight into it. The cover blocks the noise of wind and moving air.')]
# HN slides with the speaker high-pass for R = 8 Ohm (and 423 Hz instead of 42 Hz): Exercise 2 answers it with 58 Ohm
HIDE_NOTES = ('With C = 0.1 µF and R = 8 Ω', 'Now with 470 µF, fc is about 40 Hz')
KEYS = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/courses/SE009/keys.json'
CARD = [('Function generator: 10 mVpp sine at the stage-1 input', 'Function generator: High-Z, 10 mVpp sine at the stage-1 input'),
        ('Electret disconnected.', 'Microphone and speaker disconnected.'),
        ('10 mVpp input, electret disconnected', '10 mVpp input (High-Z), microphone and speaker disconnected')]


def set_para(para, new):
    runs = para.runs
    rpr = copy.deepcopy(runs[0]._r.find(qn('a:rPr'))) if runs else None
    for r in runs: r._r.getparent().remove(r._r)
    for part in re.split(r'(\*\*.*?\*\*)', new):
        if part:
            r = para.add_run(); r.text = part.strip('*')
            if rpr is not None: r._r.insert(0, copy.deepcopy(rpr))         # keeps the bold of a table word
            if part.startswith('**'): r.font.bold = True
            elif rpr is not None and new.startswith('**'): r.font.bold = False


def review(p):
    n = 0
    for s in p.slides:
        frames = [sh.text_frame for sh in s.shapes if sh.has_text_frame]
        frames += [c.text_frame for sh in s.shapes if sh.has_table for row in sh.table.rows for c in row.cells]
        for tf in frames:
            for para in list(tf.paragraphs):
                if para.text == 'Voltage follower' and title(s) == 'Review – words from Lab 4':
                    set_para(para, 'Pitch'); n += 1                 # the decoupling row of the Lab 4 words
                key = unicodedata.normalize('NFKC', para.text)          # HN slides use the ohm sign U+2126
                if key in TEXT:
                    new = TEXT[key]
                    if new: set_para(para, new)
                    else:                                           # drop the line and the empty line before it
                        prev = para._p.getprevious()
                        if prev is not None and not ''.join(prev.itertext()).strip(): prev.getparent().remove(prev)
                        para._p.getparent().remove(para._p)
                    n += 1
        if s.has_notes_slide:
            nt = s.notes_slide.notes_text_frame; t = nt.text
            for a, b in NOTES: t = t.replace(a, b)
            if t != nt.text: nt.text = t; n += 1
            if any(h in nt.text for h in HIDE_NOTES): s._element.set('show', '0')
    # text boxes that run under the picture on their right (slide 6 "Coupling capacitor", the microphone cover)
    for s in p.slides:
        pics = [x for x in s.shapes if x.shape_type == 13 and x.width > 1.5e6]
        for sh in s.shapes:
            if sh.has_text_frame and sh.text_frame.text.startswith(('Use a coupling capacitor', 'A microphone always needs a cover')):
                right = min((x.left for x in pics if x.left > sh.left), default=None)
                if right and sh.left + sh.width > right:
                    sh.width = right - sh.left - 91440
    k = open(KEYS, encoding='utf-8').read(); k2 = k
    for a, b in CARD: k2 = k2.replace(a, b)
    if k2 != k: open(KEYS, 'w', encoding='utf-8').write(k2)
    return n


# 5. Lab 4 is team work too (lecturer, 29/10/2026: "the circuit is hard"): the team measures all four values (stage 1 and
#    stage 2, 1 kHz and 5 kHz, 1.5 marks each) and one member submits them for the team, the others confirm
#    (keys.json: team_submit). Team demo 4 + measurements 6 = 10, as before.
LAB4_ROWS = [['Value', 'Measurement (microphone and speaker disconnected; function generator High-Z, 10 mVpp sine at the stage-1 input)', 'Unit'],
             ['1', 'Vpp at the output of stage 1, f = 1 kHz', 'mVpp'], ['2', 'Vpp at the output of stage 2, f = 1 kHz', 'mVpp'],
             ['3', 'Vpp at the output of stage 1, f = 5 kHz', 'mVpp'], ['4', 'Vpp at the output of stage 2, f = 5 kHz', 'mVpp']]
LAB4_MARKS = [['Item', 'Marks'], ['Team demo: speak into the microphone, the lecturer hears you in the speaker', '4'],
              ['The four team measurements (1.5 each), submitted on the student page', '6'], ['Total', '10']]
LAB4_SUBMIT = ('One member submits the four values and one photo of your circuit on the student page. The others tap Confirm '
               'on their own phone. Then call the lecturer for the tick – before the exam review.')
LAB4_SAY = ('Lab 4 is team work. Team demo: 4 points. Speak into the microphone. I must hear you in the speaker.\n'
            'Then the team measures four values: 6 points, 1.5 each. Disconnect the microphone and the speaker. Set the function '
            'generator to High-Z and put 10 millivolts peak to peak into stage 1. Measure V p p at the output of stage 1 and of '
            'stage 2, at 1 kilohertz and at 5 kilohertz.\n'
            'One member submits the four values and one photo of your circuit on the student page. The others tap Confirm on '
            'their own phone. Then call me for the tick.')
LAB4_OVERVIEW = ('Today each team builds one circuit together. The team measures four values for marks: one member submits, '
                 'the others confirm (see the last slides).')


def lab4_team(p):
    from lab3_rlc import table_rows                     # (lab3_rlc imports this file)
    ov = next(s for s in p.slides if title(s) == 'Lab 4 overview')
    for sh in ov.shapes:
        if sh.has_text_frame and sh.text_frame.text.startswith('Today each team builds one circuit together'):
            set_para(sh.text_frame.paragraphs[0], LAB4_OVERVIEW)
    nt = ov.notes_slide.notes_text_frame
    nt.text = nt.text.replace('Today each team builds one circuit together. Then each person does one measurement alone for marks.',
                              'Today each team builds one circuit together. The team measures four values for marks. One member submits, the others confirm.')
    m = next(s for s in p.slides if title(s) == 'Lab 4 – what is marked')
    tables = sorted([sh for sh in m.shapes if sh.has_table], key=lambda x: x.top)
    table_rows(tables[0].table, LAB4_ROWS); table_rows(tables[1].table, LAB4_MARKS)
    for sh in m.shapes:
        if sh.has_text_frame and sh.text_frame.text.startswith(('Submit your value', 'One member submits the four values')):
            set_para(sh.text_frame.paragraphs[0], LAB4_SUBMIT)
    m.notes_slide.notes_text_frame.text = LAB4_SAY


def lab4_keys():
    import json
    K = json.load(open(KEYS, encoding='utf-8')); L = K['labs']['4']; V = L['variants']
    var = lambda s, t, m: str(s * 100 + 3 * (t - 1) + m if m < 4 else s * 100 + 18 + t)
    if len(L['questions']) == 1:                        # still one value per member: collect the four of team 1
        vals = {s: [V[var(s, 1, m)]['keys'][0] for m in (1, 2, 3, 4)] for s in sorted({int(v) // 100 for v in V})}
        for v, X in V.items():
            s = int(v) // 100; n = int(v) % 100; t, m_ = ((n - 1) // 3 + 1, (n - 1) % 3 + 1) if n <= 18 else (n - 18, 4)
            X['keys'] = vals[s]
            X['info'] = ['Team: stage 1 and stage 2 output, 1 kHz and 5 kHz', '10 mVpp input (High-Z), microphone and speaker disconnected']
            X['card'] = [f'Electric Circuit Lab – LAB 4   |   Variant {v}   |   Team {t} – Member {m_}',
                         'Team task – the same for all members.',
                         'Function generator: High-Z, 10 mVpp sine at the stage-1 input', 'Microphone and speaker disconnected.',
                         'Measure Vpp at the output of stage 1 and of stage 2, at 1 kHz and at 5 kHz (four values).',
                         'One member submits the four values (mVpp) + one photo of your circuit on the student page (QR); the others confirm.']
        L['questions'] = [['S1 1k', 'Stage 1 output, 1 kHz', 'mVpp', 1.5], ['S2 1k', 'Stage 2 output, 1 kHz', 'mVpp', 1.5],
                          ['S1 5k', 'Stage 1 output, 5 kHz', 'mVpp', 1.5], ['S2 5k', 'Stage 2 output, 5 kHz', 'mVpp', 1.5]]
    L['team_submit'] = True
    json.dump(K, open(KEYS, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def title(s):
    return next((sh.text_frame.text.strip() for sh in s.shapes if sh.name == 'Title Bar'), '')


def drop(p, test):
    lst = p.slides._sldIdLst; n = 0
    for sid, sl in reversed(list(zip(list(lst), list(p.slides)))):
        if test(sl):
            p.part.drop_rel(sid.rId); lst.remove(sid); n += 1
    p.part.rename_slide_parts([x.rId for x in lst])
    return n


def run():
    figures()
    p = Presentation(DECK); lst = p.slides._sldIdLst
    drop(p, lambda s: s._element.cSld.get('name') == NAME)
    gone = drop(p, lambda s: any(d in ps.text_of(s) for d in DROP))
    v1 = one_final(p)
    fixed = review(p)
    lab4_team(p)
    # recap: no decoupling line on the slide or in the notes
    rec = next(s for s in p.slides if title(s).startswith('Recap – the inverting amplifier'))
    for sh in rec.shapes:
        if sh.has_text_frame:
            for para in list(sh.text_frame.paragraphs):
                if para.text.startswith(RECAP):
                    para._p.getparent().remove(para._p)
    nt = rec.notes_slide.notes_text_frame
    nt.text = nt.text.replace(', decoupling on both rails.', '.')
    # overview: step 1 is the coupling capacitor only; step 4 has the exam practice
    ov = next(s for s in p.slides if title(s) == 'Lab 4 overview')
    for sh in ov.shapes:
        if sh.has_text_frame:
            for r in (r for para in sh.text_frame.paragraphs for r in para.runs):
                r.text = r.text.replace('Coupling and decoupling capacitors', 'Coupling capacitor') \
                               .replace('Break & fix practice', 'Exam practice: Exercises 6–8')
    # the exam practice
    model = next(s for s in p.slides if title(s) == ps.MODEL)
    ref = next(s for s in p.slides if title(s) == AFTER)
    new = []
    for ex in EX:
        new += [ps.add(p, model, ex), ps.answer_slide(p, model, ex)]
    for s in new:
        s._element.cSld.set('name', NAME)
    sids = [lst[list(p.slides).index(x)] for x in new]
    for sid in sids: lst.remove(sid)
    at = list(p.slides).index(ref) + 1
    for k, sid in enumerate(sids): lst.insert(at + k, sid)
    p.save(DECK)
    lab4_keys()
    left = [i + 1 for i, s in enumerate(p.slides) if 'ecoupl' in ps.text_of(s) and s._element.get('show') != '0']
    print(f'Lab 4: {gone} decoupling slides removed | {v1} version-1 slides removed | {fixed} texts reviewed | exam practice at {at + 1}-{at + len(new)} | {len(p.slides)} slides |'
          f' "decoupl" still on visible slides: {left}')


if __name__ == '__main__':
    run()
