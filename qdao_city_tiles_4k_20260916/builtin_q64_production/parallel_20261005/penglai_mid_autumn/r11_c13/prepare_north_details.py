from pathlib import Path
import sys
from PIL import Image
F=Path(__file__).resolve().parent;ROOT=F.parent;sys.path.insert(0,str(ROOT))
from production import read,write,sha,now
p=F/'output/r11_c13-candidate.png';n=Path(read(F/'plan.json')['northCandidate'])
assert sha(p)=='1aa087f96cf986582881560436fb3fba780cbcbe13f3b29a133e4eb9c0ece180'
cur=Image.open(p).convert('RGB');old=Image.open(n).convert('RGB');out=F/'qa/external-details';out.mkdir(exist_ok=True)
for i in range(4):
 x=i*1024;im=Image.new('RGB',(1024,512));im.paste(old.crop((x,3840,x+1024,4096)),(0,0));im.paste(cur.crop((x,0,x+1024,256)),(0,256));dst=out/f'north-segment-{i+1}.png';assert not dst.exists();im.save(dst)
 write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),pixels=[1024,512],nativeScale=1,actuallyViewed=False,verdict='pending_visual_QA',sources=[dict(file=str(a),sha256=sha(a)) for a in [n,p]],reproduction=dict(canvasPixels=[1024,512],pieces=[dict(source='north',cropLTRB=[x,3840,x+1024,4096],pasteXY=[0,0]),dict(source='current',cropLTRB=[x,0,x+1024,256],pasteXY=[0,256])]),createdAt=now()))
print('4 native N details written; no candidate change.')
