from pathlib import Path
import json
from PIL import Image, ImageDraw
import numpy as np
BASE=Path(__file__).resolve().parent
GEN=BASE.parents[1]/'10-generation'
OUT=BASE/'qa-current'
OUT.mkdir(exist_ok=True)
sel=json.loads((BASE/'selection.json').read_text(encoding='utf-8'))
for d in ['E','SW']:
  for bg,color in [('light','#f6f1e7'),('dark','#242a31')]:
    for start in [1,9]:
      sheet=Image.new('RGB',(2048,1060),color);draw=ImageDraw.Draw(sheet)
      for j,n in enumerate(range(start,start+8)):
        key=d+f'{n:02}';x=j%4*512;y=j//4*530
        if key in sel:
          im=Image.open(GEN/sel[key]['archive']/'raw.png').convert('RGBA'); im.thumbnail((512,512),Image.Resampling.LANCZOS)
          sheet.paste(im,(x,y),im)
        draw.text((x+8,y+512),key,fill='white' if bg=='dark' else 'black')
      sheet.save(OUT/f'{d}-{bg}-{start:02}.jpg',quality=96)
    for part,box in [('feet',(450,840,1060,1230)),('head',(340,110,920,640))]:
      seam=Image.new('RGB',(2440,550),color);draw=ImageDraw.Draw(seam)
      for j,n in enumerate([15,16,1,2]):
        key=d+f'{n:02}'
        if key in sel:
          im=Image.open(GEN/sel[key]['archive']/'raw.png').convert('RGBA').crop(box)
          seam.paste(im,(j*610,0),im)
        draw.text((j*610+8,530),key,fill='white' if bg=='dark' else 'black')
      seam.save(OUT/f'{d}-{bg}-seam-{part}.jpg',quality=96)
print(OUT)
