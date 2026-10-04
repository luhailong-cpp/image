from pathlib import Path
import json
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[2]
rows=json.loads((B/'audit/archer-reference/ns-current-native.json').read_text())
jobs=json.loads((B/'audit/archer-reference/ns-candidate-jobs.json').read_text(encoding='utf-8'))
sel={}
for j in jobs:sel[(j['dir'],j['frame'])]=B/'sources/new'/f"{j['key']}.png"
for d in ['N','S']:
 board=Image.new('RGB',(1400,1520),(225,228,226));dr=ImageDraw.Draw(board)
 for n in range(1,17):
  r=next(r for r in rows if r['direction']==d and r['frame']==n)
  p=sel.get((d,n),Path(r['path']))
  im=Image.open(p).convert('RGBA');im.thumbnail((350,350))
  x=(n-1)%4*350;y=(n-1)//4*380
  board.paste(im,(x,y+25),im);dr.text((x+5,y+5),f'{d} {n:02} '+('NEW' if (d,n)in sel else 'OLD'),fill='black')
 board.save(B/f'audit/archer-reference/ns-{d}-ground242-contact.png')
print('done')
