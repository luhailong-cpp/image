from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1];q=R/'qa'/'independent-pass-final';q.mkdir(exist_ok=True)
coords=json.loads((R/'coordinates.json').read_text());w=Path(next(x for x in coords if x['tile']=='r03_c05' and x['subcolumn']==1)['westSource']);p=R/'tiles/r03_c05_candidate-v5_4096.png';p2=R/'tiles/r04_c05_candidate-v4_4096.png';a=Image.open(p);b=Image.open(p2);west=Image.open(w);out=Image.new('RGB',(256,1024));out.paste(west.crop((3968,3072,4096,4096)),(0,0));out.paste(a.crop((0,3072,128,4096)),(128,0));out.save(q/'r03-west-4.png')
for k in [0,2]:
 out=Image.new('RGB',(1024,256));out.paste(a.crop((k*1024,3968,(k+1)*1024,4096)),(0,0));out.paste(b.crop((k*1024,0,(k+1)*1024,128)),(0,128));out.save(q/f'r03-r04-{k+1}.png')
d={'formalAccepted':False,'sourceHashes':{str(s):hashlib.sha256(s.read_bytes()).hexdigest() for s in [p,p2,w]},'latestSelected':json.loads((R/'selected-revisions.json').read_text(encoding='utf-8-sig')),'uniqueCores':32,'nativeVersions':len(list((R/'native').glob('*.png'))),'internalStatus':'pending_material','externalStatus':'pending_remaining_context'};(q/'inputs.json').write_text(json.dumps(d,indent=2))
p=R/'progress.json';d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(versionCount=52,currentPatch=None,updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),qaRecord=str(q));p.write_text(json.dumps(d,indent=2))
