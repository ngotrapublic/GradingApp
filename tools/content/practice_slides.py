"""Labs 2-4: short hands-on practice slides in the style of the Lab 1 deck (edited by hand on 24/10/2026):
"Exercise N: <what to do> (X minutes)" in Rockwell 16, numbered steps on the left, a figure or photo on the right, one
question at the end. Practice only, not marked. Demo values are not on any card and use parts the boxes have spare
(RC 10 kOhm + 104, RLC 1 mH + 104 + 100 Ohm; Lab 3 and Lab 4 use the circuits of the lab itself).
Each slide is placed after the slide that contains `after` (or before `before`); a figure is a file in fig/ or the
largest picture of the slide that contains a text. Running again replaces the practice slides.
Run after align_web.py and rlc_slides.py (align_web finds its slides by title, so it can run before or after)."""
import copy, io
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from lxml import etree

HCM = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM'
FIG = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/'
MARK = 'Practice Exercise'
MODEL = 'Devices and components for this session'
DARK = RGBColor(0x22, 0x22, 0x22)

LAB = {
2: [
    dict(after='Example of breadboard circuit', bar='1st order RC circuits', fig='p2_lp.png',
         head='Exercise 1: Build an RC low-pass filter and change the frequency (10 minutes)',
         steps=['Take R = 10 kΩ and C = 100 nF (code 104) from the parts box.',
                'Measure R with the multimeter. Write it down.',
                'Build the circuit. CH1 = Vin, CH2 = Vout (across C).',
                'Function generator: sine, 2 Vpp, High-Z.',
                'Set 10 Hz, 100 Hz, 200 Hz, 1 kHz, 10 kHz. Write what you see in the table (next slide).'],
         ask='What happens to Vout when the frequency goes up?',
         say='Now you build one. Use 10 kilo-ohm and the 104 capacitor, not the values in the picture. '
             'Keep the amplitude at 2 volts peak-to-peak and change only the frequency. Watch the output on channel 2.'),
    dict(after='Now do the same thing as before', bar='1st order RC circuits', fig='p2_hp.png',
         head='Exercise 2: Swap R and C – a high-pass filter (5 minutes)',
         steps=['Swap R and C: the capacitor is now in series, the resistor goes to ground.',
                'CH2 = Vout across R.',
                'Use the same frequencies: 10 Hz, 100 Hz, 200 Hz, 1 kHz, 10 kHz.',
                'Fill in the second table (next slide). Compare it with the first one.'],
         ask='Which frequencies pass now? Which are blocked?',
         say='Same parts, other places. The capacitor is in series and the resistor goes to ground. '
             'Use the same frequencies and compare with Exercise 1.'),
    dict(after='Cut-off frequency (fc) = where', bar='1st order RC circuits', fig='p2_lp.png',
         head='Exercise 3: Find the cut-off frequency of your low-pass filter (5 minutes)',
         steps=['Build the low-pass filter of Exercise 1 again.',
                'Calculate fc = 1 / (2πRC) with your measured R.',
                'Read Vin on CH1 (Measure → Pk-Pk).',
                'Change the frequency until Vout = 0.707 × Vin.',
                'This frequency is your measured fc.'],
         ask='How far is your fc from your calculation? Why are they different?',
         say='This is the method of Task 1. Find the frequency where the output is 0.707 times the input. '
             'In Task 1 you do the same with the R and C on your card.'),
    dict(after='Measuring capacitance with the multimeter', bar='Capacitors', fig='p2_capcode.png',
         head='Exercise 4: Read and measure capacitors (5 minutes)',
         steps=['Each member takes one capacitor from the parts box: 103, 223 or 473.',
                'Read the code. Write the value in nF.',
                'Set the multimeter to capacitance mode.',
                'Measure the capacitor. Write it down.',
                'Put the capacitor back in its bag.'],
         ask='How far is your reading from the code? Is it within 5%?',
         say='Each of you takes one capacitor. Read the code: two digits, then the number of zeros, in picofarads. '
             'Measure it, compare, and put it back in the right bag.'),
    dict(after='This is 0.33 mH in total', bar='Inductors', fig=('You will see them in many circuits',),
         head='Exercise 5: Measure the resistance of the 1 mH inductor (2 minutes)',
         steps=['Take the 1 mH inductor. It looks like a resistor: check the bag label.',
                'Set the multimeter to resistance (Ω).',
                'Measure the inductor. Write down RL.',
                'Put it back in its bag. You need it again in Task 2.'],
         ask='An ideal inductor has 0 Ω. Why does yours not?',
         say='The inductor is a long thin wire. Measure its resistance and write it down. You need this value in Task 2.'),
    dict(after='Real components at 32 kHz', bar='Series RLC – band-pass', fig='p2_rlc.png',
         head='Exercise 6: Find the peak of a band-pass RLC filter (10 minutes)',
         steps=['Take L = 1 mH, C = 100 nF (104) and R = 100 Ω.',
                'Calculate f0 = 1 / (2π√(LC)).',
                'Build the circuit. R at the ground side. CH1 = Vin, CH2 = Vout (across R).',
                'Function generator: sine, 2 Vpp, High-Z. Start at 5 kHz.',
                'Raise the frequency slowly to 30 kHz. Find the highest Vout / Vin.'],
         ask='Is your peak at f0? Why is the highest Vout / Vin below 1?',
         say='A practice band-pass with the 104 capacitor, so the peak is lower than in Task 2. '
             'Read Vin at every frequency, because it changes near the peak. Keep the 100 ohm resistor: you can use it in Task 2.'),
],
3: [
    dict(after='Vcc / Vee = the positive', bar='Overview of op amp', fig=('Vcc / Vee = the positive',),
         head='Exercise 1: Find the pins of the LM358 (2 minutes)',
         steps=['Find the notch or the dot on the LM358. Pin 1 is next to it.',
                'Count the pins anticlockwise, seen from the top: 1 to 8.',
                'Plug the IC across the middle gap of the breadboard.',
                'Show your teammates pin 8 (Vcc), pin 4 (Vee), pins 2 and 3 (inputs) and pin 1 (output).'],
         ask='Why must the IC sit across the middle gap?',
         say='Take your LM358. Find pin 1 next to the notch and count anticlockwise. Plug it across the middle gap.'),
    dict(after='Connect 6V to Vs+ pin', bar='Constructing first amplifier', fig=('Connect 6V to Vs+ pin',),
         head='Exercise 2: Power the LM358 safely (5 minutes)',
         steps=['Switch on the trainer. Set +6 V and −6 V. Check both with the multimeter.',
                'Switch off. Connect GND to the ground rail, +6 V to pin 8, −6 V to pin 4.',
                'Ask a teammate to check your wiring.',
                'Switch on. Measure pin 8 and pin 4 against GND.',
                'Touch the IC carefully: it must not get hot.'],
         ask='What do you measure on pin 4? Why is it negative?',
         say='Power first, signal later. Set plus and minus 6 volts, switch off, wire the supply, and let a teammate check it. '
             'Then switch on and measure at the pins.'),
    dict(after='Connect 6V to Vs+ pin', bar='Constructing first amplifier', fig='p3_follower.png',
         head='Exercise 3: A voltage follower (5 minutes)',
         steps=['Connect pin 1 (output) to pin 2 (− input).',
                'Function generator to pin 3 (+ input): sine, 1 Vpp, 1 kHz.',
                'CH2 = Vin (pin 3), CH1 = Vout (pin 1). Measure Pk-Pk of both.',
                'Remove the wire from pin 1 to pin 2 when you finish.'],
         ask='What is the gain? Is the output upside down?',
         say='The simplest op-amp circuit: one wire from the output to the minus input. Compare the two channels, '
             'then remove the wire. Next we build the inverting amplifier.'),
    dict(after='Measuring gain and phase', bar='Measuring gain and phase', fig=('Your circuit should look something like this',),
         head='Exercise 4: Build the first amplifier and measure its gain (10 minutes)',
         steps=['Build the inverting amplifier: R1 = 2.2 kΩ, R2 = 30 kΩ (3 × 10 kΩ), C1 = 1 µF.',
                'Add the decoupling capacitors: 470 µF on each rail, 100 nF at pins 8 and 4.',
                'Function generator: sine, 500 Hz, 50 mVpp (easier to read than 10 mVpp).',
                'CH2 = Vin, CH1 = Vout. Measure both (Pk-Pk). Gain = Vout / Vin.',
                'Use the cursors to read Δt between the waves. Phase = 360° × Δt × f.'],
         ask='Does your gain match R2 / R1? Is the phase 180°?',
         say='Build the amplifier from the slides. Measure the gain and the phase. This is how you measure in the Lab 3 exercise.'),
    dict(after='LM358 limits you will meet', bar='LM358 limits you will meet', fig='p3_clip.png',
         head='Exercise 5: Make the output clip (3 minutes)',
         steps=['Keep your amplifier from Exercise 4.',
                'Raise the input amplitude step by step: 0.2, 0.4, 0.6, 0.8 Vpp.',
                'Watch CH1: find when the tops of the wave become flat.',
                'Measure the highest and the lowest Vout (Measure → Max, Min).',
                'Set the input back to 50 mVpp.'],
         ask='Why can the output not reach +6 V and −6 V?',
         say='Make the input bigger until the output tops become flat. That is clipping. In your exercise, keep the output below this level.'),
],
4: [
    dict(after='Now connect the oscilloscope to the speaker and observe', bar='Testing 8-Ω speaker', fig=('Using normal 1X cable',),
         head='Exercise 1: Test the speaker with the function generator (5 minutes)',
         steps=['Measure the resistance of the speaker with the multimeter.',
                'Connect the function generator (1X cable) to the speaker with jumper wires.',
                'Function generator: sine, 0.5 Vpp, 500 Hz. Listen.',
                'Change the amplitude, then the frequency (200 Hz – 5 kHz). Listen.',
                'CH1 across the speaker: measure Pk-Pk.'],
         ask='The generator is set to 0.5 Vpp. Why is the voltage at the speaker much smaller?',
         say='Measure the speaker, then drive it from the generator. Listen to the pitch and the loudness. '
             'Then measure the voltage at the speaker and compare it with the generator setting.'),
    dict(after='The schematic circuit is something like this', bar='Testing 8-Ω speaker', fig=('The schematic circuit is something like this',),
         head='Exercise 2: A coupling capacitor in front of the speaker (5 minutes)',
         steps=['Function generator: sine, 1 Vpp, 500 Hz.',
                'Put a 100 nF capacitor in series with the speaker. Measure Pk-Pk at the speaker.',
                'Replace it with 1 µF, then with 470 µF (+ lead to the generator side).',
                'Listen and measure each time.'],
         ask='Which capacitor lets the most signal through? Why?',
         say='Try three capacitors in series with the speaker: 100 nanofarad, 1 microfarad and 470 microfarad. Listen and measure each one.'),
    dict(after='Watch out for the correct pin', bar='Testing only electret', fig=('Watch out for the correct pin',),
         head='Exercise 3: Find the ground pin of the microphone (2 minutes)',
         steps=['Set the multimeter to continuity mode.',
                'Touch the metal case of the microphone with one probe.',
                'Touch the male end of each jumper with the other probe.',
                'The one that beeps is the ground pin. It must be on the black jumper.'],
         ask='What happens if the microphone is connected the wrong way round?',
         say='Use the continuity mode. The pin connected to the metal case is ground. Check that it is the black jumper.'),
    dict(after='Then talk to the electret via a rolled', bar='Testing only electret', fig=('Electret test circuit on the PB-503A',),
         head='Exercise 4: See your voice on the oscilloscope (10 minutes)',
         steps=['Build the electret test circuit: bias resistor from +6 V, ground pin to GND.',
                'Connect CH1 after the 1 µF coupling capacitor.',
                'Set CH1 to 100 mV/div and the time base to 1 ms/div.',
                'Talk or hum into the microphone through a rolled piece of paper.',
                'Press Run/Stop to freeze the wave. Measure Pk-Pk.'],
         ask='How big is your signal? Is it big enough for the speaker?',
         say='Build the test circuit and look at your voice on channel 1. Freeze the screen and read the peak-to-peak value.'),
    dict(before='Measurement at oscilloscope', bar='Constructing second amplifier', fig=('Measurement at oscilloscope', -1),
         head='Exercise 5: Test both stages with the generator first (10 minutes)',
         steps=['Do not connect the microphone yet.',
                'Function generator to the input of stage 1: sine, 10 mVpp, 1 kHz.',
                'CH1 = output of stage 1, CH2 = output of stage 2.',
                'Both outputs must be clean sine waves: no clipping, no noise.',
                'Only then connect the microphone and the speaker.'],
         ask='Why do we test with the generator before we use the microphone?',
         say='Test each stage with a known signal first. If both outputs look clean, connect the microphone and the speaker.'),
],
}


