from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys,datetime
R=Path(__file__).resolve().parent
S=R.parents[2]
sys.path.insert(0,str(S/'continuation_20261004/c07-recovery/vendor'))
sys.path.insert(0,str(S.parent/'tools'))
from mechanical_join import registered_join
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stamp=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
bind=json.loads((R/'tone-v2-bindings.json').read_text())['sources']
a={k:np.array(Image.open(v['file']).convert('RGB')) for k,v in bind.items()}
O=R/'coupled-v2';O.mkdir(exist_ok=True)
boxes={'gold-top':[7565,0,8819,1254],'corner-left':[3469,3469,4723,4723],'corner-right':[7565,3469,8819,4723]}
def crop(box):
 x0,y0,x1,y1=box;out=np.zeros((y1-y0,x1-x0,3),np.uint8);parts=[]
 for k,im in a.items():
  ox=(int(k[5:])-7)*4096;oy=(int(k[1:3])-8)*4096
  ix0=max(x0,ox);iy0=max(y0,oy);ix1=min(x1,ox+4096);iy1=min(y1,oy+4096)
  if ix0<ix1 and iy0<iy1:
   out[iy0-y0:iy1-y0,ix0-x0:ix1-x0]=im[iy0-oy:iy1-oy,ix0-ox:ix1-ox]
   parts.append({'tile':k,'tileCropLTRB':[ix0-ox,iy0-oy,ix1-ox,iy1-oy],'destinationLTRB':[ix0-x0,iy0-y0,ix1-x0,iy1-y0]})
 return out,parts
repairs=[]
for name,box in boxes.items():
 P=R/name;Q=O/name;Q.mkdir(exist_ok=True)
 native=np.array(Image.open(P/'native.png').convert('RGB'));assert native.shape==(1254,1254,3)
 ctx,parts=crop(box);yy,xx=np.mgrid[:1254,:1254]
 edges=('left','right','bottom') if box[1]==0 else ('left','right','top','bottom')
 dist=np.minimum.reduce([xx,1253-xx,1253-yy]) if box[1]==0 else np.minimum.reduce([xx,1253-xx,yy,1253-yy])
 t=np.clip((dist-16)/112,0,1);mask=np.rint(t*t*(3-2*t)*255).astype(np.uint8)
 joined,flow,tone,report=registered_join(ctx,native,mask,edges=edges,max_shift=4,flow_inner=180,flow_full=70,tone_inner=180,tone_full=70)
 Image.fromarray(mask).save(Q/'mask.png');np.save(Q/'flow.npy',flow.astype(np.float16));np.save(Q/'tone.npy',tone.astype(np.float16))
 Image.fromarray(joined).save(Q/'composite.png')
 for part in parts:
  tx0,ty0,tx1,ty1=part['tileCropLTRB'];dx0,dy0,dx1,dy1=part['destinationLTRB']
  a[part['tile']][ty0:ty1,tx0:tx1]=joined[dy0:dy1,dx0:dx1]
 perimeter=[max(0,box[0]-160),max(0,box[1]-160),min(12288,box[2]+160),min(8192,box[3]+160)]
 view,_=crop(perimeter);Image.fromarray(view).save(Q/'perimeter.png')
 old=json.loads((P/'native.png.generation.json').read_text());rec=json.loads((P/'tool-response.json').read_text())
 old['hostObservedStartedAtUtc']=rec.get('hostObservedStartedAtUtc');old['hostObservedFinishedAtUtc']=rec.get('hostObservedFinishedAtUtc')
 old['generatedAt']=None;old['generatedAtEvidence']='Actual generation timestamp not disclosed; observed tool-call interval recorded when available.'
 (P/'native.png.generation.json').write_text(json.dumps(old,indent=2),encoding='utf-8')
 repairs.append({'name':name,'globalWindowLTRB':box,'native':{'file':str(P/'native.png'),'sha256':sha(P/'native.png'),'generationRecord':str(P/'native.png.generation.json')},'parts':parts,'registration':report,'mask':str(Q/'mask.png'),'flow':str(Q/'flow.npy'),'tone':str(Q/'tone.npy'),'qaPerimeter':str(Q/'perimeter.png')})
outputs={}
for k,im in a.items():
 p=O/(k+'.png');Image.fromarray(im).save(p)
 outputs[k]={'file':str(p),'sha256':sha(p),'pixels':[4096,4096],'generationRecord':str(p)+'.generation.json'}
 rec={'file':str(p),'sha256':sha(p),'exportPixels':[4096,4096],'recordedAtUtc':stamp(),'derivedFrom':[bind[k]]+[r['native'] for r in repairs if any(v['tile']==k for v in r['parts'])],'operation':'Native-size AI seam redraws, bounded <=4px perimeter registration, local colour <=18/255, no upscale, alpha16..128px. See assembly manifest.','assemblyManifest':str(R/'coupled-v2-bindings.json'),'actualModel':None,'actualQuality':None,'unverifiedReason':'Derived from multiple builtin generations; actual models/quality undisclosed, see source records.'}
 (Path(str(p)+'.generation.json')).write_text(json.dumps(rec,indent=2),encoding='utf-8')
rec={'sources':outputs,'derivedFrom':bind,'repairs':repairs,'operation':'Three native1254 structural repairs with bounded perimeter registration. Source inner pixels unchanged. No upscale.','script':{'file':str(Path(__file__).resolve()),'sha256':sha(__file__)},'createdAtUtc':stamp(),'formalAccepted':False}
(R/'coupled-v2-bindings.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
Q=O/'qa';Q.mkdir(exist_ok=True)
for c in [7,8,9]:
 strip=np.concatenate([a[f'r08_c{c:02d}'][-192:],a[f'r09_c{c:02d}'][:192]],axis=0)
 board=np.concatenate([strip[:,i*1024:(i+1)*1024] for i in range(4)],axis=0)
 Image.fromarray(board).save(Q/f'horizontal-c{c:02d}-full.png')
print(json.dumps(outputs,indent=2))
