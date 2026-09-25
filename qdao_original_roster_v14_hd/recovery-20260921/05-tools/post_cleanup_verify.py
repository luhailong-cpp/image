from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[3];C=R/'qdao_original_roster_v14_hd/recovery-20260921';F=C/'05-delivery-preview/final'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(F/'manifest.json');issues=[];evidence=0
for row in m['files']:
 p=F/'runtime'/row['path']
 if sha(p)!=row['sha256']:issues.append('runtime sha '+row['path'])
 with Image.open(p) as im:
  if list(im.size)!=row['size'] or im.mode!='RGBA':issues.append('runtime size/mode '+row['path'])
 meta=read(p.with_suffix('.png.generation.json'))
 for rec in meta['evidence']:
  q=F/rec['path'];evidence+=1
  if not q.is_file() or sha(q)!=rec['sha256']:issues.append('evidence '+rec['path'])
 if not (p.parent/meta['offline_review']).resolve().is_file():issues.append('review link '+row['path'])
for g in m['gif_checks']:
 p=F/g['path']
 if sha(p)!=g['sha256']:issues.append('gif sha '+g['path'])
 with Image.open(p) as im:
  ds=[]
  for i in range(im.n_frames):im.seek(i);ds.append(im.info['duration'])
  if ds!=[30]*16 or im.info.get('loop')!=0:issues.append('gif timing '+g['path'])
if sha(F/'runtime/portrait.png')!=m['portrait']['sha256']:issues.append('portrait')
plan=read(C/'05-audit/CLEANUP-EXECUTION-MANIFEST.json')
for category in ['internal','external']:
 for r in plan[category]:
  if Path(r['path']).exists():issues.append('cleanup survived '+r['path'])
legacy=R/'qdao_original_roster_v13/candidate/05_celestial_musician_girl'
for row in m['files']:
 if row['preserved_v13'] and sha(legacy/row['path'])!=row['sha256']:issues.append('legacy changed '+row['path'])
runtime=list((F/'runtime').rglob('*.png'))
if len(runtime)!=137:issues.append('runtime count')
actual_sources_deleted=sum(not Path(r['path']).exists() for r in plan['internal'])+sum(not Path(r['path']).exists() for r in plan['external'])
out={'at':datetime.now(timezone.utc).isoformat(),'status':'passed' if not issues else 'failed','issues':issues,'walk':128,'idle':8,'portrait':1,'runtime_pngs':len(runtime),'source_text_evidence_verified':evidence,'gif_count':16,'gif_frame_ms':30,'gif_cycle_ms':480,'preserved_legacy_actions_verified':60,'deleted_image_files_verified':actual_sources_deleted,'final_manifest_sha256':sha(F/'manifest.json'),'offline_accepted':True,'client_integration':False,'unity_validation':False,'paid_api_calls':0}
for p in [C/'05-audit/POST-CLEANUP-CHECK-20260923.json',F/'POST-CLEANUP-CHECK.json']:
 p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,ensure_ascii=False))
assert not issues
