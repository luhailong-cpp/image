from pathlib import Path
import hashlib,json,datetime,shutil
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent
src=Path(r'C:/Users/luyua/.codex/generated_images/01a11b1a-4dc1-75e3-9f90-f22d475bffd8/exec-dcf92638-787f-4e02-8fae-b9166a0a4454.png')
dst=O/'generated-v1.png';shutil.copy2(src,dst)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
refs=[O/'input.png',Path('D:/work/image/designs/gameplay-ui/04-guild.png')]
call={'prompt':(O/'prompt.txt').read_text(encoding='utf8'),'referenced_image_paths':[str(p).replace('\\','/') for p in refs],'transparent_background':False}
(O/'call.json').write_text(json.dumps(call,ensure_ascii=False,indent=2),encoding='utf8')
im=Image.open(dst);assert im.size==(1254,1254)
d={'file':str(dst),'sha256':sha(dst),'generatedAt':datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone.utc).isoformat(),'generatedAtEvidence':'tool output local file modification time','width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf8')),'submittedParameters':dict(call,model=None,quality=None),'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露型号及质量。','evidence':{'toolResultPath':str(src),'sha256':sha(src),'outputHint':str(O/'tool-output.txt'),'displayedInToolResult':True},'prompt':str(O/'prompt.txt'),'references':[{'file':str(p),'sha256':sha(p),'role':['edit target','approved primary style'][i]} for i,p in enumerate(refs)],'formalAccepted':False}
Path(str(dst)+'.generation.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
for name,box in [('upper-generated',[490,275,790,475]),('lower-generated',[490,895,790,1095])]:
 p=O/(name+'.png');im.crop(box).save(p)
 Path(str(p)+'.generation.json').write_text(json.dumps({'file':str(p),'sha256':sha(p),'derivedFrom':[{'file':str(dst),'sha256':sha(dst),'generationRecord':str(dst)+'.generation.json'}],'operation':{'method':'native integer QA crop','bbox':box}},indent=2),encoding='utf8')
a=np.array(Image.open(refs[0]),np.float32);b=np.array(im,np.float32)
for x,y in [(638,377),(632,1001)]:
 print(x,y, np.percentile(abs(a[y-30:y+30,x-80:x+80]-b[y-30:y+30,x-80:x+80]),[50,75,95,99]).tolist())

