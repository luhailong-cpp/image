from pathlib import Path
import json,hashlib
N=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
source=N/'r04_c04-v1/package.py';s=source.read_text(encoding='utf-8');s=s.replace("'source':ref(F/'joined.png'),'nativePixelInspection'", "'image':ref(F/'joined.png'),'source':ref(F/'joined.png'),'nativePixelInspection'");source.write_text(s,encoding='utf-8')
files=[p for p in N.glob('r04_c*/**/*.json')]+[N/'local-source-checkpoint.json'];before={str(p):sha(p) for p in N.glob('r04_c*/final-v1/manifest.json')};pixels={str(p):sha(p) for p in N.glob('r04_c*/**/*.png')}
for p in N.glob('r04_c*/final-v1/visual-review.json'):
 v=read(p);q=p.parent/'joined.png';v['image']={'file':str(q),'sha256':sha(q)};save(p,v)
def refresh(v):
 changed=False
 if isinstance(v,dict):
  if isinstance(v.get('file'),str) and 'sha256' in v:
   p=Path(v['file'])
   if p.suffix=='.json' and p.is_relative_to(N) and p.exists():
    h=sha(p)
    if v['sha256']!=h:v['sha256']=h;changed=True
  for c in v.values():changed=refresh(c) or changed
 elif isinstance(v,list):
  for c in v:changed=refresh(c) or changed
 return changed
for iteration in range(20):
 changed=0
 for p in files:
  if p.exists():
   v=read(p)
   if refresh(v):save(p,v);changed+=1
 if not changed:break
else:raise AssertionError('metadata references did not converge')
assert all(sha(p)==h for p,h in pixels.items())
after={str(p):sha(p) for p in N.glob('r04_c*/final-v1/manifest.json')}
save(N/'review-contract-correction.json',{'operation':'Add exact joined image key to visual review contract, update metadata hashes through sequential local chain. All image pixels and image file hashes unchanged.','beforeManifestHashes':before,'afterManifestHashes':after,'imageFilesUnchanged':True,'imageFileCount':len(pixels),'rootStateModified':False})
print(json.dumps(after))
