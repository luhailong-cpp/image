from pathlib import Path
from PIL import Image
import numpy as np, json, sys
import build_joint as j

R=Path(__file__).resolve().parent
B=R.parents[2]
D=R/'joint-v3';D.mkdir(exist_ok=True)
Q=D/'qa';Q.mkdir(exist_ok=True)
base_path=R/'joint-v2/joint-candidate.png'
ai_path=R/'native/water-junction.png'
base=j.arr(base_path).copy();old=base[:,512:1766].copy();ai=j.arr(ai_path)
# AI repaired water only. The protected wall remains from the prior joint.
# This alpha is a finite assembly return over water texture, not a blur.
yy,xx=np.mgrid[:1254,:1254]
top=285+np.maximum(xx-500,0)*.24
alpha=np.minimum.reduce([np.clip((xx-230)/48,0,1),np.clip((1060-xx)/48,0,1),np.clip((yy-top)/48,0,1),np.clip((1160-yy)/48,0,1)])
piece=np.rint(old*(1-alpha[:,:,None])+ai*alpha[:,:,None]).astype(np.uint8)
base[:,512:1766]=piece
Image.fromarray(base).save(D/'joint-candidate.png')
np.savez_compressed(D/'water-alpha.npz',alpha=alpha)
Image.fromarray(piece).save(Q/'water-integration-native.png')
for name,box in [('water-top-return',(160,220,1120,620)),('water-bottom-return',(160,990,1120,1230)),('water-left-return',(180,270,360,1190)),('water-right-return',(930,270,1130,1190))]:
    Image.fromarray(piece).crop(box).save(Q/(name+'-native.png'))
north_path=B/'tiles/current/r09_c12-candidate.png'
south_path=B/'r10_c12/repairs/root-detail/r10_c12-internal-candidate-v7.png'
north=j.arr(north_path).copy();south=j.arr(south_path).copy()
assert np.array_equal(j.arr(B/'r10_c12/repairs/r10_c12-candidate-v5.png')[:627],south[:627])
north[3469:]=base[:627,115:4211];south[:627]=base[627:,115:4211]
north_file=D/'r09_c12-north-joint-candidate.png';south_file=D/'r10_c12-north-joint-candidate.png'
Image.fromarray(north).save(north_file);Image.fromarray(south).save(south_file)
for i in range(4):
    core=base[:,115+i*1024:115+(i+1)*1024]
    for name,start,end in [('shared',467,787),('north-return',0,470),('south-return',1000,1254)]:
        Image.fromarray(core[start:end]).save(Q/f'{name}-s{i+1}-native.png')
for i in range(1,4):
    x=115+i*1024
    Image.fromarray(base[:,x-160:x+160]).save(Q/f'segment-junction-{i}-native.png')
Image.fromarray(base[:,115:4211]).resize((1638,502),Image.Resampling.LANCZOS).save(D/'preview.png')
record={'status':'pending_native_return_review','nativeScale':1,'baseJoint':{'file':str(base_path),'sha256':j.sha(base_path),'record':str(R/'joint-v2/record.json')},'aiRepair':{'file':str(ai_path),'sha256':j.sha(ai_path),'record':str(ai_path)+'.generation.json'},'operation':'Same-coordinate native AI water repair at joint x512,y0; water-only finite 48px alpha returns. No resizing, displacement or image blur. Internal south v7 retains the three individually AI-repaired wood joins.','globalJointOriginXY':[44941,36237],'waterCropOriginInJoint':[512,0],'mask':{'file':str(D/'water-alpha.npz'),'sha256':j.sha(D/'water-alpha.npz')},'north':{'file':str(north_file),'sha256':j.sha(north_file)},'south':{'file':str(south_file),'sha256':j.sha(south_file)},'sourceNorth':{'file':str(north_path),'sha256':j.sha(north_path)},'sourceSouth':{'file':str(south_path),'sha256':j.sha(south_path)},'formalAccepted':False,'wholeCityComplete':False,'clientAccepted':False}
j.write(D/'record.json',record)
for path in [north_file,south_file]:j.write(str(path)+'.generation.json',{'file':str(path),'sha256':j.sha(path),'operationRecord':str(D/'record.json'),'nativeScale':1,'formalAccepted':False})
print(json.dumps(record))
