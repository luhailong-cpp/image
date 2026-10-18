from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil,sys
from datetime import datetime,timezone
R=Path(__file__).parent;B=R.parent.parent;Q=B/'qa/r12c07-resume2-north-ai-v1';Q.mkdir(parents=True,exist_ok=True)
H=B/'qa/r12c07-resume2-north-hard-v1';HT=json.loads((H/'assembly.json').read_text(encoding='utf-8'));N=Path(HT['northAnchor']['path'])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,j):Path(p).write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def dp(cost):
 h,w=cost.shape;prev=np.zeros((h,w),dtype=np.int8);v=cost[:,0].copy()
 for x in range(1,w):
  opts=np.stack([np.r_[np.inf,v[:-1]]+.25,v,np.r_[v[1:],np.inf]+.25]);choice=opts.argmin(axis=0);prev[:,x]=choice-1;v=cost[:,x]+opts[choice,np.arange(h)]
 out=np.empty(w,dtype=np.int32);y=int(v.argmin())
 for x in range(w-1,-1,-1):
  out[x]=y
  if x:y+=int(prev[y,x])
 return out
mode=sys.argv[1];name=sys.argv[2]
if mode=='prepare':
 x=int(sys.argv[3]);bp=Path(sys.argv[4]);a=np.asarray(Image.open(bp).convert('RGB'));n=np.asarray(Image.open(N).convert('RGB'));assert sha(N)==HT['northAnchor']['sha256'];img=np.concatenate([n[3840:4211,x:x+1254],a[115:998,x:x+1254]])
 assert img.shape==(1254,1254,3);p=R/f'{name}.input-native.png';assert not p.exists();Image.fromarray(img).save(p)
 j={'name':name,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'base':rec(bp),'northAnchor':rec(N),'input':rec(p),'size':[1254,1254],'patchContextBox':[x,-256,x+1254,998],'globalBox':[24461+x,44685,24461+x+1254,45939],'actualCoreJoinLocalY':371,'northInputPart':{'source':rec(N),'crop':[x,3840,x+1254,4211],'destination':[0,0,1254,371]},'southInputPart':{'source':rec(bp),'crop':[x,115,x+1254,998],'destination':[0,371,1254,1254]},'route':'built-in image_gen','actualModel':'not returned','prompt':Path(sys.argv[5]).read_text(encoding='utf-8')}
 save(R/f'{name}.request.json',j);print(json.dumps(j,ensure_ascii=False))
elif mode=='archive':
 src=Path(sys.argv[3]);dest=R/f'{name}.native.png';assert not dest.exists();shutil.copyfile(src,dest);im=Image.open(dest);assert im.size==(1254,1254),im.size
 j={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'request':rec(R/f'{name}.request.json'),'toolOriginal':rec(src),'archivedOriginal':rec(dest),'nativeSize':list(im.size),'route':'built-in image_gen','actualModel':'not returned','noResize':True};save(R/f'{name}.generation.json',j);print(json.dumps(j,ensure_ascii=False))
