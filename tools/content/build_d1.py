import os, sys, shutil, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from deck import *

S = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/_build'
HN = '/Users/mac/Tra/SE9_ElecCircuitLab/HN'
HCM = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM'
PHOTO_TRAINER = f'{HCM}/figures/1792490310076_265884367885448100_7083566079884472153_ee80017b4e892eea8afad622fde52bad.jpg'
FIG = f'{S}/../fig'

dk = Deck(f'{HN}/Electronic Circuit Lab Slide 1.pptx', f'{S}/build_d1')
src2 = f'{S}/u2'
o2 = slide_order(src2)
F = lambda n: tone(dk, dk.slide_file(n), 1, n)


def hn2(n):
    return tone(dk, dk.import_slide(src2, o2[n - 1], 'l2_'), 2, n)


# ---- title ----
dk.edit_text(F(1), [('4 hours', '3 hours'), ('DC circuits', 'Lab instruments & DC circuits')])

# ---- notes for class of 2026 ----
add_line_after(dk, F(1), '3 hours', 'Lecturer: TraNLT2@fe.edu.vn'); widen_shape(dk, F(1), '3 hours', 6.0)
ids = Ids()
s_notes = dk.new_slide(header(ids, 'Notes for the class of 2026') + textbox(ids, 0.6, 1.3, 7.2, 5.6,
    para('You have already taken **Electronic Lab 1**. This course is partly the same, mostly different:', 20)
    + para('Revise the basic instruments and circuits (most of Lab 1)', 20, bullet='dot')
    + para('Strengthen your circuit theory with real measurements', 20, bullet='dot')
    + para('Build modified versions of familiar circuits', 20, bullet='dot')
    + para('Build new circuits: RLC filters, op-amp amplifiers, a microphone-to-speaker circuit', 20, bullet='dot')
    + para('Go quickly through what you remember, and spend your time on the exercises.', 20))
    + fit_pic(ids, '{img0}', PHOTO_TRAINER, 8.2, 1.3, 4.6, 5.6), [PHOTO_TRAINER])

# ---- course summary (HCM: 4 x 3 h + exam) ----
ids = Ids()
rows = [['Session', 'Hours', 'Content'],
        ['**Lab 1** – Lab instruments & DC circuits', '3', 'Lab rules, multimeter, DC power supply, breadboard; oscilloscope and function generator basics; voltage & current dividers; equivalent resistance exercise'],
        ['**Lab 2** – RC and RLC circuits', '3', 'Measuring capacitance; 1st-order RC low-pass / high-pass filters; combining capacitors; series RLC low-pass, high-pass and band-pass filters (f0 ≈ 32 kHz); frequency response'],
        ['**Lab 3** – Operational amplifiers', '3', 'Op-amp basics, LM358 datasheet, dual (±) supply, decoupling capacitors; inverting amplifier: gain and 180° phase shift'],
        ['**Lab 4** – Microphone to speaker', '3', 'Speaker and coupling capacitors; electret microphone; two-stage op-amp amplifier; final circuit; exam review'],
        ['**Final exam**', '3', 'Practical exam in random groups (within your class)']]
s_sum = dk.new_slide(header(ids, 'Course Summary') + table(ids, 0.55, 1.25, [3.4, 0.9, 7.9], rows, sz=15, row_h=0.9))

# ---- assessment ----
ids = Ids()
rows = [['Component', 'Weight', 'Details'],
        ['**Lab assessment**', '50%', '- Lab 1: 12 pts, Lab 2: 14 pts, Lab 3: 14 pts, Lab 4: 10 pts (total 50 pts)\n- Absent from a lab → 0 pts for that lab'],
        ['**Final exam**', '50%', '- Practical exam, 3 hours\n- Random groups of up to 3 students, from your own class\n- Group marks + individual marks (each member measures and explains)'],
        ['**Total**', '100%', '']]
s_ass = dk.new_slide(header(ids, 'Assessment') + table(ids, 0.55, 1.4, [2.8, 1.2, 8.2], rows, sz=16, row_h=1.0)
    + textbox(ids, 0.55, 5.6, 12.2, 1.2, para('Teams: make a team of **3 students** today. You keep the same team and the same table for Lab 1 to Lab 4. Each student still has **their own** exercise.', 18)))

