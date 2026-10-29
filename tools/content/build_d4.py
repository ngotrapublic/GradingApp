import os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from deck import *

S = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/_build'
HN = '/Users/mac/Tra/SE9_ElecCircuitLab/HN'
HCM = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM'
FIG = f'{S}/../fig'
BOX = dict(fill='F3F7F0', line='B7CFA8', geom='roundRect', inset=0.12)
P = lambda s: f'{HCM}/figures/{s}'
IMG_MIC_TEST = P('1792490309922_265884367885448100_7083566079884472153_0b85f01712dc77756a064fa53d5e372a.jpg')
IMG_MIC_LEADS = P('1792490310186_265884367885448100_7083566079884472153_1082ead9565ccec91cb3b89d6d3b1170.jpg')
IMG_FINAL = P('1792490310314_265884367885448100_7083566079884472153_dc39cb8dcb6b854e22b95e166a4c077e.jpg')

dk = Deck(f'{HN}/Electronic Circuit Lab Slide 3.pptx', f'{S}/build_d4')
F = lambda n: tone(dk, dk.slide_file(n), 3, n)
src2 = f'{S}/u2'; o2 = slide_order(src2)
hn2 = lambda n: tone(dk, dk.import_slide(src2, o2[n - 1], 'l2_'), 2, n)

dk.edit_text(F(1), [('Working with integrated circuit', 'Microphone to speaker'), ('Microphone to Speaker', '& exam review'), ('4 hours', '3 hours')])

add_line_after(dk, F(1), '3 hours', 'Lecturer: TraNLT2@fe.edu.vn'); widen_shape(dk, F(1), '3 hours', 6.0)
ids = Ids()
w, g = 2.85, 0.3
steps = [('Speaker', ['8 Ω speaker on the PB-503A', 'Coupling and decoupling capacitors']),
         ('Electret microphone', ['Bias circuit', 'Capture the microphone signal']),
         ('Two-stage amplifier', ['Stage 1 from Lab 3 + stage 2', 'Test with the function generator', 'Final circuit']),
         ('Exam review', ['Exam format', 'Skills checklist', 'Break & fix practice'])]
s_ov = dk.new_slide(header(ids, 'Lab 4 overview')
    + ''.join(card(ids, 0.55 + i * (w + g), 1.3, w, 3.3, i + 1, t, b, sz=15) for i, (t, b) in enumerate(steps))
    + textbox(ids, 0.55, 5.0, 12.2, 1.8, para('Today **each team builds one circuit together**. Then each member does **one measurement** alone for marks (see the last slides).', 17), **BOX))

ids = Ids()
s_dev = dk.new_slide(header(ids, 'Devices and components for this session') + textbox(ids, 0.6, 1.25, 7.6, 5.8,
    para('For each team:', 20)
    + para('PB-503A trainer: breadboard, ±6 V supplies, built-in 8 Ω speaker', 18, bullet='dot')
    + para('Oscilloscope, function generator, 1X BNC cable, 10X probes, multimeter', 18, bullet='dot')
    + para('LM358 op-amp, electret microphone with soldered leads', 18, bullet='dot')
    + para('Resistors: 10 kΩ ×5, 2.2 kΩ ×2, 4.7 kΩ, 47 kΩ', 18, bullet='dot')
    + para('Capacitors: 1 nF, 100 nF ×4, 1 µF, 10 µF, 470 µF ×4', 18, bullet='dot')
    + para('Return the op-amp, the microphone and the 470 µF capacitors to the tray at the end.', 16))
    + fit_pic(ids, '{img0}', IMG_MIC_LEADS, 8.5, 1.25, 4.3, 5.6), [IMG_MIC_LEADS])

dk.edit_text_ok = True
s55 = hn2(55)
dk.edit_text(s55, [('We will do a similar circuit in next lab session!!!', 'We build a similar circuit today.')])

ids = Ids()
s_micpb = dk.new_slide(header(ids, 'Electret test circuit on the PB-503A')
    + fit_pic(ids, '{img0}', IMG_MIC_TEST, 0.5, 1.15, 5.6, 6.1)
    + textbox(ids, 6.5, 1.3, 6.3, 5.6,
        para('Example of the electret test circuit built on the PB-503A breadboard.', 18)
        + para('Supply the bias resistor from the **+6 V** output of the trainer.', 18, bullet='dot')
        + para('Check the **polarity** of the electret: the pin connected to the metal case goes to ground.', 18, bullet='dot')
        + para('The microphone leads are short: they are soldered to wires so that it fits the breadboard. Handle it carefully.', 18, bullet='dot')), [IMG_MIC_TEST])

