from pathlib import Path
from PIL import Image
import hashlib,json
r=Path(r'E:\work\image\qdao_chibi_roster_v12');src=r/'candidate-natural-body/29_he_xiangu/source';p=r/'review/he_xiangu_natural_walk/idle-proportion-fixes';p.mkdir(exist_ok=True)
records=[]
for name,dirs,cols,rows in [('N-S-SE-SW',['N','S','SE','SW'],2,2),('E-W',['E','W'],2,1)]:
 board=Image.new('RGBA',(cols*627,rows*627),(255,0,255,255)); old=Image.new('RGBA',board.size,(255,0,255,255))
 for i,d in enumerate(dirs):
  f=src/('walk-'+d+'-raw.png');im=Image.open(f).convert('RGBA');assert im.size==(2508,1254);box=[1254,0,1881,627];cell=im.crop(box);board.paste(cell,(i%cols*627,i//cols*627))
  idle=r/'review/he_xiangu_natural_walk/directions'/d/'idle-source-cell.png';old.paste(Image.open(idle).convert('RGBA').resize((627,627),Image.Resampling.LANCZOS),(i%cols*627,i//cols*627))
  records.append({'group':name,'direction':d,'source_walk':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'phase':3,'cell_box':box,'head_authority':'existing walk03 at same whole627 cell scale'})
 board.save(p/(name+'-walk-reference.png'));old.save(p/(name+'-old-idle-reference.png'))
(p/'reference-provenance.json').write_text(json.dumps(records,indent=2)+'\n')
print('Prepared6 full-cell walking references for6 neutral-idle proportion corrections')

