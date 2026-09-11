"""Prepare/publish only the explicitly approved 51-media 27 replacement.

inspect is read-only for production; prepare writes this repair folder only.
publish is never implicit and rechecks every approval, input and baseline hash.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,os,uuid
import numpy as np
from PIL import Image

PACK=Path(__file__).resolve().parents[1]
ROOT=PACK.parents[1]
STAGE=PACK/'staged-v2'
TARGET=ROOT/'qdao_chibi_roster_v11/27_ink_kite_ranger'
BASELINE=PACK/'production-baseline.json'
APPROVAL=STAGE/'processing/final-visual-approval.json'
DIRS=['S','SW','W','NW','N','NE','E','SE']
ROWS={'cardinal':['S','W','E','N'],'diagonal':['SW','NW','NE','SE']}
MEDIA=['portrait.png','walk-cardinal.png','walk-diagonal.png']+[f'walk/{d}/{name}' for d in DIRS for name in ['01.png','02.png','03.png','04.png','strip.png','walk.gif']]

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def safe(p,root):
 p=p.resolve();assert p.is_relative_to(root.resolve()),'Path escapes allowed directory';return p
def baseline():
 d=read(BASELINE);assert Path(d['target']).resolve()==TARGET.resolve();rows={r['path']:r for r in d['files']}
 assert len(rows)==len(d['files'])==99,'Unexpected production baseline'
 return rows
def baseline_check(rows):
 for name,r in rows.items():assert sha(safe(TARGET/name,TARGET))==r['sha256'],'Production changed since baseline: '+name
def approval_check():
 d=read(APPROVAL);assert d['schema']=='qdao.visual-approval.v1' and d['status']=='approved'
 assert isinstance(d.get('approved_utc'),str) and isinstance(d.get('reviewer'),str)
 assert len(d['files'])==51
 records={r['path']:r for r in d['files']};assert set(records)==set(MEDIA),'Approval must cover exactly the 51 relative media paths'
 for name,r in records.items():assert sha(safe(STAGE/name,STAGE))==r['sha256'],'Approved artifact changed: '+name
 return d
def rgba_sha(im):return hashlib.sha256(im.tobytes()).hexdigest()

def validate_media(base):
 """Independent PNG/GIF/strip/table and foot-anchor checks; no visual inference."""
 portrait=Image.open(base/'portrait.png');assert portrait.mode=='RGBA' and portrait.size==(1024,1024)
 records={};frame_hashes=[]
 for d in DIRS:
  frames=[];anchors=[]
  processing=read(base/'processing'/f'{d}.json')
  for i in range(1,5):
   p=base/'walk'/d/f'{i:02}.png';im=Image.open(p);assert im.mode=='RGBA' and im.size==(512,512)
   alpha=np.asarray(im.getchannel('A'));y,x=np.nonzero(alpha>8);assert len(y)
   anchor=[float(np.median(x[y>=np.percentile(y,90)])),int(y.max())]
   assert anchor[1]==471 and abs(anchor[0]-256)<=.5,f'{d}/{i}: foot anchor {anchor}'
   box=im.getchannel('A').getbbox();assert box[0]>0 and box[1]>0 and box[2]<512 and box[3]<512
   assert alpha.min()==0 and alpha.max()==255
   h=rgba_sha(im);assert h==processing['frames'][i-1]['rgba_sha256'];frame_hashes.append(h)
   frames.append(im.copy());anchors.append(anchor)
  strip=Image.open(base/'walk'/d/'strip.png');assert strip.mode=='RGBA' and strip.size==(2048,512)
  for i,im in enumerate(frames):assert strip.crop((i*512,0,(i+1)*512,512)).tobytes()==im.tobytes()
  gif=Image.open(base/'walk'/d/'walk.gif');assert gif.size==(512,512) and gif.n_frames==4
  duration=[]
  for i in range(4):gif.seek(i);duration.append(gif.info.get('duration'))
  assert duration==[120]*4
  for r in processing['outputs']:assert sha(base/r['path'])==r['sha256']
  records[d]={'foot_anchors':anchors,'gif_duration_ms':duration,'unique_frames':len(set(rgba_sha(im) for im in frames))}
 assert len(set(frame_hashes))==32,'Duplicate RGBA frames'
 for kind,directions in ROWS.items():
  sheet=Image.open(base/f'walk-{kind}.png');assert sheet.mode=='RGBA' and sheet.size==(2048,2048)
  for row,d in enumerate(directions):
   for col in range(4):assert sheet.crop((col*512,row*512,(col+1)*512,(row+1)*512)).tobytes()==Image.open(base/'walk'/d/f'{col+1:02}.png').tobytes()
 manifest=read(base/'manifest.json');assert len(manifest['files'])==51
 assert {r['path'] for r in manifest['files']}==set(MEDIA)
 for r in manifest['files']:assert sha(base/r['path'])==r['sha256']
 assert sha(base/'portrait.png')==read(base/'processing/portrait.json')['output_sha256']
 qc=read(base/'qc.json');assert not qc['errors'];assert qc['cross_direction_mean_height_ratio']<=1.10
 return {'status':'passed_numeric_validation','media':51,'unique_frames':32,'directions':records,'portrait_size':[1024,1024],'frame_size':[512,512]}

def nodes(value):
 if isinstance(value,dict):
  yield value
  for v in value.values():yield from nodes(v)
 elif isinstance(value,list):
  for v in value:yield from nodes(v)

def find_prompt(source_sha):
 """Match a final source's exact SHA to an actual recorded generation prompt."""
 matches=[]
 for path in sorted(PACK.glob('generation*.json'))+sorted((PACK/'sources').glob('*generation*.json')):
  data=read(path)
  for rec in nodes(data):
   if rec.get('sha256',rec.get('source_sha256'))!=source_sha or not isinstance(rec.get('prompt'),str):continue
   prompt=safe(PACK/rec['prompt'],PACK);assert prompt.is_file(),'Recorded prompt missing'
   if rec.get('prompt_sha256'):assert sha(prompt)==rec['prompt_sha256'],'Generation prompt changed'
   matches.append((prompt,path,rec))
 assert matches,'No source-SHA-matched generation prompt record: '+source_sha
 assert len({sha(item[0]) for item in matches})==1,'Conflicting prompt records for one source SHA'
 return matches[-1]

