# Lecturer script for Lab 1. Keys = slide numbers BEFORE the "Key words" slide was added.
# Format: SAY = what to say (short, simple English). DO = demonstrate. ASK = check questions.
KW = """SAY: Before we start, let's look at some key words. You will hear these words many times today.
SAY: Read each word with me. [Read the word, then the meaning, slowly.]
ASK: What is the difference between series and parallel? (Series: one after another. Parallel: side by side.)
TIP: Keep this slide open for a minute. Students can take a photo."""

N = {
1: """SAY: Welcome to Electronic Circuit Lab. My name is Trà. My email is TraNLT2@fe.edu.vn.
SAY: Today is Lab 1. We will learn the lab instruments and build DC circuits.
SAY: Each lab is 3 hours. There are 4 labs and 1 final exam.""",
2: """SAY: These are the learning outcomes of this course.
SAY: In short: you will use the instruments, build circuits, measure them, and compare with theory.
SAY: You don't need to remember this table. Just remember: build, measure, compare.""",
3: """SAY: This is our plan. Lab 1: instruments and DC circuits. Lab 2: RC and RLC filters. Lab 3: op-amps. Lab 4: microphone to speaker, and exam review.
SAY: After Lab 4, we have the final exam. It is also 3 hours.""",
4: """SAY: Your score has two parts: 50% from the labs, 50% from the final exam.
SAY: The labs give 50 points: 12, 14, 14 and 10.
SAY: If you are absent, you get 0 for that lab.
SAY: In a moment you will make your teams.""",
5: """SAY: This is how I give marks in every lab. Only 4 steps.
SAY: Step 1: your card is on the student page. It has your own variant number. Your circuit is different from your friends.
SAY: Step 2: you build and measure. Step 3: you call me. I look at one number on your meter and give you a tick.
SAY: Step 4: before you leave, enter your numbers on the student page, under your card, and add one to three photos of your circuit.
SAY: The rule is simple: error 10% or less = full marks. 10 to 20% = half. More than 20%, or no tick = 0.
ASK: If your answer is 1.27 mA, what do you type? (1.27 — number only.)""",
5.5: """SAY: Now we take 10 minutes for your team and the student page.
SAY: Your teams are ready. The system made them at random, from your class. 3 students per team. We have only 6 tables, so in a class of 19 one team has 4.
SAY: Take your phone and scan the QR code on the screen. Type your student ID. Check that the name is your name.
SAY: The first time, you create a password, at least 6 characters. Remember it. You use it in every lab. If you forget it, ask me and I reset it.
SAY: The student page shows your team, your member number and your variant. Your team number is your table number. Your member number is used for your card in every lab.
SAY: Now go to your table and check: trainer, multimeter, oscilloscope, function generator. Tell me if something is missing.
SAY: Your team stays the same for Lab 1 to Lab 4. The exam groups are different: they are random.
TIP: Before the class: import the class list on the web (tab Students) – teams are drawn at once. Show the student QR (tab Grade → QR for students).""",
6: """SAY: This is what we have in an electronics lab: power supplies, oscilloscope, function generator, multimeter, and components.
SAY: Today we use the multimeter, the DC power supply, the oscilloscope and the function generator.""",
7: """SAY: Lab rules. Please listen carefully.
SAY: No food and no drinks in the lab. Do not connect the output of one device to another device without checking.
SAY: Always check the power supply before you connect it. If you are not sure, ask me.
SAY: At the end, clean your table.""",
8: """SAY: Each team has one PB-503A trainer. It has a breadboard, DC supplies and a speaker.
SAY: You also have a multimeter, an oscilloscope and a function generator.
SAY: Each student gets resistors for their own variant.
DO: Show the PB-503A, point to the breadboard, the supply outputs and the speaker.""",
9: """SAY: First, the DC instruments: the multimeter and the DC power supply.""",
10: """SAY: A multimeter can measure voltage, current, resistance and capacitance. It can also check continuity and diodes.
SAY: AC means the voltage changes direction. DC means it stays in one direction.""",
11: """DO: Show the multimeter. Point to the dial, the screen and the three sockets.
SAY: Black probe always goes to COM. Red probe goes to V-Ω for voltage and resistance.
SAY: For current, the red probe goes to the mA or 10 A socket.""",
12: """SAY: Look at the maximum values on the sockets. The mA socket has a fuse. Too much current will burn it.
SAY: If you don't know the current, start with the 10 A socket.
SAY: When you know one multimeter, you can use any other one.""",
13: """SAY: Resistors have color bands. The colors tell you the value.
SAY: First bands = digits, next band = multiplier, last band = tolerance.""",
14: """DO: Read one resistor together with the students using the table.
ASK: Yellow, violet, red, gold. What is the value? (4.7 kΩ, ±5%.)""",
15: """SAY: The shop says this is 680 kΩ, 5%. Is it true? We can only know if we measure it.
ASK: What range is OK for 680 kΩ ±5%? (646 to 714 kΩ.)""",
16: """DO: Set the multimeter to Ω. Touch both ends of a resistor. Do not touch the metal with your fingers.
SAY: The printed value is not exact. Always measure your parts again.
DO: Ask every student to measure one resistor and compare with the color code.""",
17: """SAY: Continuity mode checks if a wire is connected. If it is connected, the meter beeps.
SAY: This is very useful when your circuit does not work.
DO: Show the beep with a jumper wire.""",
18: """SAY: Now we check an LED. Red probe on the long leg, black probe on the short leg.
SAY: If the LED lights up a little, it is OK.
DO: Each student checks one LED.""",
19: """SAY: Now we measure DC voltage. Set the meter to V DC.
DO: Measure the output of the power supply. Red probe on +, black probe on −.""",
20: """SAY: The DC power supply has two modes: constant voltage and constant current.""",
21: """SAY: Normally we use constant voltage mode. The voltage stays the same.""",
22: """SAY: If the circuit takes too much current, parts can be damaged.
SAY: So we set a current limit. The supply will not give more than this current.""",
23: """DO: Set 5 V and a current limit of 0.1 A. Measure the output with the multimeter.
SAY: Never set the current limit above 1 A in this lab.
DO: Let each team change the voltage and measure it.""",
24: """SAY: The PB-503A trainer also has DC outputs: positive and negative.
SAY: GND or COM is 0 V. All grounds in your circuit must connect here.
SAY: Always measure the output before you connect it. Turn the trainer off when you change wires.
SAY: In Lab 3 and Lab 4 we use +6 V and −6 V for the op-amp.""",
25: """SAY: Now: how to build a circuit on a breadboard.""",
26: """SAY: Inside the breadboard there are metal strips. They connect some holes together.
SAY: Other breadboards can be different, so always check.""",
27: """DO: Point to the long lines (supply rails) and the short lines.
SAY: The long lines are connected horizontally. The short lines are connected vertically. They stop at the middle gap.""",
28: """SAY: Beginners often make mistakes because they forget the metal strips under the holes.""",
29: """ASK: How would you build this circuit on the breadboard? Think for 30 seconds.""",
30: """SAY: This is wrong. Look: both ends of the resistor are in the same connected line.""",
31: """SAY: Here is the real circuit you built. The resistor is shorted — current does not go through it.""",
32: """SAY: To fix it, put the two legs of the resistor in different lines.""",
33: """ASK: Another example. Is this correct? (No.)""",
34: """SAY: This is the real circuit. The parts are not connected as in the schematic.""",
35: """SAY: Here is the fix. Always compare your breadboard with the schematic.""",
36: """SAY: Build your circuit node by node. A node is a point where parts connect.
SAY: At each node, check which parts are connected. Wrong node = wrong circuit.""",
37: """SAY: These schematics look different, but they are the same circuit. Look at the nodes, not the shape.""",
38: """SAY: These breadboards also look different, but they are the same circuit.
ASK: How many nodes are there?""",
39: """SAY: Now the AC instruments: the oscilloscope and the function generator.""",
40: """SAY: An oscilloscope shows a voltage as a wave on the screen. X axis = time, Y axis = voltage.""",
41: """SAY: Everything yellow is channel 1.""",
42: """SAY: Everything blue is channel 2.""",
43: """DO: Turn the vertical scale knob and the position knob. Show how the wave changes.
SAY: Use these knobs to make the wave big and clear.""",
44: """DO: Show the horizontal scale (time per division) and the trigger level.
SAY: If the wave moves on the screen, adjust the trigger.""",
45: """SAY: A 10X probe makes the signal 10 times smaller before it enters the oscilloscope.
SAY: The oscilloscope must know this. Otherwise your reading is 10 times wrong.""",
46: """SAY: Now we set up the measurements. Step 1: press Default Setup.
DO: Every team presses Default Setup now.""",
47: """SAY: Step 2: press Measure.""",
48: """SAY: Turn the multipurpose knob, choose Frequency, press the knob. Then choose Peak-to-peak, press the knob.
DO: Walk around and help teams.""",
49: """SAY: Now you can see the frequency and Vpp on the screen.""",
50: """DO: Connect the 10X probe to channel 1 and to the test signal output. Press Autoset.
SAY: You should see a square wave.""",
51: """SAY: Be careful with the oscilloscope. Do not connect high voltage.""",
52: """SAY: The maximum input is 300 V RMS. Never measure the wall socket.""",
53: """SAY: Static electricity can damage the oscilloscope. Touch a metal part before you touch the inputs.""",
54: """SAY: A function generator makes signals: sine, square, triangle. You choose the frequency and amplitude.""",
55: """SAY: First we set up the function generator. Step 1: press Utility.""",
56: """SAY: Step 2: press Output Setup. Step 3: change 50 Ω to High-Z.
SAY: Check that the amplitude is still 10 Vpp.
DO: Every team does this now.""",
57: """SAY: 50 Ω is for special 50 Ω cables at very high frequency. We do not use it.""",
58: """SAY: High-Z means the value you set is the value you get at the output. We always use High-Z.""",
59: """DO: Connect the function generator to channel 1 with the BNC cable. Set a 10 Vpp, 5 kHz sine. Turn on the output.""",
60: """DO: Display channel 1. Check that Run is green. Press Autoset.
ASK: What Vpp do you see? Is it 10 V?""",
61: """ASK: Why is the value wrong?""",
62: """SAY: Because our cable is 1X, but the oscilloscope thinks it is 10X. So it shows 10 times too much.""",
63: """SAY: Let's fix it. Step 1: press the channel 1 button.""",
64: """SAY: Step 2: press Probe Setup. Turn the knob to Attenuation. Press the knob.""",
65: """SAY: Turn the knob to 1X. Press again to confirm.
ASK: Now what Vpp do you see? (10 V.)""",
66: """SAY: Remember: normal BNC cable = 1X. 10X probe = 10X. Always check this first.
SAY: In the final exam, the oscilloscope starts in default setup. You must fix this yourself.""",
67: """SAY: You can choose other values if you need them, but today we only use 1X and 10X.""",
68: """SAY: Now we build basic DC circuits: the voltage divider and the current divider.""",
69: """DO: Each student builds this voltage divider with 2.2 kΩ and 4.7 kΩ at 5 V.
SAY: Measure the resistors first. Then measure V1 and V2.""",
70: """ASK: Is VDC equal to V1 plus V2? Is the total resistance R1 plus R2?
SAY: Check it with your numbers.""",
71: """SAY: To measure current: open the circuit at one point. Put the meter in series. Use the mA mode.
SAY: Never put the meter in current mode across a part — this makes a short circuit.""",
72: """ASK: Is I1 equal to I2? Why? (Yes. In series the current is the same.)""",
73: """DO: Now build the current divider with the same resistors. They are now in parallel.""",
74: """SAY: Open the branch you want to measure. Put the meter in series with that branch.""",
75: """DO: Measure the current in each branch and the total current.""",
76: """ASK: Is the total current equal to I1 plus I2? (Yes — Kirchhoff's current law.)""",
77: """SAY: Now we make resistor values that we cannot buy.""",
78: """SAY: Build this circuit using only 2.2 kΩ, 4.7 kΩ and 10 kΩ.
SAY: I will ask you to measure a node voltage or a branch current.
DO: Give 10 minutes. Then show the solution.""",
79: """SAY: Here is one solution.""",
80: """SAY: Look how each value is made from standard resistors in series or parallel.""",
81: """SAY: Same circuit, same nodes, same branches — only the breadboard layout is different.""",
82: """SAY: Why do we do this? Because shops sell only standard values. If you need 6.9 kΩ, you combine resistors.""",
83: """SAY: Now your exercise for today. It gives you 12 points.""",
84: """SAY: Look at the circuit. R_A and R_B are in parallel. Then R_C and R_D are in series.
SAY: Your card gives R_A, R_B, R_C and R_D. These values are not sold. You must make each one from two standard resistors. For example, 5.7 kilo-ohm is 1 kilo-ohm plus 4.7 kilo-ohm.
SAY: Follow the 5 steps. Measure R_eq before you connect the supply.
DO: Give out the variant cards now. Check that each student writes their name on the card.
TIP: When a student calls you, choose any one value (R_eq, I, I_A or V_X), read it on their meter and compare with the answer sheet.""",
85: """SAY: Type these 4 numbers on the student page, under your card. Use the unit in the table.
SAY: Also take one to three photos of your real circuit. The photo is required.
SAY: Use your measured values, not calculated values.
SAY: You can change your numbers until I check your reading. Before you leave: submit, switch off, return parts, clear your breadboard.
TIP: Give the Canvas access code now.""",
}
