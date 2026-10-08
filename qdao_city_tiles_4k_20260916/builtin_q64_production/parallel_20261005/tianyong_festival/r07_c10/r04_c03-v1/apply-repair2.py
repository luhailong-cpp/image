from pathlib import Path
import numpy as np,json,hashlib,shutil,datetime
from PIL import Image
D=Path(__file__).parent;R=D/'repair-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,o:Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
src=Path(r'C:/Users/luyua/.codex/generated_images/01a11ac1-285e-73e3-8bdd-b1f3337c0543/exec-8ca35613-c2b6-42fa-bf69-14de9761b880.png');shutil.copy2(src,R/'native.png')
req=json.loads((R/'request.json').read_text(encoding='utf8'))
save(R/'native.png.generation.json',{'operation':'builtin AI single band structural repair','observedCompletionAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'generatedAt':None,'configTarget':req['configSnapshot'],'actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'actualReturnedPixels':list(Image.open(src).size),'source':ref(src),'output':ref(R/'native.png'),'references':[ref(p) for p in req['payload']['referenced_image_paths']],'nativeScale':1,'noUpscale':True,'formalAccepted':False})
N=np.array(Image.open(D/'native.png').convert('RGB'));A=np.array(Image.open(R/'native.png').convert('RGB'));assert A.shape==N.shape==(1254,1254,3)
y,x=np.indices((1254,1254));dist=np.minimum.reduce([x-20,700-x,y-715,1215-y]).astype(float);m=np.clip(dist/32,0,1);m=m*m*(3-2*m)
P=np.rint(A*m[:,:,None]+N*(1-m[:,:,None])).astype('uint8')
Image.fromarray(P).save(R/'selected-native.png');Image.fromarray(np.rint(m*255).astype('uint8')).save(R/'repair-weight.png')
save(R/'selection.json',{'native':ref(D/'native.png'),'AIRepair':ref(R/'native.png'),'output':ref(R/'selected-native.png'),'repairMask':ref(R/'repair-weight.png'),'changeSupportLTRB':[20,715,700,1215],'selectionFadePixels':32,'nativeScale':1,'noUpscale':True,'registrationApplied':False,'outsideSupportExactOriginal':bool(np.array_equal(P[m==0],N[m==0])),'formalAccepted':False})
print(json.dumps({'selectedNative':ref(R/'selected-native.png')}))
