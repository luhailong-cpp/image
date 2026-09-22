from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;D=P/'external-v5';Q=D/'qa'
im=Image.open(D/'output/r09_c10.png').convert('RGB')
old=P.parents[1]/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5'
bottom=Image.open(old/'r10_c10.png').convert('RGB')
left=Image.open(P.parent/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png').convert('RGB')
files=[]
def save(name,image,role,boxes):
    path=Q/name;assert not path.exists();image.save(path)
    files.append({'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'role':role,'pixels':list(image.size),'sourceBoxes':boxes,'resized':False})
strip=Image.new('RGB',(4096,800));strip.paste(im.crop((0,3696,4096,4096)),(0,0));strip.paste(bottom.crop((0,0,4096,400)),(0,400))
save('bottom-detail-x1424-100pct.png',strip.crop((1024,0,1824,800)),'Bottom boundary near possible oblique edge transition',{'candidate':[1024,3696,1824,4096],'bottom':[1024,0,1824,400]})
strip=Image.new('RGB',(800,4096));strip.paste(left.crop((3696,0,4096,4096)),(0,0));strip.paste(im.crop((0,0,400,4096)),(400,0))
save('left-detail-y1424-100pct.png',strip.crop((0,1024,800,1824)),'Left boundary and return near inset-ring seam',{'left':[3696,1024,4096,1824],'candidate':[0,1024,400,1824]})
save('left-return-detail-y2380-100pct.png',im.crop((0,1980,800,2780)),'Left treatment return 2nd ring border',{'candidate':[0,1980,800,2780]})
(Q/'detail-index.json').write_text(json.dumps({'files':files},indent=2),encoding='utf-8')
print(json.dumps(files,indent=2))
