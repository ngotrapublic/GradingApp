import sys,glob
from PIL import Image, ImageDraw
d,out,sel=sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else ''
fs=sorted(glob.glob(d+'/s-*.jpg'))
if sel: idx=[int(x) for x in sel.split(',')]; fs=[fs[i-1] for i in idx]
else: idx=list(range(1,len(fs)+1))
ims=[Image.open(f) for f in fs]; w,h=ims[0].size; cols=4
for p in range(0,len(ims),16):
    chunk=ims[p:p+16]; rows=(len(chunk)+cols-1)//cols
    sh=Image.new('RGB',(cols*w,rows*(h+18)),'white'); dr=ImageDraw.Draw(sh)
    for i,im in enumerate(chunk):
        x,y=(i%cols)*w,(i//cols)*(h+18); sh.paste(im,(x,y+18)); dr.text((x+4,y+2),str(idx[p+i]),fill='red')
    sh.save(f'{out}_{p//16+1}.jpg',quality=80)
