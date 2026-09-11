"""Update only 04/14 repository-local prepared portraits, with exact guards."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os,uuid
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
EXPECTED={
 'client_ui_refresh_20260908/assets_manifest.json':'b50fe5df47bec9f7fefc27e782ec90e96aa84840049bdd495cb2bfad74517525',
 'qdao_character_diversity_v9/prepared_sync.json':'776e7df0fb00d9740eaa32d5d782166d514d6ec0ca3093958ec63f5c45b472b1',
}
BASELINE='client_ui_refresh_20260908/baseline.json'
BASELINE_SHA='455e6b52da61d3d21eba7bde83eb9b47f69b5573c50f2bddcb57831d57ecbf19'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
def backup(source,dest,expected):
 assert source.resolve().is_relative_to(ROOT)
 data=source.read_bytes();assert hashlib.sha256(data).hexdigest()==expected
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert sha(dest)==expected
 else:
  with dest.open('xb') as f:f.write(data)
 assert sha(dest)==expected
def replace(target,stage,before,after):
 assert target.resolve().is_relative_to(ROOT);assert stage.resolve().is_relative_to(ROOT)
 assert sha(target)==before,'Concurrent target change: '+str(target)
 data=stage.read_bytes();assert hashlib.sha256(data).hexdigest()==after
 temp=target.with_name(target.name+'.'+uuid.uuid4().hex[:8]+'.edge-tmp')
 with temp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 assert sha(target)==before,'Concurrent change during temp write: '+str(target)
 os.replace(temp,target);assert sha(target)==after

def main():
 assert not (HERE/'prepared-published.json').exists(),'Prepared sync already recorded'
 for name,s in EXPECTED.items():assert sha(ROOT/name)==s,'Concurrent metadata change: '+name
 assert sha(ROOT/BASELINE)==BASELINE_SHA
 review=read(HERE/'review.json');pub=read(HERE/'published.json');pub_sha=sha(HERE/'published.json');assert pub['status']=='published_and_verified'
 inv=read(ROOT/'client_ui_refresh_20260908/assets_manifest.json');sync=read(ROOT/'qdao_character_diversity_v9/prepared_sync.json')
 new_inv=copy.deepcopy(inv);new_sync=copy.deepcopy(sync);items=[];results=[]
 ids={r['path']:r for r in review['records']}
 old_by_source={r['source']:r for r in sync['records']};new_by_source={r['source']:r for r in new_sync['records']}
 mapping={r.get('source'):r for r in new_inv['records'] if r.get('category')=='profession_portrait'}
 for source,edge in ids.items():
  original=ROOT/source;assert sha(original)==edge['output_sha256']
  old=old_by_source[source];entry=mapping[source];target=ROOT/old['output'];target_sha=sha(target)
  assert target_sha==old['output_sha256']==entry['staged_sha256']
  assert old['source_sha256']==entry['source_sha256']==edge['source_sha256']
  im=Image.open(original);current=Image.open(target);assert im.mode==current.mode=='RGBA';assert im.size==(4096,4096);assert current.size==(1024,1024)
  desired=im.resize(current.size,Image.Resampling.LANCZOS)
  assert desired.getchannel('A').tobytes()==current.getchannel('A').tobytes()
  dest=HERE/'staged'/'prepared'/target.name;dest.parent.mkdir(parents=True,exist_ok=True);desired.save(dest,optimize=True)
  result_sha=sha(dest);bounds=list(desired.getchannel('A').getbbox())
  assert min(bounds[0],bounds[1],1024-bounds[2],1024-bounds[3])>4
  assert desired.getchannel('A').getextrema()==(0,255)
  lineage={'source_revision':'second_edge_cleanup_20260911','source_publication':'qdao_cutout_edge_repair_20260911/v9/published.json',
   'previous_source_sha256':old['source_sha256'],'previous_prepared_sha256':target_sha,
   'current_source_sha256':edge['output_sha256'],'output_sha256':result_sha,'all_alpha_unchanged':True,
   'record':'qdao_cutout_edge_repair_20260911/v9/prepared-published.json'}
  row=new_by_source[source];row.update(source_sha256=edge['output_sha256'],output_sha256=result_sha,
   subject_bounds=bounds,second_edge_cleanup_sync=lineage)
  entry.update(source_sha256=edge['output_sha256'],staged_sha256=result_sha,second_edge_cleanup_sync=lineage)
  for key in ['previous_prepared_sha256','historical_client_sha256','client_checked','client_sync_status']:
   assert row[key]==old[key]
  items.append({'path':old['output'],'stage':dest.relative_to(ROOT).as_posix(),'before_sha256':target_sha,'output_sha256':result_sha,
   'backup':f'qdao_cutout_edge_repair_20260911/v9/backups/prepared-{target.name[:2]}.png','kind':'prepared_portrait'})
  results.append({'source':source,'source_sha256':edge['output_sha256'],'output':old['output'],'actual_sha256':result_sha,
   'size':[1024,1024],'mode':'RGBA','alpha_range':[0,255],'subject_bounds':bounds,'all_alpha_identical_to_previous_prepared':True,
   'pixel_exact_to_current_source_resize':True,'method':'RGBA Image.Resampling.LANCZOS, optimize=True'})
 target_paths={r['output'] for r in results}
 other_prepared={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'client_ui_refresh_20260908/prepared/UI/qdao_v3/characters').glob('*.png') if p.relative_to(ROOT).as_posix() not in target_paths}
 for original,updated in zip(sync['records'],new_sync['records']):
  if original['source'] not in ids:assert original==updated
 for original,updated in zip(inv['records'],new_inv['records']):
  if original.get('source') not in ids:assert original==updated
  else:
   for key in ('client_sha256','baseline_sha256','status','client_verification'):assert original[key]==updated[key]
 for i,(path,data) in enumerate([('client_ui_refresh_20260908/assets_manifest.json',new_inv),('qdao_character_diversity_v9/prepared_sync.json',new_sync)]):
  stage=HERE/'staged'/'metadata'/f'prepared-meta-{i}.json';write(stage,data)
  items.append({'path':path,'stage':stage.relative_to(ROOT).as_posix(),'before_sha256':EXPECTED[path],
   'output_sha256':sha(stage),'backup':f'qdao_cutout_edge_repair_20260911/v9/backups/prepared-meta-{i}.json','kind':'prepared_metadata'})
 # Back up all four production files and the parent publication before any write.
 for item in items:backup(ROOT/item['path'],ROOT/item['backup'],item['before_sha256'])
 backup(HERE/'published.json',HERE/'backups'/'published-before-prepared.json',pub_sha)
 for item in items:assert sha(ROOT/item['path'])==item['before_sha256']
 for r in results:assert sha(ROOT/r['source'])==r['source_sha256']
 for path,s in other_prepared.items():assert sha(ROOT/path)==s
 report={'status':'publishing','started_utc':now(),'files':[],'sources':results,'actual_client_accessed':False,'actual_client_written':False}
 report_path=HERE/'prepared-published.json';write(report_path,report)
 try:
  for item in items:
   replace(ROOT/item['path'],ROOT/item['stage'],item['before_sha256'],item['output_sha256'])
   report['files'].append({**item,'actual_sha256':sha(ROOT/item['path']),'atomic_replace':True});write(report_path,report)
  for r in results:
   assert sha(ROOT/r['source'])==r['source_sha256'];assert sha(ROOT/r['output'])==r['actual_sha256']
   actual=Image.open(ROOT/r['output']).convert('RGBA');source=Image.open(ROOT/r['source']).convert('RGBA')
   assert actual.size==(1024,1024);assert actual.tobytes()==source.resize((1024,1024),Image.Resampling.LANCZOS).tobytes()
   item=next(x for x in items if x['path']==r['output']);old=Image.open(ROOT/item['backup']).convert('RGBA')
   assert actual.getchannel('A').tobytes()==old.getchannel('A').tobytes()
  for path,s in other_prepared.items():assert sha(ROOT/path)==s
  assert sha(ROOT/BASELINE)==BASELINE_SHA
  report.update(status='published_and_verified',completed_utc=now(),other_prepared_unchanged=other_prepared,historical_baseline_unchanged=True)
  write(report_path,report)
  assert sha(HERE/'published.json')==pub_sha,'Concurrent parent publication record change'
  pub['files'].extend(report['files']);pub['prepared_sync']={'status':'published_and_verified','count':2,
   'report':report_path.relative_to(ROOT).as_posix(),'report_sha256':sha(report_path),'sources':results,
   'other_prepared_unchanged':len(other_prepared),'historical_baseline_unchanged':True}
  write(HERE/'published.json',pub)
  print(json.dumps({'status':report['status'],'files':len(items),'sources':results,'other_prepared_unchanged':len(other_prepared)}))
 except BaseException as e:
  report.update(status='stopped_due_to_error',error=str(e));write(report_path,report);raise

if __name__=='__main__':main()
