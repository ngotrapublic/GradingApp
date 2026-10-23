import schemdraw, schemdraw.elements as elm, matplotlib
matplotlib.use('Agg')
schemdraw.config(fontsize=16, lw=2)
F='/Users/mac/Tra/SE9_ElecCircuitLab/HCM/GradingApp/tools/content/fig/'
with schemdraw.Drawing(file=F+'d4_loading.png', dpi=200, show=False) as d:
    elm.SourceV().up().length(3).label('$V_{in}$', loc='bottom', ofst=0.3)
    elm.Resistor().right(3).label('$R_1$')
    top=d.here; elm.Dot()
    elm.Resistor().down(3).label('$R_2$', loc='bottom')
    elm.Line().left(3)
    elm.Line().at(top).right(3)
    elm.Resistor().down(3).label('$R_{load}$\n(next stage)', loc='bottom').color('#C00000')
    elm.Line().left(3)
    elm.Ground().at((0,0))
    elm.Label().at((3.2,3.5)).label('$V_{out}$')
print('ok')
