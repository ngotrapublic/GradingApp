from PIL import Image
"""Export answer keys + display info for the grading web app (keys.json)."""
import json, runpy, os, shutil
W = os.path.dirname(os.path.abspath(__file__))
g = runpy.run_path(f'{W}/variants.py')
f = lambda r: f'{r/1000:g}k' if r >= 1000 else f'{r:g}'
ohm = lambda r: f'{round(r):,} Ω'.replace(',', ' ')
comb = lambda t: f'{f(t[2])}{" + " if t[1] == "+" else " // "}{f(t[3])}'
T2 = ['Low-pass (across C)', 'High-pass (across L)', 'Band-pass (across R)']
T4 = ['Stage 1 output, 1 kHz', 'Stage 2 output, 1 kHz', 'Stage 1 output, 5 kHz', 'Stage 2 output, 5 kHz']

labs = {
 '1': {'title': 'Lab 1 – Equivalent resistance', 'total': 12, 'manual': [],
       'questions': [['R_eq', 'R_eq', 'Ω', 3], ['Total current I', 'I', 'mA', 3], ['I_A', 'I_A', 'mA', 3], ['V_X', 'V_X', 'V', 3]], 'variants': {}},
 '2': {'title': 'Lab 2 – RC & RLC filters', 'total': 14, 'manual': [['graph', 'Graph + conclusion', [0, 1.5, 3], 'student']],
       'questions': [['Warm-up fc', 'fc (warm-up)', 'kHz', 2], ['R_total', 'R_total', 'Ω', 3], ['f_max', 'f_max', 'kHz', 3], ['Peak or BW', 'Peak Vout/Vin or BW', '–/kHz', 3]], 'variants': {}},
 '3': {'title': 'Lab 3 – Inverting amplifier', 'total': 14, 'manual': [],
       'questions': [['Gain from screen', 'Gain (screen)', '–', 3], ['R2/R1 used', 'R2/R1', '–', 3], ['Vout_pp measured', 'Vout pp', 'V', 4], ['Phase measured', 'Phase', '°', 4]], 'variants': {}},
 '4': {'title': 'Lab 4 – Microphone to speaker', 'total': 10, 'manual': [['demo', 'Team demo', [0, 2, 4], 'team']],
       'questions': [['Measured Vpp', 'Vpp', 'mV', 6]], 'variants': {}},
}
for k, d in g['D1'].items():
    labs['1']['variants'][k] = {'keys': [d['Req'], d['I'] * 1e3, d['IA'] * 1e3, d['VX']],
        'info': [f'R_A = {ohm(d["A"][0])} ({comb(d["A"])})', f'R_B = {ohm(d["B"][0])} ({comb(d["B"])})',
                 f'R_C = {ohm(d["C"][0])} ({comb(d["C"])})', f'R_D = {ohm(d["D"][0])} ({comb(d["D"])})']}
for k, d in g['D2'].items():
    third = d['third'] / (1e3 if d['type'] == 2 else 1)
    labs['2']['variants'][k] = {'keys': [d['fc'] / 1e3, d['Rtot'], d['fmax'] / 1e3, third],
        'info': [f'{T2[d["type"]]}, Q = {d["Q"]:g}', f'RC warm-up: {d["rc_kind"]}, R = {f(d["rc_r"])}Ω, C = {d["rc_c"]*1e9:g} nF',
                 'Last value: ' + ('bandwidth BW (kHz)' if d['type'] == 2 else 'peak Vout/Vin')]}
for k, d in g['D3'].items():
    labs['3']['variants'][k] = {'keys': [d['gain'], d['gain'], d['vout'], 180.0],
        'info': [f'R1 = {f(d["r1"])}Ω, R2 = {f(d["r2"])}Ω', f'Vin = {d["vin"]:g} Vpp, f = {d["f"]} Hz']}
for k, d in g['D4'].items():
    labs['4']['variants'][k] = {'keys': [d['vpp']], 'info': [f'Member {d["member"]}: {T4[d["member"] - 1]}', '10 mVpp input (High-Z), microphone and speaker disconnected']}
# student-facing card text (no answers) – written by make_labfiles.py
cards = json.load(open(f'{W}/cards.json', encoding='utf8'))
for lab, L_ in labs.items():
    for k, v in L_['variants'].items():
        v['card'] = cards[lab][str(k)]
# circuit figures shown with the card on the student page (generic, not secret)
FIG = f'{W}/fig'; SIMG = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/public/courses/SE009/img'
os.makedirs(SIMG, exist_ok=True)
for src, dst in [('d1_circuit.png', 'lab1_circuit.png'), ('d2_rc_lp.png', 'rc_lp.png'), ('d2_rc_hp.png', 'rc_hp.png'),
                 ('d2_lp.png', 'rlc_lp.png'), ('d2_hp.png', 'rlc_hp.png'), ('d2_bp.png', 'rlc_bp.png')]:
    shutil.copy(f'{FIG}/{src}', f'{SIMG}/{dst}')
Image.open(f'{W}/fig/hn_s3_final2_noc45.png').crop((0, 305, 1216, 790)).save(f'{SIMG}/lab4_circuit.png')   # HN final circuit v2 without the 12 V / 1 MΩ block and without C4, C5 (lab4_review.py)
for k in labs['1']['variants']: labs['1']['variants'][k]['figs'] = ['/courses/SE009/img/lab1_circuit.png']
for k, d in g['D2'].items():
    labs['2']['variants'][k]['figs'] = [f"/courses/SE009/img/rc_{'lp' if d['rc_kind'] == 'Low-pass' else 'hp'}.png",
                                        f"/courses/SE009/img/rlc_{['lp', 'hp', 'bp'][d['type']]}.png"]
for k in labs['4']['variants']: labs['4']['variants'][k]['figs'] = ['/courses/SE009/img/lab4_circuit.png']
shutil.copy(f'{FIG}/d3_inverting.png', f'{SIMG}/lab3_circuit.png')
for k in labs['3']['variants']: labs['3']['variants'][k]['figs'] = ['/courses/SE009/img/lab3_circuit.png']
for k in labs['3']['variants']: labs['3']['variants'][k]['image'] = f'lab3/v{k}.png'
labs['2']['files'] = [{'label': ['Excel template for your RLC data', 'File Excel mẫu để ghi số liệu RLC'], 'url': '/courses/SE009/files/Lab2_RLC_data_template.xlsx'}]
# Lab 3 oscilloscope screens for the student page
import shutil
img_dst = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/courses/SE009/assets/lab3'
os.makedirs(img_dst, exist_ok=True)
for k in labs['3']['variants']:
    shutil.copy(f'{W}/fig/lab3/v{k}.png', f'{img_dst}/v{k}.png')
from lab2_team import lab2_team, lab2_member4_rc, lab2_task1_design, lab2_task2_measure   # Lab 2: Task 1 design, Task 2 band-pass (team)
lab2_team(labs); lab2_member4_rc(labs); lab2_task1_design(labs); lab2_task2_measure(labs)
out = '/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/courses/SE009/keys.json'
json.dump({'labs': labs, 'rule': {'full': 0.10, 'half': 0.20}}, open(out, 'w'), ensure_ascii=False, indent=1)
print('keys ok', {k: len(v['variants']) for k, v in labs.items()})
