"""Remove the HN 12 V / 1 MΩ split-supply block from Proteus screenshots (HCM uses the PB-503A ± outputs).
The block is painted over with the Proteus background grid: each column/row takes its own median colour,
so grid lines stay exactly where they are in the rest of the picture."""
import sys
import numpy as np
from PIL import Image

def paint(src, dst, box):
    im = np.array(Image.open(src).convert('RGB')).astype(int)
    x0, y0, x1, y1 = box
    light = np.where((im.sum(2) > 450)[..., None], im, np.nan)    # ignore wires, parts and text
    col = np.nanmedian(light, axis=0)      # (W,3) colour of each column away from the drawing
    row = np.nanmedian(light, axis=1)      # (H,3)
    bg = np.median(im.reshape(-1, 3), axis=0)
    for y in range(y0, y1):
        for x in range(x0, x1):
            c, r = col[x], row[y]
            im[y, x] = min((bg, c, r), key=lambda v: v.sum())   # the darker one wins (grid line over background)
    Image.fromarray(im.astype('uint8')).save(dst)

if __name__ == '__main__':
    src, dst, *b = sys.argv[1:]
    paint(src, dst, tuple(map(int, b)))


def drop_rail_labels(xml):
    """Remove the red 6V / 0V / -6V labels HN placed next to the (now removed) 12 V block, top of the slide."""
    import re
    def keep(m):
        sp = m.group(0)
        t = ''.join(re.findall(r'<a:t>([^<]*)</a:t>', sp)).strip()
        off = re.search(r'<a:off x="\d+" y="(\d+)"', sp)
        return '' if t in ('6V', '0V', '-6V', '−6V') and off and int(off.group(1)) < 3000000 else sp
    return re.sub(r'<p:sp>.*?</p:sp>', keep, xml, flags=re.S)
