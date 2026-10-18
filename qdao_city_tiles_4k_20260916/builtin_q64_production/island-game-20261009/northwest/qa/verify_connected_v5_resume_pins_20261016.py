from pathlib import Path
import json,hashlib,datetime
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
cp=Z/'qa/r05r06_v5_geometry_closure_material_pending_20261013.json'
closure=json.loads(cp.read_text(encoding='utf-8-sig'));manifest=closure['manifest'];assert sha(manifest['path'])==manifest['sha256']
checks=[]
for t in closure['tiles']:
 for kind in ['image','record']:
  f=t[kind];assert sha(f['path'])==f['sha256'];checks.append(dict(tileId=t['tileId'],kind=kind,**f))
for k in ['finalNativeAudit','finalNativeAuditDerivation','finalAuditOutput','validator','originalRunner']:
 f=closure['strictReplay'][k];assert sha(f['path'])==f['sha256']
ind=closure['independentReview'];assert sha(ind['path'])==ind['sha256']
wp=Z/'qa/r05_c02_v5_independent_native33_connected_20261013.json';w=json.loads(wp.read_text(encoding='utf-8-sig'))
for k in ['candidate','record','qaIndex']:
 f=w[k];assert sha(f['path'])==f['sha256']
p=Z/'qa/connected_v5_resume_pin_verification_20261016.json'
out=dict(createdAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),operation='read-only hash verification of current v5 final source pointers and existing closure evidence',manifest=manifest,sources=checks,closure=info(cp),strictReplay=closure['strictReplay'],independentReview=ind,westIndependent=info(wp),geometryStatus='17/17 prior native geometry PASS reused on unchanged pinned final sources; no historical visual rescan',materialStatus='PENDING',formalAccepted=False)
assert not p.exists()
p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(report=info(p),sources=checks,closure=info(cp),strictAudit=closure['strictReplay']['finalNativeAudit'],independent=ind,westIndependent=info(wp))))

