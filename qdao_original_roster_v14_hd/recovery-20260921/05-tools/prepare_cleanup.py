from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];C=R/'qdao_original_roster_v14_hd/recovery-20260921';F=C/'05-delivery-preview/final'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(C/'05-audit/CLEANUP-PLAN-20260923.json')
m=read(F/'manifest.json')
assert m['offline_accepted'] and len(m['files'])==136
assert all(sha(F/'runtime'/r['path'])==r['sha256'] for r in m['files'])
keep={str((F/'runtime'/r['path']).resolve()).lower() for r in m['files']}
targets={}
for r in plan['workspaceFiles']:
 p=Path(r['path']).resolve();disp=r['proposedDisposition']
 eligible=disp in ['DELETE_AFTER_FINAL_ACCEPTANCE','DELETE_AFTER_FINAL_REBIND','PROTECT_UNTIL_FINAL_NAME_BOUND']
 eligible |= disp=='HOLD_REFERENCE_CONTRACT_REVIEW' and p.name!='portrait.png'
 if not eligible:continue
 assert p.is_relative_to(R) and not p.is_relative_to(F) and str(p).lower() not in keep
 if p.is_file():
  assert sha(p)==r['sha256'],str(p)
  targets[str(p)]={'path':str(p),'sha256':r['sha256'],'bytes':p.stat().st_size,'reason':disp}
for directory in [C/'05-audit/root-static',C/'05-audit/final-neighbor-static']:
 for p in directory.rglob('*'):
  if p.is_file() and p.suffix.lower() in ['.png','.gif','.webp','.jpg','.jpeg']:
   assert p.resolve().is_relative_to(R)
   targets[str(p.resolve())]={'path':str(p.resolve()),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'temporary_static_QA_images_text_measurements_preserved'}
external=[]
for r in plan['externalOriginals']:
 if not r['existsNow']:continue
 p=Path(r['path']).resolve()
 assert p.is_relative_to(Path('C:/Users/Administrator/.codex/generated_images'))
 assert p.is_file() and sha(p)==r['sha256'] and r['matchesBoundRaw']
 external.append({'path':str(p),'sha256':r['sha256'],'bytes':p.stat().st_size,'reason':'host_default_raw_bound_by_true_receipt'})
out={'schema':'qdao05-authorized-exact-file-removal-v1','created_at_utc':datetime.now(timezone.utc).isoformat(),'character':'05_celestial_musician_girl','authorization':'User repeatedly requested final-only retention; current AGENTS explicitly authorizes deletion after final/reference verification. No Git clean used.','workspace':str(R),'final_manifest_sha256':sha(F/'manifest.json'),'final_action_files':136,'final_runtime_pngs':137,'internal':list(targets.values()),'external':external,'delete_directories':False,'preserve_all_text_records':True}
(C/'05-audit/CLEANUP-EXECUTION-MANIFEST.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'internal_files':len(targets),'internal_bytes':sum(x['bytes'] for x in targets.values()),'external_files':len(external),'external_bytes':sum(x['bytes'] for x in external)}))
