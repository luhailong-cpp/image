"""Narrow, hash-guarded publication of two reviewed v9 portraits and metadata."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,sys,uuid
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REVIEW='qdao_cutout_edge_repair_20260911/v9/review.json'
EXPECTED={
 'q_daoist_character_pack_4096/manifest.json':'e18f114ec1dcf3e8caeab851716327a4a50fd41ac877d0a0f32986e051feb3a0',
 'qdao_character_diversity_v9/manifest.json':'e18f114ec1dcf3e8caeab851716327a4a50fd41ac877d0a0f32986e051feb3a0',
 'qdao_character_diversity_v9/compatibility_map.json':'becbb7fa73bbb8c5c57545d79a106e6ba801e7c410d5ebcf4d753500c599074f',
 'qdao_character_diversity_v9/validation.json':'db256254bf2b5afc8675b0b4f16f5ad88caf9dd89b5f8e19910d2104e6eacf70',
 'qdao_character_diversity_v9/visual_qa.json':'f96549bbe390a099b917cf91c5ddcc3780d744c132c99a9c04030d9dfe3cbfaa',
 'q_daoist_character_pack_4096/records/04_mountain_guardian_boy_transparent_4096.json':'1dec4503401954449c1fcbe0c632d8dd36213f1adc5f64d13add1e445b2a3c75',
 'q_daoist_character_pack_4096/records/14_short_hair_snow_summoner_girl_transparent_4096.json':'939b2a996bae999c6f62208cf456890511913f7f1a018486f7183ea96d502d17',
}
HISTORY={
 'qdao_character_diversity_v9/inherited_refinements.json':'687bba7eec092dce7c91757eef23077c2b83ea390cdaa56354834ce3c12df06e',
 'qdao_character_diversity_v9/final_edge_cleanup.json':'f020914b8e89325d9cdb6d7620c132806a290ddeeacae4427cf5d32f26bf64f3',
}
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def safe(p):
 p=p.resolve();assert p.is_relative_to(ROOT),'Path outside workspace';return p
def summary(r,review_sha):
 return {'status':'published','before_sha256':r['source_sha256'],'output_sha256':r['output_sha256'],
  'report':REVIEW,'report_sha256':review_sha,
  'processor':'qdao_cutout_edge_repair_20260911/v9/stage_expanded_edges.py',
  'changed_rgb_pixels':r['changed_rgb_pixels'],'regions':r['regions'],'protected_regions':r['protected_regions'],
  'alpha_unchanged':True,'outside_regions_unchanged':True,'unselected_rgb_unchanged':True,
  'protected_artwork_unchanged':True,'visual_review':'passed; complete reviewed contiguous edges; native 2x light/dark before-after review'}

def prepare():
 review=load(ROOT/REVIEW);assert review['status']=='staged_ready_to_publish'
 review_sha=sha(ROOT/REVIEW);rows=review['records'];by_id={Path(r['path']).stem:r for r in rows}
 for path,expected in {**EXPECTED,**HISTORY}.items():assert sha(ROOT/path)==expected,f'Concurrent metadata change: {path}'
 # Snapshot all other portrait hashes to prove this publication leaves them intact.
 others={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'q_daoist_character_pack_4096').glob('*.png') if p.stem not in by_id}
 items=[]
 for r in rows:
  source=safe(ROOT/r['path']);stage=safe(ROOT/r['staged_path'])
  assert sha(source)==r['source_sha256'];assert sha(stage)==r['output_sha256']
  items.append({'path':r['path'],'stage':r['staged_path'],'before_sha256':r['source_sha256'],
   'output_sha256':r['output_sha256'],'backup':f'qdao_cutout_edge_repair_20260911/v9/backups/source-{source.stem[:2]}.png','kind':'portrait'})
 metadata=[]
 for i,(path,expected) in enumerate(EXPECTED.items()):
  before=load(ROOT/path);after=copy.deepcopy(before)
  if path.endswith('/manifest.json'):
   count=0
   for entry,original in zip(after['assets'],before['assets']):
    if entry['id'] in by_id:
     r=by_id[entry['id']];assert entry['sha256']==r['source_sha256'];entry['sha256']=r['output_sha256'];entry['second_edge_cleanup']=summary(r,review_sha);count+=1
    else:assert entry==original
   assert count==2
  elif '/records/' in path:
   identifier=Path(path).stem;r=by_id[identifier]
   assert after['sha256']==r['source_sha256'];after['sha256']=r['output_sha256'];after['second_edge_cleanup']=summary(r,review_sha)
   for k in ('generation_export_sha256','raw_sha256','previous_sha256','inherited_refinement','final_edge_cleanup','processor_qc','final_visual_review'):
    assert after[k]==before[k],f'Historical field changed: {k}'
  elif path.endswith('compatibility_map.json'):
   count=0
   for entry,original in zip(after['mapping'],before['mapping']):
    identifier=Path(entry['new_path']).stem
    if identifier in by_id:
     r=by_id[identifier];assert entry['new_sha256']==r['source_sha256'];entry['new_sha256']=r['output_sha256'];entry['second_edge_cleanup']=summary(r,review_sha);assert entry['old_sha256']==original['old_sha256'];count+=1
    else:assert entry==original
   assert count==2
  elif path.endswith('visual_qa.json'):
   count=0
   for entry,original in zip(after['assets'],before['assets']):
    if entry['id'] in by_id:
     r=by_id[entry['id']];assert entry['sha256']==r['source_sha256'];entry['sha256']=r['output_sha256'];entry['second_edge_cleanup']=summary(r,review_sha);count+=1
    else:assert entry==original
   assert count==2
  elif path.endswith('validation.json'):
   after['second_edge_cleanup']={'status':'passed','count':2,'report':REVIEW,'report_sha256':review_sha,
    'all_alpha_unchanged':True,'all_outside_regions_unchanged':True,'all_protected_artwork_unchanged':True,
    'outputs':[{'path':r['path'],'sha256':r['output_sha256']} for r in rows]}
   after['visual_review']='passed; current hashes match visual_qa.json; second edge cleanup review appended for 04/14'
  else:raise AssertionError(path)
  stage=HERE/'staged'/'metadata'/f'{i:02d}-{Path(path).name}'
  dump(stage,after)
  item={'path':path,'stage':stage.relative_to(ROOT).as_posix(),'before_sha256':expected,'output_sha256':sha(stage),
   'backup':f'qdao_cutout_edge_repair_20260911/v9/backups/meta-{i:02d}.json','kind':'metadata'}
  items.append(item);metadata.append({'path':path,'current_fields_updated_only_for':['04','14']})
 # Back up every file before any original is replaced. Never overwrite a prior backup.
 for item in items:
  original=safe(ROOT/item['path']);backup=safe(ROOT/item['backup']);backup.parent.mkdir(parents=True,exist_ok=True)
  data=original.read_bytes();assert hashlib.sha256(data).hexdigest()==item['before_sha256']
  if backup.exists():assert sha(backup)==item['before_sha256'],'Existing backup differs'
  else:
   with backup.open('xb') as f:f.write(data)
  assert sha(backup)==item['before_sha256']
 plan={'status':'prepared_backed_up_no_production_writes','prepared_utc':now(),'review':REVIEW,'review_sha256':review_sha,
  'items':items,'untouched_portraits':others,'untouched_history':HISTORY,'metadata_scope':metadata}
 dump(HERE/'publication-plan.json',plan)
 print(json.dumps({'status':plan['status'],'files':len(items),'portraits':2,'metadata':len(metadata),'untouched_portraits':len(others)}))

def publish():
 plan=load(HERE/'publication-plan.json');assert sha(ROOT/plan['review'])==plan['review_sha256']
 report={'status':'publishing','started_utc':now(),'plan_sha256':sha(HERE/'publication-plan.json'),'files':[]}
 report_path=HERE/'published.json'
 assert not report_path.exists(),'Publication report already exists; do not repeat publication'
 for item in plan['items']:
  assert sha(ROOT/item['path'])==item['before_sha256'],f'Concurrent change: {item["path"]}'
  assert sha(ROOT/item['stage'])==item['output_sha256'];assert sha(ROOT/item['backup'])==item['before_sha256']
 for path,expected in {**plan['untouched_portraits'],**plan['untouched_history']}.items():assert sha(ROOT/path)==expected,f'Concurrent unrelated change: {path}'
 dump(report_path,report)
 try:
  for item in plan['items']:
   target=safe(ROOT/item['path']);staged=safe(ROOT/item['stage'])
   assert sha(target)==item['before_sha256'],f'Concurrent change immediately before replace: {target}'
   temp=safe(target.with_name(target.name+'.'+uuid.uuid4().hex[:8]+'.edge-tmp'))
   data=staged.read_bytes();assert hashlib.sha256(data).hexdigest()==item['output_sha256']
   with temp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
   assert sha(target)==item['before_sha256'],f'Concurrent change during temp write: {target}'
   os.replace(temp,target)
   actual=sha(target);assert actual==item['output_sha256']
   report['files'].append({**item,'actual_sha256':actual,'atomic_replace':True})
   dump(report_path,report)
  invariants=[]
  review=load(ROOT/plan['review'])
  for r in review['records']:
   item=next(x for x in plan['items'] if x['path']==r['path'])
   old=np.asarray(Image.open(ROOT/item['backup']).convert('RGBA'));new=np.asarray(Image.open(ROOT/r['path']).convert('RGBA'))
   assert old.shape==new.shape;assert np.array_equal(old[:,:,3],new[:,:,3])
   region=np.zeros(old.shape[:2],bool)
   for x0,y0,x1,y1 in r['regions']:region[y0:y1,x0:x1]=True
   assert np.array_equal(old[~region],new[~region])
   for x0,y0,x1,y1 in r['protected_regions']:assert np.array_equal(old[y0:y1,x0:x1],new[y0:y1,x0:x1])
   mask=np.asarray(Image.open(HERE/f'expanded-mask-{Path(r["path"]).name[:2]}.png'))>0
   assert np.array_equal(old[~mask],new[~mask])
   assert int((old[:,:,:3]!=new[:,:,:3]).any(axis=2).sum())==r['changed_rgb_pixels']
   invariants.append({'path':r['path'],'size':[new.shape[1],new.shape[0]],'all_alpha_identical':True,
    'changed_rgb_pixels':r['changed_rgb_pixels'],'outside_regions_changed':0,'unselected_pixels_changed':0,'protected_pixels_changed':0})
  for path,expected in {**plan['untouched_portraits'],**plan['untouched_history']}.items():assert sha(ROOT/path)==expected,f'Unrelated file changed: {path}'
  report.update({'status':'published_and_verified','completed_utc':now(),'portrait_invariants':invariants,
   'all_other_portraits_unchanged':len(plan['untouched_portraits']),'historical_records_unchanged':plan['untouched_history'],
   'git_modified':False,'actual_client_accessed':False,'actual_client_written':False,
   'review':plan['review'],'review_sha256':plan['review_sha256']})
  dump(report_path,report)
  print(json.dumps({'status':report['status'],'files':len(report['files']),'alpha_identical_portraits':len(invariants),'other_portraits_unchanged':len(plan['untouched_portraits'])}))
 except BaseException as error:
  report.update({'status':'stopped_due_to_error','error':str(error),'stopped_utc':now()});dump(report_path,report);raise

if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['prepare','publish']
 prepare() if sys.argv[1]=='prepare' else publish()
