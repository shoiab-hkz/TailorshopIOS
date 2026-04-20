"""Generate the PWA app icons.
Produces: icons/icon-180.png, icon-192.png, icon-512.png, icon-512-maskable.png
Run from the repo root:  python tools/make_icons.py
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'icons'
OUT.mkdir(exist_ok=True)

BG   = (28, 20, 9)      # #1c1409
GOLD = (240, 184, 64)   # #f0b840
GOLD_DARK = (184, 121, 26)  # #b8791a
CREAM = (255, 253, 248)

def find_font(size):
    for p in [
        'C:/Windows/Fonts/tahoma.ttf',
        'C:/Windows/Fonts/arial.ttf',
        '/System/Library/Fonts/Supplemental/Tahoma.ttf',
    ]:
        if Path(p).exists():
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def draw_icon(size, maskable=False):
    img = Image.new('RGB', (size, size), BG)
    d   = ImageDraw.Draw(img)
    # Rounded-rect plate — skip on maskable (safe area: 80%, so make bg fill edge)
    if not maskable:
        pad = int(size * 0.08)
        r   = int(size * 0.22)
        d.rounded_rectangle([pad, pad, size-pad, size-pad],
                            radius=r, fill=BG, outline=GOLD, width=max(2, size//64))
    # Scissors glyph — unicode ✂
    font = find_font(int(size * (0.55 if not maskable else 0.42)))
    txt = '✂'
    try:
        bbox = d.textbbox((0,0), txt, font=font)
        tw = bbox[2] - bbox[0]; th = bbox[3] - bbox[1]
        tx = (size - tw) // 2 - bbox[0]
        ty = (size - th) // 2 - bbox[1] - int(size*0.04)
    except Exception:
        tx = ty = size // 4
    d.text((tx, ty), txt, font=font, fill=GOLD)
    # Small Farsi caption at bottom for non-maskable
    if not maskable and size >= 180:
        cap_font = find_font(max(10, int(size*0.11)))
        cap = 'ببر و بدوز'
        try:
            bb = d.textbbox((0,0), cap, font=cap_font)
            cw = bb[2]-bb[0]
            cx = (size - cw)//2 - bb[0]
            cy = size - int(size*0.18)
        except Exception:
            cx = 0; cy = size - int(size*0.18)
        d.text((cx, cy), cap, font=cap_font, fill=CREAM)
    return img

def main():
    draw_icon(180).save(OUT / 'icon-180.png')
    draw_icon(192).save(OUT / 'icon-192.png')
    draw_icon(512).save(OUT / 'icon-512.png')
    draw_icon(512, maskable=True).save(OUT / 'icon-512-maskable.png')
    print('wrote:', *[p.name for p in OUT.glob('*.png')])

if __name__ == '__main__':
    main()
