from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
D=Path(__file__).parent;F=D/'final-v3';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
N=np.array(Image.open(D/'repair-v2/native.png').convert('RGB'));C=np.array(Image.open(D/'context.png').convert('RGBA'))
y,x=np.indices((1254,1254),dtype=float);smooth=lambda v:(lambda t:t*t*(3-2*t))(np.clip(v,0,1))
# Each pair is target source coordinate -> already-redrawn native coordinate.
right={
1050:[(0,12),(57,69),(71,82),(101,112),(116,128),(126,139),(262,284),(290,312),(448,468),(516,537),(557,578),(576,595),(975,985),(1003,1013),(1026,1032),(1042,1046),(1160,1162),(1174,1175),(1207,1210),(1253,1256)],
1100:[(0,10),(88,98),(101,112),(131,143),(146,158),(294,317),(324,345),(484,502),(552,572),(593,612),(612,629),(931,943),(959,971),(983,991),(999,1005),(1136,1136),(1188,1187),(1207,1208),(1253,1253)],
1150:[(0,9),(119,128),(131,142),(162,173),(178,189),(189,201),(326,350),(357,379),(520,537),(589,608),(630,648),(649,666),(889,901),(916,928),(939,948),(957,963),(1096,1096),(1146,1145),(1159,1158),(1175,1172),(1253,1253)],
1200:[(0,9),(149,158),(162,172),(194,204),(210,220),(221,232),(359,383),(390,414),(556,572),(625,644),(667,685),(686,703),(846,858),(873,884),(896,905),(913,919),(1057,1056),(1118,1117),(1134,1132),(1253,1253)]}
right_y=[]
for column,pairs in right.items():
 a=np.array(pairs);right_y.append(np.interp(np.arange(1254),a[:,0],a[:,1]-a[:,0]))
right_y=np.array(right_y)
dy=np.stack([np.interp(np.arange(1254),list(right),right_y[:,yy]) for yy in range(1254)])*smooth((x-500)/550)
bottom={1145:[(0,0),(650,650),(766,754),(776,764),(807,794),(837,822),(976,968),(1013,1007),(1093,1090),(1143,1142),(1167,1166),(1253,1253)],1165:[(0,0),(650,650),(792,779),(801,790),(832,820),(863,848),(1000,993),(1037,1033),(1068,1067),(1118,1117),(1143,1142),(1227,1228),(1253,1253)],1190:[(0,0),(650,650),(823,812),(832,822),(865,852),(897,882),(1030,1025),(1041,1036),(1088,1087),(1115,1113),(1228,1226),(1253,1253)],1220:[(0,0),(650,650),(859,850),(869,860),(901,891),(934,921),(1066,1063),(1080,1078),(1118,1116),(1253,1253)]}
bottom_x=[]
for row,pairs in bottom.items():
 a=np.array(pairs);bottom_x.append(np.interp(np.arange(1254),a[:,0],a[:,1]-a[:,0]))
bottom_x=np.array(bottom_x)
dx=np.stack([np.interp(np.arange(1254),list(bottom),bottom_x[:,xx]) for xx in range(1254)],axis=1)*smooth((y-820)/325)
assert abs(dx).max()<=15 and abs(dy).max()<=24
R=cv2.remap(N,(x+dx).astype('float32'),(y+dy).astype('float32'),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
wx=smooth((x-1040)/160);wy=smooth((y-1139)/61);w=np.where(C[:,:,3]==255,np.maximum(wx,wy),0)
J=np.rint(R.astype(float)*(1-w[:,:,None])+C[:,:,:3].astype(float)*w[:,:,None]).astype('uint8')
Image.fromarray(J).save(F/'joined.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(F/'source-weight.png')
np.savez_compressed(F/'registration-fields.npz',inverseDx=dx.astype('float32'),inverseDy=dy.astype('float32'))
for name,box in [('right',[900,0,1254,1254]),('bottom',[0,1000,1254,1254]),('corner',[880,920,1254,1254]),('full',[0,0,1254,1254]),('upper-right',[880,0,1254,750])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
save(F/'registration-controls.json',{'coordinateMeaning':'target source edge coordinate -> redrawn native edge coordinate','rightDyControls':right,'bottomDxControls':bottom,'method':'Signed grayscale gradient peak locations, manually assigned same physical bevel edges from profile-peaks.json. Weak competing peaks excluded. No optical flow.','diagnosticSource':ref(D/'profile-peaks.json')})
save(F/'assembly.json',{'output':ref(F/'joined.png'),'native':ref(D/'repair-v2/native.png'),'context':ref(D/'context.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':True,'registrationReason':'Bounded correction of fully generated and AI-redrawn existing profiles; no structure synthesized by warp.','allowedMaxDx':15,'allowedMaxDy':24,'actualMaxAbsDx':float(abs(dx).max()),'actualMaxAbsDy':float(abs(dy).max()),'interpolation':'OpenCV INTER_CUBIC, inverse map, BORDER_REPLICATE; output is native-scale composite, not untouched single-generation pixels','fields':ref(F/'registration-fields.npz'),'controls':ref(F/'registration-controls.json'),'rightFadeX':[500,1050],'bottomFadeY':[820,1145],'toneCorrectionApplied':False,'blendOnlyKnownPixels':True,'sourceWeight':ref(F/'source-weight.png'),'blendSmoothstepX':[1040,1200],'blendSmoothstepY':[1139,1200],'knownAtX1200OrY1200Exact':bool(np.array_equal(J[(C[:,:,3]==255)&((x>=1200)|(y>=1200))],C[:,:,:3][(C[:,:,3]==255)&((x>=1200)|(y>=1200))])),'formalAccepted':False,'visualReviewPending':True})
print(json.dumps({'joined':ref(F/'joined.png'),'maxDx':float(abs(dx).max()),'maxDy':float(abs(dy).max())}))
