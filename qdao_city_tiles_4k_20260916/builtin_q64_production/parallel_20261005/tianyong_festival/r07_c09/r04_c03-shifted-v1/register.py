from pathlib import Path
import numpy as np,json,hashlib,sys
from PIL import Image
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
D=Path(__file__).parent;F=D/'final-v2';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
N=np.array(Image.open(D/'repair-v2/native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
y,x=np.indices((1254,1254),dtype=float);smooth=lambda v:(lambda t:t*t*(3-2*t))(np.clip(v,0,1))
right={
760:[(0,0),(350,350),(479,496),(504,520),(518,533),(607,622),(662,672),(841,842),(867,870),(976,976),(1033,1034),(1100,1100),(1253,1253)],
800:[(0,0),(350,350),(501,516),(526,540),(540,553),(630,642),(686,693),(799,801),(825,828),(934,934),(991,991),(1100,1100),(1253,1253)],
850:[(0,0),(350,350),(529,541),(554,564),(568,577),(658,667),(715,720),(748,750),(773,776),(881,882),(938,939),(1100,1100),(1253,1253)],
900:[(0,0),(350,350),(557,566),(582,590),(596,602),(687,693),(722,726),(829,830),(886,886),(1100,1100),(1253,1253)],
930:[(0,0),(350,350),(574,581),(599,605),(612,618),(704,709),(733,737),(797,799),(855,855),(1100,1100),(1253,1253)]}
ry=[]
for xx,pairs in right.items():
 a=np.array(pairs);ry.append(np.interp(np.arange(1254),a[:,0],a[:,1]-a[:,0]))
ry=np.array(ry);dy=np.stack([np.interp(np.arange(1254),list(right),ry[:,yy]) for yy in range(1254)])*smooth((x-300)/460)
bottom={
1145:[(0,0),(120,120),(187,185),(214,214),(342,331),(540,525),(558,544),(599,582),(612,604),(635,627),(669,659),(677,667),(740,740),(1253,1253)],
1165:[(0,0),(120,120),(229,225),(257,257),(382,374),(575,563),(591,581),(617,609),(653,642),(661,652),(740,740),(1253,1253)],
1190:[(0,0),(150,150),(280,276),(307,303),(431,421),(620,610),(641,630),(676,666),(688,678),(760,760),(1253,1253)],
1220:[(0,0),(180,180),(338,332),(369,362),(488,478),(670,659),(689,681),(723,715),(735,727),(800,800),(1253,1253)]}
bx=[]
for yy,pairs in bottom.items():
 a=np.array(pairs);bx.append(np.interp(np.arange(1254),a[:,0],a[:,1]-a[:,0]))
bx=np.array(bx);dx=np.stack([np.interp(np.arange(1254),list(bottom),bx[:,xx]) for xx in range(1254)],axis=1)*smooth((y-820)/325)
assert abs(dx).max()<=17 and abs(dy).max()<=17
R=cv2.remap(N,(x+dx).astype('float32'),(y+dy).astype('float32'),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
w=np.where(C[:,:,3]==255,np.maximum(smooth((x-770)/160),smooth((y-1139)/61)),0)
J=np.rint(R*(1-w[:,:,None])+C[:,:,:3]*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'source-weight.png')
np.savez_compressed(F/'registration-fields.npz',inverseDx=dx.astype('float32'),inverseDy=dy.astype('float32'))
for name,box in [('right',[690,0,1000,1254]),('bottom',[0,1010,1254,1254]),('corner',[680,1010,1000,1254]),('full',[0,0,1254,1254]),('relief',[90,470,900,1120])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'registration-controls.json',{'coordinateMeaning':'target source edge coordinate -> redrawn native edge coordinate','rightDyControls':right,'bottomDxControls':bottom,'method':'Manually assigned corresponding signed grayscale bevel derivative peaks from profile-peaks; no optical flow.','diagnosticSource':ref(D/'final-v1/profile-peaks.json')})
save(F/'assembly.json',{'output':ref(F/'joined.png'),'native':ref(D/'repair-v2/native.png'),'context':ref(D/'context.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':True,'registrationReason':'Bounded correction after complete AI redraw, accurate structural layout already present','allowedMaxDx':17,'allowedMaxDy':17,'actualMaxAbsDx':float(abs(dx).max()),'actualMaxAbsDy':float(abs(dy).max()),'interpolation':'OpenCV INTER_CUBIC inverse map; BORDER_REPLICATE','fields':ref(F/'registration-fields.npz'),'controls':ref(F/'registration-controls.json'),'rightFadeX':[300,760],'bottomFadeY':[820,1145],'toneCorrectionApplied':False,'blendOnlyKnownPixels':True,'sourceWeight':ref(F/'source-weight.png'),'blendSmoothstepX':[770,930],'blendSmoothstepY':[1139,1200],'knownAtX930OrY1200Exact':bool(np.array_equal(J[(C[:,:,3]==255)&((x>=930)|(y>=1200))],C[:,:,:3][(C[:,:,3]==255)&((x>=930)|(y>=1200))])),'guidePixelsUsedInFinal':False,'formalAccepted':False,'visualReviewPending':True})
print(json.dumps({'joined':ref(F/'joined.png'),'maxDx':float(abs(dx).max()),'maxDy':float(abs(dy).max())}))
