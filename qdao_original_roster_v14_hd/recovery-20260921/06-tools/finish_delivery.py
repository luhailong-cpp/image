"""Record the completed root offline review, then rebind after authorized cleanup."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib, shutil
HERE=Path(__file__).resolve().parent
REC=HERE.parent
FINAL=REC/'06-final'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
parser=argparse.ArgumentParser();parser.add_argument('--cleaned',action='store_true');a=parser.parse_args()
m=read(FINAL/'manifest.json')
assert m['legacy_final_copies_ai_restored'] and m['actual_walk']==128 and m['actual_idle']==8
if a.cleaned:
 assert read(FINAL/'cleanup-result.json')['status']=='completed'
 assert read(FINAL/'host-cleanup-result.json')['status']=='completed'
 p=read(FINAL/'provenance/selected-sources.json')
 for r in p:
  r['source_images_retained']=False
  r['raw_retention_decision']='Verified final PNG and self-contained textual provenance, then deleted generated raw/reject/rollback/intermediate images with exact SHA inventory. Original 24 legacy 512 PNG files remain byte-exact by explicit user exception.'
 write(FINAL/'provenance/selected-sources.json',p)
 m['source_image_retention']='Generated raw/reject/rollback/intermediate images deleted after verification; full textual evidence retained. The original 24 legacy 512 PNG files remain byte-exact at original V13 paths by explicit user request.'
 review=read(FINAL/'offline-review.json')
 review['cleanup_verified_at_utc']=now()
else:
 assert read(FINAL/'verification.json')['all_checks_passed']
 browser=read(FINAL/'browser-review.json');assert browser['passed']
 m['status']='complete_passed_offline'
 m['offline_review_status']='passed_offline'
 m['formal_approval']=False
 m['formal_approval_scope']='Offline asset review passed; no client integration or release approval is claimed.'
 m['client_integration']=False
 m['browser_dynamic_review']={'performed':True,'evidence':'browser-review.json','scope':'Local offline preview only; not game-client runtime.'}
 m['known_rework_slots']=[]
 for v in m['directions'].values():v['visual_approval']=True
 for r in m['files']:r['visual_status']='passed_offline'
 review={'status':'passed_offline','reviewed_at_utc':now(),'character_id':'06_thunder_caster_boy','walk':128,'idle':8,'all_runtime_pngs_1024':True,'transparent_edges':'Deep/light full images and enlarged details inspected; previous magenta fringe repaired. Intentional navy cloth and warm coral staff ornament retained.','gait':'Eight directions inspected for alternating legs, planted/support feet and independent swing phases. Full-frame single generated sources are unique; no synthetic pose duplication.','scale':'Fixed whole-cell .88 for all sources and grounded alpha anchor [512,942]. S03 and S13/15/16 body-size mismatch and SW idle-to-walk mismatch were repaired with separate AI edits.','seams':'15 -> 16 -> 01 -> 02 inspected for every direction.','preview_timing':'16 encoded GIFs verified at 16 frames x 30ms = 480ms per loop; browser display scheduling may vary.','legacy_originals':'24 original V13 512 PNGs retained byte-exact, while final runtime uses the AI-restored 1024 versions.','builtin_route':'Actual model/quality not exposed; unverified values kept null. Paid API calls: 0.','client_integration':{'performed':False,'unity_import':False,'runtime_scene':False,'release':False},'evidence':['verification.json','browser-review.json','provenance/selected-sources.json','provenance/preserved-old-byte-baseline.json','preview/']}
 for f in ['audit.json','selection-input.json']:
  p=FINAL/f
  if p.exists():shutil.copy2(p,FINAL/'provenance'/('assembly-'+f));p.unlink()
 m['assembly_audit']='provenance/assembly-audit.json (historical, prior to final offline review)'
m['selected_provenance_sha256']=sha(FINAL/'provenance/selected-sources.json')
write(FINAL/'manifest.json',m)
review['manifest_sha256']=sha(FINAL/'manifest.json')
write(FINAL/'offline-review.json',review)
template=(FINAL/'preview-template.html' if a.cleaned else HERE/'preview-template.html').read_text(encoding='utf-8')
(FINAL/'index.html').write_text(template.replace('__MANIFEST__',json.dumps(m,ensure_ascii=False)),encoding='utf-8')
if not a.cleaned:
 shutil.copy2(HERE/'preview-template.html',FINAL/'preview-template.html')
 shutil.copy2(HERE/'verify_final.py',FINAL/'verify_final.py')
 shutil.copy2(HERE/'finish_delivery.py',FINAL/'finish_delivery.py')
print(json.dumps({'status':m['status'],'manifest_sha256':sha(FINAL/'manifest.json'),'cleanup_recorded':a.cleaned}))
