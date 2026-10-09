from pathlib import Path
import sys,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;B=R.parent;O=R/'repairs/north';O.mkdir(exist_ok=True,parents=True)
sys.path.insert(0,str(R/'repairs/internal'));import ai_helper as h
h.O=O
src=R/'repairs/internal/r11_c15-internal-candidate-v5.png';north=B/'r10_c15/tiles/r10_c15-candidate-final.png'
assert h.sha(north)=='b6b097cfb756eff9f8f75025526bc2efef635cbda7ec26e15f8aa28274385e70'
a=Image.open(src).convert('RGB');b=Image.open(north).convert('RGB');joint=Image.new('RGB',(4096,1254));joint.paste(b.crop((0,3469,4096,4096)),(0,0));joint.paste(a.crop((0,0,4096,627)),(0,627));p=O/'north-joint-source.png';joint.save(p);h.derived(p,[north,src],{'method':'exact627+627 source union','globalOrigin':[57344,40333],'seamY':627,'noResampling':True})
for i,x in enumerate([0,1024,2048,2842],1):
 n=f'north-{i}';z=O/(n+'-source.png');joint.crop((x,0,x+1254,1254)).save(z);h.derived(z,[p],{'crop':[x,0,x+1254,1254],'nativeNoRescale':True})
state={'north':{'file':str(north),'sha256':h.sha(north)},'south':{'file':str(src),'sha256':h.sha(src)},'source':str(p),'sourceSha256':h.sha(p),'globalOrigin':[57344,40333],'patchOffsets':[0,1024,2048,2842],'formalAccepted':False}
(O/'state-v1.json').write_text(json.dumps(state,indent=2),encoding='utf8')
