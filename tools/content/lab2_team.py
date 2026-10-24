"""Lab 2, Task 2 (RLC) is team work: every member gets the RLC part (filter type, Q, frequencies, answer keys,
figure) of one member of the team. The member rotates with the team number so that teams 1 and 4 build a
low-pass, teams 2 and 5 a high-pass, teams 3 and 6 a band-pass filter. Task 1 (RC warm-up) stays individual.
Must be applied to the original per-member variants."""


def lab2_team(labs, sets=(1, 2, 3)):
    V = labs['2']['variants']
    for s in sets:
        for t in range(1, 7):
            team = [s * 100 + 3 * (t - 1) + m for m in (1, 2, 3)] + [s * 100 + 18 + t]
            lead = dict(V[str(team[(t - 1) % 3])])
            lead_card = list(lead['card'])
            lead_card[2] = lead_card[2].replace('RLC:', 'RLC (team – the same circuit for all members):')
            lead_card[5] = '+ at most 2 extra points near the peak.'
            for v in team:
                m = V[str(v)]
                m['keys'][1:4] = lead['keys'][1:4]
                m['info'][0], m['info'][2] = lead['info'][0], lead['info'][2]
                m['card'][2:6] = lead_card[2:6]
                m['figs'][1] = lead['figs'][1]
    return labs


def lab2_member4_rc(labs, sets=(1, 2, 3)):
    """Task 1 (RC warm-up) is individual: member 4 of a team of 4 must not share the RC circuit of a teammate.
    Gives member 4 the first (type, R, C) whose cut-off frequency is at least 25 % away from every teammate's."""
    import math
    V = labs['2']['variants']
    opts = [(kind, r, c) for kind in ('Low', 'High') for r in ('1k', '2.2k', '4.7k') for c in (10, 22, 47)]
    fc = lambda r, c: 1 / (2 * math.pi * float(r[:-1]) * 1e3 * c * 1e-9) / 1e3
    for s in sets:
        for t in range(1, 7):
            mates = [V[str(s * 100 + 3 * (t - 1) + m)] for m in (1, 2, 3)]
            used = [m['keys'][0] for m in mates]
            m4 = V[str(s * 100 + 18 + t)]
            if all(abs(m4['keys'][0] / u - 1) >= 0.25 for u in used):
                continue
            start = (s * 6 + t) % len(opts)                         # vary the choice between teams
            for kind, r, c in opts[start:] + opts[:start]:
                f = fc(r, c)
                if all(abs(f / u - 1) >= 0.25 for u in used):
                    m4['keys'][0] = f
                    m4['info'][1] = f'RC (Task 1): {kind}-pass, R = {r}Ω, C = {c} nF'
                    m4['card'][1] = f'Task 1 – RC cut-off frequency: {kind}-pass, R = {r}Ω, C = {c} nF'
                    m4['figs'][0] = m4['figs'][0].rsplit('/', 1)[0] + ('/rc_lp.png' if kind == 'Low' else '/rc_hp.png')
                    break
    return labs


TASK2 = [(10e-9, 100), (22e-9, 100), (47e-9, 100), (10e-9, 220), (22e-9, 220), (47e-9, 220)]   # (C, R) per team, L = 1 mH


def lab2_task2_measure(labs, sets=(1, 2, 3)):
    """Lecturer, 24/10/2026: Task 2 = measure a band-pass RLC filter, the same as Exercises 6-7, with the team's own C and R
    (one capacitor, one resistor; L = 1 mH): no design, no Q, no capacitors in parallel. The team submits f0 (4 marks) and
    BW (5 marks, tolerance 20 % / 35 %); keys f0 = 1/(2π√(LC)), BW = R/(2πL) (the coil wire R_L is ignored).
    Each class: the 6 teams get the 6 (C, R) pairs, rotated by class. 9 frequencies on the card around f0.
    Sets the final Lab 2 question list: [C (Task 1), f0, BW, R (Task 1)] and keys [target fc, f0, BW, 0]."""
    import math
    L2 = labs['2']; V = L2['variants']; L = 1e-3
    for s in sets:
        for t in range(1, 7):
            C, R = TASK2[(t - 1 + 2 * s) % 6]
            f0 = 1 / (2 * math.pi * math.sqrt(L * C)) / 1e3; bw = R / (2 * math.pi * L) / 1e3
            freqs = ', '.join(f'{f0 * k:.1f}' for k in (0.25, 0.4, 0.6, 0.8, 1.0, 1.25, 1.6, 2.5, 4.0))
            for m in (1, 2, 3, 4):
                v = V.get(str(s * 100 + 3 * (t - 1) + m if m < 4 else s * 100 + 18 + t))
                if v is None:
                    continue
                v['keys'] = [v['keys'][0], f0, bw, 0]
                v['info'][0] = f'Band-pass (across R): C = {C * 1e9:g} nF, R = {R} Ω (f0 = {f0:.2f} kHz, BW = {bw:.2f} kHz)'
                v['info'][2] = 'Task 2: f0 and BW (kHz)'
                v['card'][2:6] = ['RLC (team – the same circuit for all members): Band-pass (output across R)',
                                  f'L = 1 mH, C = {C * 1e9:g} nF, R = {R} Ω',
                                  f'Frequencies (kHz): {freqs}',
                                  '+ at most 2 extra points near the peak.']
                v['figs'][1] = v['figs'][1].rsplit('/', 1)[0] + '/rlc_bp.png'
    L2['questions'] = [['Warm-up fc', 'C you chose (Task 1)', 'nF', 2, {'full': 0.05, 'half': 0.12, 'calc': 'rc_fc', 'from': 3}],
                       ['f0', 'f0 (the peak frequency)', 'kHz', 4],
                       ['BW', 'BW = fH − fL', 'kHz', 5, {'full': 0.2, 'half': 0.35}],
                       ['Task 1 R', 'R you chose (Task 1)', 'Ω', 0]]
    L2['parts'][0]['questions'] = [3, 0]
    L2['parts'][1]['questions'] = [1, 2]
    L2['parts'][0]['title'] = ['Task 1 – RC cut-off frequency (individual)', 'Bài 1 – Tần số cắt mạch RC (làm cá nhân)']
    L2['parts'][1]['title'] = ['Task 2 – band-pass RLC filter (team – one circuit for the whole team)',
                               'Bài 2 – Bộ lọc thông dải RLC (làm nhóm – cả nhóm chung một mạch)']
    L2['parts'][1]['note'] = ['The whole team builds the same band-pass filter (L, C, R on the card), measures the frequencies on the card, '
                              'finds the peak f0 and the bandwidth BW (as in Exercise 7). Each student types the team values and uploads the graph.',
                              'Cả nhóm lắp cùng một mạch thông dải (L, C, R trên đề), đo các tần số trên đề, tìm đỉnh f0 và băng thông BW '
                              '(như Exercise 7). Mỗi SV tự nhập số của nhóm và tải ảnh đồ thị.']
    return labs


