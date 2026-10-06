from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
H=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
num=sys.argv[1];src=Path(sys.argv[2]);call=json.loads((H/sys.argv[3]).read_text(encoding='utf-8-sig'));dst=H/f'attempt{num}.png';shutil.copyfile(src,dst)
im=Image.open(dst).convert('RGB');assert im.size==(1254,1254)
write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=datetime.now(timezone.utc).isoformat(),width=im.width,height=im.height,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=call['configSnapshot'],submittedParameters=call['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin tool exposes no model/quality selectors or response metadata.',prompt=call['promptFile'],references=call['references'],evidence=dict(toolOutputPath=str(src),toolOutputSha256=sha(src)),status='native_QA_pending'))
base=Image.open(H/'target.png').convert('RGB');pair=Image.new('RGB',(320,1254));pair.paste(base.crop((467,0,627,1254)),(0,0));pair.paste(im.crop((627,0,787,1254)),(160,0))
for name,y0,y1 in [('upper',250,550),('lower',760,1060)]:
 p=H/f'attempt{num}-{name}-shared.png';pair.crop((0,y0,320,y1)).save(p)
 write(str(p)+'.generation.json',dict(source=[dict(file=str(H/'target.png'),sha256=sha(H/'target.png')),dict(file=str(dst),sha256=sha(dst))],operation=dict(kind='actual_old_left_plus_generated_right_native_crop',sharedEdgeImageX=160,tileYRange=[1894+y0,1894+y1]),sha256=sha(p)))
print(str(dst),sha(dst))
