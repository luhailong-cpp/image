from pathlib import Path
from PIL import Image
import numpy as np,sys,json,hashlib
O=Path(__file__).resolve().parent;P=O.parent;T=P.parent.parent
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
base=np.array(Image.open(P/'upper-repair-v4/joined.png').convert('RGB'))
a=np.array(Image.open(P/'registration-v3/aligned-native.png').convert('RGB'))
tone0=np.load(P/'registration-v3/tone.npy')
cp=json.loads((T/'source-checkpoint.json').read_text(encoding='utf-8'));src=cp['fragment'];ctx=np.array(Image.open(src['file']).convert('RGBA').crop((1933,1933,3187,3187)))
assert np.array_equal(ctx[ctx[:,:,3]==255,:3],base[ctx[:,:,3]==255])
y,x=np.mgrid[:1254,:1254].astype(np.float32)
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
# Local residual correspondence below existing major landmark alignment.
tgray=cv2.cvtColor(ctx[:,:,0:3],cv2.COLOR_RGB2GRAY);ngray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
f=cv2.calcOpticalFlowFarneback(tgray[1024:1226],ngray[1024:1226],None,.5,4,31,5,7,1.5,0)
# Robust median over comparisonrows; only horizontal shift has geometric
# justification. Extend slowly through the new area; clip residual to6px.
dx=np.median(f[:,:,0],axis=0);dx=cv2.GaussianBlur(dx[None,:],(0,0),4)[0];dx=np.clip(dx,-6,6)
flow=np.zeros((1254,1254,2),np.float32);flow[:,:,0]=dx[None,:]*smooth((y-820)/204)*(smooth((x-230)/80))*(1-smooth((x-930)/94))
align=cv2.remap(a,x+flow[:,:,0],y,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
# Color correction from flat matchedfaces in overlap, <=12channel.
target=ctx[:,:,:3]
flat=(np.hypot(*np.gradient(target.astype(float).mean(2)))<4)&(np.hypot(*np.gradient(align.astype(float).mean(2)))<4)&(ctx[:,:,3]==255)
valid=flat[1024:1136]
delta=np.clip(target[1024:1136].astype(float)-align[1024:1136].astype(float),-12,12)
num=(delta*valid[:,:,None]).sum(0);den=valid.sum(0).astype(float)
num=cv2.GaussianBlur(num[None,:,:],(0,0),10)[0];den=cv2.GaussianBlur(den[None,:],(0,0),10)[0]
profile=np.clip(num/np.maximum(den[:,None],1e-5),-12,12)
# Blend tonalprofile fromexistingtone smoothly tokeepupperpaint.
wt=smooth((y-880)/144)[:,:,None];tone=np.clip(tone0*(1-wt)+profile[None,:,:]*wt,-12,12)
paint=np.clip(np.rint(align.astype(float)+tone),0,255)
w=smooth((y-880)/112)*(1-smooth((y-1080)/146))*smooth((x-180)/50)*(1-smooth((x-930)/94))
j=np.rint(base*(1-w[:,:,None])+paint*w[:,:,None]).astype(np.uint8)
# Right cloud relief corresponds, but old hard ownership had a tone rectangle.
# Add an explicitly coupled texture return after bounded residual registration.
rf=cv2.calcOpticalFlowFarneback(tgray[:,1024:1226],ngray[:,1024:1226],None,.5,4,31,5,7,1.5,0)
rprof=np.median(rf,axis=1);rprof=cv2.GaussianBlur(rprof[:,None,:],(0,0),sigmaX=1,sigmaY=5)[:,0];rprof=np.clip(rprof,-2,2)
rflow=np.zeros((1254,1254,2),np.float32)
rflow[:]=rprof[:,None,:]*smooth((x-900)/124)[:,:,None]
ra=cv2.remap(a,x+rflow[:,:,0],y+rflow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
rflat=(np.hypot(*np.gradient(target.astype(float).mean(2)))<4)&(np.hypot(*np.gradient(ra.astype(float).mean(2)))<4)&(ctx[:,:,3]==255)
rv=rflat[:,1024:1136];rd=np.clip(target[:,1024:1136].astype(float)-ra[:,1024:1136].astype(float),-12,12)
rnum=(rd*rv[:,:,None]).sum(1);rden=rv.sum(1).astype(float)
rnum=cv2.GaussianBlur(rnum[:,None,:],(0,0),sigmaX=1,sigmaY=10)[:,0];rden=cv2.GaussianBlur(rden[:,None],(0,0),sigmaX=1,sigmaY=10)[:,0]
rprofile=np.clip(rnum/np.maximum(rden[:,None],1e-5),-12,12)
rwt=smooth((x-900)/124)[:,:,None];rtone=np.clip(tone0*(1-rwt)+rprofile[:,None,:]*rwt,-12,12)
rpaint=np.clip(np.rint(ra.astype(float)+rtone),0,255)
rw=smooth((x-900)/124)*(1-smooth((x-1100)/126))*(1-smooth((y-1160)/66))
j=np.rint(j*(1-rw[:,:,None])+rpaint*rw[:,:,None]).astype(np.uint8)
np.save(O/'right-flow.npy',rflow);np.save(O/'right-tone.npy',rtone);Image.fromarray((rw*255).astype(np.uint8)).save(O/'right-mask.png')
# Outside explicit local return/new field no changes.
Image.fromarray(j).save(O/'joined.png');Image.fromarray(ctx).save(O/'context.png')
np.save(O/'flow.npy',flow);np.save(O/'tone.npy',tone);Image.fromarray((w*255).astype(np.uint8)).save(O/'mask.png')
qa=O/'qa';qa.mkdir(exist_ok=True)
rs={'whole':(0,0,1254,1254),'upper-left':(130,0,570,360),'left':(130,0,370,1254),'crossband':(0,540,700,930),'bottom':(0,850,1254,1254),'right':(900,0,1254,1254),'lower-gray':(230,870,560,1254),'lower-channel':(590,870,960,1254),'bottom-left-corner':(130,930,430,1254),'bottom-right-corner':(910,900,1254,1254)}
for n,b in rs.items():Image.fromarray(j).crop(b).save(qa/(n+'.png'))
(O/'qa/regions.json').write_text(json.dumps(rs,indent=2),encoding='utf-8')
(O/'assembly-draft.json').write_text(json.dumps({'checkpoint':info(T/'source-checkpoint.json'),'priorSource':src,'flowMax':float(abs(flow).max()),'dxProfile':[float(dx[i]) for i in [265,285,485,506,620,634,700,719,735,900,935]],'toneMax':float(abs(tone).max()),'output':info(O/'joined.png'),'localAccepted':False},indent=2),encoding='utf-8')
print(json.dumps({'flowMax':float(abs(flow).max()),'checkpointVersion':cp['version']}))



