import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from deck import *

S = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/_build'
HN = '/Users/mac/Tra/SE9_ElecCircuitLab/HN'
HCM = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM'
BOX = dict(fill='F3F7F0', line='B7CFA8', geom='roundRect', inset=0.12)
IMG_SCOPE = f'{HCM}/figures/1792490311209_265884367885448100_7083566079884472153_508a850dc63e2c32b94884862b53863f.jpg'

dk = Deck(f'{HN}/Electronic Circuit Lab Slide 3.pptx', f'{S}/build_d3')
F = lambda n: tone(dk, dk.slide_file(n), 3, n)

dk.edit_text(F(1), [('Working with integrated circuit', 'Operational amplifiers'), ('Microphone to Speaker', 'The inverting amplifier'), ('4 hours', '3 hours')])
dk.edit_text(F(33), [('There’s much more to learn', 'There is much more to learn about op-amps'),
                     ('But I only gives you enough overview so you can carry out this lab', 'This lab gives you the overview you need for the experiments')])
dk.edit_text(F(50), [('We will now construct a separate amplifier circuit using 2 op-amps', 'We will now construct an inverting amplifier with one op-amp'),
                     ('We will test it using function generator before connecting it to the electret circuit', 'We test it with the function generator. In Lab 4 we connect it to a microphone'),
                     ('There’s no short path for you in science', 'Build, test, then move to the next step')])
dk.edit_text(F(59), [('Set 12V at DC power supply', 'Set the PB-503A to ±6 V')])
dk.edit_text(F(62), [('We filter this at the DC power supply of the circuit', 'Noise on the supply rails reaches the output. We filter it at the DC supply of the circuit')])

add_line_after(dk, F(1), '3 hours', 'Lecturer: TraNLT2@fe.edu.vn'); widen_shape(dk, F(1), '3 hours', 6.0)
ids = Ids()
w, g = 2.85, 0.3
steps = [('Op-amp basics', ['Differential input, open-loop gain', 'Inverting amplifier']),
         ('LM358 in practice', ['Datasheet: pins and ratings', '±6 V supply, decoupling']),
         ('Gain and phase', ['Measure Vout/Vin', 'Measure the 180° phase shift']),
         ('Lab 3 exercise', ['Find R1 and R2 from an oscilloscope screen', 'Rebuild it'])]
s_ov = dk.new_slide(header(ids, 'Lab 3 overview')
    + ''.join(card(ids, 0.55 + i * (w + g), 1.3, w, 3.3, i + 1, t, b, sz=15) for i, (t, b) in enumerate(steps))
    + textbox(ids, 0.55, 5.0, 12.2, 1.8, para('You will study op-amps in detail later. Today you learn **just enough to build and measure** an inverting amplifier. Each student builds their own amplifier.', 17), **BOX))

ids = Ids()
s_dev = dk.new_slide(header(ids, 'Devices and components for this session') + textbox(ids, 0.6, 1.25, 12.0, 5.8,
    para('For each team:', 20)
    + para('PB-503A trainer (breadboard and ±6 V supplies), oscilloscope, function generator, 1X BNC cable, 10X probes, multimeter', 18, bullet='dot')
    + para('470 µF capacitors ×2 for the supply rails (return them at the end)', 18, bullet='dot')
    + para('For each student:', 20)
    + para('1 LM358 op-amp (return it at the end – we use it again in Lab 4)', 18, bullet='dot')
    + para('100 nF capacitors ×2 (decoupling at the op-amp pins)', 18, bullet='dot')
    + para('Resistors for your amplifier: take them from the team tray once you know R1 and R2', 18, bullet='dot')))

ids = Ids()
s_pm = dk.new_slide(header(ids, 'Supplying the op-amp from the PB-503A') + textbox(ids, 0.6, 1.3, 12.0, 5.6,
    para('The LM358 needs a **positive and a negative** supply so that the output can swing above and below 0 V.', 20)
    + para('Set the adjustable outputs of the trainer to **+6 V** and **−6 V**. Check both with the multimeter.', 19, bullet='num')
    + para('Connect the trainer **GND** to the ground rail of your breadboard: this is the 0 V of the circuit, of the function generator and of the oscilloscope.', 19, bullet='num')
    + para('+6 V → pin 8 (Vcc). −6 V → pin 4 (Vee). Never swap them: the IC can be destroyed.', 19, bullet='num')
    + para('Switch the trainer off while you wire. Switch on, then check the supply at pins 8 and 4.', 19, bullet='num')))

ids = Ids()
s_gp = dk.new_slide(header(ids, 'Measuring gain and phase')
    + fit_pic(ids, '{img0}', IMG_SCOPE, 0.4, 1.15, 6.4, 4.8)
    + textbox(ids, 0.4, 6.0, 6.4, 1.0, para('CH2 (blue) = input, CH1 (yellow) = output of an inverting amplifier', 14, align='ctr'))
    + textbox(ids, 7.0, 1.2, 5.9, 5.9,
        para('**Gain**', 19) + para('Display Pk-Pk of both channels: |gain| = Vout,pp / Vin,pp', 17, bullet='dot')
        + para('Here: 9.52 V / 0.262 V ≈ 36', 17, bullet='dot')
        + para('**Phase**', 19) + para('The output is upside down: a maximum of the input meets a minimum of the output → **180°** shift', 17, bullet='dot')
        + para('To measure it: use the cursors to read the time shift Δt between the two waveforms, then phase = 360° × Δt × f', 17, bullet='dot')), [IMG_SCOPE])

