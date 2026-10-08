from pathlib import Path
import json
from PIL import Image
import production_r07_c15 as m
T=m.p.T
old=T/'native/r02_c04.png'
new=Path('C:/Users/luyua/.codex/generated_images/01a10ba3-b9ef-7c02-b277-345815c70f88/exec-3f1ae363-e741-4c48-990a-960ba303c44a.png')
assert old.resolve().is_relative_to(T.resolve())
assert m.p.sha(old)=='161df3db4fb6f72bec810f5b6bd47f88a9480f5ea84673a49637f2f2f467e543'
assert (T/'rejected/r02_c04-contact-highlight-removed/generation.json').is_file()
with Image.open(new) as im:
    im.load();assert im.size==(1254,1254)
old.unlink()
m.p.record('r02_c04',str(new))
print('Rejected image removed after corrected native was available; provenance retained.')
