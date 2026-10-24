"""Render Google Material Symbols (Rounded, filled; Apache 2.0) to PNG icons for the lab rules poster.
The font is downloaded into _build/material_symbols (not in git); the PNGs go to fig/icons."""
import os
from PIL import Image, ImageDraw, ImageFont

SRC = os.path.join(os.path.dirname(__file__), '_build', 'material_symbols')
OUT = os.path.join(os.path.dirname(__file__), 'fig', 'icons')
ICONS = ['power_settings_new', 'electric_bolt', 'warning', 'electric_meter', 'electrical_services', 'fire_extinguisher',
         'no_food', 'desk', 'report', 'cleaning_services', 'developer_board', 'inventory_2', 'cable', 'check_circle', 'how_to_reg']
COLOR = (194, 65, 12, 255)           # dark orange: neutral for every program, still dark on a poor / B&W printer


def render(size=256):
    os.makedirs(OUT, exist_ok=True)
    cp = dict(l.split() for l in open(os.path.join(SRC, 'MaterialSymbolsRounded.codepoints')))
    font = ImageFont.truetype(os.path.join(SRC, 'MaterialSymbolsRounded.ttf'), int(size * 0.9))
    axes = {a['name'].decode() if isinstance(a['name'], bytes) else a['name']: a for a in font.get_variation_axes()}
    want = {'Fill': 1, 'Weight': 500, 'Grade': 0, 'Optical size': 48}
    font.set_variation_by_axes([want.get(n, a['default']) for n, a in axes.items()])
    for name in ICONS:
        ch = chr(int(cp[name], 16))
        im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        l, t, r, b = d.textbbox((0, 0), ch, font=font)
        d.text(((size - (r - l)) / 2 - l, (size - (b - t)) / 2 - t), ch, font=font, fill=COLOR)
        im.save(os.path.join(OUT, f'{name}.png'))
    print(len(ICONS), 'icons ->', OUT, '| axes', list(axes))


if __name__ == '__main__':
    render()
