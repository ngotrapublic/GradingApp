import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from deck import *

S = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/_build'
HN = '/Users/mac/Tra/SE9_ElecCircuitLab/HN'
FIG = f'{S}/../fig'
BOX = dict(fill='F3F7F0', line='B7CFA8', geom='roundRect', inset=0.12)

dk = Deck(f'{HN}/Electronic Circuit Lab Slide 2.pptx', f'{S}/build_d2')
F = lambda n: tone(dk, dk.slide_file(n), 2, n)

dk.edit_text(F(1), [('AC equipment, capacitor and inductor circuits', 'RC and RLC circuits'), ('4 hours', '3 hours')])
for n in (91, 92):
    dk.edit_text(F(n), [('Because LOOK!!!', 'Where are RLC circuits used?')])
dk.edit_text(F(92), [('And more…………..', 'And many more')])

# ---- overview ----
add_line_after(dk, F(1), '3 hours', 'Lecturer: TraNLT2@fe.edu.vn'); widen_shape(dk, F(1), '3 hours', 6.0)
ids = Ids()
w, g = 2.85, 0.3
steps = [('RC filters', ['1st-order low-pass and high-pass', 'Cut-off frequency fc', 'Warm-up exercise']),
         ('Capacitors', ['Combining capacitors', 'Measuring capacitance with the multimeter']),
         ('Series RLC', ['Resonance f0 and quality factor Q', 'One circuit, three filters']),
         ('Lab 2 exercise', ['Design for your Q', 'Measure the frequency response', 'Plot and conclude'])]
s_ov = dk.new_slide(header(ids, 'Lab 2 overview')
    + ''.join(card(ids, 0.55 + i * (w + g), 1.3, w, 3.3, i + 1, t, b, sz=15) for i, (t, b) in enumerate(steps))
    + textbox(ids, 0.55, 5.0, 12.2, 1.8, para('Reminder: at the start, the instruments are in their **default state**. Before you measure: (1) check 1X / 10X on the oscilloscope, (2) set the function generator to **High-Z**.', 17), **BOX))

# ---- devices ----
ids = Ids()
s_dev = dk.new_slide(header(ids, 'Devices and components for this session') + textbox(ids, 0.6, 1.25, 12.0, 5.8,
    para('For each team:', 20)
    + para('Oscilloscope, function generator, 1X BNC cable, two 10X probes', 18, bullet='dot')
    + para('Digital multimeter, PB-503A trainer (breadboard), jumper wires', 18, bullet='dot')
    + para('For each student:', 20)
    + para('RC warm-up: 1 resistor + 1 capacitor (on your variant card)', 18, bullet='dot')
    + para('RLC: 1 inductor 1 mH, capacitors 22 nF and 2.2 nF', 18, bullet='dot')
    + para('Resistors 47 Ω ×2, 100 Ω ×2, 220 Ω ×1 to build your R', 18, bullet='dot')
    + para('Excel file “Lab2_RLC_data_template.xlsx” (download it from the student page) on your laptop', 18, bullet='dot')))

# ---- RC warm-up exercise ----
ids = Ids()
s_rcx = dk.new_slide(header(ids, 'Warm-up exercise – RC cut-off frequency')
    + fit_pic(ids, '{img0}', f'{FIG}/d2_rc_lp.png', 0.5, 1.3, 3.0, 2.2) + fit_pic(ids, '{img1}', f'{FIG}/d2_rc_hp.png', 0.5, 3.9, 3.0, 2.2)
    + textbox(ids, 0.5, 3.45, 3.0, 0.4, para('Low-pass', 14, align='ctr')) + textbox(ids, 0.5, 6.1, 3.0, 0.4, para('High-pass', 14, align='ctr'))
    + textbox(ids, 3.9, 1.2, 9.0, 5.9,
        para('Your variant card gives the filter type (low-pass or high-pass), **R** and **C**.', 17)
        + para('Measure R and C with the multimeter.', 17, bullet='num')
        + para('Calculate the cut-off frequency fc.', 17, bullet='num')
        + para('Build the filter. Function generator: sine, **2 Vpp**, High-Z. CH1 = Vin, CH2 = Vout.', 17, bullet='num')
        + para('Change the frequency until **Vout = 0.707 × Vin**. This frequency is your measured fc.', 17, bullet='num')
        + para('Compare it with your calculation. Write it down in **kHz** for the student page.', 17, bullet='num')),
    [f'{FIG}/d2_rc_lp.png', f'{FIG}/d2_rc_hp.png'])

