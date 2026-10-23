KW = """SAY: Key words for today. The most important: coupling capacitor, decoupling capacitor, bias, stage, load.
SAY: Coupling = passes AC, blocks DC. Decoupling = sends noise from the supply to ground.
ASK: The speaker is connected to the amplifier output. What do we call the speaker? (The load.)"""

N = {
1: """SAY: Welcome to Lab 4, our last lab. We build a microphone-to-speaker circuit. Then we review for the exam.""",
2: """SAY: Today: the speaker, the microphone, the two-stage amplifier, and the exam review.
SAY: Today each team builds one circuit together. Then each person does one measurement alone for marks.""",
3: """SAY: You need the PB-503A with its speaker, the instruments, one LM358, one microphone and these parts.
SAY: The microphone legs are soldered to wires. Please handle it carefully.""",
4: """SAY: Again: electrolytic capacitors have + and −. The long leg goes to the more positive side.""",
5: """SAY: Capacitors are often used alone, without resistors. Two common uses: coupling and decoupling.""",
6: """SAY: A coupling capacitor passes AC and blocks DC.
SAY: Example: the microphone has DC on it. We only want its AC sound signal to go to the amplifier.""",
7: """SAY: A decoupling capacitor goes from the DC supply to ground. AC noise goes to ground. DC stays.
SAY: We saw this in Lab 3 at the op-amp supply.""",
8: """SAY: Here are decoupling capacitors in a microphone circuit.""",
9: """SAY: We build a similar circuit today.""",
10: """SAY: Part 1: the 8 Ω speaker.""",
11: """DO: Find the speaker on the PB-503A. Measure its resistance with the multimeter.""",
12: """SAY: You get about 10 Ω, because the jumper wires also have some resistance.""",
13: """SAY: A speaker needs an AC signal. People can hear from 20 Hz to 20 kHz.""",
14: """DO: Connect the function generator directly to the speaker with the 1X cable. Connect the oscilloscope too.""",
15: """SAY: You hear a sound. Bigger amplitude = louder. Higher frequency = higher pitch.
DO: Let students change amplitude and frequency.""",
16: """DO: Look at the signal on the speaker with the oscilloscope.""",
17: """SAY: We set 0.5 Vpp, but we see only 0.1 Vpp on the speaker.
ASK: Why? (The generator has 50 Ω inside. The speaker is only 8 Ω, so most of the voltage is lost inside the generator.)""",
18: """SAY: Now put a capacitor in series with the speaker: a coupling capacitor. Try 0.1 µF, 0.2 µF, 470 µF, 235 µF.
SAY: The + leg of the electrolytic capacitor goes toward the generator.""",
19: """SAY: Remember the 8 Ω inside the speaker. Together with C it makes a high-pass filter.""",
20: """ASK: With C = 0.1 µF and R = 8 Ω, what is fc? (About 200 kHz — too high. Sound cannot pass.)""",
21: """SAY: This is the breadboard with 0.1 µF.""",
22: """SAY: With 0.1 µF we see only noise. We hear nothing.""",
23: """SAY: Now with 470 µF, fc is about 40 Hz. Sound can pass.""",
24: """SAY: This is the breadboard with 470 µF.""",
25: """SAY: With 470 µF we see the signal and hear the sound.
SAY: Lesson: a coupling capacitor for a speaker must be big.""",
26: """SAY: Part 2: the microphone.""",
27: """SAY: We all know microphones. But how do they work?""",
28: """SAY: There are two types of condenser microphones: standard and electret.""",
29: """SAY: Sound makes a thin plate vibrate. The capacitance changes. This makes a small AC signal.""",
30: """SAY: We use an electret microphone. It is small and cheap.""",
31: """SAY: Inside there is a small transistor called a JFET. You will learn it later. It needs a DC bias.""",
32: """SAY: Microphones usually have a cover to block wind noise.""",
33: """SAY: Our electret picks up sound from all directions. A rolled paper tube helps it hear only your voice.""",
34: """SAY: Microphones give only millivolts. We always need an amplifier.""",
35: """SAY: First, test the microphone alone.""",
36: """SAY: Watch the pins. The pin connected to the metal case goes to ground.""",
37: """SAY: Build this circuit. The resistor gives DC bias to the microphone.
ASK: What is the capacitor for? (Coupling: it passes only the AC sound signal.)""",
38: """SAY: This is the circuit on the PB-503A. Use the +6 V output for the bias resistor.
DO: Check the microphone polarity in every team.""",
39: """SAY: Talk into the microphone through a rolled paper. Look at the signal on the oscilloscope.""",
40: """SAY: This is an example of the signal.""",
41: """SAY: Another example. The signal changes with your voice.""",
42: """SAY: Without the paper tube, the signal is very weak. With it, you get a clear waveform.""",
43: """SAY: We can get about 750 mVpp when we speak loudly.
ASK: Can we connect it directly to the speaker?""",
44: """SAY: Let's check.""",
45: """DO: Connect the output to the speaker. Talk into the microphone. Look at the speaker signal.""",
46: """SAY: Look at the signal at the speaker.""",
47: """SAY: It does not work. Why not?""",
48: """SAY: We see only small noise.""",
49: """SAY: Remember the speaker test earlier today?""",
50: """SAY: With 1 Vpp from the generator and 470 µF we got only 200 mVpp on the speaker.
SAY: The microphone is much weaker and can give almost no current. So the speaker gets almost nothing.""",
51: """DO: You can try 470 µF instead of 1 µF. You will still hear almost nothing.""",
52: """SAY: So we need an amplifier.""",
53: """SAY: Keep this microphone circuit on your breadboard. We use it at the end.""",
54: """SAY: Quick recap from Lab 3. Gain = − R_f / R_in.
SAY: Supply: +6 V to pin 8, −6 V to pin 4, decoupling on both rails.
SAY: Stage 1 today: R_in = 2.2 kΩ, R_f = 30 kΩ. Test it with 10 mVpp, 1 kHz.""",
55: """SAY: Now add the second stage after the first one. The output of stage 1 goes into stage 2.
SAY: Total gain = gain 1 × gain 2.""",
56: """SAY: This is the schematic of the two stages. The second op-amp is the other half of the same LM358.""",
57: """SAY: Here is the result on the oscilloscope. The small input becomes a few volts.""",
58: """DO: Connect the final output to the speaker. Try with and without 470 µF before the speaker.""",
59: """SAY: This is the two-stage amplifier on the breadboard.""",
60: """SAY: With the speaker connected directly, the sound is clear, but the speaker makes the output smaller.""",
61: """SAY: With 470 µF before the speaker, the shape is more balanced, but Vpp is lower.""",
62: """SAY: Now the final circuit, version 1.""",
63: """DO: Disconnect the function generator. Connect the microphone circuit to the amplifier through 1 µF. Connect the output to the speaker.""",
64: """SAY: This is the full circuit.""",
65: """SAY: Are we finished?""",
66: """SAY: Let's try it.""",
67: """SAY: You hear a loud echo. This is acoustic feedback: the speaker sound goes back into the microphone.
SAY: After about one minute the signal can die.""",
68: """SAY: Then you must switch off and on again to restart it.""",
69: """ASK: Why don't I give you the perfect circuit at the start?""",
70: """SAY: Because when you see a problem and fix it, you really learn why each part is needed.""",
71: """SAY: Final circuit, version 2.""",
72: """SAY: How do we stop the echo? The echo happens when the speaker is too loud and too close.""",
73: """SAY: Fix 1: lower the gain. Replace 47 kΩ with 4.7 kΩ in stage 2.""",
74: """SAY: Fix 2: add 100 nF capacitors at the op-amp supply pins.""",
75: """SAY: Fix 3: cheap microphones are very sensitive near 5 kHz. This can make the circuit unstable.
SAY: Human voice is 300 Hz to 3 kHz, so we can cut the high frequencies.""",
76: """SAY: Add 1 nF in parallel with 30 kΩ in stage 1. This is a low-pass filter. fc is about 5 kHz.""",
77: """SAY: This is version 2 of the schematic.""",
78: """SAY: Look at the changes: 4.7 kΩ, 1 nF, 100 nF.""",
79: """DO: Try with 1 µF first. Does it die out? Then try 10 µF or 470 µF.""",
80: """SAY: The echo is much smaller. You can hear your voice better.""",
81: """SAY: Here is an example on the PB-503A. Keep the wires short and tidy.
SAY: If something does not work, test each stage with the function generator and the oscilloscope.""",
82: """SAY: Now the marks for Lab 4.""",
83: """SAY: Team demo: 4 points. Speak into the microphone. I must hear you in the speaker.
SAY: Then each member does one measurement alone: 6 points. Look at your card: member 1, 2, 3, or 4 in a team of 4.
SAY: Disconnect the microphone. Put 10 mVpp from the function generator into stage 1. Measure the Vpp asked on your card.
SAY: Submit your value and a photo of your circuit on the student page.
TIP: Expected values: member 1 ≈ 134 mVpp, member 2 ≈ 286 mVpp, member 3 ≈ 99 mVpp.""",
84: """SAY: Now the exam review.""",
85: """SAY: The exam is 3 hours. About 90 minutes are for work.
SAY: Groups are random, from your class, up to 3 people. Group work = 35 points. Your own part = 15 points.
SAY: The instruments start in default state. You must set them up yourself.
SAY: If a member does nothing, they fail the exam.""",
86: """SAY: Check this list. Can you do all of these?
SAY: DC: combine resistors, measure again, redraw the schematic, measure voltages and currents, calculate and compare.
SAY: AC: design RC filters, set up the function generator and the oscilloscope, measure at many frequencies.
SAY: Alone: measure R, C, V, I; capture a signal; find a fault; explain your circuit.""",
87: """SAY: Important for two connected stages: the second stage takes current from the first one. It is a load.
SAY: Then the first stage gives a smaller output, and a filter can change its cut-off frequency.
SAY: Simple rule: the next stage should be at least 10 times bigger in ohms.""",
88: """SAY: Practice now. One member builds a small circuit and secretly makes one mistake.
SAY: Another member finds the mistake using only the instruments. The third member explains the circuit.
SAY: Change roles every 10 minutes.
SAY: Before you leave: switch off, return the LM358, the microphone and the 470 µF capacitors, clear your breadboard. Good luck in the exam!""",
}
