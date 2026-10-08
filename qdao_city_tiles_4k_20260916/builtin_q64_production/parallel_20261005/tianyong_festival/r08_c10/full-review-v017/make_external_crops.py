from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np

T=Path(__file__).resolve().parents[2]
out=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cpfile=T/'source-checkpoint.json'
cp=json.loads(cpfile.read_text(encoding='utf-8-sig'))
assert cp['version']=='v017'
entries={'r08_c10':cp['fragment'],'r08_c09':cp['coupledNeighbors']['r08_c09'],'r09_c10':cp['bottom'],'r09_c09':cp['coupledNeighbors']['r09_c09']}
images={}
for key,v in entries.items():
    assert sha(v['file'])==v['sha256']
    images[key]=Image.open(v['file']).convert('RGBA')
    assert images[key].size==(4096,4096)
index={'checkpoint':{'file':str(cpfile),'sha256':sha(cpfile)},'sources':entries,'nativeScale':1,'crops':[]}
def save(name,ims):
    canvas=Image.new('RGBA',(768,max(v[2][1]+v[1][3]-v[1][1] for v in ims)),(0,0,0,0))
    placements=[]
    for tile,box,xy in ims:
        canvas.paste(images[tile].crop(box),xy)
        placements.append({'tile':tile,'sourceLTRB':box,'pasteXY':xy})
    p=out/(name+'.png');canvas.save(p)
    index['crops'].append({'file':str(p),'sha256':sha(p),'size':list(canvas.size),'placements':placements})
for n,(y0,y1) in enumerate([(0,1152),(1024,2176),(2048,3200),(3072,4096)],1):
    save(f'left-seam-{n:02d}-y{y0}-{y1}',[('r08_c09',(3712,y0,4096,y1),(0,0)),('r08_c10',(0,y0,384,y1),(384,0))])
for y in (2048,3072):
    save(f'inherited-intersection-y{y}',[('r08_c09',(3712,y-128,4096,y+128),(0,0)),('r08_c10',(0,y-128,384,y+128),(384,0))])
save('corner-nw-known-south-half',[('r08_c09',(3712,0,4096,384),(0,0)),('r08_c10',(0,0,384,384),(384,0))])
save('corner-sw-four-tiles',[('r08_c09',(3712,3712,4096,4096),(0,0)),('r08_c10',(0,3712,384,4096),(384,0)),('r09_c09',(3712,0,4096,384),(0,384)),('r09_c10',(0,0,384,384),(384,384))])
save('corner-ne-known-sw-quarter',[('r08_c10',(3712,0,4096,384),(0,0))])
save('corner-se-known-west-half',[('r08_c10',(3712,3712,4096,4096),(0,0)),('r09_c10',(3712,0,4096,384),(0,384))])
a=np.asarray(images['r08_c09'])[:,-1,:3].astype(float)
b=np.asarray(images['r08_c10'])[:,0,:3].astype(float)
index['supplementalMetricsNotAcceptance']={'borderChannelMeanAbsDifference':float(np.abs(a-b).mean()),'perRowRgbMeanAbsDifferenceP99':float(np.quantile(np.abs(a-b).mean(axis=1),.99)),'maxRowRgbMeanAbsDifference':float(np.abs(a-b).mean(axis=1).max())}
prev=Image.open(T/'r08_c10/current/v014/r08_c10-fragment.png').convert('RGBA')
index['southReference']={'file':str(T/'r08_c10/whole-tile-qa-v014-root/visual-review.json'),'sha256':sha(T/'r08_c10/whole-tile-qa-v014-root/visual-review.json'),'activeSouth256ExactlyEqualsV014':bool(np.array_equal(np.asarray(images['r08_c10'])[3840:],np.asarray(prev)[3840:]))}
(out/'external-crop-index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(out),'crops':len(index['crops']),'metrics':index['supplementalMetricsNotAcceptance'],'south':index['southReference']},ensure_ascii=False))
