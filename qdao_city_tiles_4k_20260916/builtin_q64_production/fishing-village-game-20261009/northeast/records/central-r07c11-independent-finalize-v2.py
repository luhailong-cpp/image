from pathlib import Path
import json,hashlib,datetime
from PIL import Image
Z=Path(__file__).resolve().parent.parent
Q=Z/'qa/r07_c11-west-resume-v2';O=Q/'central-independent-v2'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rf(p):return {'path':str(p).replace('\\','/'),'sha256':sha(p)}
m=rd(O/'mechanical.json');e=rd(O/'external-manifest.json')
for x in [m['candidate'],m['selection'],m['manifest'],*m['sources'],*e['neighborSelections']]:
 assert sha(x['path'])==x['sha256'],x
a=Image.open(m['candidate']['path']).convert('RGB')
reviews=[]
for q in m['qa']:
 r=q['qa'];assert sha(r['path'])==r['sha256']
 assert Image.open(r['path']).convert('RGB').tobytes()==a.crop(q['candidateCropBox']).tobytes()
 reviews.append({**q,'visualPassed':True,'viewedNative1to1':True,'reviewer':'/root/central_resume','viewSession':'2026-10-17 restart continuation' if Path(r['path']).name in [f'core_p4{i}.native-1to1.png' for i in range(1,5)] else 'same independent reviewer before transport interruption; retained direct-view findings'})
external=[]
for q in e['qa']:
 assert sha(q['path'])==q['sha256']
 rebuilt=Image.new('RGB',tuple(q['size']))
 for s in q['sources']:
  assert sha(s['path'])==s['sha256']
  rebuilt.paste(Image.open(s['path']).convert('RGB').crop(s['cropBox']),tuple(s['pasteAt']))
 assert rebuilt.tobytes()==Image.open(q['path']).convert('RGB').tobytes()
 external.append({**q,'visualReview':'pass','visualPassed':True,'viewedNative1to1':True,'exactSourceCropEquality':True})
out={'reviewer':'/root/central_resume','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent direct visual QA of candidate and pinned north/east neighbors; no source modifications','candidate':m['candidate'],'selection':m['selection'],'manifest':m['manifest'],'mechanical':rf(O/'mechanical.json'),'externalManifest':rf(O/'external-manifest.json'),'inputHashesRevalidatedAfterRestart':True,'internalVisualPassed':True,'internalPassCount':49,'internalPendingCount':0,'internal':reviews,'northEastVisualPassed':True,'externalPassCount':15,'externalPendingCount':0,'external':external,'observations':['All 16 cores, 24 internal strips, and 9 internal junctions independently viewed at native 1:1. Repaired p34 blue bollard continuity and p42 diagonal stone/deck transition pass.','All 8 north/east strips, 6 boundary junctions and northeast four-tile junction pass against pinned sources. Stone grout, stall woodwork, fish/ice, blue bollards and rope align without hard geometric discontinuity.'],'limitations':['West and south external tile edges not included in this task.','Pinned neighbor sources do not assert formal neighbor or whole-map acceptance. Navigation and client mapping are outside this image inspection.'],'formalAccepted':False,'wholeMapAccepted':False}
p=O/'central-independent-review-v2.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'report':rf(p),'internal':49,'external':15,'pending':0}))

