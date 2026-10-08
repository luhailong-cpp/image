import json, hashlib
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
T=ROOT/'r09_c09'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(im): return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
q=read(T/'qa/qa.manifest.json')
g=read(T/'qa/guide-bands/manifest.json')
corep=T/'candidate/core4096.png'
core=Image.open(corep).convert('RGB')
assert sha(corep)==q['source']['sha256']
old=[]
for rp,key in [(T/'early-internal-qa/review.json','checks'),(T/'early-neighbor-qa/review.json','items')]:
    for item in read(rp)[key]:
        if not item.get('actualViewed',item.get('actuallyViewed',False)): continue
        fp=Path(item['file'])
        assert sha(fp)==item['sha256'],str(fp)
        im=Image.open(fp).convert('RGB')
        rs=rgb(im)
        assert rs==item.get('decodedRgbSha256',item.get('rawRGBSha256'))
        old.append((rp,item,im,rs))
checks=[]
for item in q['checks']:
    if item['kind'] in ['internal_vertical_seam','internal_horizontal_seam','four_cell_intersection']:
        checks.append(dict(item,targetCoreBox=item['sourceBox']))
for item in g['checks']:
    if item['axis']=='y':
        checks.append(dict(item,targetCoreBox=item['coreBox'],kind='horizontal_guide_inner_edge'))
assert len(checks)==49
for item in checks:
    fp=Path(item['file']); im=Image.open(fp).convert('RGB'); box=item['targetCoreBox']
    assert sha(fp)==item['sha256'],str(fp)
    assert im.tobytes()==core.crop(box).tobytes(),str(fp)
    item['source']={'file':str(corep),'sha256':sha(corep)}
    item['decodedRgbSha256']=rgb(im)
    item['finalCropEqualsCoreBox']=True
    item['newlyViewed']=False
    item['inheritance']=None
    for rp,earlier,eim,ers in old:
        if earlier.get('targetCoreBox')==box and eim.size==im.size and ers==item['decodedRgbSha256']:
            item['inheritance']={'reviewFile':str(rp),'reviewFileSha256':sha(rp),'earlierCropFile':earlier['file'],'earlierCropSha256':earlier['sha256'],'earlierDecodedRgbSha256':ers,'sameTargetCoreBox':True,'decodedRgbExactlyEqual':True,'earlierActuallyViewed':True,'observation':earlier['observation'],'requiresRepair':earlier['requiresRepair']}
            break
out={'source':q['source'],'checks':checks,'scopeCount':49,'inheritedCount':sum(c['inheritance'] is not None for c in checks),'newViewsPending':sum(c['inheritance'] is None for c in checks)}
p=T/'qa/final-internal-verification.json'
p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
print('Pending actual views:')
for c in checks:
    if c['inheritance'] is None: print(str(Path(c['file']).relative_to(T)),c['targetCoreBox'])