def text_of(s):
    out = []
    for sh in s.shapes:
        if sh.has_text_frame:
            out.append(sh.text_frame.text)
    return '\n'.join(out)


def find(p, snippet):
    hits = [s for s in p.slides if snippet in text_of(s) and not is_practice(s)]
    if len(hits) > 1:                                  # the same words in a title and in a review slide: take the title
        hits = [s for s in hits if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == snippet for sh in s.shapes)]
    assert len(hits) == 1, (snippet, len(hits))
    return hits[0]


def is_practice(s):
    return any(sh.name == MARK for sh in s.shapes)


def picture(p, spec):
    """('text',) = largest picture on the slide with that text; ('text', -1) = on the slide before it."""
    s = find(p, spec[0])
    if len(spec) > 1:
        slides = list(p.slides); s = slides[slides.index(s) + spec[1]]
    pics = [sh for sh in s.shapes if sh.shape_type == 13 and not sh.name.startswith('Logo') and sh.width > Inches(2.2)]
    best = max(pics, key=lambda sh: sh.width * sh.height)
    return io.BytesIO(best.image.blob), best.image.size


def textbox(s, x, y, w, h, name=None):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    return tf


def run_(para, text, size=16, color=DARK):
    r = para.add_run(); r.text = text
    r.font.size = Pt(size); r.font.name = 'Rockwell'; r.font.color.rgb = color
    return r


