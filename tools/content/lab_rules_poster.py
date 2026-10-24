"""A4 wall poster for the shared electronics lab: general rules + tidy-up before leaving (not tied to one course).
Writes HCM/docs/Lab_rules_poster.pptx (editable); export the PDF with LibreOffice (see the end of this file)."""
import re
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

OUT = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/docs/Lab_rules_poster.pptx'
PHOTO = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/bench_tidy.jpg'
GREEN, LIGHT, DARK, GREY = RGBColor(0x54, 0x9E, 0x39), RGBColor(0xEE, 0xF6, 0xE8), RGBColor(0x1D, 0x2A, 0x17), RGBColor(0x55, 0x55, 0x55)
W, H, M = 8.27, 11.69, 0.5                      # A4 portrait, margin

SAFETY = [
    'Switch the power **off** before you change a circuit.',
    'Set the **current limit** on the DC power supply before you connect your circuit.',
    'Check **polarity** before you switch on: electrolytic capacitors, diodes, ICs, power supply.',
    'Never leave a **powered circuit** alone.',
    'Smell, smoke or a hot part? **Switch off at once** and call the lecturer.',
    'Never open an instrument or touch mains plugs and sockets.',
    'Know where the **main power switch** and the **fire extinguisher** are.',
    'No food or drinks on the benches.',
]
EQUIPMENT = [
    'Use only the bench you are given. Do not move instruments, cables or parts to another bench or out of the lab.',
    'Choose the right **multimeter mode and range** before you measure. Never measure **current or resistance** across a power source.',
    'Unplug cables by the plug, not the wire. Handle probes with care.',
    'Keep bags off the benches and the walkways clear.',
    'Something missing or broken? **Tell the lecturer.** Do not repair it yourself.',
]
LEAVE = [
    'Switch off **every instrument** and the trainer.',
    'Clear the breadboard: **no parts, no wires**.',
    'Parts back in the parts box, in the right bag. Used or broken parts in the bin.',
    'Test leads, probes and BNC cables into the box behind the trainer.',
    'Instruments back in place, **like the photo**. Chairs in, rubbish in the bin.',
    '**Wait for the lecturer** to check your bench before you go.',
]


def runs(p, text, size, color=DARK):
    for part in re.split(r'(\*\*.*?\*\*)', text):
        if part:
            r = p.add_run(); r.text = part.strip('*') if part.startswith('**') else part
            r.font.size = Pt(size); r.font.name = 'Arial'; r.font.color.rgb = color; r.font.bold = part.startswith('**')


def listing(p, numbered):
    """Real bullet / auto-number with a hanging indent (editable in PowerPoint)."""
    pPr = p._p.get_or_add_pPr(); pPr.set('marL', str(Inches(0.3))); pPr.set('indent', str(-Inches(0.3)))
    for tag in ('a:buClr', 'a:buFont', 'a:buChar', 'a:buAutoNum', 'a:buNone'):
        for el in pPr.findall(qn(tag)): pPr.remove(el)
    clr = etree.SubElement(pPr, qn('a:buClr')); etree.SubElement(clr, qn('a:srgbClr')).set('val', '549E39')
    if numbered:
        etree.SubElement(pPr, qn('a:buFont')).set('typeface', 'Arial')
        etree.SubElement(pPr, qn('a:buAutoNum')).set('type', 'arabicPeriod')
    else:
        etree.SubElement(pPr, qn('a:buFont')).set('typeface', 'Arial')
        etree.SubElement(pPr, qn('a:buChar')).set('char', '•')


def section(s, y, title, items, numbered=False, size=14.5, h=None):
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(M), Inches(y), Inches(W - 2 * M), Inches(0.36))
    bar.fill.solid(); bar.fill.fore_color.rgb = LIGHT; bar.line.fill.background(); bar.shadow.inherit = False
    tf = bar.text_frame; tf.margin_left = Inches(0.12); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.paragraphs[0].alignment = PP_ALIGN.LEFT; runs(tf.paragraphs[0], f'**{title}**', 17, GREEN)
    tb = s.shapes.add_textbox(Inches(M), Inches(y + 0.42), Inches(W - 2 * M), Inches(h or 2)); tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.1); tf.margin_top = Inches(0.02)
    for i, t in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        listing(p, numbered); runs(p, t, size); p.space_after = Pt(3)
    return tb


prs = Presentation(); prs.slide_width, prs.slide_height = Inches(W), Inches(H)
s = prs.slides.add_slide(prs.slide_layouts[6])
top = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.05))
top.fill.solid(); top.fill.fore_color.rgb = GREEN; top.line.fill.background(); top.shadow.inherit = False
tf = top.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; runs(p, '**ELECTRONICS LAB – RULES**', 30, RGBColor(0xFF, 0xFF, 0xFF))
sub = s.shapes.add_textbox(Inches(M), Inches(1.12), Inches(W - 2 * M), Inches(0.4)); p = sub.text_frame.paragraphs[0]
p.alignment = PP_ALIGN.CENTER; runs(p, 'This lab is shared by many classes. Leave your bench the way you want to find it.', 13, GREY)
p.runs[0].font.italic = True

section(s, 1.58, '1.  Safety', SAFETY, h=3.0)
section(s, 4.9, '2.  Equipment', EQUIPMENT, h=2.4)
section(s, 7.45, '3.  Before you leave', LEAVE, numbered=True, h=2.2)
pic = s.shapes.add_picture(PHOTO, Inches(M), Inches(9.72))
k = Inches(W - 2 * M) / pic.width; pic.width = int(pic.width * k); pic.height = int(pic.height * k)
if pic.top + pic.height > Inches(H - 0.25):                         # keep it on the page
    k = (Inches(H - 0.25) - pic.top) / pic.height; pic.height = int(pic.height * k); pic.width = int(pic.width * k)
    pic.left = int((prs.slide_width - pic.width) / 2)
prs.save(OUT); print('saved', OUT)
# PDF:  soffice --headless --convert-to pdf --outdir HCM/docs HCM/docs/Lab_rules_poster.pptx
