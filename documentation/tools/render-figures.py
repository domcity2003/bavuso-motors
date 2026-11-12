"""Technical screening figure, Pillow only. Not measured motorcycle performance."""
from pathlib import Path
import csv
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'research/configuration-trades.csv').open(encoding='utf-8-sig')))
im=Image.new('RGB',(1500,1050),'#101923');d=ImageDraw.Draw(im)
fontpath=Path('C:/Windows/Fonts/arial.ttf')
def f(size): return ImageFont.truetype(str(fontpath),size)
d.text((65,45),'BAVUSO / MASS AND HIGHWAY RANGE',font=f(36),fill='#edf3f8')
d.text((65,98),'Conditional calculations at CdA 0.30 — not achieved specifications',font=f(24),fill='#efbd6b')
x0,x1,y0,y1=140,1400,185,770
def x(lb):return x0+(lb-330)/(510-330)*(x1-x0)
def y(mi):return y1-(mi-130)/(290-130)*(y1-y0)
d.rectangle((x0,y0,x(400),y(200)),fill='#152c2c')
for mass in range(340,511,20):
    d.line((x(mass),y0,x(mass),y1),fill='#293d4b',width=1)
    d.text((x(mass)-20,y1+12),str(mass),font=f(19),fill='#b7c9d6')
for miles in range(140,281,20):
    d.line((x0,y(miles),x1,y(miles)),fill='#293d4b',width=1)
    d.text((75,y(miles)-12),str(miles),font=f(19),fill='#b7c9d6')
d.line((x(400),y0,x(400),y1),fill='#f0c16b',width=3)
d.line((x0,y(200),x1,y(200)),fill='#f0c16b',width=3)
colors={'Reference allocations':'#74bce8','Focused mass target - unproven':'#81d4b7','Aggressive integration - unproven':'#cdaceb'}
for basis,color in colors.items():
    selected=[r for r in rows if r['basis']==basis and float(r['cda'])==.30]
    pts=[]
    for r in selected:
        # Coherent comparison: both mass and range include the same allowance.
        xx=x(float(r['bike_with_allowance_lb'])); yy=y(float(r.get('range_70_allowance_mass_mi',r['range_70_mi'])))
        pts.append((xx,yy));d.ellipse((xx-7,yy-7,xx+7,yy+7),fill=color)
        d.text((xx+12,yy-21),f"{r['parallel']}p",font=f(21),fill=color)
    d.line(pts,fill=color,width=3)
d.text((480,825),'Complete mass with model allowance (lb)',font=f(23),fill='#edf3f8')
d.text((65,155),'70 mph range (mi)',font=f(20),fill='#edf3f8')
for i,(label,color) in enumerate(colors.items()):
    yy=880+i*34
    d.line((65,yy+12,108,yy+12),fill=color,width=5);d.text((125,yy),label,font=f(22),fill=color)
d.text((65,1000),'100 series groups • typical cell energy • new battery • 90% energy availability • assumed road-load efficiency',font=f(18),fill='#aebfcc')
im.save(root/'visuals/configuration-trades.png')
print('Wrote documentation/visuals/configuration-trades.png')