def inspect():
 rows=baseline();diff=[]
 for name,r in rows.items():
  path=TARGET/name
  if not path.exists() or sha(path)!=r['sha256']:diff.append(name)
 report={'status':'inspection_only','production_baseline_files':99,'production_differences':diff,
  'missing_media':[name for name in MEDIA if not (STAGE/name).is_file()],
  'approval_exists':APPROVAL.exists(),'production_written':False}
 write(PACK/'publisher-preflight.json',report);print(json.dumps(report));return 0

def prepare():
 rows=baseline();baseline_check(rows);approval=approval_check();approved_sha=sha(APPROVAL)
 numeric=validate_media(STAGE)
 release=PACK/('release-'+approved_sha[:12]);release.mkdir(parents=True,exist_ok=True)
 inputs={};payload={}
 def capture(src):
  src=safe(src,ROOT);inputs[src.relative_to(ROOT).as_posix()]=sha(src);return src
 def add(name,src):
  src=capture(src);dest=safe(release/name,release);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read_bytes());assert sha(dest)==sha(src);payload[name]=dest
 def doc(name,data):
  dest=safe(release/name,release);write(dest,data);payload[name]=dest
 def prose(name,text):
  dest=safe(release/name,release);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf-8');payload[name]=dest
 for name in MEDIA:add(name,STAGE/name)
 capture(BASELINE);capture(APPROVAL);capture(Path(__file__))
 originals={};sources={};prompt_names={};history_files={}
 for key in ['portrait']+DIRS:
  rec_path=STAGE/'processing'/f'{key}.json';capture(rec_path);rec=read(rec_path)
  source=safe(Path(rec['path']),PACK/'sources');assert sha(source)==rec['sha256']
  expected_name='portrait_raw.png' if key=='portrait' else f'walk_{key}_2x2.png';assert source.name==expected_name
  prompt,generation,generation_record=find_prompt(rec['sha256']);capture(prompt);capture(generation)
  originals[key]=copy.deepcopy(rec);new=copy.deepcopy(rec)
  canonical_prompt='portrait.txt' if key=='portrait' else f'walk_{key}_2x2.txt'
  add('sources/'+expected_name,source);add('prompts/'+canonical_prompt,prompt);prompt_names[key]='prompts/'+canonical_prompt
  new['staging_source_path']=new['path'];new['path']=str((TARGET/'sources'/expected_name).resolve())
  new['prompt_file']=str((TARGET/'prompts'/canonical_prompt).resolve());new['prompt_sha256']=sha(prompt)
  new['generation_record']='processing/generation-history/'+generation.name
  new['visual_approval']={'status':'approved','record':'processing/final-visual-approval.json','sha256':approved_sha}
  sources[key]=new;doc('processing/'+key+'.json',new)
  history_files[generation.name]=generation
 for name,path in history_files.items():doc('processing/generation-history/'+name,{'original_record_path':str(path.resolve()),'original_sha256':sha(path),'record':read(path)})
 for name in ['scale-profile.json','frame-transforms.json']:add('processing/'+name,STAGE/'processing'/name)
 doc('processing/sources.json',sources)
 add('processing/final-visual-approval.json',APPROVAL)
 doc('processing/artifact-validation.json',numeric)
 # Current compatibility aliases are derived exports, explicitly not native raw art.
 assembly={}
 for kind,directions in ROWS.items():
  sheet=f'walk-{kind}.png';alias=f'sources/{kind}_assembled.png';add(alias,STAGE/sheet)
  record={'kind':'deterministic_assembly_of_approved_processed_frames','native_generation':False,
   'size':[2048,2048],'path':str((TARGET/alias).resolve()),'sha256':sha(STAGE/sheet),
   'row_order':directions,'source_records':{d:'processing/'+d+'.json' for d in directions},
   'note':'Compatibility 4x4 sheet. Native generated sources are the separate 2x2 inputs in sources/walk_DIRECTION_2x2.png.'}
  assembly[kind]=record;doc(f'processing/{kind}-pipeline-meta.json',record)
  text=f'Deterministic compatibility assembly of the new approved 512px RGBA frames; rows {", ".join(directions)}, four frames per row. This is not native generated raw art. See processing/sources.json for the eight native 2x2 inputs.\n'
  prose(f'prompts/{kind}_assembled.txt',text);prose(f'processing/{kind}-prompt-used.txt',text)
 doc('sources/assembly.json',assembly)
 doc('processing/portrait-pipeline-meta.json',sources['portrait']);add('processing/portrait-prompt-used.txt',find_prompt(sources['portrait']['sha256'])[0])
 manifest=read(capture(STAGE/'manifest.json'));manifest['sources']=sources;manifest['status']='published_visual_and_numeric_verified'
 manifest['visual_approval']={'path':'processing/final-visual-approval.json','sha256':approved_sha}
 manifest['compatibility_assembly']=assembly;manifest['current_rebuild_workflow']='qdao_cutout_edge_repair_20260911/27/tools/process_new_batch.py -> repair-folder staging -> visual approval -> publish_approved_batch.py'
 doc('manifest.json',manifest)
 qc=read(capture(STAGE/'qc.json'));qc['status']='passed_visual_and_numeric_qc';qc['visual_review']={'status':'approved','record':'processing/final-visual-approval.json','sha256':approved_sha};doc('qc.json',qc)
 status='''# 27 墨鸢：本轮交付已完成\n\n立绘、八向各四帧、八条 strip、八个 GIF 与两张 4×4 表共 51 个媒体已完成当前 SHA 的视觉和机械验收。客户端未导入。\n\n当前原画在 sources/portrait_raw.png 与 sources/walk_DIRECTION_2x2.png；原生尺寸逐份记录，1024/512/2048 为处理后的导出尺寸。sources/cardinal_assembled.png 与 diagonal_assembled.png 是新帧拼接的兼容表，不是原生生图。\n\n当前重建入口为本轮 qdao_cutout_edge_repair_20260911/27/tools/process_new_batch.py：先输出修复目录暂存，复核当前 SHA，再由同目录 publish_approved_batch.py 受保护发布。旧 assemble_directions.py、supplement_manifest.py 与旧流水线属于历史流程，不能不经复核覆盖当前成品。旧 source/ 内 raw 和 sources/ 内 rejected 候选保留为历史资料，不是当前原画。\n\n验收：processing/final-visual-approval.json、processing/artifact-validation.json、qc.json。来源：processing/sources.json 和逐方向处理记录。\n'''
 prose('STATUS.md',status);prose('README.md',status)
 # Freeze an auditable pending plan, without changing any production file.
 for path,s in inputs.items():assert sha(ROOT/path)==s,'Input changed during preparation: '+path
 baseline_check(rows)
 entries=[]
 for i,(name,path) in enumerate(sorted(payload.items())):
  existing=TARGET/name
  if name not in rows:assert not existing.exists(),'Unbaselined target already exists: '+name
  entries.append({'path':name,'release_path':path.relative_to(ROOT).as_posix(),'output_sha256':sha(path),
   'before_sha256':rows[name]['sha256'] if name in rows else None,
   'backup':'qdao_cutout_edge_repair_20260911/27/backups/'+f'{i:03d}'+Path(name).suffix})
 plan={'status':'prepared_not_published','prepared_utc':now(),'target':str(TARGET),'release':str(release),
  'approval':str(APPROVAL),'approval_sha256':approved_sha,'baseline_sha256':sha(BASELINE),'inputs':inputs,
  'files':entries,'historical_unchanged':{name:r['sha256'] for name,r in rows.items() if name not in payload},'numeric_validation':numeric}
 write(PACK/'publication-plan.json',plan)
 print(json.dumps({'status':plan['status'],'files':len(entries),'approved_media':51,'native_sources':9,'production_written':False}))