# ---- measuring capacitance ----
ids = Ids()
s_cap = dk.new_slide(header(ids, 'Measuring capacitance with the multimeter') + textbox(ids, 0.6, 1.3, 12.0, 5.6,
    para('Most multimeters have a capacitance mode (symbol **–|(–**, unit nF / µF).', 20)
    + para('Take the capacitor **out of the circuit** and make sure it is discharged.', 20, bullet='num')
    + para('Select the capacitance mode. Connect the probes to the two leads (red probe to + for polarised capacitors).', 20, bullet='num')
    + para('Wait until the reading is stable – large capacitors take a few seconds.', 20, bullet='num')
    + para('Small values (pF range) are affected by the probe leads: subtract the reading with the probes open.', 20, bullet='num')
    + para('Ceramic and film capacitors are often 5–20% away from the printed value. **Always remeasure**, as you do for resistors.', 20)))

# ---- RLC: one circuit, three filters ----
ids = Ids()
s_3f = dk.new_slide(header(ids, 'Series RLC – one circuit, three filters')
    + fit_pic(ids, '{img0}', f'{FIG}/d2_lp.png', 0.3, 1.2, 4.2, 2.4)
    + fit_pic(ids, '{img1}', f'{FIG}/d2_hp.png', 4.55, 1.2, 4.2, 2.4)
    + fit_pic(ids, '{img2}', f'{FIG}/d2_bp.png', 8.8, 1.2, 4.2, 2.4)
    + textbox(ids, 0.6, 4.0, 12.1, 3.0,
        para('L = 1 mH, C = 22 nF ∥ 2.2 nF. The same series current flows through R, L and C. **Where you take the output decides the filter:**', 18)
        + para('Across **C** → low-pass: at high frequency C is almost a short circuit.', 18, bullet='dot')
        + para('Across **L** → high-pass: at low frequency L is almost a short circuit.', 18, bullet='dot')
        + para('Across **R** → band-pass: maximum current at resonance f0.', 18, bullet='dot')
        + para('Put the output component at the **ground side**, so both probe grounds are on the same node.', 18, bullet='dot')),
    [f'{FIG}/d2_lp.png', f'{FIG}/d2_hp.png', f'{FIG}/d2_bp.png'])

# ---- key formulas ----
ids = Ids()
rows = [['Quantity', 'Formula', 'Our circuit (L = 1 mH, C = 24.2 nF)'],
        ['Resonant frequency', 'f0 = 1 / (2π√(LC))', 'f0 ≈ 32.35 kHz'],
        ['Characteristic resistance', 'Z0 = √(L / C)', 'Z0 ≈ 203 Ω'],
        ['Quality factor', 'Q = Z0 / R_total,   R_total = R + R_L', 'R_total = 203 Ω / Q'],
        ['Band-pass bandwidth', 'BW = f_H − f_L = f0 / Q', 'Vout/Vin = 0.707 × maximum at f_L and f_H'],
        ['Low-pass: peak', 'f_max = f0 × √(1 − 1/(2Q²))', 'peak Vout/Vin = Q / √(1 − 1/(4Q²))'],
        ['High-pass: peak', 'f_max = f0 / √(1 − 1/(2Q²))', 'peak Vout/Vin = Q / √(1 − 1/(4Q²))']]
s_fx = dk.new_slide(header(ids, 'Series RLC – key formulas') + table(ids, 0.55, 1.3, [3.3, 4.6, 4.3], rows, sz=16, row_h=0.62)
    + textbox(ids, 0.55, 5.85, 12.2, 1.0, para('R_L is the **resistance of the inductor wire** (a few tens of ohms). With a small Z0 it matters: always measure it.', 17), **BOX))

# ---- real components ----
ids = Ids()
s_real = dk.new_slide(header(ids, 'Real components at 32 kHz') + textbox(ids, 0.6, 1.3, 12.0, 5.6,
    para('**The inductor wire has resistance (R_L).** Measure it with the ohmmeter. Add it to R.', 19, bullet='dot')
    + para('**The function generator has 50 Ω inside.** Near f0 the circuit takes more current, so Vin goes down. So:', 19, bullet='dot')
    + para('Measure **Vin (CH1) at every frequency**, not only once.', 18, level=1, bullet='dot')
    + para('Always use the ratio **Vout / Vin**.', 18, level=1, bullet='dot')
    + para('**Probes:** use 10X probes on both channels and set 10X on the oscilloscope. Both ground clips go to circuit ground.', 19, bullet='dot')
    + para('**Parts are not exact:** L is ±10%, C is ±5%. Your f0 can be a few % away from 32.35 kHz.', 19, bullet='dot')))

