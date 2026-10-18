from pathlib import Path
import sys,json
from PIL import Image
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import bridge_repair_20261016 as b
e=b.rules();P=T/'candidate/native19-local-repairs-20261016-v1/candidate.png';N=T.parent/'r06_c07/candidate/r06_c07-candidate-hard-4c0d654c3aae.png'
x,y=2560,-627;im=Image.new('RGB',(1254,1254));im.paste(Image.open(N).convert('RGB').crop((x,4096+y,x+1254,4096)),(0,0));im.paste(Image.open(P).convert('RGB').crop((x,0,x+1254,627)),(0,627))
d=T/'repairs/north-right_fix01';d.mkdir(parents=True,exist_ok=False);f=d/'input.png';im.save(f)
b.write(d/'input.derivation.json',dict(file=str(f),sha256=b.sha(f),role='unscaled native world-aligned edit target',worldBox=[24576+x,24576+y,24576+x+1254,24576+y+1254],tileLocalBox=[x,y,x+1254,y+1254],inputs=[dict(file=str(N),sha256=b.sha(N),sourceBox=[x,4096+y,x+1254,4096],targetBox=[0,0,1254,627]),dict(file=str(P),sha256=b.sha(P),sourceBox=[x,0,x+1254,627],targetBox=[0,627,1254,1254])],resampled=False,rules=e))
print(str(f))