def publish():
 plan_path=PACK/'publication-plan.json';plan=read(plan_path);assert plan['status']=='prepared_not_published'
 assert sha(BASELINE)==plan['baseline_sha256'];rows=baseline();baseline_check(rows);approval_check()
 assert sha(APPROVAL)==plan['approval_sha256']
 for name,s in plan['inputs'].items():assert sha(ROOT/name)==s,'Frozen input changed: '+name
 report_path=PACK/'published.json';assert not report_path.exists(),'Publication already started; inspect its report instead of rerunning'
 # Complete backups of every overwritten file before the first replacement.
 for r in plan['files']:
  target=safe(TARGET/r['path'],TARGET);release=safe(ROOT/r['release_path'],PACK)
  assert sha(release)==r['output_sha256']
  if r['before_sha256'] is None:assert not target.exists()
  else:
   assert sha(target)==r['before_sha256'];backup=safe(ROOT/r['backup'],PACK/'backups');backup.parent.mkdir(parents=True,exist_ok=True)
   if backup.exists():assert sha(backup)==r['before_sha256']
   else:
    with backup.open('xb') as f:f.write(target.read_bytes())
   assert sha(backup)==r['before_sha256']
 report={'status':'publishing','started_utc':now(),'plan_sha256':sha(plan_path),'files':[]}
 write(report_path,report)
 try:
  for r in plan['files']:
   target=safe(TARGET/r['path'],TARGET);target.parent.mkdir(parents=True,exist_ok=True)
   before=r['before_sha256']
   assert (sha(target)==before) if before is not None else (not target.exists()),'Concurrent target change'
   data=(ROOT/r['release_path']).read_bytes();assert hashlib.sha256(data).hexdigest()==r['output_sha256']
   temp=target.with_name(target.name+'.'+uuid.uuid4().hex[:8]+'.publish-tmp')
   with temp.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
   assert (sha(target)==before) if before is not None else (not target.exists()),'Concurrent target change during temp write'
   os.replace(temp,target);assert sha(target)==r['output_sha256']
   report['files'].append({**r,'actual_sha256':sha(target),'atomic_replace':True});write(report_path,report)
  numeric=validate_media(TARGET)
  manifest=read(TARGET/'manifest.json')
  for key,r in manifest['sources'].items():
   assert sha(Path(r['path']))==r['sha256'];assert sha(Path(r['prompt_file']))==r['prompt_sha256']
   assert safe(Path(r['path']),TARGET/'sources').is_file();assert safe(Path(r['prompt_file']),TARGET/'prompts').is_file()
  for kind in ROWS:assert sha(TARGET/'sources'/f'{kind}_assembled.png')==sha(TARGET/f'walk-{kind}.png')
  for name,s in plan['historical_unchanged'].items():assert sha(TARGET/name)==s,'Historical file changed: '+name
  for r in plan['files']:assert sha(TARGET/r['path'])==r['output_sha256']
  report.update(status='published_and_verified',completed_utc=now(),numeric_validation=numeric,
   visual_approval_sha256=plan['approval_sha256'])
 except BaseException as e:
  report.update(status='stopped_due_to_error',error=str(e),stopped_utc=now());write(report_path,report);raise
 report['native_sources_and_prompts_verified']=9;report['historical_files_preserved']=len(plan['historical_unchanged']);report['client_accessed']=False;report['git_modified']=False
 write(report_path,report);print(json.dumps({'status':report['status'],'files':len(report['files']),'approved_media':51}))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['inspect','prepare','publish']);args=parser.parse_args()
 {'inspect':inspect,'prepare':prepare,'publish':publish}[args.command]()