# ---- how each lab session is marked ----
ids = Ids()
w, g, x0, y0 = 2.85, 0.3, 0.55, 1.25
steps = [('Get your variant', ['Your card with your **variant number** is on the student page. Work on your own variant only.']),
         ('Build & measure', ['Build the circuit on your card. Measure and write down your values.']),
         ('Call the lecturer', ['The lecturer checks **one reading** on your instrument and ticks your name.']),
         ('Submit your values', ['On the student page, enter your values and add 1–3 **photos of your circuit** before you leave.'])]
body = ''.join(card(ids, x0 + i * (w + g), y0, w, 2.9, i + 1, t, b, sz=15) for i, (t, b) in enumerate(steps))
rows = [['Your value vs. the answer key of your variant', 'Marks for that value'],
        ['Error ≤ 10%', 'Full marks'], ['10% < error ≤ 20%', 'Half marks'], ['Error > 20%, or no lecturer tick', '0']]
s_rule = dk.new_slide(header(ids, 'How each lab session is marked') + body
    + table(ids, 0.55, 4.5, [6.2, 3.4], rows, sz=16, row_h=0.45)
    + textbox(ids, 10.35, 4.5, 2.5, 1.8, para('Type **numbers only**, in the unit asked. Example: 1.27 for 1.27 mA.', 15), fill='F3F7F0', line='B7CFA8', geom='roundRect', inset=0.12))

# ---- make teams (10 minutes) ----
ids = Ids()
w, g = 2.85, 0.3
steps = [('Teams are ready', ['**3 students** per team (one team of 4 if needed).', 'Made at random by the system, in your class.']),
         ('Sign in', ['Scan the QR. Type your student ID, check your name.', 'First time: create a password and remember it.']),
         ('Find your team', ['The student page shows your team, member and variant.', 'Team number = table number.']),
         ('Check your table', ['Trainer, multimeter, oscilloscope, function generator.', 'Tell me if something is missing.'])]
s_team = dk.new_slide(header(ids, 'Your team and the student page (10 minutes)')
    + ''.join(card(ids, 0.55 + i * (w + g), 1.3, w, 3.1, i + 1, t, b, sz=15) for i, (t, b) in enumerate(steps))
    + textbox(ids, 0.55, 4.8, 12.2, 2.0,
        para('Your team stays the same for **Lab 1 to Lab 4**. You use the same table every time.', 17, bullet='dot')
        + para('Your member number (1, 2, 3, or 4 in a team of 4) is used for your variant card in every lab.', 17, bullet='dot')
        + para('The final exam groups are different: they are drawn at random on the exam day.', 17, bullet='dot'), fill='F3F7F0', line='B7CFA8', geom='roundRect', inset=0.12))

# ---- devices for this session ----
ids = Ids()
s_dev = dk.new_slide(header(ids, 'Devices and components for this session') + textbox(ids, 0.6, 1.2, 12.1, 5.9,
    para('For each team:', 20)
    + para('1 Global Specialties PB-503A trainer (breadboard, built-in DC supplies, speaker)', 18, bullet='dot')
    + para('1 DC power supply', 18, bullet='dot')
    + para('1 digital multimeter & probes', 18, bullet='dot')
    + para('1 oscilloscope, 1 function generator, 1X BNC cable, 10X probe', 18, bullet='dot')
    + para('Male-to-male jumper wires, 1 LED', 18, bullet='dot')
    + para('For each student:', 20)
    + para('Resistors for your variant (listed on your card)', 18, bullet='dot')
    + para('2.2 kΩ and 4.7 kΩ for the divider circuits', 18, bullet='dot')
    + para('Reusable parts (LED…) go back to the tray at the end of the session.', 16))
    )

# ---- PB-503A built-in supplies ----
ids = Ids()
s_pb = dk.new_slide(header(ids, 'PB-503A trainer – built-in DC supplies') + textbox(ids, 0.6, 1.3, 12.1, 5.6,
    para('The trainer has fixed and adjustable DC outputs, both **positive (+)** and **negative (−)**.', 20)
    + para('**GND / COM** is the 0 V reference of your circuit.', 20, bullet='dot')
    + para('Always **measure an output with the multimeter** before connecting it to your circuit.', 20, bullet='dot')
    + para('Turn the trainer off while you change the wiring.', 20, bullet='dot')
    + para('In Labs 3 and 4 we use the + and − outputs to supply the op-amp (±6 V).', 20, bullet='dot'))
    )

