"""Read-only DAY consolidated source check. No silent lock refresh or DAY writes.

check inspects the live manifest targeted by the native-source lock. pin creates
an immutable full integration lock only after every dependency and exact DAY
replay pass. A new manifest is never silently adopted.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;Q=T/'qa';LOCK=Q/'consolidated-integration-lock.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def need(ok,msg):
 if not ok:raise ValueError(msg)
def write(p,d):p=Path(p);need(p.resolve().is_relative_to(T.resolve()),'Write outside own c15');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def blend(a,b,m):return ((a.astype(np.uint32)*(255-m[:,:,None])+b.astype(np.uint32)*m[:,:,None]+127)//255).astype(np.uint8)
def cut(a,b):return a[b[1]:b[3],b[0]:b[2]]
def file_refs(v):
 if isinstance(v,dict):
  if 'file' in v and 'sha256' in v:yield v
  for k,x in v.items():
   if k not in ('qa','insertionQA','record'):yield from file_refs(x)
 elif isinstance(v,list):
  for x in v:yield from file_refs(x)
def material_lowpass(v):
 for _ in range(3):
  for axis in (0,1):
   pad=[(0,0),(0,0)];pad[axis]=(24,24);p=np.pad(v,pad,mode='reflect');c=np.cumsum(p,axis=axis,dtype=np.float64);c=np.concatenate((np.take(c,[0],axis=axis)*0,c),axis=axis);v=(c[49:]-c[:-49])/49 if axis==0 else (c[:,49:]-c[:,:-49])/49
 return v.astype(np.float32)
def mask_distance(mask):
 h,w=mask.shape;xx=np.arange(w)[None,:];left=xx-np.maximum.accumulate(np.where(mask,-w,xx),axis=1);right=np.minimum.accumulate(np.where(mask,2*w,xx)[:,::-1],axis=1)[:,::-1]-xx;d=np.minimum(left,right).astype(np.int32)
 for y in range(1,h):np.minimum(d[y],d[y-1]+1,out=d[y])
 for y in range(h-2,-1,-1):np.minimum(d[y],d[y+1]+1,out=d[y])
 return d
def match(before,patch,alpha,max_delta=32):
 def cat(a):f=a.astype(np.int16);return np.where((f[:,:,2]>f[:,:,0]+15)&(f[:,:,1]>f[:,:,0]+5),1,np.where((f[:,:,0]>f[:,:,2]+15)&(f[:,:,0]>f[:,:,1]+4),2,0))
 cb,cp=cat(before),cat(patch);delta=before.astype(np.float32)-patch.astype(np.float32);field=np.zeros_like(delta)
 for k in (0,1,2):
  valid=((cb==k)&(cp==k)).astype(np.float32);den=material_lowpass(valid)
  for c in range(3):v=material_lowpass(delta[:,:,c]*valid)/np.maximum(den,0.001);field[:,:,c][cp==k]=v[cp==k]
 weight=np.maximum(0,1-mask_distance(alpha>0)/112.0)**2;weight[alpha==0]=0;field=np.clip(field,-max_delta,max_delta)*weight[:,:,None]
 return np.clip(np.rint(patch.astype(np.float32)+field),0,255).astype(np.uint8),field,weight

def native_id(e):
 p=Path(e['file']);par=p.parent.name
 if par in ('wood-horizontal','wood-right'):return par+'-'+p.stem
 return par

def source_groups(m,arrays,mode='day',field_sink=None):
 seams={e['id']:e for e in m['seams']};out={}
 def join(ids,starts,orientation,label,origin):
  current=arrays[ids[0]].copy()
  for i,ident in enumerate(ids[1:],1):
   nxt=arrays[ident];start=starts[i];axis=1 if orientation=='vertical' else 0;ov=current.shape[axis]-start;e=seams[f'{label}-{i}-{i+1}'];mask=np.array(Image.open(e['maskPng']['file']).convert('L'));old=current[:,-ov:] if axis==1 else current[-ov:];later=nxt[:,:ov] if axis==1 else nxt[:ov]
   need(old.shape[:2]==mask.shape==later.shape[:2],f'Join mask mismatch {e["id"]}')
   expected=[origin[0]+start,origin[1],origin[0]+start+ov,origin[1]+current.shape[0]] if axis==1 else [origin[0],origin[1]+start,origin[0]+current.shape[1],origin[1]+start+ov]
   need(e['pairOverlapRectXYXY']==expected,f'Join coordinates mismatch {e["id"]}')
   if mode=='festival' or e.get('localColorMatch'):
    later,field,weight=match(old,later,mask,max_delta=24 if mode=='festival' else 32)
    if field_sink is not None:field_sink(e['id'],field,weight,mask)
   mix=blend(old,later,mask);current=np.concatenate((current[:,:-ov],mix,nxt[:,ov:]),axis=1) if axis==1 else np.concatenate((current[:-ov],mix,nxt[ov:]),axis=0)
  return current
 out['wood-horizontal']=join([f'wood-horizontal-s{i}' for i in range(1,5)],[0,1024,2048,2842],'vertical','wood-horizontal',[0,397])[:,128:3968]
 out['wood-right']=join(['wood-right-w1','wood-right-w2'],[0,1024],'horizontal','wood-right',[2445,1651])
 out['right-insertion-finish']=join(['right-upper','right-lower'],[0,794],'horizontal','right-insertion-finish',[2842,2048])
 for ident in ('a-left-cross','b-right-cross','c-left-bottom','d-right-bottom'):out['water-'+ident]=arrays[ident]
 for ident in ('e-hull-waterline','f-lantern-blueboard'):out[ident]=arrays[ident]
 out['water-seams-g-left-insertion']=arrays['g-left-insertion'];out['root-finishing-roof']=arrays['roof']
 need(set(out)=={e['id'] for e in m['insertions']},'Unreviewed insertion/source mapping; update operation catalog explicitly')
 return out

def replay(m,base,arrays,mode='day',field_sink=None):
 pieces=source_groups(m,arrays,mode,field_sink);result=base.copy();union=np.zeros((4096,4096),np.uint8);report=[]
 for e in m['insertions']:
  rect=e['rectXYXY'];old=cut(result,rect).copy();piece=pieces[e['id']];alpha=np.array(Image.open(e['alpha']['file']).convert('L'));need(old.shape==piece.shape and alpha.shape==old.shape[:2],f'Insertion size mismatch {e["id"]}')
  adjusted=piece
  if mode=='festival' or e.get('localBoundaryColorMatch'):
   adjusted,field,weight=match(old,piece,alpha,max_delta=24 if mode=='festival' else 32)
   if field_sink is not None:field_sink(e['id'],field,weight,alpha)
  result[rect[1]:rect[3],rect[0]:rect[2]]=blend(old,adjusted,alpha);u=cut(union,rect);np.maximum(u,alpha,out=u);report.append({'id':e['id'],'rectXYXY':rect,'alpha':e['alpha'],'outsideAlphaZeroExact':bool(np.array_equal(cut(result,rect)[alpha==0],old[alpha==0]))})
 need(np.array_equal(base[union==0],result[union==0]),'Pixels outside masks changed')
 return result,union,report

def check(pin=False):
 native_lock=read(Q/'consolidated-source-lock.json');mp=Path(native_lock['dayManifest']['file']);m=read(mp);problems=[];checked={}
 for e in file_refs(m):
  p=Path(e['file']);key=str(p)
  if key in checked:continue
  actual=sha(p) if p.exists() else None;checked[key]=actual
  if actual!=e['sha256']:problems.append({'file':key,'expected':e['sha256'],'actual':actual})
 frozen=native_lock['dayManifestSnapshot']['nativeRepairs'];identity=lambda es:[(e['file'],e['sha256'],e['sourceRectXYXY']) for e in es]
 if identity(frozen)!=identity(m['nativeRepairs']):problems.append({'nativeRepairCatalog':'changed; explicit review required'})
 proof=None
 if not problems:
  try:
   arrays={native_id(e):rgb(e['file']) for e in m['nativeRepairs']};base=rgb(m['baseline']['file']);result,union,ops=replay(m,base,arrays);expected=rgb(m['candidate']['file']);need(np.array_equal(result,expected),'DAY candidate exact replay failed');need(np.array_equal(union,np.array(Image.open(m['unionMask']['file']).convert('L'))),'DAY union mask replay failed');ex=rgb(m['extendedContext']['file']);need(np.array_equal(ex[115:4211,115:4211],result),'DAY extended core mismatch');proof={'candidatePixelIdentical':True,'unionPixelIdentical':True,'extendedCorePixelIdentical':True,'nativeRepairCount':len(arrays),'operationCatalog':ops}
  except Exception as e:problems.append({'replayFailure':str(e)})
 report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'manifest':ref(mp),'nativeSourceLock':ref(Q/'consolidated-source-lock.json'),'dependencyCount':len(checked),'problems':problems,'sharedRepairAssemblyReady':not problems,'dayReplay':proof,'pixelOutputWritten':False,'dayWritten':False}
 write(Q/'consolidated-integration-preflight.json',report)
 if pin:
  need(not problems,'Cannot pin stale or unreplayable DAY repair contract')
  locked={'createdAtUtc':report['createdAtUtc'],'manifest':ref(mp),'manifestSnapshot':m,'sourceLock':report['nativeSourceLock'],'dayReplay':proof}
  if LOCK.exists():need(read(LOCK)['manifest']==locked['manifest'],'Existing lock differs; explicit new lock path required')
  else:write(LOCK,locked)
 return report
if __name__=='__main__':print(json.dumps(check(pin='--pin' in sys.argv),ensure_ascii=False,indent=2))
