"""Merge evidence into a per-path ledger. Unknowns stay pending; never infer completion from counts."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parent
VISUAL={'.png','.jpg','.jpeg','.gif','.webp','.svg','.bmp','.tif','.tiff'}
def read(p):
 p=ROOT/p
 return json.loads(p.read_text(encoding='utf-8-sig')) if p.exists() else {}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inv=read('qdao_festival_refinement_20260910/inventory.json');ledger={}
def norm(p):
 if not isinstance(p,str):return None
 q=Path(p)
 if q.is_absolute():
  try:return q.resolve().relative_to(ROOT.resolve()).as_posix()
  except ValueError:return None
 return p.replace('\\','/')
def setrow(p,decision,reason,evidence=None,expected=None):
 p=norm(p)
 if not p or p not in ledger:return
 row=ledger[p];row.update(decision=decision,reason=reason,evidence=evidence)
 if expected:row['expected_sha256']=expected
for r in inv['records']:
 p=r['path'];role=r['role'];d='pending';reason='Still requires source/use/derivative decision.'
 if role in ['supporting_history_or_work','reference_do_not_repaint','evidence_do_not_repaint']:
  d='retain_record';reason='Historical/reference/QA/processing record; preserve original evidence rather than repaint it. This is not an accepted current game output.'
 if p.startswith(('qdao_cutout_edge_repair_20260910/','qdao_cutout_edge_repair_20260911/','qdao_exposure_refinement_v8/','docs/style-repair-','docs/style-audit-')):
  d='retain_record';reason='Versioned repair/exposure/audit snapshot. Current canonical outputs are reviewed at their actual published paths; this historical evidence retains original pixels.'
 if p.startswith('qdao_gpt_image2_refresh_v7/'):
  d='retain_record';reason='Original v7 generation/processed provenance, superseded at current formal paths by v9/v10 or festival releases; retain original raw and production snapshots.'
 if p.startswith(('tianyong_city_6x6/','tianyong_festival_gptimage2_20260910/','tianyong_festival_stylematch_20260910/')):
  d='retain_record';reason='Original client map archive or superseded style exploration. Current HD festival package is separate; never repaint archived tiles or old acceptance evidence.'
 if p.startswith('qdao_ui_style_recut_v10/contracts/'):
  d='retain_input_record';reason='Frozen v10 geometry/input/portrait contract; new source updates use separate current input snapshots. Do not change historical hashes.'
 if p.startswith('qdao_chibi_roster_v11/') and role=='source_review_pending':
  d='retain_record';reason='Original production/source candidate not selected by current final manifest index. Current accepted source cells and final directions are tracked separately; preserve generation evidence.'
 ledger[p]={'path':p,'family':r['family'],'inventory_role':role,'decision':d,'reason':reason,'evidence':'inventory.json classification/source-families.json' if d!='pending' else None}
# Actual visual reviews, with required repairs kept open until publication.
for file in ['reviews/ui-items-old-hero-review.json','reviews/v11-style-review.json','reviews/v9-pets-style-review.json','remaining-misc-review.json']:
 j=read('qdao_festival_refinement_20260910/'+file)
 for r in j.get('files',[]):
  status=r.get('status','');d=r.get('decision') or ('retain' if status in ['retained','rebuild_support_retained'] else 'pending_repair')
  if 'needs_' in status:d='pending_repair'
  setrow(r['path'],d,r.get('reason') or r.get('style_reason') or 'See actual current visual review.',file,r.get('sha256'))
 for r in j.get('excluded_history_and_reference',[]):setrow(r['path'],'retain_record',r['reason'],file,r.get('sha256'))
 for r in j.get('additional_derived_outputs',[]):setrow(r['path'],'pending_rebuild',r['reason'],file,r.get('sha256'))
# Current source-selected art in accepted map and v11 provenance; only final designs are retained.
for r in inv['records']:
 p=r['path']
 if r['role'] in ['accepted_source_art','accepted_processing_input'] and p.startswith('qdao_chibi_roster_v11/'):
  setrow(p,'retain_source_record','Original AI art or accepted layout input for one of eight visually reviewed retained designs. Edge refinement operates on transparent export RGB; preserve original keyed source and selected-cell lineage.','reviews/v11-style-review.json')
 if p.startswith('tianyong_festival_hd_20260910/') and r['role'] in ['accepted_source_art','accepted_derived_export']:
  setrow(p,'retain','Current HD Daoist chibi festival main city: root viewed assembled city; producer reviewed native tiles/seams. Keep map roads, accepted tile pixel geometry and lantern/rabbit/osmanthus accents.','../tianyong_festival_hd_20260910/qa/visual-review.json')
 if p.startswith('qdao_festival_scenes_20260910/') and r['role'] in ['accepted_source_art','accepted_derived_export']:
  setrow(p,'retain','Four native paintings for five uses were visually reviewed; jade roofs, ivory stone and restrained festival accents already meet direction. Preserve accepted clear battle/walk space and runtime crop geometry.','../qdao_festival_scenes_20260910/manifest.json')
# Current v10 publication companion and preview records only when matching exact original hashes.
pub=read('qdao_ui_style_recut_v10/publication.json')
for e in pub.get('files',[]):
 p=norm(e['path']);fp=ROOT/p
 if p in ledger and ledger[p]['decision']=='pending' and fp.suffix.lower() in VISUAL:
  expected=e.get('published_sha256')
  if expected and sha(fp)==expected:
   setrow(p,'retain_derived','Current published v10 companion/source export remains exact; parent PNGs and mother art were reviewed in this pass. Preserve current UI geometry and optional labels.','../qdao_ui_style_recut_v10/publication.json',expected)
# The generator fallback derived 112 copies are exact aliases of reviewed formal controls.
for e in read('qdao_ui_style_recut_v10/contracts/current_files.json').get('files',[]):
 if e['family'] in ['components','legacy']:
  p='qdao_ui_style_recut_v10/derived/'+e['family']+'/'+Path(e['path']).name
  if p in ledger and (ROOT/p).exists() and sha(ROOT/p)==sha(ROOT/e['path']):
   setrow(p,'retain_derived','Exact file-byte alias of current reviewed formal UI control; keep fallback rebuild source synchronized.','reviews/ui-items-old-hero-review.json',sha(ROOT/p))
# Historical attribute previews are explicitly called historical by their READMEs.
prep=read('qdao_festival_refinement_20260910/prepared-derivative-review.json')
for prefix in prep.get('attribute_exports',{}).get('historical',[]):
 for p in ledger:
  if p==prefix or (prefix.endswith('/') and p.startswith(prefix)):
   if ledger[p]['decision']=='pending':setrow(p,'retain_record','Older attribute static/interactive draft or reference asset; README names it historical. Current 31 sprites and v10-preview are reviewed separately.','prepared-derivative-review.json')
for e in prep.get('records',[]):
 d=e['decision']
 if d=='retain_current_consistent_derivative':setrow(e['path'],'retain_derived','Current prepared pixels match reviewed source under existing target size/resize rule.','prepared-derivative-review.json',e.get('current_sha256'))
 elif d=='historical_native_reference_preserve':setrow(e['path'],'retain_record','Historical login native generation input; current background uses festival package.','prepared-derivative-review.json',e.get('current_sha256'))
 elif d in ['pending_scene_sync','pending_final_hero_source_refresh','update_from_current_authoritative_source']:setrow(e['path'],'pending_rebuild','Identified source-derived gap; close only after current publication.','prepared-derivative-review.json')
# Reviewed title is not a new invented logo; it keeps the accepted title and taiji identity.
for p in ['client_ui_refresh_20260908/additional/title_logo.png','client_ui_refresh_20260908/prepared/UI/Ugui/RefreshV8/title_logo.png']:
 if p in ledger:setrow(p,'retain','Root directly viewed current calligraphic title: jade plaque, warm gold letters and taiji identity remain clear; no extra festival decoration needed on this fixed brand asset.','root direct title_logo visual review',sha(ROOT/p))
# Scene protected alpha masks, old raw sources and archive contracts.
plan=read('qdao_festival_refinement_20260910/legacy-scene-sync-plan.json')
for r in plan.get('protected_original_sources',[]):setrow(r['path'],'retain_record',r['reason'],'legacy-scene-sync-plan.json')
for r in plan.get('classification_corrections_for_next_inventory',[]):
 if r.get('correct_role')=='functional_uniform_alpha_overlay_preserve':setrow(r['path'],'retain','Functional black alpha178 runtime dim mask; preserve every pixel. It is not review evidence.','legacy-scene-sync-plan.json',sha(ROOT/r['path']))
# Current overview artifacts are part of the rebuilt v11 package, not historical QA.
edgefinal=read('qdao_festival_refinement_20260910/edge_exports/final-verification.json')
if edgefinal.get('status')=='passed':
 for r in edgefinal.get('artifacts',[]):
  if r.get('path') in ['qdao_chibi_roster_v11/roster-overview.jpg','qdao_chibi_roster_v11/movement-overview.gif']:
   setrow(r['path'],'updated','Rebuilt package preview from current repaired frames/portraits, verified in final ZIP.','edge_exports/final-verification.json',r.get('sha256'))
# Published records override earlier pending or old review hashes. Exact publications only.
publications=['prelogin/publication.json','prepared-sync/publication.json','scenes-sync/publication.json','scenes-sync/server/publication.json','scenes-sync/hero-prepared/publication.json','component-overviews/publication.json','edge_exports/publication.json','v9-edges/publication.json']
for file in publications:
 j=read('qdao_festival_refinement_20260910/'+file)
 if 'published' not in j.get('status',''):continue
 for r in j.get('files',[]):
  p=r.get('path') or r.get('target');expected=r.get('after_sha256') or r.get('sha256') or r.get('published_sha256')
  if p and expected:setrow(p,'retain_derived' if r.get('before_sha256')==expected else 'updated','Current authorized refinement or synchronized derivative published and validated; see per-file provenance and backup.',file,expected)
rows=list(ledger.values());counts=Counter(r['decision'] for r in rows);pending=[r for r in rows if r['decision'].startswith('pending')]
result={'schema':'qdao.festival.decisions.v1','updated_utc':datetime.now(timezone.utc).isoformat(),'all_images_complete':False,'inventory_count':len(rows),'decision_counts':dict(counts),'pending_count':len(pending),'files':rows,'note':'Per-file ledger distinguishes retained historical records from current approved art. Pending entries remain open; count alone never completes the task.'}
(B/'decisions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(B/'remaining-decisions.json').write_text(json.dumps({'count':len(pending),'files':pending},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'counts':dict(counts),'pending':len(pending),'pending_roots':dict(Counter(p['path'].split('/')[0] for p in pending))},ensure_ascii=False))
