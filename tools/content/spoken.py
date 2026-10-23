"""Convert SAY/DO/ASK/TIP/WORD scripts into spoken-only text for the lecturer."""
import re

DO = {
 'DO: Show the PB-503A, point to the breadboard, the supply outputs and the speaker.': 'Look at the PB-503A on your bench. Here is the breadboard, here are the supply outputs, and here is the speaker.',
 'DO: Show the multimeter. Point to the dial, the screen and the three sockets.': 'Look at the multimeter: the dial, the screen and the three sockets.',
 'DO: Read one resistor together with the students using the table.': "Let's read one resistor together with this table.",
 'DO: Set the multimeter to Ω. Touch both ends of a resistor. Do not touch the metal with your fingers.': 'Set your multimeter to Ω. Touch both ends of a resistor. Do not touch the metal with your fingers.',
 'DO: Ask every student to measure one resistor and compare with the color code.': 'Now everyone: measure one resistor and compare it with the color code.',
 'DO: Show the beep with a jumper wire.': 'Listen: when I touch both ends of a jumper wire, the meter beeps.',
 'DO: Each student checks one LED.': 'Now everyone: check one LED.',
 'DO: Measure the output of the power supply. Red probe on +, black probe on −.': 'Measure the output of the power supply. Red probe on plus, black probe on minus.',
 'DO: Set 5 V and a current limit of 0.1 A. Measure the output with the multimeter.': 'Set 5 volts and a current limit of 0.1 amp. Measure the output with the multimeter.',
 'DO: Let each team change the voltage and measure it.': 'Now each team: change the voltage and measure it.',
 'DO: Point to the long lines (supply rails) and the short lines.': 'Look at the long lines, the supply rails, and the short lines.',
 'DO: Turn the vertical scale knob and the position knob. Show how the wave changes.': 'Turn the vertical scale knob and the position knob. Watch how the wave changes.',
 'DO: Show the horizontal scale (time per division) and the trigger level.': 'This is the horizontal scale, time per division. And this is the trigger level.',
 'DO: Every team presses Default Setup now.': 'Every team: press Default Setup now.',
 'DO: Walk around and help teams.': 'Raise your hand if you need help.',
 'DO: Connect the 10X probe to channel 1 and to the test signal output. Press Autoset.': 'Connect the 10X probe to channel 1 and to the test signal output. Press Autoset.',
 'DO: Every team does this now.': 'Every team: do this now.',
 'DO: Connect the function generator to channel 1 with the BNC cable. Set a 10 Vpp, 5 kHz sine. Turn on the output.': 'Connect the function generator to channel 1 with the BNC cable. Set a 10 volt peak-to-peak, 5 kilohertz sine wave. Turn on the output.',
 'DO: Display channel 1. Check that Run is green. Press Autoset.': 'Display channel 1. Check that Run is green. Press Autoset.',
 'DO: Each student builds this voltage divider with 2.2 kΩ and 4.7 kΩ at 5 V.': 'Everyone: build this voltage divider with 2.2 kilo-ohm and 4.7 kilo-ohm, at 5 volts.',
 'DO: Now build the current divider with the same resistors. They are now in parallel.': 'Now build the current divider with the same resistors. They are now in parallel.',
 'DO: Measure the current in each branch and the total current.': 'Measure the current in each branch and the total current.',
 'DO: Give 10 minutes. Then show the solution.': 'You have 10 minutes. Then I will show you one solution.',
 'DO: Give out the variant cards now. Check that each student writes their name on the card.': 'I will give you your variant cards now. Write your name on your card.',
 'DO: Give 3 minutes for teams to set up the instruments.': 'You have 3 minutes to set up your instruments.',
 'DO: Set the function generator: 10 Vpp sine. Measure the input on channel 1.': 'Set the function generator to a 10 volt peak-to-peak sine wave. Measure the input on channel 1.',
 'DO: Fill this table together: change the frequency, read Vout.': "Let's fill this table together: change the frequency and read Vout.",
 'DO: Fill the second table.': 'Now fill the second table.',
 'DO: Solve it on the board, step by step.': "Let's solve it on the board, step by step.",
 'DO: Give the variant cards now.': 'I will give you your variant cards now.',
 'DO: Each student measures their 22 nF and 2.2 nF capacitors.': 'Now everyone: measure your 22 nanofarad and 2.2 nanofarad capacitors.',
 "DO: Check each student's calculation before they build.": 'Show me your calculation before you build.',
 'DO: Show where the notch or dot is on the chip. Pin 1 is next to it.': 'Look at the small notch or dot on the chip. Pin 1 is next to it.',
 "DO: Check each team's supply before they put the chip in.": 'Show me your supply voltages before you put the chip in.',
 'DO: Walk around and check the circuits before students switch on.': 'Do not switch on yet. I will check your circuit first.',
 'DO: Show the cursors on the oscilloscope: measure Δt between the two waves. Phase = 360 × Δt × f.': 'Use the cursors on the oscilloscope. Measure delta t between the two waves. Phase equals 360 times delta t times f.',
 'DO: Give out the variant cards (from the PDF).': 'I will give you your variant cards now.',
 'DO: Find the speaker on the PB-503A. Measure its resistance with the multimeter.': 'Find the speaker on the PB-503A. Measure its resistance with the multimeter.',
 'DO: Connect the function generator directly to the speaker with the 1X cable. Connect the oscilloscope too.': 'Connect the function generator directly to the speaker with the 1X cable. Connect the oscilloscope too.',
 'DO: Let students change amplitude and frequency.': 'Now change the amplitude and the frequency. Listen.',
 'DO: Look at the signal on the speaker with the oscilloscope.': 'Look at the signal on the speaker with the oscilloscope.',
 'DO: Check the microphone polarity in every team.': 'Show me your microphone pins before you switch on.',
 'DO: Connect the output to the speaker. Talk into the microphone. Look at the speaker signal.': 'Connect the output to the speaker. Talk into the microphone. Look at the speaker signal.',
 'DO: You can try 470 µF instead of 1 µF. You will still hear almost nothing.': 'You can try 470 microfarad instead of 1 microfarad. You will still hear almost nothing.',
 'DO: Connect the final output to the speaker. Try with and without 470 µF before the speaker.': 'Connect the final output to the speaker. Try with and without 470 microfarad before the speaker.',
 'DO: Disconnect the function generator. Connect the microphone circuit to the amplifier through 1 µF. Connect the output to the speaker.': 'Disconnect the function generator. Connect the microphone circuit to the amplifier through 1 microfarad. Connect the output to the speaker.',
 'DO: Try with 1 µF first. Does it die out? Then try 10 µF or 470 µF.': 'Try with 1 microfarad first. Does it die out? Then try 10 or 470 microfarad.',
}


def spoken(text):
    out = []
    for l in text.split('\n'):
        l = l.strip()
        if not l or l.startswith('TIP:'):
            continue
        if l.startswith('SAY:'):
            out.append(l[4:].strip())
        elif l.startswith('DO:'):
            if l not in DO:
                raise KeyError(l)
            out.append(DO[l])
        elif l.startswith('ASK:'):
            q = l[4:].strip()
            m = re.match(r'(.*?)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$', q)
            if m and m.group(1).rstrip().endswith(('?', '.')):
                out.append(m.group(1).strip())
                a = m.group(2).strip().rstrip('.')
                out.append(f'… The answer is: {a[0].lower() + a[1:] if a[:1].isupper() and not a[:2].isupper() else a}.')
            else:
                out.append(q)
        elif l.startswith('WORD:'):
            w = l[5:].strip()
            term, _, meaning = w.partition(' = ')
            out.append(f'New word: {term}. {term} means: {meaning}. Say it with me: {term}.')
        else:
            out.append(l)
    return re.sub(r'(?<![A-Za-z0-9])([A-Za-z]{1,2})_([A-Za-z0-9]+)', r'\1 \2', '\n'.join(out))
