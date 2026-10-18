from pathlib import Path
import sys,json
from PIL import Image
T=Path(__file__).resolve().parent
sys.argv=[str(T/'workflow_20261013.py'),'noop']
sys.path.insert(0,str(T));import workflow_20261013 as w
e=w.check_rules();target=next(x['worldBoxWithHalo'] for x in w.p.coordinates(w.TILE)['patches'] if x['id']=='s01_03')
im=Image.open(T/'native/s01_03_fix02.png').convert('RGB');parts=[]
for a in w.sources():
 if a.get('patch')=='s01_03':continue
 h=w.p.overlap(target,a['worldBox'])
 if not h:continue
 b=a['worldBox'];off=a['sourceOffset'];s=[h[0]-b[0]+off[0],h[1]-b[1]+off[1],h[2]-b[0]+off[0],h[3]-b[1]+off[1]];d=[h[0]-target[0],h[1]-target[1],h[2]-target[0],h[3]-target[1]]
 im.paste(Image.open(a['file']).convert('RGB').crop(s),d[:2]);parts.append(dict(a,sourceBox=s,targetBox=d))
f=T/'repairs/north-coping-fixed-anchors/input.png';w.p.save_png(f,im)
w.p.write_json(f.with_suffix('.png.derivation.json'),dict(targetWorldBox=target,nativeEditTarget=w.ref(T/'native/s01_03_fix02.png'),nativeAnchors=parts,sourceResampled=False,rules=e),replace=False)
print(str(f))

