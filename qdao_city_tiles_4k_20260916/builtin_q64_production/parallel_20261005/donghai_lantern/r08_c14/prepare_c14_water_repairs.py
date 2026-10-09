"""Plan/prepare/record c14 DAY water-repair appearance conversions.

No model call and no full image assembly is issued by this script. `plan`
writes only JSON; `prepare ID` requires all 16 verified festival native files
and their actual tone candidate before cropping its SAME window. Three exact
DAY patches are the sole layout authority. `apply_exact_masks` is an in-memory
utility for the later compositor and reuses all seven recorded DAY masks.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,io,shutil,sys
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
import assemble_c14_shared as shared
import c14_contract as contract

T=Path(__file__).resolve().parent
R=T/'repairs'
PLAN=R/'water-repair-plan.json'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
CONFIG=Path('D:/work/image/config/image-generation.json')
DEFAULT_BASE=T/'tone-assembly/output/tone-assembly-manifest.json'
DESCRIPTIONS={
 'water-join-s1':'Existing partial large timber post at far upper-left edge, pale rounded stone footing on left, and its dark water reflection below. Most of the frame is broad calm blue water. Keep that partial object exactly at its DAY location; no extra post or rope.',
 'water-join-s2':'Existing rounded dock/timber corner enters from bottom-left, short horizontal wood/rope fastener and red cloth banner enter only from right edge; shadow/reflection enters left. Keep all at their exact DAY positions; the wide central region remains open water.',
 'water-join-east-s1':'Existing timber/rope tie at upper center, two long diagonal rope strands, bottom-center post top, and timber sliver at bottom-right. Retain their exact DAY silhouettes, widths, knot topology, occlusions and reflected-shadow edges; do not move these objects into another patch.'}
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def need(v,m):
 if not v:raise ValueError(m)
def meta(p,role=None):
 d={'file':str(p),'sha256':sha(p)}
 if role:d['role']=role
 return d
def save(p,d):
 p=Path(p);need(p.resolve().is_relative_to(T.resolve()),'Output outside c14')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def build_plan():
 lock,manifest=contract.pin(shared)
 chain=manifest.get('postAssemblyRepairChain',[])
 need(len(chain)==2,'Expected reviewed two-stage DAY water repair chain')
 stages=[];patches=[];mask_count=0
 for stage_index,entry in enumerate(chain):
  need(sha(entry['file'])==entry['sha256'],'DAY integration record changed')
  d=read(entry['file']);group=Path(entry['file']).parent.name
  expected_group=('water-join','water-join-east')[stage_index]
  need(group==expected_group,'DAY repair stage ordering changed')
  x,y,x1,y1=d['changedPixelsRestrictedToRect']
  need([x,y,x1,y1]==([1421,0,2675,2278] if stage_index==0 else [2445,0,3699,1254]),'Reviewed repair region changed')
  mask_entries=[]
  for m in d['masks']:
   alpha=contract.read_mask(m);mask_count+=1
   name=Path(m['file']).name
   rect={'patch-join-mask.png':[x,1024,x1,1254],'left-insert-mask.png':[x,0,x+150,y1],'right-insert-mask.png':[x1-150,0,x1,y1],'bottom-insert-mask.png':[x,y1-150,x1,y1]}[name]
   mask_entries.append({**m,'shapeHW':list(alpha.shape),'tileRectXYXY':rect,'transposeForUse':name in ('patch-join-mask.png','bottom-insert-mask.png'),'alphaMeaning':'0 keeps first argument, 255 takes second argument; exact 0/64/191/255 integer blend'})
  stage_patches=[]
  for index,p in enumerate(d['patches']):
   pp=Path(p['file']);pr=Path(str(pp)+'.generation.json')
   shared.load_rgb(pp,p['sha256'],(1254,1254))
   need(read(pr)['sha256']==p['sha256'],'DAY native sidecar disagrees')
   key=f'{group}-{pp.stem}';py=index*1024
   native=R/group/'native'/pp.name
   item={'id':key,'group':group,'stageIndex':stage_index,'orderWithinStage':index,'daySource':{**meta(pp),'generationRecord':str(pr),'generationRecordSha256':sha(pr)},'nativeOutput':str(native),'tileRectXYXY':[x,py,x+1254,py+1254],'globalRectXYWH':[53248+x,28672+py,1254,1254],'compositionInvariant':DESCRIPTIONS[key],'actualDaySourceViewed':True,'viewDetail':'original','sourceViewEvidence':'Actual view_image review in paving_repair agent on 2026-10-08; DAY source SHA pinned here','geometryAuthority':'Only this DAY native image, not the tone context or style picture'}
   patches.append(item);stage_patches.append(key)
  stages.append({'group':group,'integrationRecord':entry,'tileRectXYXY':[x,y,x1,y1],'patchIds':stage_patches,'maskOrder':['patch-join-mask.png','left-insert-mask.png','right-insert-mask.png','bottom-insert-mask.png'] if len(stage_patches)==2 else ['left-insert-mask.png','right-insert-mask.png','bottom-insert-mask.png'],'masks':mask_entries,'blendFormula':'(old*(255-alpha)+new*alpha+127)//255; uint32 channels','edgeOverlapPixels':150,'patchOverlapPixels':230 if len(stage_patches)==2 else 0,'colorCorrection':False})
 need(len(patches)==3 and mask_count==7,'Expected three source natives and seven exact masks')
 result={'createdAtUtc':now(),'tile':'r08_c14','sourceContract':lock['sourceContract'],'assemblySourceLock':meta(contract.LOCK),'dayManifest':lock['dayManifest'],'defaultFestivalBaseManifest':str(DEFAULT_BASE),'patches':patches,'stages':stages,'requiredNativePatches':16,'style':meta(STYLE),'submissionPolicy':'DAY edit target + exact same-window true festival tone + confirmed style; no unrelated neighbor image','geometryOrMaskResampling':False,'requiredOrder':['water-join s1','water-join s2','integrate water-join with four exact masks','water-join-east s1','integrate water-join-east with three exact masks'],'boundedColorPolicy':'No correction is included by default. If an inspected insertion requires bounded RGB matching, save a separate applied integer delta field, support mask, limits and outside-support equality evidence; preserve exact DAY mask ownership and all pixel coordinates.','formalAccepted':False,'generationPerformed':False,'assemblyPerformed':False}
 return result
def plan():
 p=build_plan();save(PLAN,p)
 return {'plan':str(PLAN),'patchCoordinates':[{k:q[k] for k in ('id','tileRectXYXY','globalRectXYWH')} for q in p['patches']],'dayMasksVerified':7,'nativePatchesPresent':len(list((T/'native').glob('r??_c??.png'))),'toneCandidateAvailable':DEFAULT_BASE.exists(),'generationPerformed':False,'assemblyPerformed':False}
def find_patch(p,key):
 matches=[q for q in p['patches'] if q['id']==key];need(len(matches)==1,f'Unknown repair id {key}');return matches[0]
def load_base(base_manifest):
 base_manifest=Path(base_manifest)
 need(base_manifest.is_file(),f'Festival tone base is not ready: {base_manifest}; finish all 16 own natives and shared/tone assembly first')
 # This rejects absent, stale, resized, wrong-DAY or incomplete native sources.
 _,_,entries,_,day_hash=shared.validate_inputs()
 need(len(entries)==16,'All 16 current native files required')
 m=read(base_manifest);need(m['dayManifest']['sha256']==day_hash,'Tone base uses a different DAY manifest')
 c=m['candidate'];image=shared.load_rgb(c['file'],c['sha256'],(4096,4096))
 need(m.get('geometricDisplacementPixels',0)==0 and m.get('artResampled') is False,'Tone base must preserve native geometry')
 return Image.fromarray(image),{'candidate':c,'manifest':meta(base_manifest)}
def prepare(key,base_manifest):
 p=build_plan();q=find_patch(p,key)
 out=Path(q['nativeOutput']);need(not out.exists(),'Do not overwrite an existing native repair')
 base,base_info=load_base(base_manifest)
 guides=out.parent.parent/'guides';prompts=out.parent.parent/'prompts';guides.mkdir(parents=True,exist_ok=True);prompts.mkdir(parents=True,exist_ok=True)
 context=guides/(out.stem+'-festival-same-window.png')
 base.crop(q['tileRectXYXY']).save(context)
 save(str(context)+'.generation.json',{'file':str(context),'sha256':sha(context),'generatedByAI':False,'operation':'Exact 1254-square crop of actual complete c14 festival tone pixels; palette/context only','derivedFrom':[base_info['candidate']],'baseManifest':base_info['manifest'],'tileRectXYXY':q['tileRectXYXY'],'resized':False,'geometryAuthority':False})
 prompt=f'''Use case: lighting-weather. Edit IMAGE 1 only: exact native DAY repair for Lantern Festival game map c14, patch {key}. Return the exact same opaque 1254x1254 frame and native pixel scale.
IMAGE 1 is the ONLY object, composition, water-wave/reflection geometry authority. IMAGE 2 is actual festival pixels at the EXACT SAME tile window, supplied solely for local palette, restrained warm reflections and illumination. It may contain the old failed water join: do NOT copy that seam or its incorrect wave patterns. IMAGE 3 is the confirmed rounded clean hand-painted Daoist Q material/rendering style, no UI content.
Preserve image 1's complete geometry, every silhouette and edge crossing. Specific composition: {q['compositionInvariant']}
Convert only DAY lighting to the established Lantern Festival appearance visible in image 2. Keep water recognizably clean blue/cyan, with broad quiet low-contrast painted water shapes, soft violet shade and restrained warm reflection where the true same-window festival pixels support it. Preserve all repaired flowing contours across the former join; do not recreate upright, jagged or rectangular water boundaries. Match both outer sides naturally with no sudden color stripe. Warm existing timber toward the same honey tone, keep existing cloth red and keep all original material identities. Do not copy a post, rope, cloth, stone footing, reflection, architecture or any other shape from the tone reference into a place absent in image 1. Never add lanterns, extra objects, white wave nets, sparkles, foam, glare, noise or caustic patterns. Keep exact viewpoint, crop, scale, object footprints, occlusion, broad water-shape geometry and cast-shadow silhouette. No zoom, rotation, cropping, enlargement, blur, text, UI, grid, borders or watermark.'''
 prompt_path=prompts/(out.stem+'.txt');prompt_path.write_text(prompt,encoding='utf-8')
 refs=[meta(q['daySource']['file'],'EDIT TARGET and sole geometry authority: exact DAY native repair'),meta(context,'support only: actual festival same-window palette; never transplant objects'),meta(STYLE,'confirmed rendering/material style only; no UI')]
 request={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}
 request_path=prompts/(out.stem+'.request.json');save(request_path,request)
 save(prompts/(out.stem+'.prepared.json'),{'patch':q,'requestFile':str(request_path),'requestSha256':sha(request_path),'prompt':str(prompt_path),'promptSha256':sha(prompt_path),'references':refs,'festivalBase':base_info,'configSnapshot':read(CONFIG),'assemblySourceLock':meta(contract.LOCK),'actualViewsRequiredBeforeCall':[r['file'] for r in refs],'generationPerformed':False})
 save(PLAN,p)
 return request
def record(key,raw):
 p=build_plan();q=find_patch(p,key);out=Path(q['nativeOutput']);need(not out.exists(),'Do not overwrite native repair')
 prepared=read(out.parent.parent/'prompts'/(out.stem+'.prepared.json'))
 for ref in prepared['references']:need(sha(ref['file'])==ref['sha256'],'Prepared actual reference changed')
 need(prepared['assemblySourceLock']==meta(contract.LOCK),'Assembly source lock changed after prepare')
 need(sha(prepared['prompt'])==prepared['promptSha256'],'Prompt changed')
 need(sha(prepared['requestFile'])==prepared['requestSha256'],'Request changed')
 raw=Path(raw);im=shared.load_rgb(raw,sha(raw),(1254,1254));out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(raw,out)
 request=read(prepared['requestFile'])
 rec={'file':str(out),'sha256':sha(out),'generatedAt':now(),'timestampMeaning':'locally observed builtin result recording','width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':prepared['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**request},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，内置工具未披露实际型号与质量；配置目标不作为实际返回值。','evidence':{'toolResultSourcePath':str(raw),'toolResultSha256':sha(raw)},'prompt':prepared['prompt'],'promptSha256':prepared['promptSha256'],'requestFile':prepared['requestFile'],'requestSha256':prepared['requestSha256'],'references':prepared['references'],'geometryMatchedTo':q['daySource'],'festivalBase':prepared['festivalBase'],'tileRectXYXY':q['tileRectXYXY'],'globalRectXYWH':q['globalRectXYWH'],'resizedAfterGeneration':False,'finalArtUpscaled':False,'visualQA':'pending','formalAccepted':False}
 save(str(out)+'.generation.json',rec)
 return {'file':str(out),'sha256':sha(out),'pixels':[1254,1254],'formalAccepted':False}
def apply_exact_masks(base,converted,plan_data=None):
 """Pure array compositor for later use; caller must verify all native records.

 `converted` maps repair ids to uint8 RGB 1254-square arrays. The function
 does not write output, make visual acceptance claims, or perform correction.
 """
 p=build_plan() if plan_data is None else plan_data
 need(base.dtype==np.uint8 and base.shape==(4096,4096,3),'Native c14 core required')
 result=base.copy();operations=[]
 for stage in p['stages']:
  x,y,x1,y1=stage['tileRectXYXY'];sources=[converted[key] for key in stage['patchIds']]
  for a in sources:need(a.dtype==np.uint8 and a.shape==(1254,1254,3),'Wrong native repair shape')
  masks={Path(e['file']).name:contract.read_mask(e) for e in stage['masks']}
  if len(sources)==2:strip=np.concatenate((sources[0][:1024],shared.blend(sources[0][1024:],sources[1][:230],masks['patch-join-mask.png'].T),sources[1][230:]),axis=0)
  else:strip=sources[0].copy()
  old=result[y:y1,x:x1].copy()
  strip[:,:150]=shared.blend(old[:,:150],strip[:,:150],masks['left-insert-mask.png'])
  strip[:,-150:]=shared.blend(strip[:,-150:],old[:,-150:],masks['right-insert-mask.png'])
  strip[-150:]=shared.blend(strip[-150:],old[-150:],masks['bottom-insert-mask.png'].T)
  result[y:y1,x:x1]=strip
  operations.append({'stage':stage['group'],'exactDayMasks':stage['masks'],'tileRectXYXY':stage['tileRectXYXY'],'operationOrder':stage['maskOrder'],'colorCorrection':False})
 return result,operations
def main():
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
 sub.add_parser('plan');p=sub.add_parser('prepare');p.add_argument('id',choices=tuple(DESCRIPTIONS));p.add_argument('--base-manifest',default=str(DEFAULT_BASE))
 p=sub.add_parser('record');p.add_argument('id',choices=tuple(DESCRIPTIONS));p.add_argument('raw')
 args=parser.parse_args()
 value=plan() if args.action=='plan' else prepare(args.id,args.base_manifest) if args.action=='prepare' else record(args.id,args.raw)
 print(json.dumps(value,ensure_ascii=False,indent=2))
if __name__=='__main__':
 try:main()
 except (OSError,ValueError,KeyError) as e:raise SystemExit(f'Water repair preparation refused: {e}')
