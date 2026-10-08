from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;T=ROOT/'r09_c08';D=T/'canopy-repair'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
c=read(T/'regional/context.json');north=Path(c['northCore']['file']);base=Path(read(T/'jobs/r01_c03.receipt.json')['sourceOutputPath'])
assert sha(north)==c['northCore']['sha256']
ni=Image.open(north).convert('RGB');bi=Image.open(base).convert('RGB');assert ni.size==(4096,4096) and bi.size==(1254,1254)
out=D/'north-south-board1254.png';mp=D/'north-south-board1254.manifest.json';assert not out.exists() and not mp.exists();D.mkdir(exist_ok=True)
board=Image.new('RGB',(1254,1254));maps=[]
for p,im,box,xy in [(north,ni,(1933,3469,3187,4096),(0,0)),(base,bi,(0,115,1254,742),(0,627))]:
 part=im.crop(box);board.paste(part,xy);maps.append({'file':str(p),'sha256':sha(p),'sourceBox':box,'destinationXY':xy,'rawRGBSha256':hashlib.sha256(part.tobytes()).hexdigest(),'resampling':'none'})
board.save(out)
mp.write_text(json.dumps({'createdAtUtc':datetime.now(timezone.utc).isoformat(),'output':{'file':str(out),'sha256':sha(out),'pixels':[1254,1254]},'pixelMappings':maps,'guideOnly':True,'finalArt':False,'nativeBoundaryY':627,'boardToCellYOffset':-512,'operation':'Integer native crops and paste only; authentic north core, existing south native candidate; not a replacement halo or production artwork.'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':sha(out)}))
