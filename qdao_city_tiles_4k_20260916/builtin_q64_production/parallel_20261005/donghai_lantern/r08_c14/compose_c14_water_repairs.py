"""Compose recorded c14 water edits with exact DAY masks and bounded RGB returns.

Run only after all 16 festival natives, verified base tone, and stage repair
native records exist. --stage water-join exports the two-patch intermediate
manifest for prepare_c14_water_repairs.py --base-manifest; --stage all replays
all three from the same original tone baseline and verifies that the east
edit actually used this exact intermediate candidate. No global state writes.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,io,json,sys
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
import prepare_c14_water_repairs as prep
import assemble_c14_shared as shared

T=Path(__file__).resolve().parent
STEP,TOTAL,RADIUS=18,24,256
DEST=None
def need(v,msg):
 if not v:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def now():return datetime.now(timezone.utc).isoformat()
def info(p):return {'file':str(p),'sha256':sha(p)}
def check(item):need(sha(item['file'])==item['sha256'],f'Dependency changed: {item["file"]}')
def same(a,b):return Path(a).resolve()==Path(b).resolve()
def writable(p):
 p=Path(p);need(DEST is not None and p.resolve().is_relative_to(DEST.resolve()),'Write escaped stage output')
 p.parent.mkdir(parents=True,exist_ok=True);return p
def write_json(p,value):writable(p).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def save_image(p,pixels,metadata):
 p=writable(p);im=pixels if isinstance(pixels,Image.Image) else Image.fromarray(pixels)
 im.save(p)
 item={**info(p),'pixels':list(im.size)}
 write_json(str(p)+'.generation.json',{**item,'createdAtUtc':now(),'generatedByAI':False,'formalAccepted':False,'clientAccepted':False,'visualReview':'pending actual inspection','artResampled':False,**metadata})
 return {**item,'generationRecord':str(p)+'.generation.json','generationRecordSha256':sha(str(p)+'.generation.json')}
def field_record(name,metadata,**arrays):
 p=writable(DEST/'fields'/(name+'.npz'));np.savez_compressed(p,**arrays)
 return {'field':info(p),**metadata}
def smooth(a,radius=12,axis=0):
 pads=[(0,0)]*a.ndim;pads[axis]=(radius,radius)
 b=np.pad(a,pads,mode='edge');shape=list(b.shape);shape[axis]=1
 sums=np.concatenate((np.zeros(shape,np.float32),np.cumsum(b,axis=axis,dtype=np.float32)),axis=axis)
 lo=[slice(None)]*a.ndim;hi=lo.copy();lo[axis]=slice(None,-radius*2-1);hi[axis]=slice(radius*2+1,None)
 return (sums[tuple(hi)]-sums[tuple(lo)])/(radius*2+1)
def difference_field(old,new):
 d=np.clip(new.astype(np.float32)-old.astype(np.float32),-72,72)
 for _ in range(3):d=smooth(smooth(d,axis=0),axis=1)
 return d
def taper(distance):
 w=np.clip(1-np.abs(distance)/RADIUS,0,1);return w*w*(3-2*w)
def bounded_update(current,original,field):
 need(current.shape==original.shape==field.shape,'Correction field geometry mismatch')
 proposed=np.rint(np.clip(current.astype(np.float32)+np.clip(field,-STEP,STEP),0,255)).astype(np.int16)
 value=np.clip(proposed,original.astype(np.int16)-TOTAL,original.astype(np.int16)+TOTAL)
 value=np.clip(value,0,255).astype(np.uint8)
 applied=value.astype(np.int16)-current.astype(np.int16)
 need(int(np.abs(applied).max())<=STEP,'Per-step correction exceeds 18')
 need(int(np.abs(value.astype(np.int16)-original.astype(np.int16)).max())<=TOTAL,'Native source correction exceeds 24')
 return value,applied.astype(np.int8)
def stitch(patches,mask):
 if len(patches)==1:return patches[0].copy()
 return np.concatenate((patches[0][:1024],shared.blend(patches[0][1024:],patches[1][:230],mask.T),patches[1][230:]),axis=0)
def longitudinal_match(patches,originals,alpha,stage):
 # Transpose only coordinates, never interpolate. Each source remains separate
 # until the exact DAY alpha is applied; total native deltas are bounded.
 a,b=patches[0].transpose(1,0,2).copy(),patches[1].transpose(1,0,2).copy()
 a0,b0=originals[0].transpose(1,0,2),originals[1].transpose(1,0,2)
 overlap=230;origin=1024
 correction=np.clip(difference_field(a[:,-overlap:],b[:,:overlap])*.5,-STEP,STEP)
 offsets=np.argmax(alpha>=128,axis=1)
 xs=np.arange(1254)
 fa=correction[:,np.clip(xs-origin,0,229)]*taper(xs[None,:]-origin-offsets[:,None])[...,None]
 fb=-correction[:,np.clip(xs,0,229)]*taper(xs[None,:]-offsets[:,None])[...,None]
 a,da=bounded_update(a,a0,fa);b,db=bounded_update(b,b0,fb)
 patches=[a.transpose(1,0,2),b.transpose(1,0,2)]
 record=field_record(stage+'-patch-join',{'step':'patch-join','stage':stage,'orientation':'horizontal','radiusPixels':RADIUS,'exactDayAlphaReused':True,'maximumStepDelta':int(max(np.abs(da).max(),np.abs(db).max())),'sourceCoordinateTransforms':'exact transposition only; saved fields use original image coordinates'},source1_delta_rgb=da.transpose(1,0,2),source2_delta_rgb=db.transpose(1,0,2),day_alpha_u8=alpha.T,seam_offsets=offsets)
 return patches,record
def insertion_field(strip,old,alpha,side):
 # New repair sources approach the fixed old composite. Corrections extend
 # into drawn native pixels; artwork itself is never blurred or resampled.
 transposed=side=='bottom'
 if transposed:strip,old=strip.transpose(1,0,2),old.transpose(1,0,2)
 h,w=strip.shape[:2];overlap=150;origin=0 if side=='left' else w-overlap
 offsets=np.argmax(alpha>=128,axis=1)
 correction=np.clip(difference_field(strip[:,origin:origin+overlap],old[:,origin:origin+overlap]),-STEP,STEP)
 xs=np.arange(w)
 field=correction[:,np.clip(xs-origin,0,overlap-1)]*taper(xs[None,:]-origin-offsets[:,None])[...,None]
 return field.transpose(1,0,2) if transposed else field
def corrected_stage(base,stage,source_map,color=True):
 keys=stage['patchIds'];originals=[source_map[k].copy() for k in keys];patches=[x.copy() for x in originals]
 masks={Path(m['file']).name:prep.contract.read_mask(m) for m in stage['masks']}
 reports=[];x,y,x1,y1=stage['tileRectXYXY'];old=base[y:y1,x:x1].copy()
 if color and len(patches)==2:
  patches,r=longitudinal_match(patches,originals,masks['patch-join-mask.png'],stage['group']);reports.append(r)
 if color:
  for side in ('left','right','bottom'):
   strip=stitch(patches,masks.get('patch-join-mask.png'))
   field=insertion_field(strip,old,masks[side+'-insert-mask.png'],side)
   applied={};maximum=0
   for i in range(len(patches)):
    fy=i*1024;patches[i],delta=bounded_update(patches[i],originals[i],field[fy:fy+1254])
    applied[f'source{i+1}_delta_rgb']=delta;maximum=max(maximum,int(np.abs(delta).max()))
   reports.append(field_record(stage['group']+'-insert-'+side,{'step':'insert-'+side,'stage':stage['group'],'maximumStepDelta':maximum,'radiusPixels':RADIUS,'oldBaselineColorChanged':False,'geometryDisplacementPixels':0},**applied,day_alpha_u8=masks[side+'-insert-mask.png']))
 source_deltas={f'source{i+1}_final_delta_rgb':(patches[i].astype(np.int16)-originals[i].astype(np.int16)).astype(np.int8) for i in range(len(patches))}
 reports.append(field_record(stage['group']+'-source-final-deltas',{'stage':stage['group'],'maximumNativeSourceDelta':max(int(np.abs(d).max()) for d in source_deltas.values()),'sourceIds':keys,'nativeSourcePixelGeometryUnchanged':True},**source_deltas))
 strip=stitch(patches,masks.get('patch-join-mask.png'))
 # These three insertions are exactly the DAY operation order and argument
 # orientation, including reversed ownership at right and bottom.
 strip[:,:150]=shared.blend(old[:,:150],strip[:,:150],masks['left-insert-mask.png'])
 strip[:,-150:]=shared.blend(strip[:,-150:],old[:,-150:],masks['right-insert-mask.png'])
 strip[-150:]=shared.blend(strip[-150:],old[-150:],masks['bottom-insert-mask.png'].T)
 result=base.copy();result[y:y1,x:x1]=strip
 return result,reports
def load_sources(plan,stage_name,base_info):
 sources,evidence,records={},{},{}
 for q in plan['patches']:
  if stage_name=='water-join' and q['group']!='water-join':continue
  p=Path(q['nativeOutput']);rp=Path(str(p)+'.generation.json')
  need(p.exists() and rp.exists(),f'Complete recorded festival repair required: {p}')
  r=read(rp);need(same(r['file'],p),'Repair native identity differs')
  sources[q['id']]=shared.load_rgb(p,r['sha256'],(1254,1254))
  need(r['route']=='builtin' and r['resizedAfterGeneration'] is False and r['finalArtUpscaled'] is False,'Repair native is not unscaled builtin output')
  need(r['geometryMatchedTo']==q['daySource'],'Repair bound to different DAY geometry')
  need(r['tileRectXYXY']==q['tileRectXYXY'] and r['globalRectXYWH']==q['globalRectXYWH'],'Repair placement differs')
  need(r['actualModel'] is None and r['actualQuality'] is None,'Unexpected model evidence; review before use')
  need(r['submittedParameters']['model'] is None and r['submittedParameters']['quality'] is None,'Unsupported explicit selectors')
  need(sha(r['prompt'])==r['promptSha256'] and sha(r['requestFile'])==r['requestSha256'],'Repair prompt or request changed')
  need(Path(r['prompt']).read_text(encoding='utf-8')==r['submittedParameters']['prompt'],'Submitted prompt differs')
  need(r['evidence']['toolResultSha256']==r['sha256'],'Tool evidence SHA differs');check({'file':r['evidence']['toolResultSourcePath'],'sha256':r['sha256']})
  refs=r['references'];need(len(refs)==len(r['submittedParameters']['referenced_image_paths'])==3,'Expected exact DAY/same-window/style inputs')
  for ref,submitted in zip(refs,r['submittedParameters']['referenced_image_paths']):check(ref);need(same(ref['file'],submitted),'Submitted reference ordering differs')
  need(same(refs[0]['file'],q['daySource']['file']) and refs[0]['sha256']==q['daySource']['sha256'],'DAY primary input differs')
  check(r['festivalBase']['candidate']);check(r['festivalBase']['manifest'])
  if q['group']=='water-join':need(r['festivalBase']['candidate']['sha256']==base_info['candidate']['sha256'],'First repair must use current original tone baseline')
  evidence[q['id']]={'native':info(p),'generationRecord':info(rp),'daySource':q['daySource'],'tileRectXYXY':q['tileRectXYXY'],'festivalBase':r['festivalBase']}
  records[q['id']]=r
 return sources,evidence,records
def export_qa(core,candidate,plan,stage_name):
 image=Image.fromarray(core);qa=[]
 def crop(name,rect,purpose):
  rect=[max(0,rect[0]),max(0,rect[1]),min(4096,rect[2]),min(4096,rect[3])]
  qa.append(save_image(DEST/'qa'/(name+'.png'),image.crop(rect),{'derivedFrom':[candidate],'operation':'exact native crop, no scaling','tileRectXYXY':rect,'pixelScale':1,'purpose':purpose,'visualReview':'pending'}))
 for q in plan['patches']:
  if stage_name=='water-join' and q['group']!='water-join':continue
  x,y,x1,y1=q['tileRectXYXY'];key=q['id']
  crop(key+'-full1254-return',[x,y,x1,y1],'Complete repaired native window; check all local object and wave geometry')
  for name,rect in [('left',[x-448,y,x+448,y1]),('right',[x1-448,y,x1+448,y1]),('top',[x,y-448,x1,y+448]),('bottom',[x,y1-448,x1,y1+448])]:crop(key+'-edge-'+name,rect,'Full native patch boundary and bounded correction return; clipped at outer tile edge, no outside-neighbor acceptance')
 for axis in ('x','y'):
  for boundary in (1024,2048,3072):
   for part in range(4):
    rect=[boundary-448,part*1024,boundary+448,(part+1)*1024] if axis=='x' else [part*1024,boundary-448,(part+1)*1024,boundary+448]
    crop(f'{axis}{boundary}-return-part{part+1:02}',rect,'Entire internal seam in four native 896-wide segments; includes correction falloff')
 corners=Image.new('RGB',(1024,1024));corner_rects=[]
 for box,pos in [((0,0,512,512),(0,0)),((3584,0,4096,512),(512,0)),((0,3584,512,4096),(0,512)),((3584,3584,4096,4096),(512,512))]:corners.paste(image.crop(box),pos);corner_rects.append({'sourceRect':box,'destination':pos})
 qa.append(save_image(DEST/'qa/four-tile-corners.png',corners,{'derivedFrom':[candidate],'operation':'four native corner crops, no scaling','crops':corner_rects,'pixelScale':1,'adjacentTilesAccepted':False}))
 junctions=Image.new('RGB',(1536,1536));junction_rects=[]
 for row,y in enumerate((1024,2048,3072)):
  for col,x in enumerate((1024,2048,3072)):
   box=(x-256,y-256,x+256,y+256);pos=(col*512,row*512);junctions.paste(image.crop(box),pos);junction_rects.append({'sourceRect':box,'destination':pos})
 qa.append(save_image(DEST/'qa/nine-internal-junctions.png',junctions,{'derivedFrom':[candidate],'operation':'nine native junction crops, no scaling','crops':junction_rects,'pixelScale':1}))
 return qa
def compose(stage_name,color=True):
 global DEST
 DEST=T/('water-repaired-stage1' if stage_name=='water-join' else 'water-repaired')
 plan=prep.build_plan();base_image,base_info=prep.load_base(prep.DEFAULT_BASE)
 base_manifest=read(base_info['manifest']['file']);need(not base_manifest.get('waterRepairStage'),'Original tone baseline required, not already-repaired intermediate')
 base=np.array(base_image);converted,evidence,records=load_sources(plan,stage_name,base_info)
 stage_plan={**plan,'stages':plan['stages'][:1] if stage_name=='water-join' else plan['stages']}
 # Raw baseline is generated from the identical original base and unchanged
 # festival repair pixels using only the seven (or first four) exact DAY masks.
 raw,raw_operations=prep.apply_exact_masks(base,converted,stage_plan)
 current=base.copy();reports=[];support=np.zeros((4096,4096),bool);intermediate_proof=None
 for index,stage in enumerate(stage_plan['stages']):
  if index==1:
   east=records['water-join-east-s1'];ref=east['festivalBase'];intermediate=read(ref['manifest']['file'])
   need(intermediate.get('waterRepairStage')=='water-join','East patch must use actual coherent stage1 festival context')
   expected=shared.load_rgb(ref['candidate']['file'],ref['candidate']['sha256'],(4096,4096))
   need(np.array_equal(current,expected),'Current first-stage replay differs from exact festival context used by east edit')
   intermediate_proof={'candidate':ref['candidate'],'manifest':ref['manifest'],'pixelIdenticalToCurrentStage1Replay':True}
  current,steps=corrected_stage(current,stage,converted,color);reports.extend(steps)
  x,y,x1,y1=stage['tileRectXYXY'];support[y:y1,x:x1]=True
  # This guarantees stage1 is byte-stable as the later east generation context.
  if index==0:
   raw1,_=prep.apply_exact_masks(base,converted,{**plan,'stages':plan['stages'][:1]})
   d1=np.clip(current.astype(np.int16)-raw1.astype(np.int16),-TOTAL,TOTAL)
   current=(raw1.astype(np.int16)+d1).astype(np.uint8)
 delta=np.clip(current.astype(np.int16)-raw.astype(np.int16),-TOTAL,TOTAL).astype(np.int8)
 result=(raw.astype(np.int16)+delta.astype(np.int16)).astype(np.uint8)
 need(np.array_equal(result[~support],base[~support]),'Correction escaped authorized repair ROI union')
 need(not np.any(delta[~support]),'Final delta escaped authorized union')
 final_field=field_record('final-applied-delta',{'reference':'Pure exact-DAY-mask raw replay of unchanged festival repair natives','maximumFinalChannelDelta':int(np.abs(delta).max()),'shapeHWC':list(delta.shape)},delta_rgb=delta,authorized_support=support)
 support_item=save_image(DEST/'fields/final-applied-support.png',np.any(delta!=0,axis=2).astype(np.uint8)*255,{'operation':'Actual nonzero RGB correction support; not artwork','finalArt':False})
 dependencies=[base_info['candidate'],base_info['manifest'],info(prep.contract.LOCK),plan['sourceContract'],plan['dayManifest']]
 for e in evidence.values():dependencies.extend([e['native'],e['generationRecord'],e['daySource']])
 for stage in stage_plan['stages']:dependencies.extend([stage['integrationRecord'],*stage['masks']])
 common={'operation':'Exact DAY water repair masks with bounded native-source RGB returns','derivedFrom':dependencies,'dayManifest':plan['dayManifest'],'assemblySourceLock':info(prep.contract.LOCK),'sourceContract':plan['sourceContract'],'waterRepairStage':stage_name,'repairNativeSources':evidence,'baseFestival':base_info,'dayMasksExact':True,'rawMaskOperations':raw_operations,'geometryDisplacementPixels':0,'geometricDisplacementPixels':0,'artResampled':False,'artUpscaled':False,'imageBlur':False,'colorCorrection':color,'maximumPerStepChannelDelta':STEP,'maximumPerNativeSourceChannelDelta':TOTAL,'maximumFinalChannelDelta':int(np.abs(delta).max()),'finalDeltaField':final_field,'actualCorrectionSupport':support_item,'toneOperations':reports,'differenceFieldSmoothing':'Three radius12 box passes per axis, RGB difference field only; no artwork blur','outsideAuthorizedUnionExactlyIdentical':True,'completePixelCandidate':True,'formalAccepted':False,'clientAccepted':False,'globalStateModified':False,'wholeCityComplete':False,'currentDayPostRepairsAppliedToFestival':stage_name=='all','requiredPostAssemblyRepairs':[] if stage_name=='all' else plan['stages'][1:],'eastInputStage1Consistency':intermediate_proof}
 raw_item=save_image(DEST/'output/r08_c14-exact-mask-raw.png',raw,{**common,'operation':'Pure exact-mask replay without RGB matching','colorCorrection':False,'maximumFinalChannelDelta':0,'finalDeltaField':None,'actualCorrectionSupport':None,'toneOperations':[]})
 candidate=save_image(DEST/'output/r08_c14.png',result,{**common,'rawExactMaskBaseline':raw_item})
 extinfo=base_manifest['extendedContext'];extended=shared.load_rgb(extinfo['file'],extinfo['sha256'],(4326,4326));extended[115:4211,115:4211]=result
 ext=save_image(DEST/'output/extended-context.png',extended,{**common,'unchangedHaloSource':extinfo,'cropXYXY':[115,115,4211,4211]})
 preview=save_image(DEST/'output/preview-1024.png',Image.fromarray(result).resize((1024,1024),Image.Resampling.LANCZOS),{'derivedFrom':[candidate],'operation':'Quarter-size overview only','artResampled':True,'finalArt':False,'notNativePixelQA':True})
 qa=export_qa(result,candidate,plan,stage_name)
 for dep in dependencies:check(dep)
 need(np.array_equal(shared.load_rgb(candidate['file'],candidate['sha256'],(4096,4096)).astype(np.int16),raw.astype(np.int16)+delta.astype(np.int16)),'Saved candidate differs from raw plus recorded delta')
 manifest={**common,'createdAtUtc':now(),'script':info(__file__),'candidate':candidate,'extendedContext':ext,'preview':preview,'rawExactMaskBaseline':raw_item,'qa':qa,'qaCoverage':{'full1254RepairWindows':len(converted),'allFourEdgesPerRepair':len(converted)*4,'internal896WideReturnSegments':24,'tileCorners':4,'internalJunctions':9,'allActualVisualReviewPending':True},'savedCandidateExactlyEqualsRawPlusDelta':True,'outsideAuthorizedUnionChangedPixels':0}
 mp=DEST/'output/tone-assembly-manifest.json';write_json(mp,manifest)
 return {'stage':stage_name,'candidate':candidate,'manifest':str(mp),'maximumFinalDelta':int(np.abs(delta).max()),'qaImageCount':len(qa),'formalAccepted':False,'globalStateModified':False}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',choices=('water-join','all'),required=True);parser.add_argument('--no-color-match',action='store_true',help='Raw exact mask only; east context must match selected stage1 mode')
 args=parser.parse_args();print(json.dumps(compose(args.stage,not args.no_color_match),ensure_ascii=False,indent=2))
if __name__=='__main__':
 try:main()
 except (OSError,ValueError,KeyError) as e:raise SystemExit(f'Water repair composition refused: {e}')
