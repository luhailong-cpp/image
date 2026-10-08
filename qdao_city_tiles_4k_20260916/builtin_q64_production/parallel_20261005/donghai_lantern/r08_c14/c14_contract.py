"""Pinned c14 source validation and exact current DAY repair-chain replay.

Only JSON preflight evidence is written here. Native source paths are resolved
from the DAY manifest, never guessed from patch ids. The original batch
source-contract is read and hashed without modification.
"""
from pathlib import Path
from datetime import datetime, timezone
import io,json,hashlib
import numpy as np
from PIL import Image

T=Path(__file__).resolve().parent
QA=T/'qa'
LOCK=QA/'assembly-source-lock.json'
REPORT=QA/'assembly-preflight.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def need(v,message):
 if not v:raise ValueError(message)
def same(a,b):return Path(a).resolve()==Path(b).resolve()
def meta(p):return {'file':str(p),'sha256':sha(p)}
def dump(p,d):
 p=Path(p);need(p.resolve().is_relative_to(QA.resolve()),'Preflight output outside c14/qa')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def pin(shared):
 contract_path=T/'source-contract.json';contract=read(contract_path)
 need(contract['tile']=='r08_c14' and contract['globalCoreXYWH']==[53248,28672,4096,4096],'Wrong own source contract coordinates')
 need(same(contract['dayDirectory'],shared.DAY/'r08_c14'),'Wrong contract DAY directory')
 need(contract['nativeWindowOriginXY']==[53133,28557] and contract['nativePixels']==[1254,1254],'Wrong native contract')
 need(sha(contract['west']['file'])==contract['west']['sha256']==contract['westSourceSha256'],'Pinned west candidate changed')
 live_manifest=read(shared.DAY_MANIFEST)
 if LOCK.exists():
  locked=read(LOCK)
  need(sha(contract_path)==locked['sourceContract']['sha256'],'Own source-contract changed after assembly snapshot; refresh requires explicit review')
  need(sha(shared.DAY_MANIFEST)==locked['dayManifest']['sha256'],'DAY manifest changed after assembly snapshot; review new native sources and repairs before creating a new snapshot')
  need(live_manifest==locked['dayManifestSnapshot'],'DAY manifest snapshot content differs')
 else:
  locked={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceContract':meta(contract_path),'sourceContractSnapshot':contract,'dayManifest':meta(shared.DAY_MANIFEST),'dayManifestSnapshot':live_manifest,'snapshotPolicy':'Immutable lock; refuse silent source updates. Existing own source-contract not rewritten.'}
  dump(LOCK,locked)
 return locked,live_manifest
def validate_inputs(shared,allow_partial=False):
 locked,m=pin(shared);parameters=m['parameters']
 need(parameters['order']=='assemble each row left-to-right, then rows top-to-bottom','Unknown DAY assembly order')
 for key in ('registration','colorCorrection','spatialResampling','imageBlur','maskBlur'):need(parameters[key] is False,f'Unsupported DAY processing: {key}')
 for k,v in {'core':1024,'halo':115,'overlap':230,'patchPixels':[1254,1254],'extendedPixels':[4326,4326],'cropXYXY':[115,115,4211,4211],'globalRectXYWH':[53248,28672,4096,4096]}.items():need(parameters[k]==v,f'DAY parameter mismatch: {k}')
 need(m['coverage']['fullCoverage'] is True,'DAY native coverage incomplete')
 day_entries={x['id']:x for x in m['nativeSources']};expected={f'r{r:02}_c{c:02}' for r in range(1,5) for c in range(1,5)}
 need(set(day_entries)==expected,'DAY must contain exactly 16 unique coordinates')
 arrays,day_arrays,evidence,missing={},{},[],[]
 for row in range(1,5):
  for column in range(1,5):
   name=f'r{row:02}_c{column:02}';de=day_entries[name]
   dp=Path(de['file']);drp=Path(de['recordFile']);dr=read(drp)
   need(dp.resolve().is_relative_to((shared.DAY/'r08_c14').resolve()),f'DAY source outside c14: {name}')
   need(de['extendedRectXYWH']==[(column-1)*1024,(row-1)*1024,1254,1254],f'DAY native coordinate mismatch: {name}')
   need(sha(drp)==de['recordSha256'] and dr['sha256']==de['sha256'] and same(dr['file'],dp),f'DAY actual source record mismatch: {name}')
   day_arrays[row,column]=shared.load_rgb(dp,de['sha256'],(1254,1254))
   op=T/'native'/f'{name}.png';orp=Path(str(op)+'.generation.json')
   if not op.exists():missing.append(name);continue
   need(orp.exists(),f'Own generation record missing: {name}')
   record=read(orp)
   need(same(record['file'],op) and [record['width'],record['height']]==[1254,1254],f'Own native identity mismatch: {name}')
   need(record['route']=='builtin' and record['resizedAfterGeneration'] is False and record.get('finalArtUpscaled') is not True,f'Own native provenance mismatch: {name}')
   arrays[row,column]=shared.load_rgb(op,record['sha256'],(1254,1254))
   geo=record['geometryMatchedTo'];gp=Path(geo['file'])
   authority=geo.get('dayAuthorityFile',geo['file']);authority_sha=geo.get('dayAuthoritySha256',geo['sha256'])
   need(same(authority,dp) and authority_sha==de['sha256']==geo['sha256'],f'Own geometryMatchedTo disagrees with current DAY nativeSources: {name}')
   need(sha(gp)==geo['sha256'],f'Own geometry snapshot bytes changed: {name}')
   gr=Path(geo.get('generationRecord',str(gp)+'.generation.json'))
   need(sha(gr)==geo['generationRecordSha256'],f'Geometry record changed: {name}')
   if not same(gp,dp):
    grj=read(gr);origins=grj.get('derivedFrom',[])
    need(any(same(x['file'],dp) and x['sha256']==de['sha256'] and x.get('generationRecordSha256')==de['recordSha256'] for x in origins),f'Frozen geometry snapshot lacks exact current DAY provenance: {name}')
   else:need(same(gr,drp) and geo['generationRecordSha256']==de['recordSha256'],f'Direct geometry record differs: {name}')
   refs,submitted=record['references'],record['submittedParameters']
   need(len(refs)==len(submitted['referenced_image_paths']) and len(refs)>=3,f'Incomplete submitted references: {name}')
   for ref,actual in zip(refs,submitted['referenced_image_paths']):need(same(ref['file'],actual) and sha(ref['file'])==ref['sha256'],f'Reference changed/unsubmitted: {name}')
   need(same(refs[0]['file'],gp) and refs[0]['sha256']==geo['sha256'],f'Geometry not actual first submitted image: {name}')
   for key in ('model','quality'):need(submitted.get(key,'missing') is None,f'False model selector: {name}')
   for key in ('actualModel','actualQuality'):need(record.get(key,'missing') is None,f'Unexpected actual model/quality evidence: {name}')
   need(sha(record['prompt'])==record['promptSha256'],f'Prompt changed: {name}')
   if record.get('requestFile'):need(sha(record['requestFile'])==record['requestSha256'],f'Request changed: {name}')
   ev=record['evidence'];need(ev.get('toolResultSha256',ev.get('sha256'))==record['sha256'],f'Tool-result SHA mismatch: {name}')
   raw=Path(ev['toolResultSourcePath']);need(raw.exists() and sha(raw)==record['sha256'],f'Tool-result absent/changed: {name}; record any authorized cache cleanup before reuse')
   evidence.append({'id':name,'file':str(op),'sha256':record['sha256'],'pixels':[1254,1254],'recordFile':str(orp),'recordSha256':sha(orp),'dayGeometry':{'file':str(dp),'sha256':de['sha256'],'recordFile':str(drp),'recordSha256':de['recordSha256']},'geometrySnapshot':{'file':str(gp),'sha256':geo['sha256']},'extendedRectXYWH':de['extendedRectXYWH'],'allActualReferenceHashesVerified':True,'sourceResized':False,'geometryVisuallyAccepted':False,'actualModel':None,'actualQuality':None})
 need(sha(shared.DAY_MANIFEST)==locked['dayManifest']['sha256'],'DAY changed during source validation')
 if not allow_partial:need(not missing,f'Missing own native patches: {missing}')
 return arrays,day_arrays,evidence,m,locked['dayManifest']['sha256'],missing
def read_mask(entry):
 need(sha(entry['file'])==entry['sha256'],f'DAY repair mask changed: {entry["file"]}')
 with Image.open(entry['file']) as im:
  need(im.mode=='L','Repair mask must be native grayscale')
  alpha=np.array(im)
 need(set(np.unique(alpha)).issubset({0,64,191,255}),'Unsupported DAY repair transition values')
 return alpha
def apply_day_repair(shared,core,entry):
 need(sha(entry['file'])==entry['sha256'],'DAY repair integration manifest changed')
 doc=read(entry['file']);rect=doc['changedPixelsRestrictedToRect'];x,y,x1,y1=rect
 need(y==0 and x1-x==1254,'Unsupported DAY repair rectangle')
 for k in ('sourceResampling','upscale','colorCorrection'):need(doc[k] is False,f'Unsupported DAY repair {k}')
 sources=[shared.load_rgb(p['file'],p['sha256'],(1254,1254)) for p in doc['patches']]
 masks={Path(e['file']).name:read_mask(e) for e in doc['masks']}
 if len(sources)==2:
  need(y1==2278,'Unsupported two-patch repair dimensions')
  strip=np.concatenate((sources[0][:1024],shared.blend(sources[0][1024:],sources[1][:230],masks['patch-join-mask.png'].T),sources[1][230:]),axis=0)
 else:need(len(sources)==1 and y1==1254,'Unsupported DAY repair patch count');strip=sources[0].copy()
 old=core[:y1,x:x1].copy()
 strip[:,:150]=shared.blend(old[:,:150],strip[:,:150],masks['left-insert-mask.png'])
 strip[:,-150:]=shared.blend(strip[:,-150:],old[:,-150:],masks['right-insert-mask.png'])
 strip[-150:]=shared.blend(strip[-150:],old[-150:],masks['bottom-insert-mask.png'].T)
 result=core.copy();result[:y1,x:x1]=strip
 proof={'record':entry,'rectXYXY':rect,'patches':[{'file':p['file'],'sha256':p['sha256']} for p in doc['patches']],'masks':doc['masks'],'operationOrder':['patch-join if present','left insert','right insert','bottom insert'],'sourceResized':False}
 return result,proof
def verify_day_replay(shared,day_arrays,m,masks):
 base,_=shared.assemble(day_arrays,masks);core=base[115:4211,115:4211].copy();proof=[]
 chain=m.get('postAssemblyRepairChain',[])
 if m.get('postAssemblyRepair'):need(chain,'Current DAY post-repair manifest lacks full replay chain')
 for e in chain:core,p=apply_day_repair(shared,core,e);proof.append(p)
 result=base.copy();result[115:4211,115:4211]=core
 expected_extended=shared.load_rgb(m['extendedContext']['file'],m['extendedContext']['sha256'],(4326,4326))
 expected_core=shared.load_rgb(m['output']['file'],m['output']['sha256'],(4096,4096))
 need(np.array_equal(result,expected_extended),'Exact current DAY extended replay failed')
 need(np.array_equal(core,expected_core),'Exact current DAY core replay failed')
 return {'dayExtendedReplayPixelIdentical':True,'dayCoreReplayPixelIdentical':True,'dayNativeSources':16,'sharedMaskCount':15,'postAssemblyRepairChain':proof,'festivalPostRepairSourcesRequired':[{'daySource':p,'requiredOwnNative':str(T/'repairs'/Path(p['file']).parent.name/'native'/Path(p['file']).name),'status':'not-validated-by-base-assembly'} for r in proof for p in r['patches']],'finalGeometryAcceptance':False}
def preflight(shared):
 a,d,e,m,h,missing=validate_inputs(shared,allow_partial=True);masks,mask_evidence=shared.load_day_masks(m)
 proof=verify_day_replay(shared,d,m,masks)
 report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'source-preflight-passed-waiting-for-own-native' if missing else 'source-preflight-passed-all-native-ready','sourceContract':meta(T/'source-contract.json'),'immutableSourceLock':meta(LOCK),'dayManifest':{'file':str(shared.DAY_MANIFEST),'sha256':h},'ownNativeCount':len(e),'missingNativeCount':len(missing),'missingNative':missing,'ownNativeSources':e,'dayMaskEvidence':mask_evidence,**proof,'pixelOutputsWritten':False,'formalAccepted':False,'visualInspectionPerformed':False,'nativeSourcesOrRecordsModified':False}
 need(sha(shared.DAY_MANIFEST)==h,'DAY manifest changed during replay');dump(REPORT,report)
 return {k:v for k,v in report.items() if k not in ('ownNativeSources','dayMaskEvidence','postAssemblyRepairChain')}
