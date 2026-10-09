from pathlib import Path
import sys,json
from PIL import Image
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import helper as h
O=T/'repairs/internal-ai';O.mkdir(exist_ok=True)
for d in ['native','evidence','prompts']:(O/d).mkdir(exist_ok=True)
spec=json.loads((O/'targets.json').read_text(encoding='utf8'))
src=T/'repairs/internal-quilt/r11_c11-internal-v2.png';im=Image.open(src)
for e in spec:
 x,y=e['origin'];box=[x,y,x+1254,y+1254];f=O/(e['name']+'-target.png');im.crop(box).save(f);h.p.derived(f,[src],{'method':'native integer repair crop','boxLTRB':box})
h.p.write(T/'qa/inspection-internal-v2.json',{'source':str(src),'sourceSHA256':h.p.sha(src),'inspected':'6 native seam boards, 9 native junctions, 9 full 1254 context crops','findings':spec,'knownSharedIssues':['north p13/p14 artificial guide y115 band','west p31/p41 artificial guide x115 band'],'formalAccepted':False})

