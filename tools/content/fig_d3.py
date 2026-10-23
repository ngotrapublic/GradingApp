import schemdraw, schemdraw.elements as elm, matplotlib
matplotlib.use('Agg')
schemdraw.config(fontsize=16, lw=2)
F='/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/'
with schemdraw.Drawing(file=F+'d3_decouple.png', dpi=200, show=False) as d:
    elm.Line().at((0,6)).right(9); elm.Label().at((-0.4,6)).label('+6 V', loc='left', halign='right')
    elm.Line().at((0,3)).right(9); elm.Label().at((-0.4,3)).label('GND', loc='left', halign='right')
    elm.Line().at((0,0)).right(9); elm.Label().at((-0.4,0)).label('−6 V', loc='left', halign='right')
    elm.Capacitor(polar=True).at((2,6)).down().length(3).label('470 µF', loc='bottom')
    elm.Capacitor(polar=True).at((2,3)).down().length(3).label('470 µF', loc='bottom')
    elm.Capacitor().at((6,6)).down().length(3).label('100 nF', loc='bottom')
    elm.Capacitor().at((6,3)).down().length(3).label('100 nF', loc='bottom')
    for x in (2,6):
        for y in (6,3,0): elm.Dot().at((x,y))
    elm.Label().at((2,6.6)).label('at the trainer', fontsize=14)
    elm.Label().at((6,6.6)).label('next to the LM358', fontsize=14)
print('ok')
