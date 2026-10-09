from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
from datetime import datetime,timezone
D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();ref=lambda p:{'file':str(p),'sha256':sha(p)}
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
host=Path('C:/Users/luyua/.codex/generated_images/01a11b00-53b8-70a3-bc9b-96606ec052ee')
records=[('native-original.png','exec-4515bee7-a068-4b84-8fa2-9dd81de1e793.png','request.json'),('repair-1-native.png','exec-7d263b94-e281-46e3-8ea3-f2985b65b66b.png','repair-request.json'),('repair-2-native.png','exec-50949114-7f6a-4cf3-bccb-b2b238480b4d.png','repair-2-request.json')]
for local,h,request in records:
 if not (D/local).exists():shutil.copy2(host/h,D/local)
 save(D/(local+'.generation.json'),{'file':str(D/local),'sha256':sha(D/local),'tool':'image_gen.imagegen','route':'builtin','generatedAt':None,'observedCompletionAtUtc':datetime.now(timezone.utc).isoformat(),'configSnapshot':read(D/'request.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,'size':None},'actualModel':None,'actualQuality':None,'request':ref(D/request),'hostOutput':ref(host/h),'width':1254,'height':1254,'nativeScale':1,'formalAccepted':False})
a=np.array(Image.open(D/'native-original.png').convert('RGB'));b=np.array(Image.open(D/'repair-2-native.png').convert('RGB'));w=np.zeros((1254,1254),np.float32)
rois=[[850,390,965,670],[415,985,1110,1090]]
for x1,y1,x2,y2 in rois:
 y,x=np.mgrid[y1:y2,x1:x2];d=np.minimum.reduce([(x-x1)/8,(x2-1-x)/8,(y-y1)/(40 if y1==390 else 8),(y2-1-y)/(40 if y1==390 else 8)]);v=np.clip(d,0,1);v=v*v*(3-2*v);w[y1:y2,x1:x2]=v
out=np.rint(a*(1-w[:,:,None])+b*w[:,:,None]).astype('uint8');assert np.array_equal(out[w==0],a[w==0]);Image.fromarray(out).save(D/'native-repaired.png');Image.fromarray(np.rint(w*255).astype('uint8')).save(D/'repair-mask.png')
save(D/'repair-proof.json',{'source':ref(D/'native-original.png'),'repair1':ref(D/'repair-1-native.png'),'repair2':ref(D/'repair-2-native.png'),'output':ref(D/'native-repaired.png'),'mask':ref(D/'repair-mask.png'),'allowedNativeLTRB':rois,'outsideMaskIdentical':True,'operation':'True AI native repair crops with 8pixel edge transition; no blur, resize, geometric warp or tone correction.','closedFindings':['Vertical joint notch removed','Unfinished lower joint redrawn as a continuous rounded L-corner meeting the existing downward joint, with no floating taper'],'repair1Result':'Notch corrected but lower taper persisted, therefore repair2 was required.','repair2Result':'Model closed the lower line as an L-corner rather than requested full T-junction; coherent paving boundary within reference structure.','formalAccepted':False})
save(D/'native-repaired.png.generation.json',{'file':str(D/'native-repaired.png'),'sha256':sha(D/'native-repaired.png'),'derivedFrom':[ref(D/'native-original.png'),ref(D/'repair-2-native.png')],'operation':'Explicit native AI repair ROI composition','repairProof':ref(D/'repair-proof.json'),'newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1,'formalAccepted':False})
print(json.dumps(ref(D/'native-repaired.png')))
