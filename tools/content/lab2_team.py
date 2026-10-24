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


def lab2_bandpass(labs):
    """Lecturer, 24/10/2026: Task 2 is band-pass for every team (output across R); Task 1 is "RC cut-off frequency", not a
    warm-up. Keys: R_total = Z0 / Q (unchanged), f_max = f0, last value = BW = f0 / Q. Question tokens stay the same
    (records already stored keep their meaning); only labels change. Safe to run again."""
    import math, re
    L2 = labs['2']; V = L2['variants']
    f0 = 1 / (2 * math.pi * math.sqrt(1e-3 * (22e-9 + 2.2e-9)))
    for v in V.values():
        Q = float(re.search(r'Q = ([0-9.]+)', v['info'][0]).group(1))
        v['keys'][2] = f0 / 1e3; v['keys'][3] = f0 / Q / 1e3
        v['info'][0] = f'Band-pass (across R), Q = {Q:g}'
        v['info'][2] = 'Last value: bandwidth BW (kHz)'
        v['info'][1] = v['info'][1].replace('RC warm-up:', 'RC (Task 1):')
        v['card'][1] = v['card'][1].replace('Warm-up: RC ', 'Task 1 – RC cut-off frequency: ')
        v['card'][2] = 'RLC (team – the same circuit for all members): Band-pass (output across R)'
        v['figs'][1] = v['figs'][1].rsplit('/', 1)[0] + '/rlc_bp.png'
    q = L2['questions']
    q[0][1] = 'fc (cut-off frequency)'
    q[2][1] = 'f_max (the peak, = f0)'
    q[3][1], q[3][2] = 'BW', 'kHz'
    L2['parts'][0]['title'] = ['Task 1 – RC cut-off frequency (individual)', 'Bài 1 – Tần số cắt mạch RC (làm cá nhân)']
    L2['parts'][1]['title'] = ['Task 2 – band-pass RLC filter (team – one circuit for the whole team)',
                               'Bài 2 – Bộ lọc thông dải RLC (làm nhóm – cả nhóm chung một mạch)']
    return labs
