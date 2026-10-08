from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,datetime
R=Path(__file__).resolve().parent.parent;D=R/'repairs';Q=D/'qa-v1';F=D/'fields-v1'
Q.mkdir(exist_ok=True);F.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
names=[f'p{r}{c}' for r in range(1,5) for c in range(1,5)]
paths={n:R/'native'/(n+'.png') for n in names};paths['p32']=D/'p32-cloth-corrected-native.png'
A={n:np.array(Image.open(p).convert('RGB'),dtype=np.float32) for n,p in paths.items()}
G={}
for n,a in A.items():gy,gx=np.gradient(a.mean(axis=2));G[n]=np.hypot(gx,gy)
field={n:np.zeros_like(a)for n,a in A.items()};den={n:np.zeros((1254,1254),np.float32)for n in names};yy,xx=np.mgrid[:1254,:1254];profiles=[]
for r in range(1,5):
 for c in range(1,5):
  a=f'p{r}{c}'
  for axis,rr,cc in [('x',r,c+1),('y',r+1,c)]:
   if rr>4 or cc>4:continue
   b=f'p{rr}{cc}'
   if axis=='x':aa=A[a][:,1024:];bb=A[b][:,:230];ga=G[a][:,1024:];gb=G[b][:,:230]
   else:aa=A[a][1024:];bb=A[b][:230];ga=G[a][1024:];gb=G[b][:230]
   points=np.arange(0,1254,32);vals=[];counts=[]
   for v in points:
    lo=max(0,v-48);hi=min(1254,v+49)
    if axis=='x':da=aa[lo:hi,91:139];db=bb[lo:hi,91:139];gga=ga[lo:hi,91:139];ggb=gb[lo:hi,91:139]
    else:da=aa[91:139,lo:hi];db=bb[91:139,lo:hi];gga=ga[91:139,lo:hi];ggb=gb[91:139,lo:hi]
    diff=da-db;good=(gga<4)&(ggb<4)&(np.max(abs(diff),axis=2)<64)
    counts.append(int(good.sum()));vals.append(np.median(diff[good],axis=0)if good.sum()>40 else np.zeros(3))
   vals=np.array(vals);pf=np.stack([np.interp(np.arange(1254),points,vals[:,k])for k in range(3)],axis=1)
   for n,center,fac in [(a,1139,-.5),(b,115,.5)]:
    w=np.maximum(0,1-abs((xx if axis=='x' else yy)-center)/224)**2
    field[n]+=fac*(pf[:,None,:]if axis=='x'else pf[None,:,:])*w[:,:,None];den[n]+=w
   profiles.append({'a':a,'b':b,'axis':axis,'points':points.tolist(),'medianAminusB':vals.tolist(),'eligibleCounts':counts})
northPath=R.parent/'repairs/left-edge/both-side/c12-right-revised-candidate-v3.png';north=np.array(Image.open(northPath).convert('RGB'),dtype=np.float32)
for c in range(1,5):
 n=f'p1{c}';origin=(c-1)*1024-115;points=np.arange(0,1254,32);vals=[]
 for v in points:
  lo=max(0,v-48,-origin);hi=min(1254,v+49,4096-origin)
  if hi<=lo:vals.append(np.zeros(3));continue
  a=north[4001:4096,origin+lo:origin+hi];b=A[n][20:115,lo:hi];diff=a-b
  good=(G[n][20:115,lo:hi]<4)&(np.max(abs(diff),axis=2)<48)
  vals.append(np.median(diff[good],axis=0)if good.sum()>40 else np.zeros(3))
 vals=np.array(vals);pf=np.stack([np.interp(np.arange(1254),points,vals[:,k])for k in range(3)],axis=1);w=np.maximum(0,1-abs(yy-115)/224)**2
 field[n]+=pf[None,:,:]*w[:,:,None];den[n]+=w
 profiles.append({'a':'north c12','b':n,'axis':'y','points':points.tolist(),'medianAminusB':vals.tolist(),'northFixed':True})
C={};fieldRecords=[]
for n in names:
 field[n]/=np.maximum(1,den[n])[:,:,None];np.clip(field[n],-18,18,out=field[n]);C[n]=np.clip(np.rint(A[n]+field[n]),0,255).astype(np.uint8)
 p=F/(n+'-rgb-field.npz');np.savez_compressed(p,rgbAdditiveCorrection=field[n]);fieldRecords.append({'name':n,'file':str(p),'sha256':sha(p),'actualMaxAbs':float(abs(field[n]).max())})
def cut(a,b,axis,forced=None):
 # Work on long-dimension rows and the230-pixel overlap columns.
 if axis=='y':a=a.transpose(1,0,2);b=b.transpose(1,0,2)
 diff=np.mean(np.minimum(abs(a.astype(float)-b.astype(float)),64)**2,axis=2)**.5
 ga=np.gradient(a.astype(float).mean(axis=2),axis=1);gb=np.gradient(b.astype(float).mean(axis=2),axis=1)
 cost=diff+np.minimum(abs(ga-gb),25)*.2+abs(np.arange(230)-115)[None,:]*.025
 h=cost.shape[0];lo,hi=65,166;cost=cost[:,lo:hi];back=np.zeros((h,hi-lo),np.int8);dp=cost[0].copy()
 for y in range(1,h):
  opts=np.stack([np.r_[np.inf,dp[:-1]]+.5,dp,np.r_[dp[1:],np.inf]+.5]);which=opts.argmin(axis=0);dp=cost[y]+opts[which,np.arange(hi-lo)];back[y]=which-1
 path=np.empty(h,int);path[-1]=int(dp.argmin())
 for y in range(h-1,0,-1):path[y-1]=path[y]+int(back[y,path[y]])
 path+=lo
 if forced:
  for start,end,value in forced:path[start:end]=value
 return path
