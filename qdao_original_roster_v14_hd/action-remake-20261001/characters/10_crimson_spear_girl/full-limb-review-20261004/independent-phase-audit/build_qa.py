from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
from datetime import datetime,timezone
O=Path(__file__).resolve().parent;R=O.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=[]
for direction in ['E','W']:
 for indices in [[13,14,15,16],[1,2,3,4],[5,6,7,8],[9,10,11,12]]:
  paths=[R/'runtime/run'/direction/f'{n:02}.png' for n in indices]
  for view,crop in [('body',(160,330,940,990)),('legs',(240,670,840,990))]:
   w=crop[2]-crop[0];h=crop[3]-crop[1];sheet=Image.new('RGB',(w*4,h+30),(206,215,221));d=ImageDraw.Draw(sheet)
   for i,p in enumerate(paths):
    im=Image.open(p).convert('RGBA').crop(crop);sheet.paste(im,(w*i,30),im);d.text((w*i+6,8),f'run/{direction}/{p.stem}',fill=(0,0,0))
   out=O/f'{direction}-{indices[0]:02}-{indices[-1]:02}-{view}.jpg';sheet.save(out,quality=94)
   refs=[{'file':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in paths]
   rec={'file':out.relative_to(R).as_posix(),'sha256':sha(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'operation':{'type':'fixed-crop-contact-sheet-for-independent-phase-review','crop':crop,'alphaBackground':[206,215,221]},'derivedFrom':refs}
   Path(str(out)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  source+=refs
(O/'source-sha.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
print('32 current runtime PNGs snapshotted by SHA; 16 fixed-crop QA pages')
