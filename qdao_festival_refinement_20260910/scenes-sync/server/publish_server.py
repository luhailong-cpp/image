"""Publish only approved server hero derivatives; no client operations."""
import argparse,copy,hashlib,json,shutil,time
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=lambda:datetime.now(timezone.utc).isoformat()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p):
 with Image.open(p) as im:
  im.load();d={'size':list(im.size),'mode':im.mode,'sha256':sha(p),'bytes':p.stat().st_size}
  if im.mode=='RGBA':d.update(alpha_sha256=hashlib.sha256(im.getchannel('A').tobytes()).hexdigest(),alpha_range=list(im.getchannel('A').getextrema()))
  return d
def merge(rel,fn):
 p=ROOT/rel
 for _ in range(5):
  raw=p.read_bytes();m=json.loads(raw.decode('utf-8-sig'));updated=fn(copy.deepcopy(m))
  if p.read_bytes()!=raw:time.sleep(.1);continue
  b=RUN/'before-metadata'/rel;b.parent.mkdir(parents=True,exist_ok=True)
  if not b.exists():b.write_bytes(raw)
  write(p,updated);return {'path':rel,'before_sha256':hashlib.sha256(raw).hexdigest(),'after_sha256':sha(p),'backup':b.relative_to(RUN).as_posix()}
 raise RuntimeError('Concurrent metadata edit: '+rel)
def guards(plan):
 for k,i in plan['inputs'].items():
  if sha(RUN/i['path'])!=i['sha256']:raise RuntimeError('Snapshot changed: '+k)
  if k in ('hero_new','base_svg','controls_svg','labels_svg') and sha(ROOT/i['source_repository_path'])!=i['sha256']:raise RuntimeError('Current input changed: '+k)
