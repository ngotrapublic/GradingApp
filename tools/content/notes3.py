KW = """SAY: Key words for today. The most important: op-amp, gain, inverting, phase shift.
SAY: Inverting means the output is upside down. 180 degrees of phase shift means the same thing.
ASK: Vin = 0.1 V, Vout = 2 V. What is the gain? (20.)"""

N = {
1: """SAY: Welcome to Lab 3: operational amplifiers. Today we build an inverting amplifier.""",
2: """SAY: Today: op-amp basics, the LM358 chip, how to measure gain and phase, and the Lab 3 exercise.
SAY: You will study op-amps in detail later. Today we learn only what we need to build one.""",
3: """SAY: Each student gets one LM358 and two 100 nF capacitors. Each team gets two 470 µF capacitors.
SAY: The LM358 and the 470 µF capacitors go back to the tray at the end. We use them again in Lab 4.""",
4: """SAY: Electrolytic capacitors have + and −. The long leg is +. It goes to the more positive voltage.
SAY: If you connect it the wrong way, it can burst. Check twice.""",
5: """SAY: Part 1: what is an op-amp?""",
6: """SAY: Op-amps are a big topic. Today we only learn the basics.""",
7: """SAY: An op-amp is an IC. It has two inputs: V+ and V−. It amplifies the difference between them.""",
8: """SAY: This is the V+ input, the non-inverting input.""",
9: """SAY: This is the V− input, the inverting input. The op-amp takes V+ minus V−.""",
10: """SAY: Then it multiplies the difference by a very big gain.""",
11: """SAY: The op-amp needs power: a positive supply and a negative supply.
SAY: Don't mix them up: V+ and V− are inputs. Vs+ and Vs− are power pins.""",
12: """SAY: Without feedback, the gain is huge, maybe 100 000. This is open-loop gain. We cannot control it.
SAY: So we add resistors to set the gain.""",
13: """SAY: This is the inverting amplifier. R1 goes to the input, R2 goes from output back to the input.
SAY: Gain = − R2 / R1. The minus sign means the output is upside down.""",
14: """ASK: R1 = 1 kΩ, R2 = 10 kΩ, Vin = 0.2 Vpp. What is Vout? (2 Vpp, upside down.)""",
15: """SAY: Now, a real op-amp.""",
16: """SAY: We use the LM358. It has 8 pins. Which pin is which? We need the datasheet.""",
17: """SAY: Always find the datasheet before you use a chip. Search "LM358 datasheet".""",
18: """SAY: Look at the pin diagram. One LM358 has two op-amps inside: A and B.
SAY: Pin 8 = Vcc, positive supply. Pin 4 = Vee, negative supply or ground.
DO: Show where the notch or dot is on the chip. Pin 1 is next to it.""",
19: """SAY: Always check the ratings: maximum supply voltage, input range, output current.
SAY: Otherwise the chip can be damaged, or the circuit does not work.""",
20: """SAY: This is the ratings table from the datasheet.""",
21: """SAY: Today we only need: the supply range, and that the output cannot reach the supply rails.""",
22: """SAY: Part 2: build the amplifier.""",
23: """SAY: We build one inverting amplifier with one op-amp. We test it with the function generator.
SAY: Always work step by step. Build, test, then go to the next step.""",
24: """SAY: This is the first inverting amplifier.""",
25: """SAY: On the PB-503A, set +6 V and −6 V. Measure both with the multimeter.
SAY: Connect the trainer GND to the ground rail of your breadboard.
SAY: +6 V to pin 8, −6 V to pin 4. Never swap them.
DO: Check each team's supply before they put the chip in.""",
26: """SAY: Connect +6 V to pin 8 and −6 V to pin 4, as in this picture.""",
27: """SAY: Now the rest of the circuit. 3 × 10 kΩ in series make 30 kΩ.
SAY: Function generator: 10 mVpp, 500 Hz.""",
28: """SAY: Noise on the supply goes to the output. So we filter the supply.""",
29: """SAY: We put capacitors from each supply rail to GND.
SAY: 470 µF removes low-frequency noise like 50 Hz. 100 nF next to the chip removes high-frequency noise.
SAY: On the −6 V rail, the + leg of the capacitor goes to GND.""",
30: """SAY: Your circuit should look like this.
DO: Walk around and check the circuits before students switch on.""",
31: """SAY: How to measure gain: show Pk-Pk on both channels. Gain = Vout,pp / Vin,pp.
SAY: Here: 9.52 V divided by 0.262 V is about 36.
SAY: Phase: the output is upside down. When the input is at the top, the output is at the bottom. That is 180 degrees.
DO: Show the cursors on the oscilloscope: measure Δt between the two waves. Phase = 360 × Δt × f.""",
32: """SAY: Three limits of the LM358.
SAY: One: with ±6 V the output can only go from about −5 V to +4.5 V. If the wave is too big, the top is cut flat. This is clipping.
SAY: Two: with big gain, it works only at lower frequencies. Use 100 Hz to 2 kHz today.
SAY: Three: small signals pick up noise. Keep wires short.""",
33: """SAY: Now your exercise: 14 points.""",
34: """SAY: Your card shows an oscilloscope screen. Blue is the input, yellow is the output.
SAY: Read the two Pk-Pk values in the Measurements box, on the right of the screen. Gain = Vout / Vin. Then choose R1 and R2 so that R2 / R1 = gain.
SAY: The numbers at the bottom, like 500 millivolts per div, are the size of one square of the grid. They are not the signal.
SAY: Build it, set the function generator like the blue signal, and make your screen look like the card.
SAY: Open your card on the student page now.
TIP: When a student calls you, check that their screen looks like the card and read one value.""",
35: """SAY: Type these numbers on the student page, under your card, and add a photo of your circuit. Gain and R2/R1 have no unit. Vout in volts. Phase in degrees.
SAY: Before you leave: submit, return the LM358 and the 470 µF capacitors, switch off, clear your breadboard.
TIP: Give the Canvas access code now.""",
}
