"""Publish only visually accepted RGB-only v9 boundary repairs, then sync current indexes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,subprocess,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
V9=ROOT/'qdao_character_diversity_v9';PACK=ROOT/'q_daoist_character_pack_4096'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def backup(p):
 target=HERE/'before'/p.relative_to(ROOT)
 target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():shutil.copy2(p,target)
 return target
def rel(p):return p.relative_to(ROOT).as_posix()
def contract(old,new,allow_hidden=False):
 a=np.array(Image.open(old));b=np.array(Image.open(new))
 assert a.shape==b.shape and a.shape[2]==4
 assert np.array_equal(a[:,:,3],b[:,:,3]),str(new)
 hidden_changed=int(np.any(a[a[:,:,3]==0]!=b[a[:,:,3]==0],axis=1).sum())
 if not allow_hidden:assert hidden_changed==0,str(new)
 return {'alpha_changed_pixels':0,'transparent_rgba_changed_pixels':hidden_changed,'alpha_sha256':hashlib.sha256(b[:,:,3].tobytes()).hexdigest(),'changed_rgb_pixels':int(np.any(a[:,:,:3]!=b[:,:,:3],axis=2).sum()),'size':[b.shape[1],b.shape[0]],'mode':'RGBA'}
def main():
 now=datetime.now(timezone.utc).isoformat()
 assert not (HERE/'publication.json').exists(),'Publication exists; run verify_current.py'
 stage=read(HERE/'stage.json')['records']; initial=read(ROOT/'qdao_festival_refinement_20260910/reviews/v9-pets-style-review.json')
 sources=[r for r in stage if r['path'].startswith('q_daoist_character_pack_4096/')]
 needs={r['path'] for r in initial['files'] if r['kind']=='v9_authoritative_static' and r['status']=='needs_edit'}
 assert len(sources)==19 and {r['path'] for r in sources}==needs
 reviews={r['path']:r for r in read(HERE/'visual-approval.json')['records']}
 for r in sources:
  v=reviews[r['path']];assert v['status']=='accepted' and v['output_sha256']==r['output_sha256']
  assert sha(ROOT/r['path'])==r['source_sha256'] and sha(ROOT/r['staged_path'])==r['output_sha256']
  assert sha(ROOT/r['processor'])==r['processor_sha256']
  for e in v['evidence']:assert sha(ROOT/e['path'])==e['sha256']
  contract(ROOT/r['before_path'],ROOT/r['staged_path'])
 hero=next(r for r in stage if r['character_id']=='hero1024')
 assert sha(ROOT/hero['path'])==hero['output_sha256'];contract(ROOT/hero['before_path'],ROOT/hero['path'])
 for r in initial['files']:
  if r['status']=='retained':assert sha(ROOT/r['path'])==r['sha256'],'Retained file changed: '+r['path']
 meta=[V9/'visual_qa.json',V9/'manifest.json',PACK/'manifest.json',V9/'compatibility_map.json',V9/'validation.json',V9/'completion.json',V9/'followup_completion.json',V9/'prepared_sync.json',V9/'roster_overview.png',V9/'build_manifest.py',V9/'build_overview.py',ROOT/'qdao_asset_refresh_v6/hero_compat_manifest.json',ROOT/'qdao_asset_refresh_v6/build_hero_compat.py',ROOT/'client_ui_refresh_20260908/assets_manifest.json']
 for p in meta:backup(p)
 prep_before=read(V9/'prepared_sync.json')
 for r in prep_before['records']:backup(ROOT/r['output'])
 m=read(V9/'manifest.json');assert len(m['assets'])==24
 oldm={r['path']:r['sha256'] for r in m['assets']}
 for r in sources:assert oldm[Path(r['path']).name]==r['source_sha256']
 hc=read(ROOT/'qdao_asset_refresh_v6/hero_compat_manifest.json')
 canonical=next(r for r in sources if r['path'].endswith('/00_reference_topright_boy_transparent_4096.png'))
 assert len(hc['assets'])==9
 for r in hc['assets']:assert sha(ROOT/r['path'])==canonical['source_sha256'];backup(ROOT/r['path'])
 pub=[]
 for r in sources:
  shutil.copy2(ROOT/r['staged_path'],ROOT/r['path'])
  pub.append({**r,'kind':'v9_source','status':'published','published_utc':now,'visual_review':'qdao_festival_refinement_20260910/v9-edges/visual-approval.json'})
 for r in hc['assets']:
  p=ROOT/r['path']
  if r['path'] not in needs:
   shutil.copy2(ROOT/canonical['staged_path'],p)
   pub.append({'path':r['path'],'kind':'verified_hero_4096_alias','status':'published','source_sha256':canonical['source_sha256'],'output_sha256':sha(p),'before_path':rel(HERE/'before'/r['path']),'canonical':canonical['path'],'visual_review':'qdao_festival_refinement_20260910/v9-edges/visual-approval.json',**contract(HERE/'before'/r['path'],p)})
 pub.append({**hero,'kind':'hero_1024_fixed_canvas','status':'published','visual_review':'qdao_festival_refinement_20260910/v9-edges/hero1024-visual-approval.json'})
 visual=[]
 initial_sources={r['path']:r for r in initial['files'] if r['kind']=='v9_authoritative_static'}
 bypath={r['path']:r for r in sources}
 pointer='qdao_festival_refinement_20260910/v9-edges/current-visual-review.json'
 for row in m['assets']:
  p=PACK/row['path'];full=rel(p);im=Image.open(p);a=np.array(im);digest=sha(p)
  row.update(sha256=digest,bytes=p.stat().st_size,strong_chroma_candidates=int(((a[:,:,0]>200)&(a[:,:,1]<100)&(a[:,:,2]>200)&(a[:,:,3]>0)).sum()))
  evidence=reviews.get(full)
  if full in bypath:
   r=bypath[full]
   chain={'record':'qdao_festival_refinement_20260910/v9-edges/publication.json','review':pointer,'before_sha256':r['source_sha256'],'output_sha256':digest,'alpha_unchanged':True,'date_utc':now,'scope':'transparent-boundary RGB only; accepted costume and small festival accents retained'}
   row['festival_edge_refinement']=chain
   rp=PACK/row['record']
   if rp.parent==PACK/'records':
    backup(rp);rr=read(rp);assert rr['sha256']==r['source_sha256'];rr.update(sha256=digest,festival_edge_refinement=chain);dump(rp,rr)
   visual.append({**evidence,'sha256':digest,'current_status':'accepted_after_rgb_edge_refinement'})
  else:
   ir=initial_sources[full];assert ir['status']=='retained' and digest==ir['sha256']
   visual.append({'path':full,'character_id':ir.get('character_id'),'sha256':digest,'current_status':'retained_accepted','review':'qdao_festival_refinement_20260910/reviews/v9-pets-style-review.json','reason':ir.get('reason',ir.get('rationale','Retained after actual current style review; intentional colors protected.'))})
 m['current_visual_review']=pointer;m['festival_refinement']={'date_utc':now,'changed_sources':19,'preserved_sources':5,'style':'道家Q版；春节／元宵／中秋点缀适量，沿用已有法器、红绳、莲灯、月簪；直发和角色身份保留','report':'qdao_character_diversity_v9/festival_edge_refinement.json','historical_visual_qa_preserved':True}
 dump(HERE/'current-visual-review.json',{'status':'passed','reviewed_utc':now,'scope':'24 current static v9 formal sources, 19 RGB edge refined / 5 retained','historical_visual_qa':'qdao_character_diversity_v9/visual_qa.json','historical_visual_qa_rewritten':False,'records':visual})
 dump(V9/'manifest.json',m);dump(PACK/'manifest.json',m)
 comp=read(V9/'compatibility_map.json')
 for row in comp['mapping']:row['new_sha256']=sha(ROOT/row['new_path'])
 comp['current_refinement']='qdao_character_diversity_v9/festival_edge_refinement.json';comp['current_hashes_updated_utc']=now;dump(V9/'compatibility_map.json',comp)
 for row in hc['assets']:
  row.setdefault('historical_compatibility_export_sha256',row['sha256']);row['sha256']=sha(ROOT/row['path']);row['bytes']=(ROOT/row['path']).stat().st_size
  row['source_sha256']=hero['output_sha256']
  row['method']='Ancestral LANCZOS compatibility export, followed by published v8 exposure refinement and fixed-canvas RGB-only boundary cleanup; current 4096 Alpha preserved, not resampled from current 1024.'
  row['current_canonical_4096']=canonical['path']
  row['refinement_chain']={'historical_export_sha256':row['historical_compatibility_export_sha256'],'v8_exposure_output_sha256':canonical['source_sha256'],'current_output_sha256':canonical['output_sha256'],'current_1024_source_sha256':hero['output_sha256'],'alpha_unchanged_in_current_refinement':True,'report':'qdao_festival_refinement_20260910/v9-edges/publication.json'}
 hc['current_refinement']='qdao_character_diversity_v9/festival_edge_refinement.json';hc['current_hashes_updated_utc']=now;dump(ROOT/'qdao_asset_refresh_v6/hero_compat_manifest.json',hc)
 subprocess.run([sys.executable,'-B',str(V9/'sync_prepared.py')],cwd=ROOT,check=True)
 prepared=read(V9/'prepared_sync.json');oldprep={r['output']:r for r in prep_before['records']};changed=[]
 for row in prepared['records']:
  p=ROOT/row['output'];old=HERE/'before'/row['output']
  stats=contract(old,p,allow_hidden=True)
  if sha(old)!=sha(p):
   changed.append({'path':row['output'],'kind':'prepared_1024','status':'published','source':row['source'],'current_4096_source_sha256':row['source_sha256'],'source_sha256':sha(old),'output_sha256':sha(p),'before_path':rel(old),'method':'Full RGBA LANCZOS resample of reviewed current 4096 source; pre/post Alpha exact',**stats})
  else:assert stats['changed_rgb_pixels']==0
 assert len(changed)==17
 pub.extend(changed)
 prepared['current_refinement']={'date_utc':now,'changed':17,'retained':5,'all_alpha_unchanged':True,'report':'qdao_character_diversity_v9/festival_edge_refinement.json'}
 dump(V9/'prepared_sync.json',prepared)
 op=V9/'build_overview.py';txt=op.read_text(encoding='utf-8');txt=txt.replace('00 与额外主角参考保持原样','00 与额外主角参考造型保留');op.write_text(txt,encoding='utf-8')
 subprocess.run([sys.executable,'-B',str(op)],cwd=ROOT,check=True)
 # Stop legacy entry points from replacing fixed-canvas refinements or falsifying historical QA.
 for p in [V9/'build_manifest.py',ROOT/'qdao_asset_refresh_v6/build_hero_compat.py']:
  txt=p.read_text(encoding='utf-8');needle='def main():\n'
  guard="def main():\n    current = Path(__file__).resolve().parents[1] / 'qdao_character_diversity_v9/festival_edge_refinement.json'\n    if current.exists():\n        import runpy\n        runpy.run_path(str(current.parent.parent / 'qdao_festival_refinement_20260910/v9-edges/verify_current.py'), run_name='__main__')\n        return\n"
  assert needle in txt;txt=txt.replace(needle,guard,1);p.write_text(txt,encoding='utf-8')
 report={'status':'published','completed_utc':now,'source_count':19,'prepared_count':17,'hero_aliases_outside_v9':7,'hero_fixed_canvas_1024':1,'changed_png_count':len(pub),'all_alpha_unchanged':True,'all_canvas_and_identity_preserved':True,'actual_client_written':False,'new_art_generation':False,'historical_visual_qa_unchanged_sha256':sha(V9/'visual_qa.json'),'review':'qdao_festival_refinement_20260910/v9-edges/current-visual-review.json','review_sha256':sha(HERE/'current-visual-review.json'),'publication':'qdao_festival_refinement_20260910/v9-edges/publication.json','method':'Local same-image RGB donor fitting at transparent boundary; current canvases and all Alpha bytes preserved. Protected original purple characters/pet fur retained.'}
 dump(HERE/'publication.json',{'status':'published','published_utc':now,'count':len(pub),'records':pub,'retained_files':[{'path':r['path'],'sha256':r['sha256']} for r in initial['files'] if r['status']=='retained'],'overview':{'path':rel(V9/'roster_overview.png'),'sha256':sha(V9/'roster_overview.png'),'method':'Existing deterministic roster composition from current 22 source portraits'}})
 report['publication_sha256']=sha(HERE/'publication.json');dump(V9/'festival_edge_refinement.json',report)
 valid=read(V9/'validation.json');valid['current_validation_utc']=now;valid['visual_review']='passed; current hashes match v9-edges/current-visual-review.json; visual_qa.json remains historical'
 valid['festival_edge_refinement']={'report':'qdao_character_diversity_v9/festival_edge_refinement.json','report_sha256':sha(V9/'festival_edge_refinement.json'),'all_current_hashes_match':True,'all_alpha_unchanged':True,'changed_source_count':19,'prepared_count':17}
 valid['reviewed_color_candidates']=sum(r['strong_chroma_candidates'] for r in m['assets']);dump(V9/'validation.json',valid)
 comp=read(V9/'completion.json')
 for row in comp['artifacts']:row['sha256']=sha(V9/row['path'])
 comp['refinement_completed_utc']=now;comp['current_refinement']='festival_edge_refinement.json';comp['artifacts'].append({'path':'festival_edge_refinement.json','sha256':sha(V9/'festival_edge_refinement.json')});dump(V9/'completion.json',comp)
 follow=read(V9/'followup_completion.json')
 for row in follow['artifacts']:
  if row['path'] in ['qdao_character_diversity_v9/prepared_sync.json','qdao_character_diversity_v9/sync_prepared.py']:row['sha256']=sha(ROOT/row['path'])
 follow['portrait_refinement_completed_utc']=now;follow['portrait_refinement_record']='qdao_character_diversity_v9/festival_edge_refinement.json';dump(V9/'followup_completion.json',follow)
 print(json.dumps({'status':'published','png_count':len(pub),'sources':19,'prepared':17,'other_hero_aliases':7,'hero1024':1,'overview_refreshed':True}),flush=True)
if __name__=='__main__':main()
