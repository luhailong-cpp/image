"""Independently reconstruct original-Q V14 HD exports; never approves art by itself."""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];DIRS=('N','NE','E','SE','S','SW','W','NW')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def require(v,message):
 if not v:raise ValueError(message)
def imread(p):
 with Image.open(p) as im:return im.convert('RGBA')
def mod(name):
 p=ROOT/'tools/vendor'/f'{name}.py';spec=importlib.util.spec_from_file_location('independent_'+name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def verify(character,direction=None,require_visual=False,frame_number=None):
 require(character and all(c.isalnum() or c in '_-' for c in character),'Invalid character ID');out=ROOT/'candidate'/character
 manifest=read(out/'manifest.json');records=read(out/'processing/frame-sources.json');profile=read(out/'processing/scale-profile.json')
 require(manifest['character_id']==character and manifest['version']==14 and manifest['frame_count']==16 and manifest['frame_duration_ms']==30 and manifest['cycle_duration_ms']==480,'Wrong identity/timing')
 require(manifest.get('frame_size')==[1024,1024] and manifest.get('portrait_size')==[1024,1024] and manifest.get('runtime_geometry')=={'reference_frame_size':512,'pixels_per_unit':104,'pivot':[.5,.08]},'Wrong V14 HD runtime geometry')
 require(frame_number is None or direction in DIRS and 1<=frame_number<=16,'Single-frame audit requires direction and frame1..16')
 require(not require_visual or frame_number is None,'Single-frame audit cannot approve a character')
 require(sha(out/'processing/frame-sources.json')==manifest['sources_sha256'],'Source mapping changed')
 require(profile['per_subject_bbox_scaling'] is False and profile['root_px']==[512,942] and profile['alignment_version']==2,'Unsupported canonical alignment/scale')
 selected=[direction] if direction else list(DIRS);keys=[f'walk/{direction}/{frame_number:02d}.png'] if frame_number else [f'walk/{d}/{i:02d}.png' for d in selected for i in range(1,17)]
 if not frame_number:keys += [f'idle/{d}.png' for d in selected if (out/f'idle/{d}.png').exists()]
 if not direction:require(len(keys)==136 and (out/'portrait.png').exists(),'Full character needs 128 walk, eight independent idle and portrait')
 files={r['path']:r['sha256'] for r in manifest['files']};require(len(files)==len(manifest['files']),'Duplicate manifest paths')
 keyer=mod('generate2dsprite');edge=mod('edge_despill');source_cells=set();missing_receipts=[];native_dimensions=[];native_heights=[];factors=[]
 for key in keys:
  require(key in records and key in files,f'Missing output/source: {key}');rec=records[key];src=rec['source'];path=out/src['path']
  with Image.open(out/key) as exported:
   require(exported.format=='PNG' and exported.mode=='RGBA' and exported.size==(1024,1024),'Final frame must be a 1024x1024 RGBA PNG')
   alpha=np.asarray(exported)[:,:,3];require(alpha.min()==0 and alpha.max()==255,'Final frame needs transparent background and opaque body')
  require(sha(path)==src['sha256'] and sha(out/key)==files[key]==rec['output_sha256'],'Source or output SHA changed')
  require(sha(out/rec['prompt']['path'])==rec['prompt']['sha256'],'Exact generation prompt changed')
  raw=imread(path);rows,cols=src['grid'];index=src['cell_index'];r,c=divmod(index,cols)
  require((rows,cols) in (((4,4),(2,4),(2,2),(2,1),(1,2),(1,1)) if rec['kind']=='walk' else ((2,4),(1,1))), 'Unsupported source grid')
  start=src.get('sequence_start_frame',1 if rec['kind']=='walk' else 0)
  if rec['kind']=='walk':
   require((rows,cols) not in ((1,2),(2,1)) or src.get('output_frame_map') is not None,'1x2 and 2x1 source pairs require explicit final-frame mapping')
   mapping=src.get('output_frame_map') or list(range(start,start+rows*cols))
   selected_indices=src.get('selected_source_cell_indices',list(range(rows*cols)));assigned=[v for v in mapping if v is not None]
   require(len(mapping)==rows*cols and selected_indices and len(set(selected_indices))==len(selected_indices) and set(selected_indices)=={i for i,v in enumerate(mapping) if v is not None} and index in selected_indices and len(set(assigned))==len(assigned) and all(isinstance(v,int) and 1<=v<=16 for v in assigned) and mapping[index]==rec['frame'],'Explicit source-cell to final-frame mapping is incorrect')
  else:
   idle_order=src.get('output_direction_map') or list(DIRS)
   require(len(idle_order)==rows*cols and index in range(rows*cols) and idle_order[index]==rec['direction'] and rec['direction'] in DIRS and ((rows,cols)==(1,1) and src.get('output_direction_map')==[rec['direction']] and src.get('selected_source_cell_indices')==[0] or (rows,cols)==(2,4) and set(idle_order)==set(DIRS)),'Explicit idle source-cell direction mapping incorrect')
  require(src['native_size']==list(raw.size),'Original source dimensions changed')
  box=[round(c*raw.width/cols),round(r*raw.height/rows),round((c+1)*raw.width/cols),round((r+1)*raw.height/rows)]
  require(box==src['cell_xyxy'],'Source crop is not an original complete cell')
  identity=(src['sha256'],tuple(box));require(identity not in source_cells,'Original generated cell reused');source_cells.add(identity)
  factor=1024/max(raw.width/cols,raw.height/rows)*profile['common_scale'];require(rec['whole_cell_scale']==factor and rec['common_scale']==profile['common_scale'],'Per-frame scale or wrong character-wide scale')
  require(min(raw.width/cols,raw.height/rows,box[2]-box[0],box[3]-box[1])>=1024,'Native source cell is below1024; old small frames are not HD')
  require(0<factor<=1,'HD upscaling or invalid factor')
  native_dimensions.append([box[2]-box[0],box[3]-box[1]]);factors.append(factor)
  cell=raw.crop(box);prepared=cell.copy();threshold=rec.get('alpha_cleanup_threshold',0)
  require(threshold in (0,8) and (threshold==0 or np.asarray(raw)[:,:,3].min()<255),'Invalid alpha cleanup threshold or applied to opaque source')
  if threshold:
   prepared_array=np.array(prepared);prepared_array[:,:,3][prepared_array[:,:,3]<=threshold]=0;prepared=Image.fromarray(prepared_array,'RGBA').copy()
  chroma_thresholds=rec.get('chroma_thresholds',[100,150]);require(chroma_thresholds in ([100,150],[50,75],[0,0]),'Unsupported recorded chroma-key thresholds')
  native_alpha=chroma_thresholds==[0,0]
  require(not native_alpha or (rec.get('chroma_profile')=='native-alpha' and threshold==0 and np.asarray(raw)[:,:,3].min()==0 and np.asarray(raw)[:,:,3].max()==255),'Wrong native-alpha evidence')
  keyed=prepared.copy() if native_alpha else keyer.remove_bg_magenta(prepared,*chroma_thresholds);alpha=np.asarray(keyed)[:,:,3]
  require(not any(np.any(a>8 if native_alpha else a) for a in (alpha[0],alpha[-1],alpha[:,0],alpha[:,-1])),f'Original art clipped at cell boundary: {key}')
  native_y,native_x=np.where(alpha>8);native_heights.append(int(native_y.max()-native_y.min()+1))
  size=(round(cell.width*factor),round(cell.height*factor));normal=keyed.resize(size,Image.Resampling.LANCZOS) if keyed.size!=size else keyed.copy();clean,stats=(normal.copy(),{'protected_red_changes':0,'outside_band_changes':0}) if native_alpha else edge.despill(normal,radius=4,reference_radius=12)
  require(np.array_equal(np.asarray(normal)[:,:,3],np.asarray(clean)[:,:,3]) and np.array_equal(np.asarray(normal)[:,:,1],np.asarray(clean)[:,:,1]),'Edge cleanup changed alpha/green')
  require(stats['protected_red_changes']==0 and stats['outside_band_changes']==0,'Edge cleanup altered protected/non-edge pixels')
  y,x=np.where(np.asarray(clean)[:,:,3]>8);require(len(x)>0,'Empty cleaned source');top=int(y.min());limit=top+max(1,int((int(y.max())-top)*.42));ax=float(np.median(x[y<limit]));delta=[round(512-ax),942-int(y.max())]
  require(delta==rec['translation_px'],'Wrong whole-frame integer alignment')
  y0,x0=np.where(np.asarray(clean)[:,:,3]>0);require(x0.min()+delta[0]>=1 and x0.max()+delta[0]<=1022 and y0.min()+delta[1]>=1 and y0.max()+delta[1]<=1022,'Output alignment clips source alpha')
  final=Image.new('RGBA',(1024,1024));final.paste(clean,tuple(delta))
  require(final.tobytes()==imread(out/key).tobytes(),f'Reconstructed final differs: {key}')
  for stage,im in [('cell',cell),('keyed',keyed),('normalized',normal),('cleaned',clean),('final',final)]:
   evidence=rec['stages'][stage];require(sha(out/evidence['path'])==evidence['sha256'] and imread(out/evidence['path']).tobytes()==im.tobytes(),f'Stage evidence changed: {key}/{stage}')
  require(rec['generation']['tool']=='built-in image_gen','New frames must originate from real image generation')
  receipt=rec['generation'].get('receipt')
  if receipt:require(sha(out/receipt['path'])==receipt['sha256'],'Generation receipt changed')
  else:missing_receipts.append(key)
 directions={};means=[]
 for d in ([] if frame_number else selected):
  review_files={r['path']:r['sha256'] for r in manifest.get('review_files',[])}
  require(sha(out/f'review/strips/{d}.png')==review_files.get(f'review/strips/{d}.png'),'Review strip SHA differs from manifest')
  frames=[imread(out/f'walk/{d}/{i:02d}.png') for i in range(1,17)];strip=imread(out/f'review/strips/{d}.png');require(strip.size==(16384,1024),'Review strip must be16384x1024');hashes=[];heights=[];scales=[]
  for i,frame in enumerate(frames):
   require(frame.size==(1024,1024),'Frame is not1024square');require(strip.crop((1024*i,0,1024*(i+1),1024)).tobytes()==frame.tobytes(),'Strip cell differs from standalone frame');hashes.append(hashlib.sha256(frame.tobytes()).hexdigest());a=np.asarray(frame);y,x=np.where(a[:,:,3]>8);height=int(y.max()-y.min()+1);heights.append(height);axis=float(np.median(x[y<int(y.min())+max(1,int((height-1)*.42))]));require(abs(axis-512)<=.5 and int(y.max())==942,'Foot/body axis drift');scales.append(float(np.sqrt(np.count_nonzero(a[:,256:768,3])/(1024*1024))))
  require(len(set(hashes))==16,'Duplicate walk frames');cv=float(np.std(scales)/np.mean(scales));require(cv<=.08,'Body-scale CV exceeds .08');mean=float(np.mean(heights));means.append(mean);drift=None
  if (out/f'idle/{d}.png').exists():
   idle=imread(out/f'idle/{d}.png');require(hashlib.sha256(idle.tobytes()).hexdigest() not in hashes,'Idle duplicated from walk');ys,xs=np.where(np.asarray(idle)[:,:,3]>8);drift=abs((int(ys.max()-ys.min()+1))/mean-1);require(drift<=.08,'Idle/walk height drift exceeds .08')
  directions[d]={'frames':16,'unique':16,'strip_cells_equal':16,'body_scale_cv':cv,'idle_walk_height_drift':drift}
 require(not means or max(means)/min(means)<=1.10,'Cross-direction mean-height ratio exceeds1.10')
 if not direction:
  expected={'portrait.png',*[f'idle/{d}.png' for d in DIRS],*[f'walk/{d}/{i:02d}.png' for d in DIRS for i in range(1,17)]};require(set(files)==expected and len(files)==137,'Wrong final137-runtime-PNG inventory')
  portrait=read(out/'processing/portrait-source.json');source=out/portrait['preserved_source'];require(sha(source)==portrait['source_sha256'],'Original portrait changed');require(imread(source).size==(4096,4096),'Original portrait is not4096');expected_portrait=imread(source).resize((1024,1024),Image.Resampling.LANCZOS);require(expected_portrait.tobytes()==imread(out/'portrait.png').tobytes() and sha(out/'portrait.png')==portrait['output_sha256']==files['portrait.png'],'Portrait is not exact whole-image downsample')
 visual='pending'
 if require_visual:
  require(not direction,'Final visual pass must cover whole character');require(not missing_receipts,'Generation receipts missing');v=read(out/'review/visual-review.json');require(v.get('status')=='passed' and v.get('reviewed_manifest_sha256')==sha(out/'manifest.json') and v.get('reviewed_qc_sha256')==sha(out/'qc.json'),'Visual review missing/stale');require(set(v.get('reviewed_directions',[]))==set(DIRS) and v.get('normal_size_review') and v.get('enlarged_review') and v.get('seam_15_16_01_review') and v.get('anatomical_contacts_01_09_review') and v.get('native_resolution_review') and v.get('closeup_1080p_review') and str(v.get('native_resolution_notes','')).strip() and str(v.get('closeup_1080p_notes','')).strip(),'Visual review scope incomplete');require(v.get('reviewed_artifacts')==files,'Visual review refers to different PNGs');visual='passed'
 return {'version':14,'character_id':character,'status':'passed' if visual=='passed' else 'partial_sources_pending_visual' if frame_number else 'passed_numeric_sources_pending_visual','scope':f'{direction}/{frame_number:02d}' if frame_number else direction or 'all8','verified_at_utc':datetime.now(timezone.utc).isoformat(),'manifest_sha256':sha(out/'manifest.json'),'qc_sha256':sha(out/'qc.json'),'visual_review':visual,'visual_review_sha256':sha(out/'review/visual-review.json') if visual=='passed' else None,'missing_generation_receipts':missing_receipts,'direction_results':directions,'reconstructed_frames':len(keys),'synthetic_frames_created':0,'native_resolution':{'minimum_cell_px':min(min(d) for d in native_dimensions),'minimum_subject_height_px':min(native_heights),'max_whole_cell_scale':max(factors),'upscaled_frames':0}}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--character',required=True);p.add_argument('--direction',choices=DIRS);p.add_argument('--frame',type=int);p.add_argument('--require-visual',action='store_true');a=p.parse_args()
 if not a.character or not all(c.isalnum() or c in '_-' for c in a.character):p.error('Invalid character ID')
 try:result=verify(a.character,a.direction,a.require_visual,a.frame);code=0
 except Exception as e:result={'status':'failed','character_id':a.character,'error':str(e)};code=1
 out=ROOT/'candidate'/a.character;out.mkdir(parents=True,exist_ok=True);dest=out/(f'review/validation-{a.direction}-{a.frame:02d}.json' if a.frame else f'review/validation-{a.direction}.json' if a.direction else 'validation.json');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result));return code
if __name__=='__main__':sys.exit(main())
