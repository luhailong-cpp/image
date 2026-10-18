from pathlib import Path
import json,hashlib,argparse
import numpy as np
from PIL import Image
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pin=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
ap=argparse.ArgumentParser();ap.add_argument('--version',type=int,required=True);a=ap.parse_args()
p=Z/f'tiles/r05_c05_candidate-v{a.version}_4096.png';record=p.with_suffix('.native-repair.json')
base=Z/'tiles/r05_c05_candidate-v1_4096.png';oldip=Z/'qa/assembly_r05_c05_candidate-v1_4096/qa_index.json'
assert sha(base)=='b0a9f4bef308ebe9899b5324497767cfd8d07b197c168837f998150efb38801e'
assert sha(oldip)=='82df7fb3b9094c74e008a06548ba1146cc560aea9a89f3fc08e256ab76d3fc7f'
new=Image.open(p).convert('RGB');old=Image.open(base).convert('RGB')
q=Z/f'qa/r05_c05_v{a.version}_internal_delta_review_20261017';q.mkdir(exist_ok=False)
items=[];changed=[]
for item in json.loads(oldip.read_text())['seamAndJunctionCrops']:
 fp=Path(item['path']);assert sha(fp)==item['sha256']
 box=item['tileCropBoxHalfOpen'];im=new.crop(box)
 assert np.array_equal(np.array(Image.open(fp).convert('RGB')),np.array(old.crop(box)))
 same=np.array_equal(np.array(im),np.array(old.crop(box)))
 if not same:fp=q/fp.name;im.save(fp);changed.append(fp.name)
 assert np.array_equal(np.array(Image.open(fp).convert('RGB')),np.array(im))
 items.append({**item,**pin(fp),'reusedUnchangedV1Crop':same,'currentTileCropExactPixels':True,'reviewStatus':'reuse_prior_exact_pixel_review' if same else 'pending_changed_crop_review','prior':dict(path=item['path'],sha256=item['sha256'])})
pr=q/'preview_1024px_NOT_FOR_GAME.png';new.resize((1024,1024),Image.Resampling.LANCZOS).save(pr)
delta=np.any(np.array(new)!=np.array(old),axis=2)
edge={k:int(delta[b].sum()) for k,b in [('north',(slice(0,115),slice(None))),('south',(slice(3981,4096),slice(None))),('west',(slice(None),slice(0,115))),('east',(slice(None),slice(3981,4096)))]}
d=dict(tileId='r05_c05',candidate=pin(p),record=pin(record),baseline=pin(base),priorIndex=pin(oldip),seamAndJunctionCrops=items,changedCropCount=len(changed),unchangedReusedCount=33-len(changed),changedNames=changed,outer115ChangedPixelCounts=edge,preview={**pin(pr),'role':'downsampled inspection only not game art'},internalClosurePassed=False,formalAccepted=False)
ip=q/'qa_index.json'
with ip.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2);f.write('\n')
print(json.dumps(dict(candidate=pin(p),record=pin(record),qaIndex=pin(ip),changed=changed,unchangedReused=33-len(changed),outer115Delta=edge)))

