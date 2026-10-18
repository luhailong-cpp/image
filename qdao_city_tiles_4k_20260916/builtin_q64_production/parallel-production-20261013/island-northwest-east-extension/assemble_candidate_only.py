from pathlib import Path
from PIL import Image
import json,hashlib,sys
R=Path(__file__).resolve().parent;tile,ver=sys.argv[1:3];sel=json.loads((R/'selected-revisions.json').read_text(encoding='utf-8-sig'));out=R/'tiles'/f'{tile}_candidate-{ver}_4096.png';assert not out.exists();im=Image.new('RGB',(4096,4096));records=[]
for r in range(1,5):
 for c in range(1,5):
  stem=f'{tile}_s{r:02d}_{c:02d}';p=R/'native'/f'{stem}_{sel.get(stem,"a01")}.png';a=Image.open(p);assert a.size==(1254,1254);im.paste(a.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024));records.append({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'crop':[115,115,1139,1139],'destination':[(c-1)*1024,(r-1)*1024]})
im.save(out);d={'tile':tile,'dimensions':[4096,4096],'method':'16 unscaled1024 cores; no blur or synthesized pixels','sources':records,'formalAccepted':False,'internalSeams':'pending_surface_material','sha256':hashlib.sha256(out.read_bytes()).hexdigest()};out.with_suffix('.json').write_text(json.dumps(d,indent=2));print(json.dumps({'path':str(out),'sha256':d['sha256']}))