ids = Ids()
s_lim = dk.new_slide(header(ids, 'LM358 limits you will meet') + textbox(ids, 0.6, 1.3, 12.0, 5.6,
    para('**Output swing.** With ±6 V the output cannot reach the supply rails – roughly −5 V to +4.5 V. If Vout,pp is too large, the tops of the sine wave are flattened (clipping).', 19, bullet='dot')
    + para('→ Choose the input amplitude so that Vout,pp stays below about 8 V.', 18, level=1, bullet='dot')
    + para('**Bandwidth.** Gain × bandwidth ≈ 1 MHz. With a gain of 40 the amplifier works only up to about 25 kHz.', 19, bullet='dot')
    + para('→ Use audio frequencies (100 Hz – 2 kHz) for today’s measurements.', 18, level=1, bullet='dot')
    + para('**Noise.** Small input signals (mV) are easily covered by noise: short wires, decoupling capacitors, good grounding.', 19, bullet='dot')))

ids = Ids()
s_dec = dk.new_slide(header(ids, 'Decoupling the supply rails')
    + fit_pic(ids, '{img0}', f'{S}/../fig/d3_decouple.png', 0.5, 1.3, 6.2, 4.6)
    + textbox(ids, 7.0, 1.3, 5.8, 5.6,
        para('Noise on the supply rails reaches the output of the amplifier. Capacitors to GND short the AC noise and keep the DC.', 18)
        + para('**470 µF** on each rail: removes low-frequency noise (50 Hz).', 17, bullet='dot')
        + para('**100 nF** right next to pins 8 and 4: removes high-frequency noise.', 17, bullet='dot')
        + para('Electrolytic capacitors are polarised: **+ lead to the more positive side**. On the −6 V rail the + lead goes to GND.', 17, bullet='dot')
        + para('A reversed electrolytic capacitor can burst.', 17, bullet='dot')), [f'{S}/../fig/d3_decouple.png'])

ids = Ids(); s_sec = hn_section(dk, 'Lab 3 exercise', 'From an oscilloscope screen back to the circuit')
ids = Ids()
s_ex = dk.new_slide(header(ids, 'Lab 3 exercise – find R1 and R2') + textbox(ids, 0.6, 1.2, 7.6, 5.9,
    para('Your card shows an **oscilloscope screen** of an inverting amplifier. CH2 (blue) = input. CH1 (yellow) = output.', 17)
    + para('Read Vin and Vout (Pk-Pk) in the Measurements box beside the screen. Gain = Vout / Vin.', 17, bullet='num')
    + para('Choose **R1 (input)** and **R2 (feedback)** so that R2 / R1 = gain.', 17, bullet='num')
    + para('Build the amplifier: ±6 V supply and decoupling capacitors.', 17, bullet='num')
    + para('Set the function generator like CH2 on your card (amplitude and frequency).', 17, bullet='num')
    + para('Make your screen **look the same** as the card. Measure Vout,pp and the phase shift.', 17, bullet='num')
    + para('Call the lecturer. Then submit your values and a photo of your circuit on the student page.', 17, bullet='num'))
    + textbox(ids, 8.5, 1.2, 4.3, 3.2, para('**Hint**', 17) + para('Several resistor pairs may give the same ratio. Any pair within 10% of the gain is fine.', 16) + para('500 mV/div at the bottom = the size of one square of the grid. It is not the signal amplitude.', 16), **BOX))

ids = Ids()
rows = [['Value to submit (student page)', 'Unit', 'Marks'],
        ['Gain read from the screen on your card (positive number)', '–', '3'],
        ['R2 / R1 of the resistors you used (nominal values)', '–', '3'],
        ['Measured output amplitude Vout,pp', 'V', '4'],
        ['Measured phase shift between output and input', 'degrees', '4'],
        ['**Total**', '', '**14**']]
s_sub = dk.new_slide(header(ids, 'Lab 3 – What to submit') + table(ids, 0.55, 1.3, [8.0, 1.4, 1.1], rows, sz=16, row_h=0.55)
    + textbox(ids, 0.55, 5.6, 12.2, 1.3, para('Before you leave: submit your values on the **student page**, return the LM358 and the 470 µF capacitors to the tray, switch off all instruments and clear your breadboard.', 18)))

add_callout(dk, F(34), 'Op-amp', 'an IC that amplifies the difference of its two inputs')
add_callout(dk, F(37), 'Gain', 'how many times bigger the output is')
add_callout(dk, F(40), 'Inverting', 'the output is upside down (180°)', pos='N')
add_callout(dk, F(41), 'Feedback resistor', 'from the output back to the input (R2)')
add_callout(dk, F(44), 'Datasheet', 'the maker’s document: pins and limits')
add_callout(dk, F(45), 'Vcc / Vee', 'the positive / negative supply pins', pos='L')
add_callout(dk, s_dec, 'Decoupling capacitor', 'from the supply to GND; removes noise')
add_callout(dk, s_gp, 'Phase shift', 'how far one wave is moved, in degrees')
add_callout(dk, s_lim, 'Clipping', 'the top of the wave is cut flat')
order = ([F(1), *review_slides(dk, 2), s_ov, s_dev, F(4)] + [F(n) for n in range(32, 52)] + [s_pm, F(58), F(59)]
         + [F(62), s_dec, F(64)] + [s_gp, s_lim, s_sec, s_ex, s_sub])
dk.finalize(order, None)
