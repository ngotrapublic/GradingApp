import schemdraw, schemdraw.elements as elm, matplotlib
matplotlib.use('Agg')
schemdraw.config(fontsize=16, lw=2)
F='/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/'
E={'R':lambda: elm.Resistor(), 'L':lambda: elm.Inductor2(loops=3), 'C':lambda: elm.Capacitor()}
LBL={'R':'$R$', 'L':'$L$', 'C':'$C$'}
for name, seq, title in [('d2_lp',['R','L','C'],'Low-pass: output across C'),('d2_hp',['R','C','L'],'High-pass: output across L'),('d2_bp',['L','C','R'],'Band-pass: output across R')]:
    with schemdraw.Drawing(file=F+name+'.png', dpi=200, show=False) as d:
        elm.SourceSin().up().length(3).label('$V_{in}$\n(CH1)', loc='bottom', ofst=0.3)
        E[seq[0]]().right().length(3).label(LBL[seq[0]])
        E[seq[1]]().right().length(3).label(LBL[seq[1]])
        top=d.here
        elm.Line().right(0.5)
        E[seq[2]]().down().length(3).label(LBL[seq[2]], loc='bottom')
        elm.Line().left(6.5)
        elm.Line().at(top).right(2.5); elm.Dot(open=True).label('$V_{out}$ (CH2)', loc='right')
        elm.Line().at((6.5,0)).right(2.0); elm.Dot(open=True)
        elm.Ground().at((0,0))
        elm.Label().at((4.5,4.4)).label(title)
for name, kind in [('d2_rc_lp','lp'),('d2_rc_hp','hp')]:
    with schemdraw.Drawing(file=F+name+'.png', dpi=200, show=False) as d:
        elm.SourceSin().up().length(3).label('$V_{in}$', loc='bottom', ofst=0.3)
        (elm.Resistor() if kind=='lp' else elm.Capacitor()).right().length(3).label('$R$' if kind=='lp' else '$C$')
        top=d.here; elm.Dot()
        (elm.Capacitor() if kind=='lp' else elm.Resistor()).down().length(3).label('$C$' if kind=='lp' else '$R$', loc='bottom')
        elm.Line().left(3)
        elm.Line().at(top).right(2); elm.Dot(open=True).label('$V_{out}$', loc='right')
        elm.Line().at((3,0)).right(2); elm.Dot(open=True)
        elm.Ground().at((0,0))
print('ok')
