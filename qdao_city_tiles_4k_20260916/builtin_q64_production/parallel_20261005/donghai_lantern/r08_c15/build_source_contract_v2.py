"""Explicit approved c15 DAY v2 contract; current pixels and historical base replay.
All writes are within own source-contract-v2. DAY is read-only. No hash override.
"""
from pathlib import Path
from datetime import datetime,timezone
import copy,io,json,hashlib,shutil,sys
import numpy as np
from PIL import Image
import assemble_c15_shared as a
import replay_c15_consolidated as r
T=Path(__file__).resolve().parent;D=T/'source-contract-v2';DAY=T.parent.parent/'donghai_day';DT=DAY/'r08_c15'
sha=r.sha;read=r.read;need=r.need;ref=r.ref

def write(p,d):p=Path(p);need(p.resolve().is_relative_to(D.resolve()),'Write escaped new own contract');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def raw(a):return hashlib.sha256(a.tobytes()).hexdigest()
def pngsha(a):b=io.BytesIO();Image.fromarray(a).save(b,format='PNG');return hashlib.sha256(b.getvalue()).hexdigest()
def verify(e):need(Path(e['file']).exists() and sha(e['file'])==e['sha256'],'Dependency mismatch: '+e['file'])
def snap(e,category):
 verify(e);p=D/'snapshots'/category/(e['sha256'][:16]+'-'+Path(e['file']).name);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():need(sha(p)==e['sha256'],'Existing snapshot changed')
 else:shutil.copyfile(e['file'],p)
 return {'authority':e,'snapshot':ref(p)}
def check_field(field,weight,entry,label,proof):
 verify(entry)
 with np.load(entry['file'],allow_pickle=False) as z:
  need(np.array_equal(field.astype(np.float16),z['delta_rgb']),f'Recomputed RGB field differs {label}');need(np.array_equal(weight.astype(np.float16),z['weight']),f'Recomputed field weight differs {label}')
 proof.append({'id':label,'field':entry,'computedFloat16MatchesRecorded':True,'calculation':'Original float precision recomputation before rounding; stored float16 only checked, never substituted'})
