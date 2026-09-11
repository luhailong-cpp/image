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
ORIGINAL_BASELINE=PACK/'production-baseline.json'
TRANSITION=PACK/'root-reviewed-baseline-transition.json'
BASELINE=PACK/'production-baseline-reviewed.json' if (PACK/'production-baseline-reviewed.json').exists() else ORIGINAL_BASELINE
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
 if BASELINE!=ORIGINAL_BASELINE:
  transition=read(TRANSITION);assert transition['schema']=='qdao.root-reviewed-baseline-transition.v1' and transition['status']=='root_reviewed'
  assert sha(ORIGINAL_BASELINE)==transition['original_baseline']['sha256']==sha(PACK/'production-baseline.original.json')
  assert sha(BASELINE)==transition['reviewed_baseline']['sha256']
  previous={r['path']:r for r in read(ORIGINAL_BASELINE)['files']};assert set(previous)==set(rows)
  updates={r['path']:r for r in transition['allowed_updates']}
  assert set(updates)=={'manifest.json','processing/scale-profile.json','prompts/walk_E_2x2.txt','prompts/walk_W_2x2.txt','qc.json','STATUS.md'}
  for name,row in rows.items():
   if name in updates:
    update=updates[name];assert previous[name]['sha256']==update['baseline_sha256'] and row['sha256']==update['actual_sha256']
    assert sha(safe(PACK/update['read_only_snapshot'],PACK/'production-drift-20260911'))==update['actual_sha256']==update['backup_sha256']
   else:assert row['sha256']==previous[name]['sha256'],'Unreviewed baseline change'
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

def assembled(rec):
 return bool(rec.get('assembled')) or rec.get('source_type')=='assembled_2x2_from_native_generations'

def real_prompt(rec):
 # Inline prompt prose is generation history, never a filesystem path.
 for field in ['prompt_file','prompt']:
  value=rec.get(field)
  if not isinstance(value,str) or len(value)>240 or '\n' in value or '\r' in value:continue
  try:
   path=safe(PACK/value,PACK)
   if not path.is_file():continue
  except (OSError,ValueError,AssertionError):continue
  if rec.get('prompt_sha256'):assert sha(path)==rec['prompt_sha256'],'Generation prompt changed'
  return path
 return None

def find_prompt(source_sha):
 """Prefer the nine final accepted input mappings; skip all inline prose."""
 final=PACK/'generation-final.json'
 generation_files=[final] if final.exists() else sorted(PACK.glob('generation*.json'))+sorted((PACK/'sources').glob('*generation*.json'))
 matches=[]
 for path in generation_files:
  data=read(path)
  candidates=data['records'] if path==final else nodes(data)
  for rec in candidates:
   if rec.get('sha256',rec.get('source_sha256'))!=source_sha:continue
   prompt=real_prompt(rec)
   if prompt is None and not assembled(rec):continue
   matches.append((prompt,path,rec))
 assert matches,'No source-SHA-matched final generation/prompt record: '+source_sha
 assert len({sha(item[0]) if item[0] is not None else None for item in matches})==1,'Conflicting prompt records for one source SHA'
 return matches[-1]

def remap_paths(value,mapping):
 if isinstance(value,dict):return {k:remap_paths(v,mapping) for k,v in value.items()}
 if isinstance(value,list):return [remap_paths(v,mapping) for v in value]
 if isinstance(value,str):return mapping.get(value,mapping.get(value.replace('\\','/'),value))
 return value

