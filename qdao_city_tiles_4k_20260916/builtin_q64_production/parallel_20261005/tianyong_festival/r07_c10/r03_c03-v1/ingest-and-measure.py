from pathlib import Path
import json,hashlib,shutil,datetime,sys
import numpy as np
from PIL import Image
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
D=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def save(p,o):Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
src=Path(r'C:/Users/luyua/.codex/generated_images/01a11b05-7488-7d11-bfe3-c3b64c8f7651/exec-9989cba8-a829-4f24-92d7-26a3b88c339a.png')
shutil.copy2(src,D/'native.png')
req=json.loads((D/'request.json').read_text(encoding='utf-8-sig'))
save(D/'native.png.generation.json',{'operation':'builtin AI outpaint','observedCompletionAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'generatedAt':None,'configTarget':req['configSnapshot'],'actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'actualReturnedPixels':list(Image.open(src).size),'source':ref(src),'output':ref(D/'native.png'),'references':json.loads((D/'preparation.json').read_text(encoding='utf-8-sig'))['references'],'nativeScale':1,'noUpscale':True,'formalAccepted':False})
C=np.array(Image.open(D/'context.png').convert('RGBA'))
N=np.array(Image.open(D/'native.png').convert('RGB'))
assert N.shape[:2]==(1254,1254)
c=cv2.cvtColor(C[:,:,:3],cv2.COLOR_RGB2GRAY).astype(float)
n=cv2.cvtColor(N,cv2.COLOR_RGB2GRAY).astype(float)
gxC=np.gradient(c,axis=1);gxN=np.gradient(n,axis=1)
measures=[]
for y in [1040,1070,1100,1130,1160,1190,1220,1240]:
 for lo,hi in [(0,200),(250,500),(550,900),(900,1139)]:
  start=lo+10;end=hi-10
  cg=gxC[y-4:y+5,start:end]
  if np.max(abs(cg))<1.5:continue
  scores=[np.mean(abs(cg-gxN[y-4:y+5,start+s:end+s])) for s in range(-10,11)]
  sh=int(np.argmin(scores))-10
  measures.append({'y':y,'xRange':[start,end],'inverseDx':sh,'score':min(scores),'scoreAtZero':scores[10]})
q=D/'qa';q.mkdir(exist_ok=True)
Image.fromarray(N[920:,:,:]).save(q/'native-bottom.png')
Image.fromarray(C[1024:,:1139,:3]).save(q/'source-bottom.png')
save(D/'measurements.json',{'controls':measures})
print(json.dumps({'native':ref(D/'native.png'),'measurements':measures},indent=2))