def numbered(para):
    pPr = para._p.get_or_add_pPr(); pPr.set('marL', '457200'); pPr.set('indent', '-317500')
    for tag in ('a:buFont', 'a:buAutoNum'):
        el = pPr.find(qn(tag))
        if el is not None:
            pPr.remove(el)
    etree.SubElement(pPr, qn('a:buFont')).set('typeface', '+mj-lt')
    etree.SubElement(pPr, qn('a:buAutoNum')).set('type', 'arabicPeriod')


def add(p, model, ex):
    s = p.slides.add_slide(model.slide_layout)
    for sh in model.shapes:
        if sh.name == 'Title Bar':
            s.shapes._spTree.append(copy.deepcopy(sh._element)); bar = s.shapes[-1]
            bar.text_frame.paragraphs[0].runs[0].text = ex['bar']
            for r in bar.text_frame.paragraphs[0].runs[1:]: r._r.getparent().remove(r._r)
        elif sh.name.startswith('Logo'):
            s.shapes.add_picture(io.BytesIO(sh.image.blob), sh.left, sh.top, sh.width, sh.height)
    tf = textbox(s, 0.6, 1.45, 7.3, 0.45, MARK); run_(tf.paragraphs[0], ex['head'])
    tf = textbox(s, 0.65, 2.15, 7.0, 3.4)
    for i, t in enumerate(ex['steps']):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); numbered(para); run_(para, t)
        para.space_after = Pt(6)
    tf = textbox(s, 0.65, 5.75, 7.0, 0.8); run_(tf.paragraphs[0], ex['ask'])
    # figure on the right, fitted into the free area, top-aligned like the Lab 1 slides
    if isinstance(ex['fig'], str):
        from PIL import Image
        src = FIG + ex['fig']; size = Image.open(src).size
    else:
        src, size = picture(p, ex['fig'])
    bx, by, bw, bh = 8.0, 1.2, 5.0, 5.8
    k = min(bw / size[0], bh / size[1]); w, h = size[0] * k, size[1] * k
    s.shapes.add_picture(src, Inches(bx + (bw - w) / 2), Inches(by + (0 if h > 3.5 else (bh - h) / 3)), Inches(w), Inches(h))
    s.notes_slide.notes_text_frame.text = ex['say']
    return s


def run():
    for n, exercises in LAB.items():
        path = f'{HCM}/Lab{n}/HCM Electronic Circuit Lab {n}.pptx'
        p = Presentation(path); lst = p.slides._sldIdLst
        for sid, sl in reversed(list(zip(list(lst), list(p.slides)))):
            if is_practice(sl):
                p.part.drop_rel(sid.rId); lst.remove(sid)
        p.part.rename_slide_parts([x.rId for x in lst])
        model = next(s for s in p.slides if any(sh.name == 'Title Bar' and sh.text_frame.text.strip() == MODEL for sh in s.shapes))
        last = {}                                         # anchor -> the slide placed after it most recently
        for ex in exercises:
            anchor = ex.get('after') or ex['before']
            ref = last.get(anchor) or find(p, anchor)
            s = add(p, model, ex)
            slides = list(p.slides); sid = lst[-1]; lst.remove(sid)
            pos = slides.index(ref) + (1 if ('after' in ex or anchor in last) else 0)
            lst.insert(pos, sid); last[anchor] = s
        p.save(path)
        where = [i + 1 for i, s in enumerate(p.slides) if is_practice(s)]
        print(f'Lab {n}: {len(p.slides)} slides; exercises at {where}')


if __name__ == '__main__':
    run()