TASK1_TARGETS = [0.5, 0.75, 1.0, 1.5, 3.5, 5.0, 7.5, 10.0, 15.0]     # kHz; each has an R, C pair within 3.5 % (see below)
TASK1_R = [220, 330, 470, 680, 1000, 1500, 2200, 3300, 4700, 6800, 10000, 15000, 22000]
TASK1_C = [10e-9, 22e-9, 47e-9]


def lab2_task1_design(labs, sets=(1, 2, 3)):
    """Lecturer, 24/10/2026 (option A): Task 1 is a design. The card gives the filter type and a target cut-off frequency;
    the student chooses R (13 standard values) and C (10, 22 or 47 nF), builds the filter and checks fc on the scope.
    The student submits R and C; marks come from fc = 1/(2πRC) vs the target (key).
    Members 1-3 of a team get 3 neighbouring targets of the list (always >= 25 % apart), member 4 is 4 places further.
    Low-pass / high-pass alternate. Tolerance: full 5 %, half 12 % (the best pair is always within 3.5 %)."""
    import math
    V = labs['2']['variants']; n = len(TASK1_TARGETS)
    fc = lambda r, c: 1 / (2 * math.pi * r * c)
    for s in sets:
        for t in range(1, 7):
            for m in (1, 2, 3, 4):
                v = V.get(str(s * 100 + 3 * (t - 1) + m if m < 4 else s * 100 + 18 + t))
                if v is None:
                    continue
                k = (s * 5 + (t - 1) * 3 + (m - 1 if m < 4 else 4)) % n
                target = TASK1_TARGETS[k]; kind = ('Low', 'High')[(t + m) % 2]
                f, r, c = min(((fc(r, c), r, c) for r in TASK1_R for c in TASK1_C), key=lambda x: abs(x[0] / (target * 1e3) - 1))
                rs = f'{r / 1000:g} kΩ' if r >= 1000 else f'{r} Ω'
                v['keys'][0] = target
                v['info'][1] = (f'RC (Task 1): {kind}-pass, target fc = {target:g} kHz '
                                f'(closest: {rs} + {c * 1e9:g} nF = {f / 1e3:.3g} kHz)')
                v['card'][1] = (f'Task 1 – RC cut-off frequency: design a {kind.lower()}-pass filter with fc = {target:g} kHz. '
                                f'Choose R (220 Ω … 22 kΩ) and C (10, 22 or 47 nF). Submit the R and C you chose.')
                v['figs'][0] = v['figs'][0].rsplit('/', 1)[0] + ('/rc_lp.png' if kind == 'Low' else '/rc_hp.png')
    # the student submits R and C (the design); marks from fc = 1/(2πRC) vs the target. Question layout: lab2_task2_measure.
    labs['2']['parts'][0]['note'] = ['Design: choose R and C for the target fc on your card. Submit the R and C you chose (the printed values). '
                                     'Marks: fc = 1/(2πRC) within ±5 % of the target (half: ±12 %). The lecturer checks fc on your oscilloscope.',
                                     'Thiết kế: chọn R và C cho f_c mục tiêu trên đề. Nộp R và C đã chọn (giá trị in trên linh kiện). '
                                     'Điểm: f_c = 1/(2πRC) lệch ≤ ±5 % so với mục tiêu (nửa điểm: ±12 %). Giảng viên kiểm tra f_c trên osci.']
    return labs