# ---- exercise ----
ids = Ids(); s_sec = hn_section(dk, 'Lab 2 exercise', 'Series RLC filter')
ids = Ids()
s_ex = dk.new_slide(header(ids, 'Lab 2 exercise – design and build') + textbox(ids, 0.6, 1.2, 7.4, 5.9,
    para('Your variant card gives the **filter type** (low-pass, high-pass or band-pass) and the **quality factor Q**. L = 1 mH, C = 22 nF ∥ 2.2 nF.', 17)
    + para('Measure R_L of your inductor. Calculate R_total = Z0 / Q. Then R = R_total − R_L.', 17, bullet='num')
    + para('Make R from 47 Ω, 100 Ω and 220 Ω resistors (series or parallel).', 17, bullet='num')
    + para('Measure **R and the inductor together** with the ohmmeter. This is your R_total.', 17, bullet='num')
    + para('Build your filter. Put the output part at the ground side.', 17, bullet='num')
    + para('Function generator: sine, 2 Vpp, High-Z. CH1 = Vin, CH2 = Vout.', 17, bullet='num'))
    + textbox(ids, 8.3, 1.2, 4.5, 3.3, para('**Your card shows**', 17) + para('Variant number', 16, bullet='dot') + para('Filter type', 16, bullet='dot')
        + para('Q', 16, bullet='dot') + para('RC warm-up: type, R, C', 16, bullet='dot') + para('Frequency list for the measurement', 16, bullet='dot'), **BOX))

ids = Ids()
s_ms = dk.new_slide(header(ids, 'Lab 2 exercise – measure and plot') + textbox(ids, 0.6, 1.2, 12.1, 5.9,
    para('Download **Lab2_RLC_data_template.xlsx** from the student page (under your Lab 2 card) and open it. For each frequency on your card, measure Vin (CH1) and Vout (CH2), peak-to-peak. Type them in. The graph draws itself.', 17, bullet='num')
    + para('Find the highest Vout / Vin. Add more points near the peak. Write down **f_max** (kHz).', 17, bullet='num')
    + para('**Low-pass or high-pass:** write down the **highest Vout / Vin**.', 17, bullet='num')
    + para('**Band-pass:** find f_L and f_H where Vout/Vin = 0.707 × highest value. **BW = f_H − f_L** (kHz).', 17, bullet='num')
    + para('Write 1–3 sentences: compare your results with the theory. Why are they different?', 17, bullet='num')
    + para('Call the lecturer. Show one reading on the oscilloscope **and** your graph. Add a photo of your circuit on the student page.', 17, bullet='num')))

ids = Ids()
rows = [['Value to submit (student page)', 'Unit', 'Marks'],
        ['Warm-up: measured cut-off frequency fc', 'kHz', '2'],
        ['Measured R_total (R + inductor, DC)', 'Ω', '3'],
        ['Frequency of maximum output f_max', 'kHz', '3'],
        ['- Low-pass / high-pass: highest Vout/Vin\n- Band-pass: bandwidth BW', '–\nkHz', '3'],
        ['Graph + conclusion (checked by the lecturer at your bench)', '–', '3'],
        ['**Total**', '', '**14**']]
s_sub = dk.new_slide(header(ids, 'Lab 2 – What to submit') + table(ids, 0.55, 1.3, [8.0, 1.3, 1.1], rows, sz=16, row_h=0.55)
    + textbox(ids, 0.55, 5.9, 12.2, 1.0, para('Before you leave: submit your values on the **student page**, switch off all instruments and clear your breadboard.', 18)))

add_callout(dk, F(42), 'Low-pass / high-pass', 'passes low / passes high frequencies', pos='TR')
add_callout(dk, F(44), 'Filter', 'passes some frequencies, blocks others')
add_callout(dk, F(46), 'Cut-off frequency (fc)', 'where Vout = 0.707 × Vin', pos='L')
add_callout(dk, F(49), 'Capacitor', 'stores charge; unit farad (F)')
add_callout(dk, F(76), 'Inductor', 'a coil of wire; unit henry (H)', pos='L')
add_callout(dk, F(81), 'Resonance (f0)', 'where the effects of L and C cancel')
add_callout(dk, F(82), 'Q and BW', 'Q = how sharp the peak is; BW = width of the passed band', pos='T')
add_callout(dk, s_cap, 'Tolerance', 'how far a real part is from its printed value')
order = ([F(1), *review_slides(dk, 1), s_ov, s_dev] + [F(n) for n in range(33, 48)] + [s_rcx]
         + [F(n) for n in (48, 49, 50, 56, 57, 58)] + [s_cap]
         + [F(n) for n in range(75, 83)] + [s_3f, s_fx, s_real, F(91), F(92), s_sec, s_ex, s_ms, s_sub])
dk.finalize(order, None)
