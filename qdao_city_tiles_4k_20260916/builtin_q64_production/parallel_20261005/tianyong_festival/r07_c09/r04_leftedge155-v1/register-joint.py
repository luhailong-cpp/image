from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
D=Path(__file__).parent;F=D/'final-v4';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,indent=2),encoding='utf-8')
B=np.array(Image.open(D/'final-v2/joined.png').convert('RGB'));A=np.array(Image.open(D/'bottom-joint-repair/native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
Y,X=np.indices((1254,1254),dtype=float);smooth=lambda v:(lambda t:t*t*(3-2*t))(np.clip(v,0,1))
controls={1145:[(0,0),(55,55),(80,77),(98,101),(106,110),(132,122),(142,137),(170,170),(1253,1253)],1165:[(0,0),(55,55),(79,76),(98,100),(106,110),(131,122),(141,138),(170,170),(1253,1253)],1190:[(0,0),(55,55),(79,76),(97,100),(106,109),(131,123),(140,139),(170,170),(1253,1253)]}
rows=[]
for yy,pairs in controls.items():
 a=np.array(pairs);rows.append(np.interp(np.arange(1254),a[:,0],a[:,1]-a[:,0]))
rows=np.array(rows);dx=np.stack([np.interp(np.arange(1254),list(controls),rows[:,xx]) for xx in range(1254)],axis=1)*smooth((Y-1020)/120)
assert abs(dx).max()<=10
R=B.copy();R[627:]=A[:627]
R=cv2.remap(R,(X+dx).astype('float32'),Y.astype('float32'),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
w=smooth((X-25)/30)*(1-smooth((X-165)/30))*smooth((Y-990)/40)*(1-smooth((Y-1145)/55))
J=np.rint(B*(1-w[:,:,None])+R*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'joint-repair-weight.png')
np.savez_compressed(F/'registration-fields.npz',inverseDx=dx.astype('float32'),inverseDy=np.zeros_like(dx,dtype='float32'))
save(F/'registration-controls.json',{'method':'Corresponding signed grayscale derivative peaks at exact native bottom joint; after actual AI redraw, small inverse horizontal correction only','coordinateMeaning':'target context source x -> generated repair source x','bottomDxControls':controls,'fadeY':[1020,1140],'nativeWindowYOffset':627})
for name,box in [('full',[0,0,1254,1254]),('right',[91,0,401,1254]),('bottom',[0,1010,1254,1254]),('joint-detail',[0,980,230,1254])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'assembly.json',{'output':ref(F/'joined.png'),'native':ref(D/'repair-v1/native.png'),'context':ref(D/'context.png'),'priorComposite':ref(D/'final-v2/joined.png'),'priorAssembly':ref(D/'final-v2/assembly.json'),'nativeScale':1,'noUpscale':True,'registrationApplied':True,'maxDx':10,'maxDy':0,'actualMaxAbsDx':float(abs(dx).max()),'actualMaxAbsDy':0,'jointRepairNative':ref(D/'bottom-joint-repair/native.png'),'jointRepairPreparation':ref(D/'bottom-joint-repair/preparation.json'),'repairCropTransform':'originalWindow(x,y) <- repairWindow(x,y-627), native scale','registrationFields':ref(F/'registration-fields.npz'),'registrationControls':ref(F/'registration-controls.json'),'interpolation':'OpenCV INTER_CUBIC, inverse map, BORDER_REPLICATE; only inside explicit repair weight reaches final','repairWeight':ref(F/'joint-repair-weight.png'),'repairMaskX':[25,55,165,195],'repairMaskY':[990,1030,1145,1200],'outsideRepairExact':bool(np.array_equal(J[w==0],B[w==0])),'knownBeyondBlendExact':bool(np.array_equal(J[(C[:,:,3]==255)&((X>=331)|(Y>=1200))],C[:,:,:3][(C[:,:,3]==255)&((X>=331)|(Y>=1200))])),'formalAccepted':False,'visualReviewPending':True})
print(json.dumps({'joined':ref(F/'joined.png'),'maxDx':float(abs(dx).max())}))