# ---- exercise ----
ids = Ids()
s_sec = hn_section(dk, 'Lab 1 exercise', 'Equivalent resistance')

ids = Ids()
fig = f'{FIG}/d1_circuit.png'
s_ex = dk.new_slide(header(ids, 'Lab 1 exercise – Equivalent resistance')
    + fit_pic(ids, '{img0}', fig, 0.4, 1.2, 5.6, 4.4)
    + textbox(ids, 0.4, 5.75, 5.6, 1.3, para('R_A, R_B, R_C, R_D on your card are **not standard values**. You cannot buy them. You must make each one from 2 standard resistors.', 15), fill='F3F7F0', line='B7CFA8', geom='roundRect', inset=0.12)
    + textbox(ids, 6.3, 1.15, 6.6, 6.1,
        para('Find 2 **standard resistors** for each of R_A, R_B, R_C, R_D (series or parallel). Example: 5.7 kΩ = 1 kΩ + 4.7 kΩ. Measure each one.', 17, bullet='num')
        + para('Build the circuit. **Do not connect the supply yet.** Measure **R_eq** between the two supply points.', 17, bullet='num')
        + para('Set the supply to **5.00 V**. Check it with the multimeter. Then connect it.', 17, bullet='num')
        + para('Measure: total current **I**, current **I_A** in R_A, voltage **V_X** (X to 0 V).', 17, bullet='num')
        + para('Call the lecturer. Then submit your numbers and a photo of your circuit on the student page.', 17, bullet='num')), [fig])

ids = Ids()
rows = [['Value to submit (student page)', 'Unit', 'Marks'],
        ['R_eq – total resistance, supply disconnected', 'Ω', '3'],
        ['I – total current from the supply', 'mA', '3'],
        ['I_A – current through R_A', 'mA', '3'],
        ['V_X – voltage at node X', 'V', '3'],
        ['**Total**', '', '**12**']]
s_sub = dk.new_slide(header(ids, 'Lab 1 – What to submit') + table(ids, 0.55, 1.3, [6.6, 1.3, 1.3], rows, sz=16, row_h=0.55)
    + textbox(ids, 10.0, 1.3, 2.8, 3.85,
        para('**Remember**', 16) + para('Use **measured** values, not calculated ones.', 15, bullet='dot')
        + para('Enter numbers only, in the unit shown.', 15, bullet='dot')
        + para('No lecturer tick → 0 for the measured values.', 15, bullet='dot')
        + para('Add 1–3 photos of your real circuit.', 15, bullet='dot'), fill='F3F7F0', line='B7CFA8', geom='roundRect', inset=0.12)
    + textbox(ids, 0.55, 5.6, 12.3, 1.3, para('Before you leave: (1) submit your values on the **student page**, (2) switch off all instruments, (3) put parts back in the tray, (4) clear your breadboard.', 18)))

IMP2 = {n: hn2(n) for n in range(4, 33)}
add_callout(dk, F(10), 'Multimeter (DMM)', 'one meter for V, I and R')
add_callout(dk, F(11), 'Probe', 'the wire and metal tip that touch the circuit', pos='P')
add_callout(dk, F(22), 'Current limit', 'the highest current the supply will give', pos='L')
add_callout(dk, F(25), 'Breadboard', 'a board to build circuits without soldering', pos='L')
add_callout(dk, F(35), 'Node', 'a point where two or more parts connect')
add_callout(dk, F(39), 'Series', 'one after another → same current', pos='L')
add_callout(dk, F(43), 'Parallel', 'side by side → same voltage', pos='L')
add_callout(dk, F(53), 'Equivalent resistance', 'one resistor that can replace a group', pos='L')
add_callout(dk, IMP2[5], 'Oscilloscope', 'shows a voltage as a wave', pos='L')
add_callout(dk, IMP2[19], 'Function generator', 'makes AC signals (sine, square…)')
add_callout(dk, IMP2[13], 'Peak-to-peak (Vpp)', 'from the lowest to the highest point of a wave', pos='L')
order = ([F(1), F(3), s_sum, s_ass, s_rule, s_team, F(6), F(7), s_dev]
         + [F(n) for n in range(9, 24)] + [s_pb]
         + [F(n) for n in range(24, 38)]
         + [IMP2[n] for n in range(4, 33)]
         + [F(n) for n in range(38, 47)]
         + [F(n) for n in range(52, 58)]
         + [s_sec, s_ex, s_sub])
dk.finalize(order, None)
