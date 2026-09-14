from pathlib import Path
from PIL import Image
import json,hashlib
C=Path(r'E:\work\image\qdao_chibi_roster_v12\candidate-stable-body\23_lantern_courier');R=C.parent.parent/'review/23_lantern_natural_fixes';fixes=json.loads((C/'corrections.json').read_text());checks=[]
for d,changes in fixes.items():
 im=Image.open(C/f'source/walk-{d}-original.png').convert('RGB');cols=2 if d in ['N','S'] else 4;cw=im.width//cols;ch=im.height//(8//cols)
 for n,fix in changes.items():
  p=C/'source'/fix['file'];cell=Image.open(p).convert('RGB');s=min(cw/cell.width,ch/cell.height);cell=cell.resize((round(cell.width*s),round(cell.height*s)),Image.Resampling.LANCZOS);i=int(n)-1;im.paste((255,0,255),(i%cols*cw,i//cols*ch,(i%cols+1)*cw,(i//cols+1)*ch));im.paste(cell,(i%cols*cw+(cw-cell.width)//2,i//cols*ch+(ch-cell.height)//2))
 out=Image.open(C/f'source/walk-{d}.png').convert('RGB');assert im.tobytes()==out.tobytes(),d;checks.append({'direction':d,'exact_rgb_rebuild_match':True,'correction_phases':[int(x) for x in changes]})
(R/'rebuild-map-verification.json').write_text(json.dumps({'status':'passed','method':'independent in-memory replay of candidate assemble_corrections semantics; no mutation of source images','directions':checks},indent=2)+'\n',encoding='utf-8');print('candidate corrections map reproduces all6 modified sheets exactly')
