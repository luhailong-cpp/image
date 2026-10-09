from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(__file__).parent;F=D/'final-v3';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
B=np.array(Image.open(D/'final-v2/joined.png').convert('RGB'));A=np.array(Image.open(D/'bottom-joint-repair/native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
Y,X=np.indices((1254,1254));smooth=lambda v:(lambda t:t*t*(3-2*t))(np.clip(v,0,1))
w=smooth((X-25)/30)*(1-smooth((X-165)/30))*smooth((Y-990)/40)*(1-smooth((Y-1145)/55))
R=B.copy();R[627:]=A[:627]
J=np.rint(B*(1-w[:,:,None])+R*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'joint-repair-weight.png')
for name,box in [('full',[0,0,1254,1254]),('right',[91,0,401,1254]),('bottom',[0,1010,1254,1254]),('joint-detail',[0,980,230,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'output':ref(F/'joined.png'),'native':ref(D/'repair-v1/native.png'),'context':ref(D/'context.png'),'priorComposite':ref(D/'final-v2/joined.png'),'priorAssembly':ref(D/'final-v2/assembly.json'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'jointRepairNative':ref(D/'bottom-joint-repair/native.png'),'jointRepairPreparation':ref(D/'bottom-joint-repair/preparation.json'),'repairCropTransform':'originalWindow(x,y) <- repairWindow(x,y-627), no resize or warp','repairWeight':ref(F/'joint-repair-weight.png'),'repairMaskX':[25,55,165,195],'repairMaskY':[990,1030,1145,1200],'outsideRepairExact':bool(np.array_equal(J[w==0],B[w==0])),'knownBeyondBlendExact':bool(np.array_equal(J[(C[:,:,3]==255)&((X>=331)|(Y>=1200))],C[:,:,:3][(C[:,:,3]==255)&((X>=331)|(Y>=1200))])),'formalAccepted':False,'visualReviewPending':True})
for yy in [1145,1165,1190]:
 for name,M in [('context',C),('old',B),('new',J)]:
  v=np.convolve(M[yy-3:yy+4,:,:3].mean(axis=(0,2)),np.ones(7)/7,'same');a=np.gradient(v);peaks=[[i,round(a[i],2)] for i in range(60,160) if abs(a[i])>2 and abs(a[i])==max(abs(a[i-4:i+5]))];print(yy,name,peaks)