elif mode=='compose':
 req=load(R/f'{name}.request.json');bp=Path(sys.argv[3]);x0,y0,x1,y1=map(int,sys.argv[4:8]);band=int(sys.argv[8]);version=sys.argv[9] if len(sys.argv)>9 else 'v1';o=Q/f'{name}-{version}';assert not o.exists();o.mkdir()
 base=np.asarray(Image.open(bp).convert('RGB'));native=np.asarray(Image.open(R/f'{name}.native.png').convert('RGB'));px=req['patchContextBox'][0];patchbase=np.asarray(Image.open(req['input']['path']).convert('RGB'))
 assert 2163<=x0<x1<=4326 and 115<=y0<y1<=900
 rx0,rx1=x0-px,x1-px;ry0,ry1=y0+256,y1+256;cost=np.mean(np.abs(native[ry0:ry1,rx0:rx1].astype(float)-base[y0:y1,x0:x1].astype(float)),axis=2);h,w=cost.shape
 by=min(band,h//3);bx=min(band,w//3);top=dp(cost[:by]);bottom=dp(cost[-by:])+h-by;left=dp(cost[:,:bx].T);right=dp(cost[:,-bx:].T)+w-bx;yy,xx=np.indices((h,w));m=(yy>=top[None,:])&(yy<=bottom[None,:])&(xx>=left[:,None])&(xx<=right[:,None]);mask=np.zeros((4326,4326),dtype=np.uint8);
 lockedObjects=[[2188,145,2230,185],[2525,465,2570,505]] if name.startswith('N03') else []
 for ax,ay,bx0,by0 in lockedObjects:
  ix0,iy0,ix1,iy1=max(ax,x0),max(ay,y0),min(bx0,x1),min(by0,y1)
  if ix1>ix0 and iy1>iy0:m[iy0-y0:iy1-y0,ix0-x0:ix1-x0]=False
 mask[y0:y1,x0:x1]=m;out=base.copy();out[y0:y1,x0:x1][m]=native[ry0:ry1,rx0:rx1][m];np.save(o/'mask-uint8.npy',mask);Image.fromarray(mask[y0:y1,x0:x1]*255).save(o/'mask-local.png');Image.fromarray(out).save(o/'context-native.png');Image.fromarray(out[115:4211,115:4211]).save(o/'candidate-native-4096.png')
 replay=base.copy();mm=np.load(o/'mask-uint8.npy').astype(bool);replay[y0:y1,x0:x1][mm[y0:y1,x0:x1]]=native[ry0:ry1,rx0:rx1][mm[y0:y1,x0:x1]];saved=np.asarray(Image.open(o/'context-native.png').convert('RGB'))
 crops=[]
 boxes={'center':[max(0,x0-60),max(0,y0-60),min(4326,x1+60),min(4326,y1+60)],'top':[max(0,x0-60),max(0,y0-90),min(4326,x1+60),min(4326,y0+by+90)],'bottom':[max(0,x0-60),max(0,y1-by-90),min(4326,x1+60),min(4326,y1+90)],'left':[max(0,x0-90),max(0,y0-60),min(4326,x0+bx+90),min(4326,y1+60)],'right':[max(0,x1-bx-90),max(0,y0-60),min(4326,x1+90),min(4326,y1+60)]}
 for label,box in boxes.items():
  aa,bb,cc,dd=box;p=o/f'{label}-native.png';Image.fromarray(out[bb:dd,aa:cc]).save(p);crops.append({'label':label,**rec(p),'contextBox':box,'cropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(p))!=out[bb:dd,aa:cc],axis=2).sum())})
 n=np.asarray(Image.open(N).convert('RGB'));joins=[]
 for i in [2,3]:
  xx0=115+i*1024;p=o/f'N{i+1:02d}-actual-core-native.png';c=np.concatenate([n[3866:4211,xx0:xx0+1024],out[115:1015,xx0:xx0+1024]]);Image.fromarray(c).save(p);joins.append({'id':f'N{i+1:02d}',**rec(p),'size':[1024,1245],'southContextBox':[xx0,115,xx0+1024,1015],'cropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(p))!=c,axis=2).sum())})
 trace={'name':name,'version':version,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'candidate_pending_visual_QA','formalAccepted':False,'base':rec(bp),'baseAssembly':rec(bp.parent/'assembly.json'),'request':rec(R/f'{name}.request.json'),'generation':rec(R/f'{name}.generation.json'),'native':rec(R/f'{name}.native.png'),'northAnchor':rec(N),'patchContextBox':req['patchContextBox'],'selectedAllowedContextBox':[x0,y0,x1,y1],'lockedObjectContextBoxes':lockedObjects,'nativeSourceCropBox':[rx0,ry0,rx1,ry1],'method':'Only integer source pixels under a binary four-sided DP mask; source offset from request; keep upstream and N01/N02 unchanged.','mask':rec(o/'mask-uint8.npy'),'hardPaths':{'topRelativeToAllowedBox':top.tolist(),'bottomRelativeToAllowedBox':bottom.tolist(),'leftRelativeToAllowedBox':left.tolist(),'rightRelativeToAllowedBox':right.tolist()},'context':rec(o/'context-native.png'),'candidate':rec(o/'candidate-native-4096.png'),'nativeQACrops':crops,'actualCoreJoins':joins,'proof':{'fullContextReplayDifferentPixels':int(np.any(replay!=saved,axis=2).sum()),'changesOutsideAllowedTop900':int(np.any(out[900:]!=base[900:],axis=2).sum()),'changesInN01N02CoreColumns':int(np.any(out[:,115:2163]!=base[:,115:2163],axis=2).sum()),'northAnchorUnchanged':sha(N)==HT['northAnchor']['sha256'],'changedPixels':int(np.any(out!=base,axis=2).sum()),'noResize':True,'noBlend':True,'noBlur':True,'nativeSize':[1254,1254]},'script':rec(Path(__file__))};save(o/'assembly.json',trace);print(json.dumps({'context':trace['context'],'candidate':trace['candidate'],'proof':trace['proof'],'output':o.as_posix()},ensure_ascii=False))
