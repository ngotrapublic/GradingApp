from openpyxl import Workbook
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
F0=32352.84
wb=Workbook(); ws=wb.active; ws.title='Lab 2 data'
ws['A1']='Lab 2 – RLC frequency response'; ws['A1'].font=Font(bold=True,size=14)
ws['A2']='Variant:'; ws['B2'].fill=PatternFill('solid',fgColor='FFF2CC')
ws['A3']='Filter type:'; ws['B3'].fill=PatternFill('solid',fgColor='FFF2CC')
hdr=['f (kHz)','Vin p-p (V) – CH1','Vout p-p (V) – CH2','Vout / Vin']
for i,h in enumerate(hdr,1):
    c=ws.cell(5,i,h); c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='1F4E78'); c.alignment=Alignment(wrap_text=True,horizontal='center')
mult=[0.25,0.5,0.7,0.85,1,1.15,1.4,2,4]
thin=Side(style='thin',color='999999')
for r in range(6,26):
    if r-6 < len(mult): ws.cell(r,1,round(F0*mult[r-6]/1000,1))
    for c in (1,2,3): ws.cell(r,c).fill=PatternFill('solid',fgColor='FFF2CC')
    ws.cell(r,4,f'=IF(OR(B{r}="",C{r}=""),NA(),C{r}/B{r})').number_format='0.000'
    for c in range(1,5): ws.cell(r,c).border=Border(top=thin,bottom=thin,left=thin,right=thin)
ws['A27']='Rows 15–25: add extra points near the peak (any order is fine).'
ws['A29']='Conclusion (1–3 sentences):'; ws['A29'].font=Font(bold=True)
ws.merge_cells('A30:D34'); ws['A30'].fill=PatternFill('solid',fgColor='FFF2CC'); ws['A30'].alignment=Alignment(wrap_text=True,vertical='top')
for col,w in zip('ABCD',[12,16,16,12]): ws.column_dimensions[col].width=w
ch=ScatterChart(); ch.title='Frequency response'; ch.style=13
ch.x_axis.title='f (kHz, log scale)'; ch.y_axis.title='Vout / Vin'
ch.x_axis.scaling.logBase=10; ch.x_axis.scaling.min=5; ch.x_axis.scaling.max=200
ch.x_axis.delete=False; ch.y_axis.delete=False
s=Series(Reference(ws,min_col=4,min_row=6,max_row=25),Reference(ws,min_col=1,min_row=6,max_row=25),title='Vout/Vin')
s.marker.symbol='circle'; s.marker.size=7; s.graphicalProperties.line.noFill=True
ch.series.append(s); ch.legend=None; ch.width=18; ch.height=10
ws.add_chart(ch,'F5')
wb.save('/Users/mac/Tra/SE9_ElecCircuitLab/HCM/Lab2/Lab2_RLC_data_template.xlsx'); print('ok')
