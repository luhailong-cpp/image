from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
issues=[];items=[];ai=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in sorted(R.rglob('*.png')):
 rec=Path(str(p)+'.generation.json')
 if not rec.exists():issues.append({'file':str(p),'issue':'missing record'});continue
 try:d=json.loads(rec.read_text(encoding='utf-8-sig'))
 except Exception as e:issues.append({'file':str(p),'issue':str(e)});continue
 s=sha(p)
 if d.get('sha256')!=s:issues.append({'file':str(p),'issue':'hash mismatch'})
 if d.get('tool')=='image_gen.imagegen':
  ai.append(str(p));refs=d.get('references',[])
  if d.get('actualModel') is not None or d.get('actualQuality') is not None:issues.append({'file':str(p),'issue':'actual non-null'})
  if not any('04-guild.png' in z.get('file','') for z in refs):issues.append({'file':str(p),'issue':'missing actual style reference'})
  for ref in refs:
   fp=Path(ref['file'])
   if not fp.exists() or ref['sha256']!=sha(fp):issues.append({'file':str(p),'issue':'reference mismatch','reference':str(fp)})
 if p.parent.name=='native' and Image.open(p).size!=(1254,1254):issues.append({'file':str(p),'issue':'not native1254'})
 items.append({'file':str(p),'sha256':s,'record':str(rec),'generated':d.get('tool')=='image_gen.imagegen'})
data={'PNGCount':len(items),'AIImageCount':len(ai),'records':items,'issues':issues};(R/'generation-record-index.json').write_text(json.dumps(data,indent=2),encoding='utf8');print(json.dumps({'PNGCount':len(items),'AIImageCount':len(ai),'issues':issues},indent=2))
