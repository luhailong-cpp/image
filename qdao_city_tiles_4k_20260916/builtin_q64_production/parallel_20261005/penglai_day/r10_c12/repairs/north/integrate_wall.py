from pathlib import Path
from PIL import Image
import numpy as np, sys
import build_joint as j
R=Path(__file__).resolve().parent;B=R.parents[2]
sys.path.insert(0,str(B));import production as p
p.ROOT=R
source=Path('C:/Users/luyua/.codex/generated_images/01a10ba6-e6fa-7390-b78d-21394b0a60ef/exec-90e65844-373b-4517-80d0-582637c2b58e.png')
ai_path=R/'native/wall-junction.png'
if not ai_path.exists():p.ingest(source,'wall-junction',R/'prompts/wall-junction.prompt.txt',[str(R/'references/wall-junction-input.png'),'D:/work/image/designs/gameplay-ui/04-guild.png'],'native_wall_junction_repair')
D=R/'joint-v4';D.mkdir(exist_ok=True);Q=D/'qa';Q.mkdir(exist_ok=True)
base_path=R/'joint-v3/joint-candidate.png';base=j.arr(base_path).copy();old=base[:,1536:2790].copy();ai=j.arr(ai_path)
yy,xx=np.mgrid[:1254,:1254]
def rect(box,fade):
    x0,y0,x1,y1=box
    return np.minimum.reduce([np.clip((xx-x0)/fade,0,1),np.clip((x1-xx)/fade,0,1),np.clip((yy-y0)/fade,0,1),np.clip((y1-yy)/fade,0,1)])
wall=rect([465,-1,870,380],40)
groove=rect([365,-1,420,545],8)
alpha=np.maximum(wall,groove)
piece=np.rint(old*(1-alpha[:,:,None])+ai*alpha[:,:,None]).astype(np.uint8)
base[:,1536:2790]=piece
Image.fromarray(base).save(D/'joint-candidate.png');np.savez_compressed(D/'wall-alpha.npz',alpha=alpha)
Image.fromarray(piece[:460]).save(Q/'wall-return-native.png')
Image.fromarray(piece).crop((350,180,435,355)).save(Q/'groove-return-native.png')
prev=j.read(R/'joint-v3/record.json');north_path=Path(prev['north']['file']);south_path=Path(prev['south']['file'])
north=j.arr(north_path).copy();south=j.arr(south_path).copy()
north[3469:]=base[:627,115:4211];south[:627]=base[627:,115:4211]
north_file=D/'r09_c12-north-joint-candidate.png';south_file=D/'r10_c12-north-joint-candidate.png'
Image.fromarray(north).save(north_file);Image.fromarray(south).save(south_file)
for i in range(4):
    core=base[:,115+i*1024:115+(i+1)*1024]
    for name,start,end in [('shared',467,787),('north-return',0,470),('south-return',1000,1254)]:Image.fromarray(core[start:end]).save(Q/f'{name}-s{i+1}-native.png')
for i in range(1,4):
    x=115+i*1024;Image.fromarray(base[:,x-160:x+160]).save(Q/f'segment-junction-{i}-native.png')
Image.fromarray(base[:,115:4211]).resize((1638,502),Image.Resampling.LANCZOS).save(D/'preview.png')
record={'status':'pending_native_return_review','baseJoint':{'file':str(base_path),'sha256':j.sha(base_path),'record':str(R/'joint-v3/record.json')},'aiRepair':{'file':str(ai_path),'sha256':j.sha(ai_path),'record':str(ai_path)+'.generation.json'},'operation':'Native same-coordinate localized AI wall and groove repair, 40px wall return and 8px groove return. No resizing, displacement, or image blur. Inherits joint-v3 AI water patch and internal v7 south repairs.','globalJointOriginXY':[44941,36237],'mask':{'file':str(D/'wall-alpha.npz'),'sha256':j.sha(D/'wall-alpha.npz')},'repairCropOriginXY':[1536,0],'north':{'file':str(north_file),'sha256':j.sha(north_file)},'south':{'file':str(south_file),'sha256':j.sha(south_file)},'sourceNorth':prev['north'],'sourceSouth':prev['south'],'formalAccepted':False,'wholeCityComplete':False,'clientAccepted':False}
j.write(D/'record.json',record)
for path in [north_file,south_file]:j.write(str(path)+'.generation.json',{'file':str(path),'sha256':j.sha(path),'operationRecord':str(D/'record.json'),'nativeScale':1,'formalAccepted':False})
print(record)
