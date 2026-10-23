import re
def patch(fn, pairs):
    s = open(fn).read()
    for o, n in pairs:
        assert o in s, (fn, o[:60])
        s = s.replace(o, n)
    open(fn, 'w').write(s)

patch('build_d2.py', [
 ("[('AC equipment, capacitor and inductor circuits', 'RC and RLC circuits'), ('4 hours', '3 hours')]",
  "[('AC equipment, capacitor and inductor circuits', 'RC and RLC circuits'), ('4 hours', '3 hours  ·  Lecturer: TraNLT2@fe.edu.vn')]"),
 ("para('Reminder: every lab starts with the instruments in their **default state** (oscilloscope Default Setup, function generator 50 Ω). Check the probe attenuation (1X/10X) and set the function generator output to **High-Z** before you measure.', 17)",
  "para('Reminder: at the start, the instruments are in their **default state**. Before you measure: (1) check 1X / 10X on the oscilloscope, (2) set the function generator to **High-Z**.', 17)"),
 ("""        + para('Change the frequency until **Vout = 0.707 × Vin**. This frequency is the measured fc.', 17, bullet='num')
        + para('Compare with your calculation. Keep the value for Canvas (in **kHz**).', 17, bullet='num')),""",
  """        + para('Change the frequency until **Vout = 0.707 × Vin**. This frequency is your measured fc.', 17, bullet='num')
        + para('Compare it with your calculation. Write it down in **kHz** for Canvas.', 17, bullet='num')),"""),
 ("""    para('**Inductor resistance R_L.** Measure the inductor with the ohmmeter. It is part of R_total.', 19, bullet='dot')
    + para('**Function generator output resistance (50 Ω).** Near resonance the circuit draws more current, so the generator voltage drops. Therefore:', 19, bullet='dot')
    + para('Measure **Vin on CH1 at the circuit input at every frequency**, not just once.', 18, level=1, bullet='dot')
    + para('Always use the ratio **Vout / Vin**, not Vout alone.', 18, level=1, bullet='dot')
    + para('**Probes.** Use 10X probes on both channels (set 10X on the oscilloscope). Both ground clips on the circuit ground.', 19, bullet='dot')
    + para('**Component tolerance.** L is ±10%, C is ±5%: your measured f0 may differ from 32.35 kHz by a few percent.', 19, bullet='dot')))""",
  """    para('**The inductor wire has resistance (R_L).** Measure it with the ohmmeter. Add it to R.', 19, bullet='dot')
    + para('**The function generator has 50 Ω inside.** Near f0 the circuit takes more current, so Vin goes down. So:', 19, bullet='dot')
    + para('Measure **Vin (CH1) at every frequency**, not only once.', 18, level=1, bullet='dot')
    + para('Always use the ratio **Vout / Vin**.', 18, level=1, bullet='dot')
    + para('**Probes:** use 10X probes on both channels and set 10X on the oscilloscope. Both ground clips go to circuit ground.', 19, bullet='dot')
    + para('**Parts are not exact:** L is ±10%, C is ±5%. Your f0 can be a few % away from 32.35 kHz.', 19, bullet='dot')))"""),
 ("""    + para('Measure R_L of your inductor. Calculate R_total = Z0 / Q and the resistor R = R_total − R_L.', 17, bullet='num')
    + para('Build R from 47 Ω, 100 Ω and 220 Ω resistors (series / parallel).', 17, bullet='num')
    + para('With the ohmmeter, measure **R + inductor in series** (DC). This is your measured R_total.', 17, bullet='num')
    + para('Build your filter (output component at the ground side).', 17, bullet='num')
    + para('Function generator: sine, 2 Vpp, High-Z. CH1 = Vin at the circuit input, CH2 = Vout.', 17, bullet='num'))""",
  """    + para('Measure R_L of your inductor. Calculate R_total = Z0 / Q. Then R = R_total − R_L.', 17, bullet='num')
    + para('Make R from 47 Ω, 100 Ω and 220 Ω resistors (series or parallel).', 17, bullet='num')
    + para('Measure **R and the inductor together** with the ohmmeter. This is your R_total.', 17, bullet='num')
    + para('Build your filter. Put the output part at the ground side.', 17, bullet='num')
    + para('Function generator: sine, 2 Vpp, High-Z. CH1 = Vin, CH2 = Vout.', 17, bullet='num'))"""),
 ("""    para('Open **Lab2_RLC_data_template.xlsx**. For each frequency on your card, measure Vin (CH1) and Vout (CH2) peak-to-peak and type them in. The ratio and the graph update automatically.', 17, bullet='num')
    + para('Find the maximum of Vout / Vin precisely: add extra points around the peak. Note **f_max** (kHz).', 17, bullet='num')
    + para('**Low-pass / high-pass:** note the **peak value of Vout / Vin**.', 17, bullet='num')
    + para('**Band-pass:** find f_L and f_H where Vout/Vin = 0.707 × maximum. Note the **bandwidth BW = f_H − f_L** (kHz).', 17, bullet='num')
    + para('Write a 1–3 sentence conclusion in the file: compare your measured f_max, Q / BW with the theory and explain the difference.', 17, bullet='num')
    + para('Call the lecturer: show one reading on the oscilloscope **and** your graph with the conclusion.', 17, bullet='num')))""",
  """    para('Open **Lab2_RLC_data_template.xlsx**. For each frequency on your card, measure Vin (CH1) and Vout (CH2), peak-to-peak. Type them in. The graph draws itself.', 17, bullet='num')
    + para('Find the highest Vout / Vin. Add more points near the peak. Write down **f_max** (kHz).', 17, bullet='num')
    + para('**Low-pass or high-pass:** write down the **highest Vout / Vin**.', 17, bullet='num')
    + para('**Band-pass:** find f_L and f_H where Vout/Vin = 0.707 × highest value. **BW = f_H − f_L** (kHz).', 17, bullet='num')
    + para('Write 1–3 sentences: compare your results with the theory. Why are they different?', 17, bullet='num')
    + para('Call the lecturer. Show one reading on the oscilloscope **and** your graph.', 17, bullet='num')))"""),
])
patch('build_d3.py', [
 ("('4 hours', '3 hours')])\ndk.edit_text(F(33)", "('4 hours', '3 hours  ·  Lecturer: TraNLT2@fe.edu.vn')])\ndk.edit_text(F(33)"),
 ("para('Op-amps are covered in detail in a later theory course. Today you learn **just enough to build and measure** an inverting amplifier. Each student builds their own amplifier.', 17)",
  "para('You will study op-amps in detail later. Today you learn **just enough to build and measure** an inverting amplifier. Each student builds their own amplifier.', 17)"),
 ("""    para('Your card shows an **oscilloscope screen** of an inverting amplifier: CH2 = input from the function generator, CH1 = output.', 17)
    + para('Read the input amplitude and frequency from the screen. Calculate the gain.', 17, bullet='num')
    + para('Choose **R1 (input) and R2 (feedback)** from the team tray so that R2 / R1 gives this gain.', 17, bullet='num')
    + para('Build the amplifier with ±6 V supply and decoupling capacitors.', 17, bullet='num')
    + para('Set the function generator to the same input as on your card.', 17, bullet='num')
    + para('**Reproduce the screen** on your oscilloscope. Measure Vout,pp and the phase shift.', 17, bullet='num')
    + para('Call the lecturer, then submit on Canvas.', 17, bullet='num'))""",
  """    para('Your card shows an **oscilloscope screen** of an inverting amplifier. CH2 (blue) = input. CH1 (yellow) = output.', 17)
    + para('Read Vin and Vout from the screen. Gain = Vout / Vin.', 17, bullet='num')
    + para('Choose **R1 (input)** and **R2 (feedback)** so that R2 / R1 = gain.', 17, bullet='num')
    + para('Build the amplifier: ±6 V supply and decoupling capacitors.', 17, bullet='num')
    + para('Set the function generator like CH2 on your card (amplitude and frequency).', 17, bullet='num')
    + para('Make your screen **look the same** as the card. Measure Vout,pp and the phase shift.', 17, bullet='num')
    + para('Call the lecturer. Then submit on Canvas.', 17, bullet='num'))"""),
])
patch('build_d4.py', [
 ("('Microphone to Speaker', '& exam review'), ('4 hours', '3 hours')]", "('Microphone to Speaker', '& exam review'), ('4 hours', '3 hours  ·  Lecturer: TraNLT2@fe.edu.vn')]"),
 ("para('Today the **team builds one circuit together**. Each member is then marked individually on one measurement (see the end of the slides).', 17)",
  "para('Today **each team builds one circuit together**. Then each member does **one measurement** alone for marks (see the last slides).', 17)"),
 ("""        para('A circuit designed alone changes when you connect the next stage to its output: the next stage **draws current** and acts as a load.', 18)
        + para('Without the load: Vout = Vin · R2 / (R1 + R2)', 17, bullet='dot')
        + para('With the load: R2 becomes R2 ∥ R_load → Vout drops', 17, bullet='dot')
        + para('The same happens with filters: the second filter loads the first one and shifts its cut-off frequency.', 17, bullet='dot')
        + para('Rule of thumb: make the impedance of the next stage **at least 10 × larger** than that of the previous stage.', 17, bullet='dot')),""",
  """        para('When you connect a second stage, it **takes current** from the first stage. We call it a **load**.', 18)
        + para('No load: Vout = Vin · R2 / (R1 + R2)', 17, bullet='dot')
        + para('With load: R2 becomes R2 ∥ R_load, so Vout goes down', 17, bullet='dot')
        + para('Filters too: the second filter changes the cut-off frequency of the first one.', 17, bullet='dot')
        + para('Simple rule: the next stage should be **10 times bigger** (in Ω) than the stage before.', 17, bullet='dot')),"""),
])
print('patched')
