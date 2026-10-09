"""Compose c15 converted consolidated repairs only from a fully pinned contract.

Default --check validates complete festival sources and exact DAY replay. --build
writes a new immutable candidate with exact masks and separately recorded bounded
RGB difference fields. No source conversion, DAY write, or global registration.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
import numpy as np
from PIL import Image
import replay_c15_consolidated as r
T=r.T;B=T/'repairs/consolidated-sync';D=B/'assembled';sha=r.sha;read=r.read;ref=r.ref;need=r.need

def write(p,d):r.write(p,d)
def save(p,pixels,metadata):
 p=Path(p);need(p.resolve().is_relative_to(D.resolve()),'Image output escaped assembly directory');p.parent.mkdir(parents=True,exist_ok=True);im=pixels if isinstance(pixels,Image.Image) else Image.fromarray(pixels);need(not p.exists(),'Immutable output already exists: '+str(p));im.save(p);i={**ref(p),'pixels':list(im.size)};write(str(p)+'.generation.json',{**i,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'actualModel':None,'actualQuality':None,'generatedByAI':False,'formalAccepted':False,'artResampled':False,**metadata});return {**i,'generationRecord':ref(str(p)+'.generation.json')}

def validate():
 need(r.LOCK.exists(),'Full DAY integration lock absent. Run read-only preflight and explicitly pin a consistent, exact-replayed manifest first.')
 lock=read(r.LOCK);need(sha(lock['manifest']['file'])==lock['manifest']['sha256'],'Pinned DAY integration manifest changed');m=lock['manifestSnapshot'];need(read(lock['manifest']['file'])==m,'Manifest snapshot mismatch')
 for e in r.file_refs(m):need(Path(e['file']).exists() and sha(e['file'])==e['sha256'],'Pinned DAY dependency mismatch: '+e['file'])
 day_arrays={r.native_id(e):r.rgb(e['file']) for e in m['nativeRepairs']};day_result,_,_=r.replay(m,r.rgb(m['baseline']['file']),day_arrays);need(np.array_equal(day_result,r.rgb(m['candidate']['file'])),'Pinned DAY exact replay failed')
 base_manifest=T/'tone-assembly/output/tone-assembly-manifest.json';bm=read(base_manifest);bi=bm.get('candidate',bm.get('output'));need(bi is not None,'Festival base manifest lacks candidate');need(sha(bi['file'])==bi['sha256'],'Festival base changed');base=r.rgb(bi['file']);need(base.shape==(4096,4096,3),'Festival base incomplete')
 arrays={};sources=[];missing=[]
 for e in m['nativeRepairs']:
  ident=r.native_id(e);p=B/'native'/(ident+'.png')
  if not p.exists():missing.append(ident);continue
  record=read(str(p)+'.generation.json');need(sha(p)==record['sha256'],'Own native hash mismatch '+ident);need(record['route']=='builtin' and record['actualModel'] is None and record['actualQuality'] is None,'Native route/model evidence mismatch');need(record['submittedParameters']['model'] is None and record['submittedParameters']['quality'] is None,'False selector provenance');need(record['resizedAfterGeneration'] is False and record['finalArtUpscaled'] is False,'Native resampling not allowed')
  n=r.rgb(p);need(n.shape==(1254,1254,3),'Own repair native must be1254 square');need(record['dayNativeRepair']['sha256']==e['sha256'] and Path(record['dayNativeRepair']['file']).resolve()==Path(e['file']).resolve(),'Own repair DAY authority changed');need(record['sourceRectXYXY']==e['sourceRectXYXY'],'Source geometry rectangle changed');need(sha(record['prompt'])==record['promptSha256'],'Prompt changed')
  for rr in record['references']:need(sha(rr['file'])==rr['sha256'],'Submitted reference changed')
  raw=record['evidence']['toolResultSourcePath'];need(Path(raw).exists() and sha(raw)==record['sha256'],'Raw tool result changed or missing');need(len(record['references'])==len(record['submittedParameters']['referenced_image_paths'])>=3,'Incomplete submitted image reference provenance')
  arrays[ident]=n;sources.append({'id':ident,'native':ref(p),'record':ref(str(p)+'.generation.json'),'daySource':e,'sourceRectXYXY':e['sourceRectXYXY']})
 need(not missing,'Missing actual festival repair natives: '+', '.join(missing))
 return m,base,bm,base_manifest,arrays,sources

def qa_image(result,candidate,m):
 im=Image.fromarray(result);items=[]
 def crop(name,rect):
  rect=[max(0,rect[0]),max(0,rect[1]),min(4096,rect[2]),min(4096,rect[3])];items.append(save(D/'qa'/(name+'.png'),im.crop(rect),{'derivedFrom':[candidate],'operation':'exact native pixel crop','tileRectXYXY':rect,'pixelScale':1,'visualReview':'pending'}))
 for e in m['nativeRepairs']:
  ident=r.native_id(e);x,y,x1,y1=e['sourceRectXYXY'];crop(ident+'-full1254',[x,y,x1,y1])
  for side,box in [('left',[x-224,y,x+224,y1]),('right',[x1-224,y,x1+224,y1]),('top',[x,y-224,x1,y+224]),('bottom',[x,y1-224,x1,y1+224])]:crop(ident+'-'+side,box)
 for axis in ('x','y'):
  for k in (1024,2048,3072):
   for n in range(4):crop(f'{axis}{k}-return-part{n+1:02}',[k-448,n*1024,k+448,(n+1)*1024] if axis=='x' else [n*1024,k-448,(n+1)*1024,k+448])
 corners=Image.new('RGB',(1024,1024));boxes=[]
 for b,p in [((0,0,512,512),(0,0)),((3584,0,4096,512),(512,0)),((0,3584,512,4096),(0,512)),((3584,3584,4096,4096),(512,512))]:corners.paste(im.crop(b),p);boxes.append({'sourceRect':b,'destination':p})
 items.append(save(D/'qa/four-tile-corners.png',corners,{'derivedFrom':[candidate],'crops':boxes,'pixelScale':1,'visualReview':'pending'}));sheet=Image.new('RGB',(1536,1536));boxes=[]
 for j,y in enumerate((1024,2048,3072)):
  for i,x in enumerate((1024,2048,3072)):b=[x-256,y-256,x+256,y+256];p=[i*512,j*512];sheet.paste(im.crop(b),p);boxes.append({'sourceRect':b,'destination':p})
 items.append(save(D/'qa/nine-internal-junctions.png',sheet,{'derivedFrom':[candidate],'crops':boxes,'pixelScale':1,'visualReview':'pending'}));return items

def run(build=False):
 m,base,bm,bmp,arrays,sources=validate()
 if not build:return {'ready':True,'nativeCount':len(arrays),'dayExactReplay':True,'pixelOutputWritten':False,'lock':ref(r.LOCK)}
 need(not D.exists(),'Immutable assembly directory already exists; choose explicit new stage path')
 fields=[]
 def field_sink(ident,field,weight,mask):
  p=D/'fields'/(ident+'.npz');p.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(p,delta_rgb=field.astype(np.float32),weight=weight.astype(np.float32),exact_day_alpha=mask);fields.append({'id':ident,**ref(p),'maxAbsoluteDelta':float(np.abs(field).max()),'artBlurred':False,'sourceResampled':False})
 # Raw chain uses every exact DAY alpha and preserves unchanged festival source pixels.
 raw_manifest=json.loads(json.dumps(m))
 for seam in raw_manifest['seams']:seam.pop('localColorMatch',None)
 for insertion in raw_manifest['insertions']:insertion['localBoundaryColorMatch']=None
 raw,raw_union,raw_ops=r.replay(raw_manifest,base,arrays,mode='raw')
 tone,union,operations=r.replay(m,base,arrays,mode='festival',field_sink=field_sink);need(np.array_equal(raw_union,union),'Color matching changed alpha support')
 delta=np.clip(tone.astype(np.int16)-raw.astype(np.int16),-24,24).astype(np.int8);result=(raw.astype(np.int16)+delta).astype(np.uint8);need(np.array_equal(result[union==0],base[union==0]),'Final correction escaped alpha union');need(int(np.abs(delta).max())<=24,'Final bounded delta exceeded24')
 dp=D/'fields/final-applied-delta.npz';np.savez_compressed(dp,delta_rgb=delta,exact_day_alpha_union=union)
 common={'operation':'Exact reviewed DAY consolidated masks plus bounded festival RGB difference returns','dayIntegrationLock':ref(r.LOCK),'priorFestivalManifest':ref(bmp),'repairSources':sources,'maskOperations':operations,'rawMaskOperations':raw_ops,'sourceResampled':False,'artResampled':False,'imageBlur':False,'maskBlur':False,'geometryChanged':False,'colorFields':fields,'finalDeltaField':ref(dp),'maximumFinalChannelDelta':int(np.abs(delta).max()),'outsideAlphaUnionChangedPixels':0,'formalAccepted':False,'clientAccepted':False,'completePixelCandidate':True,'wholeCityComplete':False,'visualReview':'pending full native QA','globalRegistryModified':False}
 raw_info=save(D/'output/r08_c15-exact-mask-raw.png',raw,{**common,'operation':'Raw exact alpha replay; no color corrections','colorFields':[],'finalDeltaField':None,'maximumFinalChannelDelta':0});candidate=save(D/'output/r08_c15.png',result,{**common,'rawBaseline':raw_info})
 exi=bm['extendedContext'];need(sha(exi['file'])==exi['sha256'],'Festival halo source changed');ex=r.rgb(exi['file']);need(ex.shape==(4326,4326,3),'Wrong halo dimensions');need(np.array_equal(ex[115:4211,115:4211],base),'Festival halo/core incoherent');ex[115:4211,115:4211]=result;extended=save(D/'output/extended-context.png',ex,{**common,'unchangedHaloSource':exi,'cropXYXY':[115,115,4211,4211]});qa=qa_image(result,candidate,m);write(D/'output/integration-manifest.json',{**common,'candidate':candidate,'extendedContext':extended,'rawBaseline':raw_info,'qa':qa,'script':ref(__file__),'createdAtUtc':datetime.now(timezone.utc).isoformat()})
 return {'candidate':candidate,'nativeCount':len(arrays),'qaCount':len(qa),'outsideAlphaUnionChangedPixels':0,'formalAccepted':False}
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build',action='store_true');args=parser.parse_args()
 try:print(json.dumps(run(args.build),ensure_ascii=False,indent=2))
 except (ValueError,FileNotFoundError,KeyError) as e:raise SystemExit('Consolidated composition refused: '+str(e))