quiltRecords=[];rows=[];owners=[]
for r in range(1,5):
 arr=np.zeros((1254,4326,3),np.uint8);own=np.zeros((1254,4326),np.uint8);arr[:,:1254]=C[f'p{r}1'];own[:,:1254]=4*(r-1)+1
 for c in range(2,5):
  n=f'p{r}{c}';ox=(c-1)*1024;a=arr[:,ox:ox+230];b=C[n][:,:230]
  forced=[(470,860,115)] if (r,c)==(3,3)else None
  path=cut(a,b,'x',forced);take=np.arange(230)[None,:]>=path[:,None];arr[:,ox:ox+230]=np.where(take[:,:,None],b,a);own[:,ox:ox+230]=np.where(take,4*(r-1)+c,own[:,ox:ox+230]);arr[:,ox+230:ox+1254]=C[n][:,230:];own[:,ox+230:ox+1254]=4*(r-1)+c
  p=F/f'row{r}-col{c}-cut.npz';np.savez_compressed(p,path=path);quiltRecords.append({'axis':'x','pair':[f'p{r}{c-1}',n],'path':str(p),'sha256':sha(p),'nativeRange':[int(path.min()),int(path.max())],'forcedPotOwnership':forced})
 rows.append(arr[:,115:4211]);owners.append(own[:,115:4211])
out=np.zeros((4326,4096,3),np.uint8);owner=np.zeros((4326,4096),np.uint8);out[:1254]=rows[0];owner[:1254]=owners[0]
for r in range(1,4):
 oy=r*1024;a=out[oy:oy+230];b=rows[r][:230];path=cut(a,b,'y');take=np.arange(230)[:,None]>=path[None,:];out[oy:oy+230]=np.where(take[:,:,None],b,a);owner[oy:oy+230]=np.where(take,owners[r][:230],owner[oy:oy+230]);out[oy+230:oy+1254]=rows[r][230:];owner[oy+230:oy+1254]=owners[r][230:]
 p=F/f'row{r+1}-cut.npz';np.savez_compressed(p,path=path);quiltRecords.append({'axis':'y','rows':[r,r+1],'path':str(p),'sha256':sha(p),'nativeRange':[int(path.min()),int(path.max())]})
out=out[115:4211];owner=owner[115:4211];dst=D/'r10_c12-candidate-v1.png';im=Image.fromarray(out);im.save(dst);op=F/'native-source-owner.png';Image.fromarray(owner).save(op)
qa=[]
for axis in ['x','y']:
 for v in [1024,2048,3072]:
  crop=im.crop((v-160,0,v+160,4096))if axis=='x'else im.crop((0,v-160,4096,v+160)).transpose(Image.Transpose.ROTATE_90)
  s=Image.new('RGB',(1280,1048),'#303030');draw=ImageDraw.Draw(s)
  for i in range(4):s.paste(crop.crop((0,i*1024,320,(i+1)*1024)),(i*320,24));draw.text((i*320+2,3),f'{axis}{v} part{i+1} native',fill='white')
  p=Q/f'{axis}{v}-full-native.png';s.save(p);qa.append({'file':str(p),'sha256':sha(p),'scale':'1:1','scope':f'full4096 {axis}{v} +/-160','actuallyViewed':False})
s=Image.new('RGB',(1152,1224),'#303030');draw=ImageDraw.Draw(s)
for ri,y in enumerate([1024,2048,3072]):
 for ci,x in enumerate([1024,2048,3072]):s.paste(im.crop((x-192,y-192,x+192,y+192)),(ci*384,ri*408+24));draw.text((ci*384+3,ri*408+3),f'junction{x},{y} native',fill='white')
p=Q/'nine-junctions-native.png';s.save(p);qa.append({'file':str(p),'sha256':sha(p),'scale':'1:1','scope':'nine junctions','actuallyViewed':False})
for i in range(4):
 s=Image.new('RGB',(1024,280),'#303030');s.paste(Image.fromarray(north.astype(np.uint8)).crop((i*1024,3968,(i+1)*1024,4096)),(0,24));s.paste(im.crop((i*1024,0,(i+1)*1024,128)),(0,152));ImageDraw.Draw(s).text((0,3),f'north shared segment{i+1} native',fill='white');p=Q/f'north-shared-s{i+1}-native.png';s.save(p);qa.append({'file':str(p),'sha256':sha(p),'scale':'1:1','scope':f'north segment{i+1}','actuallyViewed':False})
im.resize((1254,1254),Image.Resampling.LANCZOS).save(D/'preview-v1.png')
write(D/'candidate-record-v1.json',{'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file':str(dst),'sha256':sha(dst),'pixels':[4096,4096],'sources':[{'id':n,'file':str(p),'sha256':sha(p),'record':str(p)+'.generation.json'}for n,p in paths.items()],'operation':'native hard pixel ownership paths after bounded local additive RGB fields; no source resize, displacement or image blur. p32 priorAI repair has independent precise derivation.','colorCapPerChannel':18,'colorSupport':224,'colorProfiles':profiles,'fields':fieldRecords,'quilt':quiltRecords,'ownerMask':{'file':str(op),'sha256':sha(op)},'northSource':{'file':str(northPath),'sha256':sha(northPath),'unchanged':True},'registrationApplied':False,'diagnosticOnly':str(D/'overlap-diagnostics.json'),'qa':qa,'formalAccepted':False,'clientAccepted':False})
print(json.dumps({'file':str(dst),'sha256':sha(dst),'qaBoards':len(qa)}))
