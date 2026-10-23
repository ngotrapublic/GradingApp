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
