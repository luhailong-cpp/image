from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'r09_c09/qa'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
sources=[('r08_c09/selected/core4096.png',(3584,3584,4096,4096),(0,0)),('r08_c10/selected/core4096.png',(0,3584,512,4096),(512,0)),('r09_c09/candidate/core4096.png',(3584,0,4096,512),(0,512)),('r09_c10/selected/core4096.png',(0,0,512,512),(512,512))]
board=Image.new('RGB',(1024,1024));items=[]
dest=OUT/'northeast-four-tile-junction.png';record=OUT/'northeast-four-tile-junction.manifest.json'
assert not dest.exists() and not record.exists()
for name,box,xy in sources:
 p=ROOT/name;im=Image.open(p);assert im.size==(4096,4096);crop=im.convert('RGB').crop(box);board.paste(crop,xy)
 items.append({**ref(p),'sourceBoxXYXY':box,'destinationXY':xy,'cropRawRGBSha256':hashlib.sha256(crop.tobytes()).hexdigest(),'resampling':'none'})
board.save(dest)
record.write_text(json.dumps({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'output':ref(dest),'pixels':[1024,1024],'crossingXY':[512,512],'worldCrossingXY':[36864,32768],'pixelMappings':items,'operation':'Integer crop/paste only','visualInspectionPerformed':False,'formalAccepted':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'image':str(dest),'sha256':sha(dest),'manifest':str(record)}))
