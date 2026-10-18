from pathlib import Path
import hashlib,json,datetime
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sp=Z/'connected-coast-current-selection-20261016.json'
d=json.loads(sp.read_text(encoding='utf-8'))
assert len(d['selectedNative'])==16 and not d['inflight']
m=[]
for r in range(1,5):
 row=[]
 for c in range(1,5):
  ee=[x for x in d['selectedNative'] if x['row']==r and x['col']==c];assert len(ee)==1
  e=ee[0];assert sha(e['path'])==e['sha256'] and sha(e['generationRecord'])==e['generationSha256']
  assert sha(e['quickReview']['path'])==e['quickReview']['sha256']
  row.append({'path':e['path'],'sha256':e['sha256'],'generationRecord':e['generationRecord'],'generationSha256':e['generationSha256'],'quickReview':e['quickReview']})
 m.append(row)
out=Z/'qa/r02_c01_connected_explicit_manifest_v1_20261017.json'
v={'schemaVersion':1,'tileId':'r02_c01','nativePixels':1254,'corePixels':1024,'haloPixels':115,'patchMatrix':m,'sourceSelection':{'path':sp.as_posix(),'sha256':sha(sp)},'authority':'Parent /root explicitly delegated r02_c01 production and assembly to connected continuation. No other tile or global state changes.','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with out.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'path':out.as_posix(),'sha256':sha(out),'sources':16}))