ids = Ids()
s_recap = dk.new_slide(header(ids, 'Recap – the inverting amplifier from Lab 3') + textbox(ids, 0.6, 1.3, 12.0, 5.6,
    para('Gain of an inverting amplifier: **Vout / Vin = − R_f / R_in** (180° phase shift).', 20, bullet='dot')
    + para('Supply the LM358 from the trainer: **+6 V → pin 8 (Vcc), −6 V → pin 4 (Vee)**, GND = 0 V.', 20, bullet='dot')
    + para('Decouple both supply rails: 470 µF (watch the polarity!) and 100 nF close to the op-amp.', 20, bullet='dot')
    + para('Today, stage 1: R_in = 2.2 kΩ, R_f = 30 kΩ (3 × 10 kΩ). Test it with the function generator: **10 mVpp, 1 kHz**.', 20, bullet='dot')
    + para('Build and test **step by step**: stage 1 → stage 2 → microphone → speaker.', 20, bullet='dot')))

ids = Ids()
s_photo = dk.new_slide(header(ids, 'Example – final circuit on the PB-503A')
    + fit_pic(ids, '{img0}', IMG_FINAL, 0.5, 1.15, 5.6, 6.1)
    + textbox(ids, 6.5, 1.3, 6.3, 5.6,
        para('Microphone, coupling capacitor and op-amp amplifier on one breadboard.', 18)
        + para('Keep the wires short and tidy: long loops pick up 50 Hz noise.', 18, bullet='dot')
        + para('Keep supply wires (red / black / blue) separate from the signal path.', 18, bullet='dot')
        + para('If something does not work: test each stage with the function generator and the oscilloscope.', 18, bullet='dot')), [IMG_FINAL])

# ---- Lab 4 marks ----
ids = Ids(); s_sec1 = hn_section(dk, 'Lab 4 – marks')
ids = Ids()
rows = [['Member (see your card)', 'Measurement (microphone and speaker disconnected; function generator High-Z, 10 mVpp sine at the stage-1 input)', 'Unit'],
        ['Member 1', 'Vpp at the output of stage 1, f = 1 kHz', 'mVpp'],
        ['Member 2', 'Vpp at the output of stage 2, f = 1 kHz', 'mVpp'],
        ['Member 3', 'Vpp at the output of stage 1, f = 5 kHz', 'mVpp'],
        ['Member 4 (team of 4)', 'Vpp at the output of stage 2, f = 5 kHz', 'mVpp']]
rows2 = [['Item', 'Marks'], ['Team demo: speak into the microphone, the lecturer hears you in the speaker', '4'],
         ['Your individual measurement (checked by the lecturer, submitted on the student page)', '6'], ['**Total**', '**10**']]
s_mk = dk.new_slide(header(ids, 'Lab 4 – what is marked')
    + table(ids, 0.55, 1.25, [2.6, 8.3, 1.3], rows, sz=15, row_h=0.5)
    + table(ids, 0.55, 4.3, [10.9, 1.3], rows2, sz=15, row_h=0.45)
    + textbox(ids, 0.55, 6.25, 12.2, 0.7, para('Submit your value and a photo of your circuit on the **student page** before the exam review.', 17)))

# ---- exam review ----
ids = Ids(); s_sec2 = hn_section(dk, 'Exam review')
ids = Ids()
rows = [['', 'Final exam'], ['Duration', '3 hours (about 90 minutes of work + setup, instructions and questions)'],
        ['Groups', 'Random groups of up to 3 students, drawn within your class on the exam day'],
        ['Marks', '- Group work: 35 points\n- Individual: 15 points (contribution + personal skills)'],
        ['Allowed', 'Lab instruments and components on your table. No help from other groups.'],
        ['Important', '- The instruments start in their default state. Set them up yourself.\n- A member who does nothing fails the exam.']]
s_fmt = dk.new_slide(header(ids, 'Final exam – format') + table(ids, 0.55, 1.3, [2.2, 10.0], rows, sz=17, row_h=0.8))

ids = Ids()
s_chk = dk.new_slide(header(ids, 'Skills checklist for the exam') + textbox(ids, 0.6, 1.2, 6.0, 5.9,
    para('**DC circuits**', 19)
    + para('Combine standard resistors to get a value close to a target', 16, bullet='dot')
    + para('Remeasure every component and redraw the schematic with the actual values', 16, bullet='dot')
    + para('Measure node voltages and branch currents', 16, bullet='dot')
    + para('Calculate them with Ohm’s law and Kirchhoff’s laws and compare', 16, bullet='dot'))
    + textbox(ids, 6.8, 1.2, 6.0, 5.9,
    para('**AC circuits**', 19)
    + para('Design RC low-pass / high-pass filters for a given fc; combine R and C', 16, bullet='dot')
    + para('Function generator: High-Z, amplitude, frequency, offset = 0', 16, bullet='dot')
    + para('Oscilloscope: 1X / 10X setting, display frequency and Vpp', 16, bullet='dot')
    + para('Measure Vout at several frequencies and record it in a table', 16, bullet='dot')
    + para('**Individually**: measure R, C, V, I; capture a signal; find and fix a fault; explain your circuit', 16, bullet='dot')))

