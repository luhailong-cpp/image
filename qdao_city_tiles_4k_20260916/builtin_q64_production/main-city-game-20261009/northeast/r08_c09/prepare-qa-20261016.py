from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).parent
Q=T/'qa/core-baseline/1368c15ca794536c2a6b'
O=T/'qa/review-20261016';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((Q/'assembly.json').read_text(encoding='utf-8-sig'))
assert all(sha(Path(s['file']))==s['sha256'] for s in a['inputs']['nativeSources'])
candidate=Q/'r08_c09-core-baseline.candidate.png'
records=[]
for axis in ['vertical','horizontal']:
 fs=sorted(Q.glob(axis+'-*-join-100pct.png'))
 for ix in range(0,len(fs),3):
  subset=fs[ix:ix+3]; imgs=[Image.open(p).convert('RGB') for p in subset]
  # Native QA only; no image pixels scaled.
  if axis=='vertical':
   sheet=Image.new('RGB',(sum(i.width for i in imgs),max(i.height for i in imgs)))
   offset=0
   for im in imgs:sheet.paste(im,(offset,0));offset+=im.width
  else:
   sheet=Image.new('RGB',(max(i.width for i in imgs),sum(i.height for i in imgs)))
   offset=0
   for im in imgs:sheet.paste(im,(0,offset));offset+=im.height
  dest=O/f'{axis}-{ix//3+1}.png';assert not dest.exists();sheet.save(dest)
  records.append({'file':str(dest),'order':[p.name for p in subset],'nativePixelScale':1})
for r in range(1,4):
 fs=[Q/f'intersection-r{r}-c{c}-100pct.png' for c in range(1,4)]
 imgs=[Image.open(p).convert('RGB') for p in fs]
 sheet=Image.new('RGB',(sum(i.width for i in imgs),max(i.height for i in imgs)));offset=0
 for im in imgs:sheet.paste(im,(offset,0));offset+=im.width
 dest=O/f'corners-r{r}.png';assert not dest.exists();sheet.save(dest)
 records.append({'file':str(dest),'order':[p.name for p in fs],'nativePixelScale':1})
data={'candidate':str(candidate),'candidateSha256':sha(candidate),'inputSignature':a['inputSignature'],'sourcesVerifiedUnchanged':True,'sheets':records}
(O/'sheets.json').write_text(json.dumps(data,indent=2),encoding='utf8')
print(json.dumps(data,indent=2))
