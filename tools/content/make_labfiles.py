import runpy, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from labfiles import build
g = runpy.run_path(os.path.dirname(__file__) + '/variants.py')
OUT = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM'
tmk = lambda k: ((k % 100 - 1) // 3 + 1, (k % 100 - 1) % 3 + 1) if k % 100 <= 18 else (k % 100 - 18, 4)
ohm = lambda r: f'{round(r):,} Ω'.replace(',', ' ')
f = lambda r: f'{r/1000:g}k' if r >= 1000 else f'{r:g}'

# ---------------- Lab 1 ----------------
Q1 = [('Variant number', 'Variant number (printed on your card)', '', 0, None),
      ('R_eq', 'R_eq – total resistance between the two supply nodes, supply disconnected. Unit: Ω (ohm). Numbers only.', 'Ω', 3, lambda d: d['Req']),
      ('Total current I', 'Total current I from the 5 V supply. Unit: mA. Numbers only.', 'mA', 3, lambda d: d['I'] * 1e3),
      ('I_A', 'I_A – current through R_A. Unit: mA. Numbers only.', 'mA', 3, lambda d: d['IA'] * 1e3),
      ('V_X', 'V_X – voltage at node X with respect to 0 V. Unit: V. Numbers only.', 'V', 3, lambda d: d['VX'])]
card1 = lambda c, d: [(f'Electric Circuit Lab – LAB 1   |   Variant {c}   |   Team {tmk(c)[0]} – Member {tmk(c)[1]}', True),
                      (f'R_A = {ohm(d["A"][0])}', True), (f'R_B = {ohm(d["B"][0])}', True), (f'R_C = {ohm(d["C"][0])}', True), (f'R_D = {ohm(d["D"][0])}', True),
                      ('Supply: 5.00 V (circuit on the slide)', False),
                      ('Make each resistor from 2 standard resistors (series/parallel).', False),
                      ('Submit R_eq, I, I_A, V_X + a photo of your circuit on the student page (QR).', False)]
comb = lambda t: f'{f(t[2])}{" + " if t[1] == "+" else " // "}{f(t[3])}'
key1 = [('R_A (Ω)', lambda d: round(d['A'][0])), ('Ghép R_A', lambda d: comb(d['A'])), ('R_B (Ω)', lambda d: round(d['B'][0])), ('Ghép R_B', lambda d: comb(d['B'])),
        ('R_C (Ω)', lambda d: round(d['C'][0])), ('Ghép R_C', lambda d: comb(d['C'])), ('R_D (Ω)', lambda d: round(d['D'][0])), ('Ghép R_D', lambda d: comb(d['D'])),
        ('R_eq (Ω)', lambda d: round(d['Req'])), ('I (mA)', lambda d: round(d['I'] * 1e3, 3)), ('I_A (mA)', lambda d: round(d['IA'] * 1e3, 3)), ('V_X (V)', lambda d: round(d['VX'], 3))]
build(1, 12, g['D1'], Q1, None, key1, [], f'{OUT}/Lab1')

# ---------------- Lab 2 ----------------
F0 = g['F0']; T = ['Low-pass (output across C)', 'High-pass (output across L)', 'Band-pass (output across R)']
flist = ', '.join(f'{F0 * m / 1000:.1f}' for m in [0.25, 0.5, 0.7, 0.85, 1, 1.15, 1.4, 2, 4])
Q2 = [('Variant number', 'Variant number (printed on your card)', '', 0, None),
      ('Warm-up fc', 'Warm-up fc – measured cut-off frequency of your RC filter. Unit: kHz. Numbers only.', 'kHz', 2, lambda d: d['fc'] / 1e3),
      ('R_total', 'R_total – measured DC resistance of your resistor R and the inductor in series. Unit: Ω. Numbers only.', 'Ω', 3, lambda d: d['Rtot']),
      ('f_max', 'f_max – frequency of maximum Vout/Vin. Unit: kHz. Numbers only.', 'kHz', 3, lambda d: d['fmax'] / 1e3),
      ('Peak or BW', 'Peak or BW – low-pass/high-pass: maximum value of Vout/Vin (no unit). Band-pass: bandwidth f_H − f_L in kHz. Numbers only.', '–/kHz', 3, lambda d: d['third'] / (1e3 if d['type'] == 2 else 1))]
def card2(c, d):
    cc = d['rc_c'] * 1e9
    return [(f'Electric Circuit Lab – LAB 2   |   Variant {c}   |   Team {tmk(c)[0]} – Member {tmk(c)[1]}', True),
            (f'Warm-up: RC {d["rc_kind"]}, R = {f(d["rc_r"])}Ω, C = {cc:g} nF', False),
            (f'RLC: {T[d["type"]]}', True), (f'Q = {d["Q"]:g}   (L = 1 mH, C = 22 nF ∥ 2.2 nF)', True),
            (f'Frequencies (kHz): {flist}', False),
            ('+ extra points near the peak.', False),
            ('Submit + a photo of your circuit on the student page (QR).', False)]
key2 = [('Cụm', lambda d: d['team']), ('Loại', lambda d: ['LP', 'HP', 'BP'][d['type']]), ('Q', lambda d: d['Q']),
        ('RC', lambda d: f'{d["rc_kind"][:4]} {f(d["rc_r"])}/{d["rc_c"]*1e9:g}n'), ('fc (kHz)', lambda d: round(d['fc'] / 1e3, 2)),
        ('R_total (Ω)', lambda d: round(d['Rtot'], 1)), ('f_max (kHz)', lambda d: round(d['fmax'] / 1e3, 2)),
        ('Peak Vout/Vin | BW (kHz)', lambda d: round(d['third'] / (1e3 if d['type'] == 2 else 1), 2))]
build(2, 14, g['D2'], Q2, None, key2, [('Đồ thị+kết luận', 3)], f'{OUT}/Lab2',
      guide_extra='\nLab 2: khi tick, xem luôn đồ thị + kết luận trên laptop SV và ghi 0 / 1.5 / 3 vào cột "Đồ thị+kết luận".')
print('ok')

# ---------------- Lab 4 ----------------
TASK = ['Vpp at the output of stage 1, f = 1 kHz', 'Vpp at the output of stage 2 (final output), f = 1 kHz', 'Vpp at the output of stage 1, f = 5 kHz', 'Vpp at the output of stage 2 (final output), f = 5 kHz']
Q4 = [('Variant number', 'Variant number (printed on your card)', '', 0, None),
      ('Measured Vpp', 'Measured Vpp – your individual measurement (see your card). Function generator 10 mVpp sine at the stage-1 input, electret disconnected. Unit: mVpp. Numbers only.', 'mVpp', 6, lambda d: d['vpp'])]
card4 = lambda c, d: [(f'Electric Circuit Lab – LAB 4   |   Variant {c}', True), (f'Team {d["team"]} – Member {d["member"]}', True),
                      ('Function generator: High-Z, 10 mVpp sine at the stage-1 input', False), ('Microphone and speaker disconnected.', False),
                      (f'Measure: {TASK[d["member"] - 1]}', True), ('Submit in mVpp + a photo of your circuit on the student page (QR).', False)]
key4 = [('Cụm', lambda d: d['team']), ('Thành viên', lambda d: d['member']), ('Đo', lambda d: TASK[d['member'] - 1]), ('Vpp (mV)', lambda d: round(d['vpp'], 1))]
build(4, 10, g['D4'], Q4, None, key4, [('Demo nhóm', 4)], f'{OUT}/Lab4',
      guide_extra='\nLab 4: cả cụm demo nói vào mic → GV nghe ở loa → ghi 0/2/4 vào cột "Demo nhóm" cho cả 3 SV. Tick cho từng SV khi xem số đo cá nhân.')

# ---------------- Lab 3 ----------------
import scope
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
IMG = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/lab3'
os.makedirs(IMG, exist_ok=True); os.makedirs(f'{OUT}/Lab3', exist_ok=True)
D3 = g['D3']
for k, d in D3.items():
    scope.draw(f'{IMG}/v{k}.png', d['vin'], d['vout'], d['f'], f'Lab 3 · Variant {k}', seed=k)
import textwrap, re
def card_pdf(lab, D, card_fn, img=None):
    for cls in (1, 2, 3):
        with PdfPages(f'{OUT}/Lab{lab}/HCM_Lab{lab}_Phieu_de_Lop{cls}.pdf') as pdf:
            pages = [(f'Team {t}', [(t, m) for m in (1, 2, 3)]) for t in range(1, 7)]
            pages += [('Member 4 (team of 4 only)', [(t, 4) for t in ts]) for ts in ((1, 2, 3), (4, 5, 6))]
            for title, cards in pages:
                fig = plt.figure(figsize=(8.27, 11.69))
                fig.text(0.06, 0.975, f'Electric Circuit Lab – LAB {lab}   |   Class {cls}   |   {title}', fontsize=13, weight='bold', va='top')
                for j_, (team, m) in enumerate(cards):
                    k = cls * 100 + (3 * (team - 1) + m if m <= 3 else 18 + team); d = D[k]; top = 0.94 - j_ * 0.315
                    fig.add_artist(plt.Rectangle((0.04, top - 0.3), 0.92, 0.3, transform=fig.transFigure, fill=False, ec='#999', lw=0.8))
                    lines = card_fn(k, d)
                    y = top - 0.015
                    for j, (t, bold) in enumerate(lines):
                        for part in textwrap.wrap(t, 95 if img else 80):
                            part = re.sub(r'(?<![A-Za-z0-9])([A-Za-z]{1,2})_([A-Za-z0-9]+)', r'$\1_{\2}$', part)
                            fig.text(0.06, y, part, fontsize=11.5 if j == 0 else (9 if img else 11), weight='bold' if bold else 'normal', va='top'); y -= (0.018 if img else 0.024)
                    if img:
                        ax = fig.add_axes([0.07, top - 0.295, 0.86, y - (top - 0.295) - 0.005]); ax.axis('off'); ax.imshow(plt.imread(img(k)))
                pdf.savefig(fig); plt.close(fig)
card_pdf(1, g['D1'], card1); card_pdf(2, g['D2'], card2); card_pdf(4, g['D4'], card4)
card3 = lambda k, d: [(f'Variant {k}   |   Team {d["team"]} – Member {d["member"]}', True),
                      ('Inverting amplifier, LM358, supply ±6 V. CH2 (blue) = input, CH1 (yellow) = output.', False),
                      ('Find R1 and R2, build the amplifier, make your screen look the same. Measure Vout,pp and the phase shift. Submit + a photo of your circuit on the student page (QR).', False)]
card_pdf(3, D3, card3, img=lambda k: f'{IMG}/v{k}.png')
Q3 = [('Variant number', 'Variant number (printed on your card)', '', 0, None),
      ('Gain from screen', 'Gain from screen – the gain you read from the oscilloscope screen on your card (positive number, no unit). Numbers only.', '–', 3, lambda d: d['gain']),
      ('R2/R1 used', 'R2/R1 used – ratio of the nominal values of the resistors you used (no unit). Numbers only.', '–', 3, lambda d: d['gain']),
      ('Vout_pp measured', 'Vout_pp measured – output amplitude on your oscilloscope. Unit: V (volt). Numbers only.', 'V', 4, lambda d: d['vout']),
      ('Phase measured', 'Phase measured – phase shift between output and input. Unit: degrees. Numbers only.', 'độ', 4, lambda d: 180.0)]
key3 = [('Cụm', lambda d: d['team']), ('TV', lambda d: d['member']), ('R1 / R2', lambda d: f'{f(d["r1"])} / {f(d["r2"])}'),
        ('Vin pp (V)', lambda d: d['vin']), ('f (Hz)', lambda d: d['f']), ('Gain', lambda d: round(d['gain'], 3)),
        ('Vout pp (V)', lambda d: round(d['vout'], 3)), ('Pha (°)', lambda d: 180)]
build(3, 14, D3, Q3, None, key3, [], f'{OUT}/Lab3',
      guide_extra='\nLab 3: phiếu đề có ảnh osci nên in từ file HCM_Lab3_Phieu_de_LopX.pdf (2 phiếu/trang A4, cắt theo đường gạch).')
print('lab3 ok')

# ---------------- card texts for the student web page (same text as the PDF cards) ----------------
import json as _json
_cards = {'1': {k: [t for t, _ in card1(k, d)] for k, d in g['D1'].items()},
          '2': {k: [t for t, _ in card2(k, d)] for k, d in g['D2'].items()},
          '3': {k: [t for t, _ in card3(k, d)] for k, d in D3.items()},
          '4': {k: [t for t, _ in card4(k, d)] for k, d in g['D4'].items()}}
_json.dump(_cards, open(os.path.dirname(os.path.abspath(__file__)) + '/cards.json', 'w'), ensure_ascii=False)
print('cards.json ok')
