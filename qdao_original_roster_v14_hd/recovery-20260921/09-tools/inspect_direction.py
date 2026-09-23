"""Render honest alpha-composited contact/legs/seam views; no asset modification."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw
from common import DELIVERY, DIRS

p = argparse.ArgumentParser()
p.add_argument('direction', choices=DIRS)
args = p.parse_args()
work = DELIVERY / 'work' / args.direction
out = work / 'qa'
out.mkdir(parents=True, exist_ok=True)
frames = []
backgrounds = {'dark': (25, 32, 40), 'light': (242, 239, 225)}
for name, bg in backgrounds.items():
    contact = Image.new('RGB', (1280, 1360), bg)
    legs = Image.new('RGB', (1600, 1320), bg)
    draw, ld = ImageDraw.Draw(contact), ImageDraw.Draw(legs)
    sequence = []
    for f in range(1, 17):
        src = work / 'runtime' / 'walk' / args.direction / f'{f:02d}.png'
        if not src.exists():
            continue
        im = Image.open(src).convert('RGBA')
        comp = Image.new('RGBA', im.size, bg + (255,))
        comp.alpha_composite(im)
        comp = comp.convert('RGB')
        x, y = (f - 1) % 4, (f - 1) // 4
        contact.paste(comp.resize((320, 320), Image.Resampling.LANCZOS), (x * 320, y * 340 + 20))
        draw.text((x * 320 + 6, y * 340 + 5), f'{args.direction} {f:02d}', fill='white' if name == 'dark' else 'black')
        crop = comp.crop((312, 642, 712, 962))
        legs.paste(crop, (x * 400, y * 330 + 10))
        ld.text((x * 400 + 6, y * 330), f'{f:02d}', fill='white' if name == 'dark' else 'black')
        sequence.append(comp.resize((512, 512), Image.Resampling.LANCZOS))
    contact.save(out / f'contact-{name}.jpg', quality=95)
    legs.save(out / f'legs-{name}.jpg', quality=95)
    if len(sequence) == 16:
        sequence[0].save(out / f'walk-30ms-{name}.gif', save_all=True, append_images=sequence[1:], duration=30, loop=0, disposal=2, optimize=False)
    seam = Image.new('RGB', (1600, 450), bg)
    sd = ImageDraw.Draw(seam)
    for i, f in enumerate((15, 16, 1, 2)):
        src = work / 'runtime' / 'walk' / args.direction / f'{f:02d}.png'
        if src.exists():
            im = Image.open(src).convert('RGBA')
            comp = Image.new('RGBA', im.size, bg + (255,))
            comp.alpha_composite(im)
            seam.paste(comp.convert('RGB').resize((400, 400), Image.Resampling.LANCZOS), (i * 400, 30))
            sd.text((i * 400 + 5, 8), f'{args.direction} {f:02d}', fill='white' if name == 'dark' else 'black')
    seam.save(out / f'seam-{name}.jpg', quality=95)
print(out)