def validate_sources(base):
 """Verify copied provenance and reproduce composite input layouts without edits."""
 manifest=read(base/'manifest.json');sources=manifest['sources'];assert set(sources)==set(['portrait']+DIRS)
 for key,rec in sources.items():
  # During preparation these paths already name the intended production files.
  def artifact(value):
   path=safe(Path(value),TARGET);return safe(base/path.relative_to(TARGET),base)
  source=artifact(rec['path']);prompt=artifact(rec['prompt_file'])
  assert sha(source)==rec['sha256'] and sha(prompt)==rec['prompt_sha256']
  with Image.open(source) as im:assert list(im.size)==rec['native_size']
  assert read(base/'processing'/f'{key}.json')==rec
  for node in nodes(rec):
   for reference in node.get('reference_images',[]):
    reference_path=artifact(reference['path']);assert sha(reference_path)==reference['sha256']
    if reference.get('native_source'):
     native=artifact(reference['native_source']);assert sha(native)==reference['native_sha256']
     if reference.get('source_box'):
      assert Image.open(native).crop(reference['source_box']).convert('RGB').tobytes()==Image.open(reference_path).convert('RGB').tobytes()
    if reference.get('prompt_file'):assert sha(artifact(reference['prompt_file']))==reference['prompt_sha256']
    if reference.get('extraction_record'):assert sha(artifact(reference['extraction_record']))==reference['extraction_record_sha256']
    if isinstance(reference.get('evidence'),dict) and reference['evidence'].get('path'):
     assert sha(artifact(reference['evidence']['path']))==reference['evidence']['sha256']
  if not assembled(rec):continue
  lineage=rec['generation_lineage'];assert [r['frame'] for r in lineage['frames']]==[1,2,3,4]
  if lineage.get('spec_file'):assert sha(artifact(lineage['spec_file']))==lineage['spec_sha256']
  if lineage.get('assembler_file'):assert sha(artifact(lineage['assembler_file']))==lineage['assembler_sha256']
  raw_hashes=set()
  for raw in lineage['raw_artifacts']:
   path=artifact(raw['path']);raw_prompt=artifact(raw['prompt_file'])
   assert path.is_relative_to(base/'sources/frame-originals') and raw_prompt.is_relative_to(base/'prompts/frame-originals')
   assert sha(path)==raw['sha256'] and sha(raw_prompt)==raw['prompt_sha256']
   with Image.open(path) as im:assert list(im.size)==raw['native_size']
   raw_hashes.add(raw['sha256'])
  original=Image.open(source).convert('RGB');rebuilt=Image.new('RGB',original.size,(255,0,255))
  coverage=np.zeros((original.height,original.width),dtype=np.uint8)
  for frame in lineage['frames']:
   raw=artifact(frame['raw_source']);raw_prompt=artifact(frame['prompt_file'])
   assert sha(raw)==frame['raw_sha256'] and frame['raw_sha256'] in raw_hashes
   assert sha(raw_prompt)==frame['prompt_sha256']
   im=Image.open(raw);assert list(im.size)==frame['raw_native_size']
   l,t,r,b=frame['source_box'];x,y,right,bottom=frame['target_box']
   assert 0<=l<r<=im.width and 0<=t<b<=im.height
   assert 0<=x<right<=original.width and 0<=y<bottom<=original.height
   scale=frame['whole_canvas_scale'];assert scale>0
   assert abs((r-l)*scale-(right-x))<1e-8 and abs((b-t)*scale-(bottom-y))<1e-8
   tile=im.crop((l,t,r,b)).convert('RGB')
   if tile.size!=(right-x,bottom-y):tile=tile.resize((right-x,bottom-y),Image.Resampling.LANCZOS)
   rebuilt.paste(tile,(x,y));coverage[y:bottom,x:right]+=1
  assert np.all(coverage==1),'Composite cells overlap or leave an undocumented gap'
  assert rebuilt.tobytes()==original.tobytes(),'Composite source pixels do not match recorded raw-cell layout'
 return {'status':'passed_source_lineage_validation','processing_inputs':9,'composite_layouts_reproduced':sum(assembled(r) for r in sources.values())}

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
 final_generation=read(PACK/'generation-final.json')
 assert len(final_generation['records'])==9,'Require exactly nine final accepted processing-input records'
 assert len({r.get('sha256',r.get('source_sha256')) for r in final_generation['records']})==9
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
 if BASELINE!=ORIGINAL_BASELINE:
  capture(ORIGINAL_BASELINE);capture(PACK/'production-baseline.original.json');capture(TRANSITION)
  for update in read(TRANSITION)['allowed_updates']:capture(PACK/update['read_only_snapshot'])
 originals={};sources={};prompt_names={};history_files={};native_artifacts={};relocations={}
 # Current reference paths must resolve in the release, including raw-cell references.
 for key in ['portrait']+DIRS:
  original=safe(Path(read(STAGE/'processing'/f'{key}.json')['path']),PACK/'sources')
  final=str((TARGET/'sources'/original.name).resolve())
  relocations[str(original)]=final;relocations[original.relative_to(PACK).as_posix()]=final
 def archive_reference(value,expected,mapping,kind='image'):
  original=safe(PACK/value,PACK);assert sha(original)==expected,'Reference/history input changed: '+str(value);capture(original)
  existing=mapping.get(value,mapping.get(str(original),mapping.get(str(value).replace('\\','/'))))
  if existing is not None:return existing
  folder={'image':'sources/reference-originals','prompt':'prompts/reference-originals','record':'processing/generation-history/reference-records'}[kind]
  dest=folder+'/'+expected[:12]+'-'+original.name;add(dest,original);final=str((TARGET/dest).resolve())
  mapping[value]=final;mapping[str(original)]=final;mapping[original.relative_to(PACK).as_posix()]=final
  return final
 def archive_reference_chain(value,mapping):
  if isinstance(value,list):return [archive_reference_chain(v,mapping) for v in value]
  if not isinstance(value,dict):return value
  value=copy.deepcopy(value)
  if isinstance(value.get('reference_images'),list):
   refs=[]
   for ref in value['reference_images']:
    ref=copy.deepcopy(ref)
    for pathkey,hashkey,kind in [('path','sha256','image'),('native_source','native_sha256','image'),('prompt_file','prompt_sha256','prompt'),('extraction_record','extraction_record_sha256','record')]:
     if not ref.get(pathkey):continue
     # Some producer records provide an extraction path without its hash; freeze the actual file now.
     if not ref.get(hashkey):ref[hashkey]=sha(safe(PACK/ref[pathkey],PACK))
     ref[pathkey]=archive_reference(ref[pathkey],ref[hashkey],mapping,kind)
    evidence=ref.get('evidence')
    if isinstance(evidence,dict) and evidence.get('path'):
     evidence['path']=archive_reference(evidence['path'],evidence['sha256'],mapping,'record')
    refs.append(ref)
   value['reference_images']=refs
  origin=value.get('generation_origin')
  if isinstance(origin,dict):
   for pathkey,hashkey in [('record_file','record_sha256'),('reference_lineage_file','reference_lineage_sha256')]:
    if origin.get(pathkey) and origin.get(hashkey):origin[pathkey]=archive_reference(origin[pathkey],origin[hashkey],mapping,'record')
  return {k:archive_reference_chain(v,mapping) if k not in ['reference_images','generation_origin'] else v for k,v in value.items()}
 for key in ['portrait']+DIRS:
  rec_path=STAGE/'processing'/f'{key}.json';capture(rec_path);rec=read(rec_path)
  source=safe(Path(rec['path']),PACK/'sources');assert sha(source)==rec['sha256']
  expected_name='portrait_raw.png' if key=='portrait' else f'walk_{key}_2x2.png';assert source.name==expected_name
  prompt,generation,generation_record=find_prompt(rec['sha256']);capture(generation)
  composite=assembled(generation_record) or assembled(rec)
  if prompt is not None:capture(prompt)
  originals[key]=copy.deepcopy(rec);new=copy.deepcopy(rec)
  canonical_prompt='portrait.txt' if key=='portrait' else f'walk_{key}_2x2.txt'
  add('sources/'+expected_name,source)
  if prompt is not None:add('prompts/'+canonical_prompt,prompt)
  else:
   assert composite,'A native generated input requires an actual prompt file'
   prose('prompts/'+canonical_prompt,'Deterministic 2x2 layout of separately generated art cells. This is an assembly recipe, not an ImageGen prompt. See processing/'+key+'.json generation_lineage for native raw sources, source boxes, uniform scales, target boxes, and each actual generation prompt.\n')
  prompt_names[key]='prompts/'+canonical_prompt
  new['staging_source_path']=new['path'];new['path']=str((TARGET/'sources'/expected_name).resolve())
  new['prompt_file']=str((TARGET/'prompts'/canonical_prompt).resolve());new['prompt_sha256']=sha(release/'prompts'/canonical_prompt)
  new['generation_record']='processing/generation-history/'+generation.name
  new['source_type']=generation_record.get('source_type',rec.get('source_type','native_generated_art'))
  new['native_generation']=not composite
  if composite:
   new['assembled']=True;new['native_size_semantics']='assembled processing-input canvas, not one native generated image'
   lineage=copy.deepcopy(generation_record.get('generation_lineage',rec.get('generation_lineage')))
   assert isinstance(lineage,dict) and len(lineage['frames'])==4 and lineage['raw_artifacts'],'Assembled input requires exact per-frame native lineage'
   local_map=copy.deepcopy(relocations)
   if lineage.get('spec_file'):
    spec=safe(PACK/lineage['spec_file'],PACK);assert sha(spec)==lineage['spec_sha256']
    dest='processing/generation-history/'+key+'-assembly-spec.json';add(dest,spec)
    local_map[lineage['spec_file']]=str((TARGET/dest).resolve());local_map[str(spec)]=str((TARGET/dest).resolve())
   if lineage.get('assembler_sha256'):
    helper=PACK/'tools/assemble_direction_inputs.py';assert sha(helper)==lineage['assembler_sha256']
    dest='processing/generation-history/assemble_direction_inputs.py';add(dest,helper)
    lineage['assembler_file']=str((TARGET/dest).resolve())
   for index,raw in enumerate(lineage['raw_artifacts']):
    raw_path=safe(PACK/raw['path'],PACK);assert sha(raw_path)==raw['sha256'];capture(raw_path)
    with Image.open(raw_path) as raw_im:assert list(raw_im.size)==raw['native_size']
    raw_prompt=real_prompt(raw);assert raw_prompt is not None,'Native per-frame prompt missing';capture(raw_prompt)
    raw_dest='sources/frame-originals/'+key+'-'+str(index).zfill(2)+'-'+raw_path.name
    prompt_dest='prompts/frame-originals/'+key+'-'+str(index).zfill(2)+'-'+raw_prompt.name
    add(raw_dest,raw_path);add(prompt_dest,raw_prompt)
    for original,final in [(raw['path'],str((TARGET/raw_dest).resolve())),(str(raw_path),str((TARGET/raw_dest).resolve())),(raw.get('prompt_file',raw.get('prompt')),str((TARGET/prompt_dest).resolve())),(str(raw_prompt),str((TARGET/prompt_dest).resolve()))]:
     if isinstance(original,str):local_map[original]=final;local_map[original.replace('\\','/')]=final
    native_artifacts[raw['sha256']]={'path':raw_dest,'sha256':raw['sha256'],'native_size':raw['native_size']}
   for frame in lineage['frames']:
    raw=safe(PACK/frame['raw_source'],PACK);assert sha(raw)==frame['raw_sha256']
    with Image.open(raw) as raw_im:assert list(raw_im.size)==frame['raw_native_size']
    assert any(x['sha256']==frame['raw_sha256'] for x in lineage['raw_artifacts'])
    assert len(frame['source_box'])==len(frame['target_box'])==4
   lineage=archive_reference_chain(lineage,local_map)
   new['generation_lineage']=remap_paths(lineage,local_map);new['source']='deterministic layout of separately generated native art cells'
  else:native_artifacts[rec['sha256']]={'path':'sources/'+expected_name,'sha256':rec['sha256'],'native_size':rec['native_size']}
  if generation_record.get('reference_images'):
   new['reference_images']=archive_reference_chain({'reference_images':generation_record['reference_images']},copy.deepcopy(relocations))['reference_images']
  new['visual_approval']={'status':'approved','record':'processing/final-visual-approval.json','sha256':approved_sha}
  sources[key]=new;doc('processing/'+key+'.json',new);history_files[generation.name]=generation
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
   'note':'Compatibility 4x4 sheet. The separate sources/walk_DIRECTION_2x2.png files are processing inputs; some are composite layouts. Actual native sources are listed in each generation_lineage.'}
  assembly[kind]=record;doc(f'processing/{kind}-pipeline-meta.json',record)
  text=f'Deterministic compatibility assembly of the new approved 512px RGBA frames; rows {", ".join(directions)}, four frames per row. This is not native generated raw art. See processing/sources.json for the eight processing inputs and their actual native generation lineages.\n'
  prose(f'prompts/{kind}_assembled.txt',text);prose(f'processing/{kind}-prompt-used.txt',text)
 doc('sources/assembly.json',assembly)
 doc('processing/portrait-pipeline-meta.json',sources['portrait']);add('processing/portrait-prompt-used.txt',release/'prompts/portrait.txt')
 manifest=read(capture(STAGE/'manifest.json'));manifest['sources']=sources;manifest['status']='published_visual_and_numeric_verified';manifest['source_resolution_note']='Processing-input canvas sizes do not imply native generation resolution for assembled inputs. source_type/native_generation identify composites; generation_lineage records each actual raw native size, source crop, scale, target placement and prompt.'
 manifest['visual_approval']={'path':'processing/final-visual-approval.json','sha256':approved_sha}
 manifest['compatibility_assembly']=assembly;manifest['current_rebuild_workflow']='qdao_cutout_edge_repair_20260911/27/tools/process_new_batch.py -> repair-folder staging -> visual approval -> publish_approved_batch.py'
 doc('manifest.json',manifest)
 qc=read(capture(STAGE/'qc.json'));qc['status']='passed_visual_and_numeric_qc';qc['visual_review']={'status':'approved','record':'processing/final-visual-approval.json','sha256':approved_sha};doc('qc.json',qc)
 status='''# 27 墨鸢：本轮交付已完成\n\n立绘、八向各四帧、八条 strip、八个 GIF 与两张 4×4 表共 51 个媒体已完成当前 SHA 的视觉和机械验收。客户端未导入。\n\n当前处理输入在 sources/portrait_raw.png 与 sources/walk_DIRECTION_2x2.png，共9个输入；其中部分2×2是分别生成的姿态原画排版，不能计作一张原生生图。实际原生图及逐帧native尺寸、source_box、缩放和提示词见generation_lineage与sources/frame-originals/。1024/512/2048为处理后的导出尺寸。sources/cardinal_assembled.png 与 diagonal_assembled.png 是新帧拼接的兼容表，不是原生生图。\n\n当前重建入口为本轮 qdao_cutout_edge_repair_20260911/27/tools/process_new_batch.py：先输出修复目录暂存，复核当前 SHA，再由同目录 publish_approved_batch.py 受保护发布。旧 assemble_directions.py、supplement_manifest.py 与旧流水线属于历史流程，不能不经复核覆盖当前成品。旧 source/ 内 raw 和 sources/ 内 rejected 候选保留为历史资料，不是当前原画。\n\n验收：processing/final-visual-approval.json、processing/artifact-validation.json、qc.json。来源：processing/sources.json 和逐方向处理记录。\n'''
 prose('STATUS.md',status);prose('README.md',status)
 numeric=validate_media(release);source_validation=validate_sources(release)
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
  'files':entries,'historical_unchanged':{name:r['sha256'] for name,r in rows.items() if name not in payload},'numeric_validation':numeric,'source_validation':source_validation,'native_generation_artifacts':list(native_artifacts.values())}
 write(PACK/'publication-plan.json',plan)
 print(json.dumps({'status':plan['status'],'files':len(entries),'approved_media':51,'processing_inputs':9,'native_generation_artifacts':len(native_artifacts),'production_written':False}))

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
  source_validation=validate_sources(TARGET)
  manifest=read(TARGET/'manifest.json')
  for key,r in manifest['sources'].items():
   assert sha(Path(r['path']))==r['sha256'];assert sha(Path(r['prompt_file']))==r['prompt_sha256']
   assert safe(Path(r['path']),TARGET/'sources').is_file();assert safe(Path(r['prompt_file']),TARGET/'prompts').is_file()
  for r in manifest['sources'].values():
   for raw in r.get('generation_lineage',{}).get('raw_artifacts',[]):
    assert sha(Path(raw['path']))==raw['sha256'];assert sha(Path(raw['prompt_file']))==raw['prompt_sha256']
    assert safe(Path(raw['path']),TARGET/'sources/frame-originals').is_file()
   for frame in r.get('generation_lineage',{}).get('frames',[]):
    assert sha(Path(frame['raw_source']))==frame['raw_sha256'];assert sha(Path(frame['prompt_file']))==frame['prompt_sha256']
    with Image.open(frame['raw_source']) as raw_im:assert list(raw_im.size)==frame['raw_native_size']
  for kind in ROWS:assert sha(TARGET/'sources'/f'{kind}_assembled.png')==sha(TARGET/f'walk-{kind}.png')
  for name,s in plan['historical_unchanged'].items():assert sha(TARGET/name)==s,'Historical file changed: '+name
  for r in plan['files']:assert sha(TARGET/r['path'])==r['output_sha256']
  report.update(status='published_and_verified',completed_utc=now(),numeric_validation=numeric,source_validation=source_validation,
   visual_approval_sha256=plan['approval_sha256'])
 except BaseException as e:
  report.update(status='stopped_due_to_error',error=str(e),stopped_utc=now());write(report_path,report);raise
 report['processing_inputs_and_prompts_verified']=9;report['historical_files_preserved']=len(plan['historical_unchanged']);report['client_accessed']=False;report['git_modified']=False;report['native_generation_artifacts_verified']=len(plan['native_generation_artifacts'])
 write(report_path,report);print(json.dumps({'status':report['status'],'files':len(report['files']),'approved_media':51}))

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['inspect','prepare','publish']);args=parser.parse_args()
 {'inspect':inspect,'prepare':prepare,'publish':publish}[args.command]()
