"""Independent native-pixel c14/c15 edge composition; no DAY seam mask exists or is claimed."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;OWN=D.parent.parent;sys.path.insert(0,str(OWN))
import compose_west as cw
import finish_west as fw
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def verify(e):assert sha(e['file'])==e['sha256'],e['file']
def write(p,d):
 p=Path(p);assert p.resolve().is_relative_to(D.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rgb(p):return np.asarray(Image.open(p).convert('RGB')).copy()
def save(p,a,m):
 p=Path(p);assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);im=a if isinstance(a,Image.Image) else Image.fromarray(a);im.save(p)
 assert np.array_equal(np.asarray(Image.open(p)),np.asarray(im));e={**ref(p),'pixels':list(im.size)};write(str(p)+'.generation.json',{**e,**m,'actualModel':None,'actualQuality':None,'generatedByAI':False,'formalAccepted':False});return e
def mask(a,b,label,rect,transpose=False):
 if transpose:a,b=a.transpose(1,0,2),b.transpose(1,0,2)
 assert a.shape==b.shape
 h,w=a.shape[:2];af=a.astype(np.float32);bf=b.astype(np.float32)
 cost=np.abs(af-bf).mean(2)+.005*np.abs(np.arange(w)[None,:]-(w-1)/2)
 cost[:,:5]=1e8;cost[:,-5:]=1e8
 # The only smoothing here is accumulated cost/path selection, never image resampling.
 cumulative=cost[0].copy();backs=np.zeros((h,w),np.int8)
 for y in range(1,h):
  three=np.stack((np.r_[1e12,cumulative[:-1]],cumulative,np.r_[cumulative[1:],1e12]))
  best=np.argmin(three,axis=0);backs[y]=best.astype(np.int8)-1;cumulative=cost[y]+three[best,np.arange(w)]
 offsets=np.empty(h,np.int32);offsets[-1]=int(cumulative.argmin())
 for y in range(h-1,0,-1):offsets[y-1]=offsets[y]+backs[y,offsets[y]]
 assert np.abs(np.diff(offsets)).max()<=1
 distance=np.arange(w)[None,:]-offsets[:,None];alpha=np.where(distance<=-2,0,np.where(distance==-1,64,np.where(distance==0,191,255))).astype(np.uint8)
 if transpose:alpha=alpha.T
 p=D/'masks'/(label+'.npz');p.parent.mkdir(exist_ok=True);assert not p.exists();np.savez_compressed(p,alpha_u8=alpha,seam_offsets=offsets,pair_rect_xyxy=np.array(rect),transition_pixels=np.array(2))
 png=save(D/'masks'/(label+'.png'),alpha,{'operation':'OWN independently computed minimum RGB mismatch path, no displacement','pairRectXYXY':rect,'notArtwork':True})
 return alpha,{'id':label,'orientation':'horizontal' if transpose else 'vertical','pairRectXYXY':rect,'maskNpz':ref(p),'maskPng':png,'ownComputedMask':True,'DAYMaskReplayed':False,'pathMaximumNeighborStep':int(np.abs(np.diff(offsets)).max()),'transitionPartialPixels':2}
def own_field(label,metadata,**arrays):
 if 'day_alpha' in arrays:arrays['own_alpha']=arrays.pop('day_alpha')
 p=D/'fields'/(label+'.npz');p.parent.mkdir(exist_ok=True);assert not p.exists();np.savez_compressed(p,**arrays)
 return {'id':label,'field':ref(p),**metadata,'maskAuthority':'independent OWN generated-overlap seam','DAYRgbFieldApplied':False,'artBlurred':False}
def main():
 assert not (D/'output/west-final-manifest.json').exists()
 cp=D/'source-contract.json';contract=read(cp);sources={e['id']:e for e in contract['sources']}
 for e in sources.values():verify(e['snapshot'])
 base=np.concatenate([rgb(sources[k]['snapshot']['file']) for k in ['festival-c14','festival-c15']],axis=1)
 patches=[];natives=[]
 for i in range(1,5):
  p=D/'native'/f's{i}.png';rp=Path(str(p)+'.generation.json');r=read(rp);verify(r);assert r['pixels']==[1254,1254] and r['route']=='builtin' and r['actualModel'] is None and r['actualQuality'] is None
  assert r['pairRectXYXY']==[3469,[0,1024,2048,2842][i-1],4723,[0,1024,2048,2842][i-1]+1254]
  verify(r['request']);verify(r['prompt']);verify(r['sourceContract']);assert r['sourceContract']['sha256']==sha(cp)
  for e in r['references']:verify(e)
  raw=Path(r['evidence']['toolResultSourcePath']);assert sha(raw)==r['sha256']==r['evidence']['toolResultSha256'];patches.append(rgb(p));natives.append({'id':f's{i}',**ref(p),'record':ref(rp)})
 strip=patches[0].copy();masks={};seams=[]
 for i,y in enumerate([1024,2048,2842],1):
  overlap=len(strip)-y;label=f'strip-s{i}-s{i+1}';a,e=mask(strip[-overlap:],patches[i][:overlap],label,[3469,y,4723,y+overlap],True);masks[label]=a;seams.append(e);strip=np.concatenate((strip[:-overlap],cw.blend(strip[-overlap:],patches[i][:overlap],a),patches[i][overlap:]))
 for side,a,b,rect in [('left',base[:,3469:3619],strip[:,:150],[3469,0,3619,4096]),('right',strip[:,-150:],base[:,4573:4723],[4573,0,4723,4096])]:
  alpha,e=mask(a,b,'insert-'+side,rect);masks['insert-'+side]=alpha;seams.append(e)
 raw=cw.compose(base,patches,masks)
 fw.field_record=own_field
 result,fields,deltafield=fw.matched_four(base,patches,masks,raw)
 assert np.array_equal(result[:,:3469],base[:,:3469]) and np.array_equal(result[:,4723:],base[:,4723:])
 delta=result[:,3469:4723].astype(np.int16)-raw[:,3469:4723].astype(np.int16);assert np.abs(delta).max()<=24
 with np.load(deltafield['field']['file']) as z:assert np.array_equal(raw[:,3469:4723].astype(np.int16)+z['delta_rgb'],result[:,3469:4723])
 common={'sourceContract':ref(cp),'nativeRepairSources':natives,'geometrySyncPending':ref(D/'geometry-sync-pending.json'),'authorizedPairRectXYXY':[3469,0,4723,4096],'seams':seams,'DAYSharedEdgeMasksApplied':False,'OWNIndependentlyComputedSeams':True,'toneFields':fields,'finalToneDelta':deltafield,'maximumToneDeltaFromExactOwnMaskRaw':int(np.abs(delta).max()),'outsideAuthorizedStripChangedPixels':0,'c14OutsideEast627ExactlyPreserved':True,'c15OutsideWest627ExactlyPreserved':True,'resized':False,'geometryWarped':False,'imageBlur':False,'DAYWritten':False,'globalRegistryModified':False,'formalAccepted':False}
 outputs=[]
 for name,pix,rect in [('pair-r08_c14-c15',result,[0,0,8192,4096]),('r08_c14',result[:,:4096],[0,0,4096,4096]),('r08_c15',result[:,4096:],[4096,0,8192,4096])]:outputs.append({'id':name,**save(D/'output'/(name+'.png'),pix,{**common,'pairRectXYXY':rect})})
 rawinfo=save(D/'output/shared-strip-exact-mask-raw.png',raw[:,3469:4723],{'sourceContract':ref(cp),'operation':'pure own masks, no RGB field','resized':False})
 qa=[]
 def crop(name,box):
  x,y,x1,y1=box;qa.append({'id':name,**save(D/'qa'/(name+'.png'),result[y:y1,x:x1],{'derivedFrom':outputs,'pairRectXYXY':box,'pixelScale':1,'resized':False,'actualVisualReview':'pending'}),'pairRectXYXY':box})
 for name,center,width in [('common-edge',4096,512),('attachment-left',3544,896),('attachment-right',4648,896)]:
  for i in range(4):crop(f'{name}-return-part{i+1:02}',[center-width//2,i*1024,center+width//2,(i+1)*1024])
 for i,(y,ov) in enumerate([(1024,230),(2048,230),(2842,460)],1):crop(f'longitudinal-{i}-return',[3469,y-256,4723,min(4096,y+ov+256)])
 for name,x in [('left',3469),('right',4723)]:
  crop(f'corner-{name}-top',[x-256,0,x+256,512]);crop(f'corner-{name}-bottom',[x-256,3584,x+256,4096])
 crop('attachment-top-full',[3469,0,4723,256]);crop('attachment-bottom-full',[3469,3840,4723,4096]);crop('source-bar-rope-junction',[3830,820,4400,1330]);crop('old-water-crop-line',[3960,3070,4380,3320])
 assert len(qa)==23
 man={**common,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'script':ref(__file__),'sharedMathHelpers':[ref(cw.__file__),ref(fw.__file__)],'outputs':outputs,'rawStrip':rawinfo,'qa':qa,'qaCoverage':{'fullCommonEdge':4096,'bothOuterReturns':4096,'longitudinalReturns':3,'corners':4,'topBottomFull':True,'explicitSourceDefectFocus':2,'nativeScale':1},'status':'immutable complete pair, actual QA pending'}
 write(D/'output/west-final-manifest.json',man);print(json.dumps({'outputs':outputs,'manifest':ref(D/'output/west-final-manifest.json'),'qaCount':len(qa)},indent=2))
if __name__=='__main__':main()