def publish():
 if (RUN/'publication.json').exists():raise RuntimeError('Already published; use verify')
 plan=read(RUN/'plan.json');v=read(RUN/'staged-validation.json');a=read(RUN/'visual-approval.json')
 assert v['status']=='ready_for_visual_review' and not v['errors'] and a['status']=='passed'
 approved={f['path']:f['sha256'] for f in a['files']};guards(plan)
 assert len(v['files'])==15 and len(approved)==15
 for f in v['files']:
  assert approved[f['path']]==f['sha256']==sha(RUN/f['staged'])
  assert sha(ROOT/f['path'])==f['before_sha256'],'Concurrent target changed: '+f['path']
 write(RUN/'publication-journal.json',{'status':'publishing','started_at_utc':now(),'target_count':15})
 rows=[]
 for f in v['files']:
  if f['decision']!='retain_unchanged_control_layer':shutil.copyfile(RUN/f['staged'],ROOT/f['path'])
  rows.append({'path':f['path'],'role':f['role'],'decision':f['decision'],'before_sha256':f['before_sha256'],'after_sha256':sha(ROOT/f['path']),'size':f['size'],'mode':f['mode'],'bytes':f['bytes'],'alpha_sha256':f.get('alpha_sha256'),'backup':f['backup'],'alpha_exact':f['alpha_exact'],'outside_hero_rectangle_exact':f['outside_hero_rectangle_exact'] if f['path']!=plan['stale_prepared_alias'] else None,'stale_prepared_alias_updated_to_current_ui':f['path']==plan['stale_prepared_alias'],'changed_pixels_against_current_composite':f['changed_pixels'],'visual_status':'passed','current_inputs':'plan.json','hero_sha256':plan['inputs']['hero_new']['sha256'],'background_sha256':plan['inputs']['retained_server_city']['sha256'],'client_written':False})
 local_record='../qdao_festival_refinement_20260910/scenes-sync/server/publication.json'
 metadata=[]
 def layer(m):
  m.setdefault('source_revision_history',[]).append({'sources':m.get('sources'),'outputs':m.get('outputs'),'source_builder':m.get('source_builder'),'backup':'../qdao_festival_refinement_20260910/scenes-sync/server/before-metadata/q_daoist_login_ui_uncropped_highres_final_layers/manifest_native_q5.json'})
  by={r['path']:r for r in rows}
  for o in m['outputs']:
   r=by[o['path']];o.update(sha256=r['after_sha256'],bytes=r['bytes'],hero_source_sha256=r['hero_sha256'],current_publication=local_record)
  m['source_builder']='qdao_festival_refinement_20260910/scenes-sync/server/compose_server.mjs'
  m['current_input_snapshot']='qdao_festival_refinement_20260910/scenes-sync/server/plan.json'
  m['sources']=[{'path':'qdao_chibi_game_pack_v4/hero-transparent_1024.png','sha256':plan['inputs']['hero_new']['sha256'],'size':[1024,1024],'role':'current_corrected_transparent_hero'},{'path':'qdao_festival_refinement_20260910/scenes-sync/server/current-inputs/retained_server_city.png','sha256':plan['inputs']['retained_server_city']['sha256'],'size':[2560,1080],'role':'retained_approved_server_background_snapshot'}]
  m['staged_only']=False;m['hero_rgb_refinement']={'record':local_record,'hero_alpha_unchanged':True,'all_layer_alpha_unchanged':True,'svg_layout_and_labels_unchanged':True,'background_unchanged':True,'client_written':False};return m
 metadata.append(merge('q_daoist_login_ui_uncropped_highres_final_layers/manifest_native_q5.json',layer))
 def v5(m):
  for e in m['screens']:
   if e['id']=='02_server_select':
    e.setdefault('source_history',[]).append({'source':copy.deepcopy(e['source']),'export':copy.deepcopy(e['export']),'recipe':e['recipe'],'backup':'../qdao_festival_refinement_20260910/scenes-sync/server/before/qdao_ui_redesign_v5/source/02_server_select.png'})
    for kind in ('source','export'):e[kind].update(info(ROOT/'qdao_ui_redesign_v5'/e[kind]['path']))
    e['creation_method']='v10_geometry_and_retained_scene_recomposed_with_current_corrected_hero'
    e['recipe']='../qdao_festival_refinement_20260910/scenes-sync/server/compose_server.mjs'
    e['current_input_snapshot']='../qdao_festival_refinement_20260910/scenes-sync/server/plan.json'
    e['current_export_provenance']=local_record
  m['server_hero_refinement']={'record':local_record,'screen_id':'02_server_select','background_unchanged':True,'text_and_controls_unchanged':True,'client_written':False};return m
 metadata.append(merge('qdao_ui_redesign_v5/manifest.json',v5))
 def prepared(m):
  m['server_hero_prepared_refresh']={'status':'repository_prepared_copy_updated','record':local_record,'client_checked':False,'client_written':False,'historical_client_status_unchanged':True,'records':[x for x in rows if x['path']==plan['stale_prepared_alias']]};return m
 metadata.append(merge('client_ui_refresh_20260908/assets_manifest.json',prepared))
 write(RUN/'publication.json',{'status':'published_pending_final_file_check','published_at_utc':now(),'files':rows,'metadata_updates':metadata,'images_changed':13,'control_files_retained':2,'visual_approval':'visual-approval.json','staged_validation':'staged-validation.json','client_written':False,'frozen_contracts_modified':False})
 verify()
def verify():
 pub=read(RUN/'publication.json');plan=read(RUN/'plan.json');guards(plan);errors=[]
 for f in pub['files']:
  i=info(ROOT/f['path'])
  if any(i[k]!=f[k] for k in ('size','mode','bytes')) or i['sha256']!=f['after_sha256']:errors.append('Output mismatch: '+f['path'])
  if f['mode']=='RGBA' and i['alpha_sha256']!=f['alpha_sha256']:errors.append('Alpha changed: '+f['path'])
  if sha(RUN/f['backup'])!=f['before_sha256']:errors.append('Backup mismatch: '+f['path'])
 write(RUN/'final-verification.json',{'status':'passed' if not errors else 'failed','verified_at_utc':now(),'files':15,'changed':13,'retained_controls':2,'rgba_alpha_exact':8,'errors':errors,'client_written':False})
 if errors:raise RuntimeError(str(errors))
 pub['status']='published_and_verified';pub['final_verification']='final-verification.json';write(RUN/'publication.json',pub)
 write(RUN/'publication-journal.json',{'status':'complete','completed_at_utc':now()})
 print(json.dumps({'status':pub['status'],'files':15,'images_changed':13,'control_files_retained':2,'errors':errors}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['publish','verify']);globals()[p.parse_args().action]()
