from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime
D=Path(__file__).parent;F=D/'final-v2';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True);ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
n=np.array(Image.open(D/'native.png').convert('RGB'));r=np.array(Image.open(D/'repair-v3/native.png').convert('RGB'));c=np.array(Image.open(D/'context.png').convert('RGBA'))
y,x=np.indices((1254,1254));sm=lambda v:np.clip(v,0,1)**2*(3-2*np.clip(v,0,1))
rp=n.copy();rp[700:]=r[:554];w=sm((y-740)/40);j=np.rint(n*(1-w[:,:,None])+rp*w[:,:,None]).astype('uint8')
cw=np.where(c[:,:,3]==255,sm((y-1024)/16),0);j=np.rint(j*(1-cw[:,:,None])+c[:,:,:3]*cw[:,:,None]).astype('uint8')
Image.fromarray(j).save(F/'joined.png');Image.fromarray(np.rint(cw*255).astype('uint8')).save(F/'source-weight.png')
for name,box in [('full-native',(0,0,1254,1254)),('body-bridge',(0,680,1139,1139)),('bottom',(0,1000,1254,1254))]:Image.fromarray(j).crop(box).save(Q/(name+'.png'))
record={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':ref(D/'native.png'),'repair':ref(D/'repair-v3/native.png'),'context':ref(D/'context.png'),'output':ref(F/'joined.png'),'nativeScale':1,'noUpscale':True,'registrationApplied':False,'maxDx':0,'maxDy':0,'repairWindowGlobalLTRB':[39821,24137,41075,25391],'repairToMainTranslation':[0,700],'translationIsExactWorldCropMapping':True,'repairBlendMainY':[740,780],'sourceWeightY':[1024,1040],'sourceWeight':ref(F/'source-weight.png'),'sourceExactBelow1040InKnownRegion':bool(np.array_equal(j[1040:,:1139],c[1040:,:1139,:3])),'actualModel':None,'actualQuality':None,'formalAccepted':False,'notes':['Selected native repair upper body only; unselected lower repair geometry not used. Source existing complete rim and pendant lower body retained.','No deformation, resize, tone correction or enlarged guide pixels. Main body bridge may require visual QA.']}
(F/'assembly.json').write_text(json.dumps(record,indent=2),encoding='utf8')
q=json.loads((D/'request.json').read_text(encoding='utf-8-sig'));q['selectedFinalDirectory']='final-v2';(D/'request.json').write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(ref(F/'joined.png')))