def run():
 cp=DT/'output/assembly-manifest.json';current=read(cp);verify(current['output']);verify(current['extendedContext']);need(len(current['postprocessingChain'])==1,'Unexpected DAY published chain')
 chain=current['postprocessingChain'][0];verify(chain['integrationManifest']);approved=read(chain['integrationManifest']['file']);verify(approved['priorIntegrationManifest']);final=read(approved['priorIntegrationManifest']['file']);verify(chain['priorOutput']['historicalRecord']);historical=read(chain['priorOutput']['historicalRecord']['file']);need(historical['output']['sha256']==final['baseline']['sha256']==chain['priorOutput']['sha256'],'Historical base identity mismatch');need(final['baseline']==approved['baseline'],'Approved historical base differs')
 # The two mutated baseline paths are resolved through the exact immutable historical record;
 # current files are verified separately, and old PNG bytes are reconstructed below.
 for stage in (final,approved):
  for key,value in stage.items():
   if key=='baseline':continue
   for e in r.file_refs(value):verify(e)
 masks,mask_evidence=a.load_day_masks(historical);day_arrays={}
 for e in historical['nativeSources']:
  verify({'file':e['file'],'sha256':e['sha256']});verify({'file':e['recordFile'],'sha256':e['recordSha256']});rr,cc=map(int,(e['id'][1:3],e['id'][5:7]));day_arrays[rr,cc]=a.load_rgb(e['file'],e['sha256'],(1254,1254))
 extended,_=a.assemble(day_arrays,masks);base=extended[115:4211,115:4211].copy();need(pngsha(base)==historical['output']['sha256'],'Historical base PNG-byte replay failed');need(pngsha(extended)==historical['extendedContext']['sha256'],'Historical extended PNG-byte replay failed')
 entries={}
 for e in approved['nativeRepairs']:
  ident=r.native_id(e)
  if ident in entries:need(e['file']==entries[ident]['file'] and e['sha256']==entries[ident]['sha256'],'Repeated native differs')
  else:entries[ident]=e
 need(len(approved['nativeRepairs'])==20 and len(entries)==19,'Unreviewed native count')
 arrays={k:r.rgb(e['file']) for k,e in entries.items()};need(all(v.shape==(1254,1254,3) for v in arrays.values()),'Wrong native dimensions');fields=[];seams={e['id']:e for e in final['seams']}
 def join_field(label,field,weight,mask):check_field(field,weight,seams[label]['localColorMatch'],label,fields)
 first16=copy.deepcopy(final);first16['insertions']=first16['insertions'][:11]
 pieces=r.source_groups(first16,arrays,'day',join_field);pieces['root-finishing-left-insertion']=arrays['left-insertion'];pieces['water-left-horizontal']=arrays['water-left-horizontal'];need(set(pieces)=={e['id'] for e in final['insertions']},'Final insertion catalog mismatch')
 image=base.copy();union=np.zeros((4096,4096),np.uint8);ops=[]
 for e in final['insertions']:
  rect=e['rectXYXY'];old=r.cut(image,rect).copy();piece=pieces[e['id']];alpha=np.array(Image.open(e['alpha']['file']).convert('L'));need(old.shape==piece.shape and alpha.shape==piece.shape[:2],'Final shape mismatch')
  adjusted,field,weight=r.match(old,piece,alpha);check_field(field,weight,e['localBoundaryColorMatch'],e['id'],fields);image[rect[1]:rect[3],rect[0]:rect[2]]=r.blend(old,adjusted,alpha);np.maximum(r.cut(union,rect),alpha,out=r.cut(union,rect));ops.append({'id':e['id'],'coordinateSpace':'core','rectXYXY':rect,'alpha':e['alpha'],'colorField':e['localBoundaryColorMatch']})
 need(np.array_equal(image,r.rgb(final['candidate']['file'])),'Final stage exact pixels differ');need(np.array_equal(union,np.array(Image.open(final['unionMask']['file']).convert('L'))),'Final union differs');extended[115:4211,115:4211]=image;need(np.array_equal(extended,r.rgb(final['extendedContext']['file'])),'Final extended replay failed');final_proof={'corePixelIdentical':True,'extendedPixelIdentical':True,'coreRawRGBSha256':raw(image),'corePNGReencodedSha256':pngsha(image),'expectedCore':final['candidate']}
 # Approved append operations: re-use roof native with larger ROI, then native right halo.
 extras=approved['insertions'][len(final['insertions']):];need([e['id'] for e in extras]==['roof-full-end','east-hull-through-halo'],'Unknown approved operations')
 roof,halo=extras;rect=roof['rectXYXY'];old=r.cut(image,rect).copy();alpha=np.array(Image.open(roof['alpha']['file']).convert('L'));adjusted,field,weight=r.match(old,arrays['roof'],alpha);check_field(field,weight,roof['localBoundaryColorMatch'],'roof-full-end',fields);image[rect[1]:rect[3],rect[0]:rect[2]]=r.blend(old,adjusted,alpha);np.maximum(r.cut(union,rect),alpha,out=r.cut(union,rect));extended[115:4211,115:4211]=image;ops.append({'id':'roof-full-end','coordinateSpace':'core','sourceId':'roof','rectXYXY':rect,'alpha':roof['alpha'],'colorField':roof['localBoundaryColorMatch']})
 rect=halo['rectInExtendedXYXY'];src=entries['right-halo-finish']['sourceRectInExtendedXYXY'];local=[rect[0]-src[0],rect[1]-src[1],rect[2]-src[0],rect[3]-src[1]];piece=r.cut(arrays['right-halo-finish'],local);old=r.cut(extended,rect).copy();alpha=np.array(Image.open(halo['alpha']['file']).convert('L'));need(piece.shape==old.shape and alpha.shape==old.shape[:2],'Halo source/placement mismatch');adjusted,field,weight=r.match(old,piece,alpha);check_field(field,weight,halo['localBoundaryColorMatch'],'east-hull-through-halo',fields);extended[rect[1]:rect[3],rect[0]:rect[2]]=r.blend(old,adjusted,alpha);image=extended[115:4211,115:4211].copy();halo_union=np.zeros((4326,4326),np.uint8);halo_union[rect[1]:rect[3],rect[0]:rect[2]]=alpha;np.maximum(union,halo_union[115:4211,115:4211],out=union);ops.append({'id':'east-hull-through-halo','coordinateSpace':'extended','sourceId':'right-halo-finish','sourceRectInExtendedXYXY':src,'sourceCropXYXY':local,'rectInExtendedXYXY':rect,'rectInTileAndHaloXYXY':halo['rectInTileAndHaloXYXY'],'alpha':halo['alpha'],'colorField':halo['localBoundaryColorMatch']})
 need(np.array_equal(image,r.rgb(approved['candidate']['file'])),'Approved core exact replay failed');need(np.array_equal(extended,r.rgb(approved['extendedContext']['file'])),'Approved extended exact replay failed');need(np.array_equal(image,r.rgb(current['output']['file'])),'Current DAY output differs from approved replay');need(np.array_equal(extended,r.rgb(current['extendedContext']['file'])),'Current DAY halo differs from approved replay');need(np.array_equal(union,np.array(Image.open(approved['unionMask']['file']).convert('L'))),'Approved union mask mismatch')
 # Freeze after every dependency and replay has passed. Old 16 lock is untouched.
 oldp=T/'qa/consolidated-source-lock.json';old=read(oldp);old_entries={r.native_id(e):e for e in old['dayManifestSnapshot']['nativeRepairs']};catalog=[]
 source_ops={'wood-horizontal':[f'wood-horizontal-s{i}' for i in range(1,5)],'wood-right':['wood-right-w1','wood-right-w2'],'right-insertion-finish':['right-upper','right-lower'],'water-seams-g-left-insertion':['g-left-insertion'],'root-finishing-roof':['roof'],'roof-full-end':['roof'],'root-finishing-left-insertion':['left-insertion'],'water-left-horizontal':['water-left-horizontal'],'east-hull-through-halo':['right-halo-finish']}
 for id in ('a-left-cross','b-right-cross','c-left-bottom','d-right-bottom'):source_ops['water-'+id]=[id]
 for id in ('e-hull-waterline','f-lantern-blueboard'):source_ops[id]=[id]
 for op in ops:op['sourceIds']=source_ops[op['id']]
 for ident,e in entries.items():
  frozen=snap(e,'native-geometry');record=snap(e['record'],'native-records');prior=old_entries.get(ident);need(prior is None or prior['sha256']==e['sha256'],'An old source was replaced unexpectedly');own=T/'repairs/consolidated-sync/native'/(ident+'.png');uses=[o['id'] for o in ops if ident in o['sourceIds']];rect=e.get('sourceRectXYXY',e.get('sourceRectInTileAndRightHaloXYXY'))
  catalog.append({'id':ident,'daySource':e,'geometrySnapshot':frozen,'generationRecordSnapshot':record,'sourceRectTileAndHaloXYXY':rect,'coordinateSpace':'tile-and-right-halo' if ident=='right-halo-finish' else 'core','statusVersusOld16':'retained-identical' if prior else 'new-required','usedByOperations':uses,'festivalNativePath':str(own),'festivalConversionExists':own.exists(),'festivalConversion':ref(own) if own.exists() else None,'generationTask':'Reuse existing conversion only after its DAY source SHA and rectangle verify; otherwise builtin 1254 style conversion with actual festival same-window context and 04-guild','rightHaloRequired':ident=='right-halo-finish'})
 masks_fields={}
 for container in (historical['seams'],approved['seams'],approved['insertions']):
  for item in container:
   for key in ('maskPng','maskNpz','alpha','localColorMatch','localBoundaryColorMatch'):
    if item.get(key):e=item[key];masks_fields[(e['file'],e['sha256'])]=snap(e,'masks-and-fields')
 for k,e in [('published-assembly',ref(cp)),('historical-assembly',chain['priorOutput']['historicalRecord']),('final-integration',approved['priorIntegrationManifest']),('approved-integration',chain['integrationManifest']),('approved-review',chain['review'])]:snap(e,'manifests')
 output_snap=snap(approved['candidate'],'verified-day-output');ext_snap=snap(approved['extendedContext'],'verified-day-output')
 proof={'historicalBasePNGByteIdentical':True,'historicalExtendedPNGByteIdentical':True,'historicalCoreSHA':historical['output']['sha256'],'historicalExtendedSHA':historical['extendedContext']['sha256'],'finalStage':final_proof,'approvedCorePixelIdentical':True,'approvedExtendedPixelIdentical':True,'currentOutputPixelIdentical':True,'currentExtendedPixelIdentical':True,'approvedUnionPixelIdentical':True,'computedFieldsMatchRecordedFloat16':fields,'coreRawRGBSha256':raw(image),'extendedRawRGBSha256':raw(extended),'publishedTilesFileExists':(DAY/'tiles/r08_c15.png').exists()}
 contract={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c15','revision':2,'status':'verified-current-DAY-approved-chain','oldNativeSourceLock':ref(oldp),'currentDayAssembly':ref(cp),'approvedManifest':chain['integrationManifest'],'finalManifest':approved['priorIntegrationManifest'],'historicalAssembly':chain['priorOutput']['historicalRecord'],'authoritativeOutput':current['output'],'authoritativeExtended':current['extendedContext'],'dayGeometrySnapshot':output_snap,'dayExtendedSnapshot':ext_snap,'nativeSourceCount':19,'nativeReferenceCount':20,'original16Retained':16,'original16Replaced':0,'newSourceIds':[e['id'] for e in catalog if e['statusVersusOld16']=='new-required'],'nativeSources':catalog,'joinOperations':[e for e in approved['seams'] if e.get('localColorMatch')],'insertionOperations':ops,'maskAndColorFieldSnapshots':list(masks_fields.values()),'dayReplay':proof,'legacyBaselineResolution':'Two overwritten baseline file references resolved only by historical manifest SHA plus exact PNG-byte native replay. Never treated as current hash matches.','publishedTileStatus':'absent; current DAY output/assembly-manifest is authoritative','oldLockOverwritten':False,'dayWritten':False,'festivalPixelsGenerated':False,'formalAccepted':False,'script':ref(__file__)}
 write(D/'source-contract.json',contract);write(D/'day-replay-proof.json',proof);write(D/'conversion-tasks.json',{'sourceContract':ref(D/'source-contract.json'),'tasks':catalog,'newSourceIds':contract['newSourceIds'],'roofReuse':'One unchanged roof conversion drives both root-finishing-roof and roof-full-end masks; no duplicate generation required'})
 print(json.dumps({'contract':ref(D/'source-contract.json'),'uniqueNative':19,'old16Retained':16,'newSourceIds':contract['newSourceIds'],'dayExactReplay':True,'historicalBaseBytesExact':True,'geometrySnapshot':output_snap['snapshot'],'extendedSnapshot':ext_snap['snapshot']},ensure_ascii=False,indent=2))
if __name__=='__main__':run()
