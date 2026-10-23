KW = """SAY: Today's key words. Read them with me.
SAY: The most important: filter, cut-off frequency, resonance f0, Q and bandwidth.
ASK: A low-pass filter passes which frequencies? (Low ones.)"""

N = {
1: """SAY: Welcome to Lab 2: RC and RLC circuits. Today we work with AC signals and filters.""",
2: """SAY: Today has 4 parts: RC filters, capacitors, series RLC, and the Lab 2 exercise.
SAY: Remember: at the start, the instruments are in default state. First, set 1X or 10X on the oscilloscope and High-Z on the function generator.
DO: Give 3 minutes for teams to set up the instruments.""",
3: """SAY: Each team uses the oscilloscope, function generator, multimeter and PB-503A.
SAY: Each student gets parts for the warm-up and for the RLC exercise. Use only the parts for your own variant.
SAY: Download the Excel template from the student page now.""",
4: """SAY: Part 1: first-order RC circuits. One resistor and one capacitor.""",
5: """DO: Set the function generator: 10 Vpp sine. Measure the input on channel 1.
SAY: Build the circuit. Then change the frequency and watch the output.""",
6: """SAY: Here is an example on the breadboard. The output is across the capacitor.""",
7: """DO: Fill this table together: change the frequency, read Vout.""",
8: """ASK: What do you notice? (Low frequency → big output. High frequency → small output.)""",
9: """SAY: Now swap R and C. The output is now across the resistor. Do the same measurements.""",
10: """DO: Fill the second table.""",
11: """ASK: What do you notice now? (Now high frequency → big output.)""",
12: """SAY: The first circuit is a low-pass filter. It passes low frequencies.""",
13: """SAY: Low-pass: lower frequency gives a higher output. High-pass: higher frequency gives a higher output.""",
14: """SAY: Look at the two curves. They cross at the cut-off frequency.""",
15: """SAY: Filters are in almost every electronic device. They remove noise and unwanted signals.""",
16: """SAY: Use circuit theory: the capacitor impedance is 1 / (jωC). Write Vout / Vin for both circuits.
DO: Solve it on the board, step by step.""",
17: """SAY: The cut-off frequency is fc = 1 / (2πRC). At fc, Vout = 0.707 × Vin.
SAY: Use the total R and total C.""",
18: """ASK: Calculate fc for the circuit on the slide. Compare with what you measured.""",
19: """SAY: Warm-up exercise: 2 points. Your card gives the type, R and C.
SAY: Calculate fc. Build it. Change the frequency until Vout = 0.707 × Vin. That is your measured fc. Write it in kHz.
DO: Give the variant cards now.""",
20: """SAY: Part 2: capacitors.""",
21: """SAY: A capacitor stores charge. Its unit is the farad. In the lab we use nF and µF.""",
22: """SAY: You saw capacitors in filters. They are also used in many other circuits.""",
23: """SAY: What if you need a value you don't have? You combine capacitors.""",
24: """SAY: Capacitors in parallel: just add the values. Look at the picture: the total is 3 µF.
SAY: Careful: this is the opposite of resistors.""",
25: """SAY: Capacitors in series: use 1/C = 1/C1 + 1/C2 + ... The picture gives 0.33 µF.
ASK: Why is it opposite to resistors? Think at home.""",
26: """SAY: Most multimeters can measure capacitance.
SAY: Take the capacitor out of the circuit. Discharge it. Select the capacitance mode. Wait for a stable number.
DO: Each student measures their 22 nF and 2.2 nF capacitors.
SAY: The exam may ask you to measure a capacitor. Practise now.""",
27: """SAY: Part 3: inductors.""",
28: """SAY: An inductor is a coil of wire. Its unit is the henry. We use 1 mH today.""",
29: """SAY: An RL circuit is also a filter. L and C together make a resonant circuit, like in radios.""",
30: """SAY: Inductors combine like resistors: series = add, parallel = 1/L rule.""",
31: """SAY: Now the RLC circuit.""",
32: """SAY: An RLC circuit has a resistor, an inductor and a capacitor.""",
33: """SAY: L and C both store energy. They pass the energy back and forth. This makes a resonant frequency f0.
SAY: At f0, the current is maximum.""",
34: """SAY: f0 = 1 / (2π√(LC)). The bandwidth depends on R. Big Q = narrow peak.
SAY: Smaller R gives a bigger Q. We check this in the exercise.""",
35: """SAY: One series RLC circuit can make three filters. It depends on where you take the output.
SAY: Across C = low-pass. Across L = high-pass. Across R = band-pass.
SAY: Put the output part at the ground side, so both probe grounds go to the same point.
ASK: Why must both probe grounds be on the same point? (The grounds are connected inside the oscilloscope.)""",
36: """SAY: These are the formulas for today. With L = 1 mH and C = 24.2 nF, f0 is about 32.35 kHz.
SAY: Z0 = √(L/C) ≈ 203 Ω. Q = Z0 / R_total.
SAY: For low-pass and high-pass with Q above 1, the peak is not exactly at f0. Use the formulas in the last two rows.
SAY: Don't forget: R_total = your R + R_L of the coil.""",
37: """SAY: Real parts are not perfect.
SAY: The coil wire has resistance. Measure it.
SAY: The function generator has 50 Ω inside. Near f0, Vin goes down. So measure Vin at every frequency and use Vout / Vin.
SAY: L and C are not exact. Your f0 can be a few percent away.""",
38: """SAY: Where are RLC circuits used? For example in AM radio receivers.""",
39: """SAY: And in oscillators that make sine waves. And many more.""",
40: """SAY: Now the Lab 2 exercise: 12 points.""",
41: """SAY: Your card gives the filter type and Q. In your team, one student does low-pass, one high-pass, one band-pass.
SAY: Measure R_L. Calculate R_total = 203 / Q. Then R = R_total − R_L. Make R from 47, 100 and 220 Ω.
SAY: Measure R and the coil together with the ohmmeter. That is your R_total for the student page.
DO: Check each student's calculation before they build.""",
42: """SAY: Download the Excel file from the student page, under your Lab 2 card. Measure Vin and Vout at each frequency on your card. Type them into the Excel file. The graph draws itself.
SAY: Find the peak carefully: add points near it.
SAY: Low-pass and high-pass: write the highest Vout / Vin. Band-pass: find f_L and f_H, then BW.
SAY: Write 1 to 3 sentences of conclusion. Then call me.
TIP: When you tick, look at the graph and conclusion on the laptop and give 0, 1.5 or 3 points.""",
43: """SAY: Type these numbers on the student page, under your card. Use kHz for frequencies. Add a photo of your circuit.
SAY: Before you leave: submit, switch off, clear your breadboard.
TIP: Give the Canvas access code now.""",
}