ids = Ids()
s_load = dk.new_slide(header(ids, 'Connecting two stages – loading')
    + fit_pic(ids, '{img0}', f'{FIG}/d4_loading.png', 0.5, 1.4, 5.8, 3.4)
    + textbox(ids, 6.6, 1.3, 6.2, 5.6,
        para('When you connect a second stage, it **takes current** from the first stage. We call it a **load**.', 18)
        + para('No load: Vout = Vin × R2 / (R1 + R2)', 17, bullet='dot')
        + para('With load: R2 becomes R2 ∥ R_load, so Vout goes down', 17, bullet='dot')
        + para('Filters too: the second filter changes the cut-off frequency of the first one.', 17, bullet='dot')
        + para('Simple rule: the next stage should be **10 times bigger** (in Ω) than the stage before.', 17, bullet='dot')), [f'{FIG}/d4_loading.png'])

ids = Ids()
s_fix = dk.new_slide(header(ids, 'Practice – break & fix') + textbox(ids, 0.6, 1.3, 12.0, 5.6,
    para('In your team, take turns (about 10 minutes each):', 20)
    + para('One member builds a small circuit from Lab 1 or Lab 2 and **secretly** introduces one fault: a wire in the wrong row, a missing connection, a wrong resistor, the oscilloscope on the wrong attenuation, the function generator on 50 Ω…', 18, bullet='num')
    + para('Another member finds the fault using only the instruments: continuity test, voltage measurements, the oscilloscope.', 18, bullet='num')
    + para('The third member explains to the others how the circuit should work and what each measurement shows.', 18, bullet='num')
    + para('Before you leave: switch off all instruments, return the op-amp, the microphone and the 470 µF capacitors to the tray, clear your breadboard.', 18)))

IMP2 = {n: hn2(n) for n in list(range(51, 55)) + list(range(59, 75))}
add_callout(dk, IMP2[52], 'Coupling capacitor', 'passes AC, blocks DC')
add_callout(dk, IMP2[62], 'Speaker', 'turns an AC voltage into sound', pos='L')
add_callout(dk, F(9), 'Electret microphone', 'a small mic: sound → small voltage', pos='L')
add_callout(dk, F(16), 'Bias', 'the DC voltage a part needs to work', pos='N')
add_callout(dk, F(66), 'Stage', 'one part of a chain of circuits', pos='L')
add_callout(dk, F(71), 'Load', 'what is connected to an output and takes current', pos='L')
add_callout(dk, F(78), 'Acoustic feedback', 'speaker sound goes back into the mic → echo')
add_callout(dk, s_fix, 'Troubleshoot', 'find and fix a fault')
order = ([F(1), *review_slides(dk, 3), s_ov, s_dev, F(4)] + [IMP2[n] for n in (51, 52, 53, 54)] + [s55] + [IMP2[n] for n in range(59, 75)]
         + [F(n) for n in range(5, 17)] + [s_micpb] + [F(n) for n in range(17, 32)]
         + [s_recap] + [F(n) for n in range(66, 92)] + [s_photo]
         + [s_sec1, s_mk, s_sec2, *review_slides(dk, 4), s_fmt, s_chk, s_load, s_fix])
# HN schematics show a 12 V source + 2 × 1 MΩ to make ±6 V; HCM uses the PB-503A ± outputs, so that block is removed
import glob, hashlib
_md5 = lambda f: hashlib.md5(open(f, 'rb').read()).hexdigest()
NODIV = {'af236e23c930d333662a5fd0c3ceb5aa': 'hn_s3_twostage_nodiv.png', '4c024dab9611ed8bb2896cc246f5e4e4': 'hn_s3_final1_nodiv.png', '314078be32624326a40df4d59c436ed4': 'hn_s3_final2_nodiv.png'}   # painted by fix_divider.py
for f in glob.glob(f'{dk.d}/ppt/media/*.png'):
    if _md5(f) in NODIV:
        shutil.copy(f'{FIG}/{NODIV[_md5(f)]}', f)
from fix_divider import drop_rail_labels
for r in glob.glob(f'{dk.d}/ppt/slides/_rels/*.rels'):
    if any(os.path.exists(f'{dk.d}/ppt/media/{m}') and NODIV.get(_md5(f'{dk.d}/ppt/media/{m}')) == 'hn_s3_final1_nodiv.png'
           for m in __import__('re').findall(r'media/([^"]+)', open(r).read())):
        x = f'{dk.d}/ppt/slides/' + os.path.basename(r)[:-5]
        open(x, 'w', encoding='utf8').write(drop_rail_labels(open(x, encoding='utf8').read()))
dk.finalize(order, None)
