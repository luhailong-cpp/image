from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np,json,hashlib,shutil
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c01-v1");R=D/'coupled-whole-object-v1';F=D/'final-v2';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()}
host=Path(r"C:/Users/luyua/.codex/generated_images/01a11b05-7488-7d11-bfe3-c3b64c8f7651/exec-760071ba-a042-4167-a1e0-1fe6f37f9379.png");shutil.copy2(host,R/'native.png');assert Image.open(host).size==(1254,1254)
p=json.loads((R/'preparation.json').read_text(encoding='utf-8'));(R/'native.png.generation.json').write_text(json.dumps({'operation':'builtin AI whole-object coupled redraw','output':ref(R/'native.png'),'host':ref(host),'preparation':ref(R/'preparation.json'),'configTarget':p['configTarget'],'actualReturnedPixels':[1254,1254],'actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'nativeScale':1,'formalAccepted':False},indent=2),encoding='utf-8')
smooth=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
N=np.array(Image.open(D/'native.png').convert('RGB'));A=np.array(Image.open(D/'alignment-repair-v2/native.png').convert('RGB'));B=np.array(Image.open(R/'native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'));S=np.array(Image.open(R/'source-composite.png').convert('RGBA'));mask=Image.open(R/'mask.png').convert('L')
# A narrow source ownership feather is used outside the AI repaint region; no geometric operations.
m=np.array(mask.filter(ImageFilter.GaussianBlur(5))).astype(float)/255; m=np.maximum(m,np.array(mask).astype(float)/255);m=np.where(S[:,:,3]==255,m,1)
lower=np.rint(S[:,:,:3]*(1-m[:,:,None])+B*m[:,:,None]).astype(np.uint8)
J=np.zeros((2278,1254,3),np.uint8);J[:1254]=N
w=smooth(np.arange(904)/30)[:,None,None];J[350:1254]=np.rint(J[350:1254]*(1-w)+A[:904]*w).astype(np.uint8)
J[1024:]=lower
y,x=np.indices((1139,1254));cw=smooth((x-1040)/160);cw=np.where(C[:1139,:,3]==255,cw,0)
J[:1139]=np.rint(J[:1139]*(1-cw[:,:,None])+C[:1139,:,:3]*cw[:,:,None]).astype(np.uint8)
Image.fromarray(J).save(F/'joined.png');Image.fromarray(J[:1254]).save(F/'main1254.png')
for name,box in [('main1254',[0,0,1254,1254]),('upper-native',[0,0,1254,1254]),('lower-native',[0,1024,1254,2278]),('middle-overlap',[0,700,1254,1500]),('right',[900,0,1254,2278]),('lower-left-perimeter',[105,1139,260,2278]),('return-tail',[0,2050,1254,2278])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
assembly={'output':ref(F/'joined.png'),'sources':[ref(D/'native.png'),ref(D/'alignment-repair-v2/native.png'),ref(R/'native.png'),ref(D/'context.png'),ref(R/'source-composite.png')],'nativeSourcePlacements':[{'source':ref(D/'native.png'),'destOffset':[0,0]},{'source':ref(D/'alignment-repair-v2/native.png'),'destOffset':[0,350]},{'source':ref(R/'native.png'),'destOffset':[0,1024]}],'globalLTRB':[36749,19341,38003,21619],'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'toneCorrectionApplied':False,'wholeObjectCoupledReturnRequired':True,'formalAccepted':False,'actualModel':None,'actualQuality':None,'upperTransition':[350,380],'mainRightSourceSmoothstepX':[1040,1200],'lowerSourceOwnershipMask':ref(R/'mask.png'),'maskOutsideFeatherGaussianRadius':5}
(F/'assembly.json').write_text(json.dumps(assembly,indent=2),encoding='utf-8');print(json.dumps(ref(F/'joined.png')))

