"""Reference-only preparation for the tile immediately south of r09_c16."""
from pathlib import Path
from PIL import Image
import numpy as np
import json, hashlib, math
from datetime import datetime, timezone
R = Path(__file__).resolve().parent
P = R.parents[3]
T = R / 'r10_c16'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value): Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def main():
    assert not (T/'plan.json').exists(), 'Existing plan retained'
    for name in ['guides','prompts','native','output','qa']: (T/name).mkdir(parents=True,exist_ok=True)
    handoff=json.loads((R/'handoff.json').read_text(encoding='utf-8-sig'))
    plan_source=Path(handoff['plan']['file'])
    assert sha(plan_source)==handoff['plan']['sha256']
    full=json.loads(plan_source.read_text(encoding='utf-8-sig'))
    tile=next(x for x in full['tiles'] if x['id']=='r10_c16')
    x,y,w,h=tile['finalPixelRect']
    assert [x,y,w,h]==[61440,36864,4096,4096]
    source=Path(handoff['layout']['file'])
    assert sha(source)==handoff['layout']['sha256']
    global_box=[x-115,y-115,x+w+115,y+h+115]
    target=T/'guides/local-layout.png'
    with Image.open(source) as image:
        image.load(); assert image.size==(1254,1254)
        rgb=np.array(image.convert('RGB'))
        extended=Image.fromarray(np.pad(rgb,((0,0),(0,4),(0,0)),mode='edge'))
        box=[v*1254/65536 for v in global_box]
        extended.transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(target)
        ey0,ey1=math.floor(box[1]),math.ceil(box[3])
        edge=rgb[ey0:ey1,-3:]
    now=datetime.now(timezone.utc).isoformat()
    border={'mapBounds':[0,0,65536,65536],'requestedGlobalBox':global_box,'beyondRightMapPixels':115,'rightmostCoreCoordinateExclusive':65536,'rightHaloPurpose':'context only; excluded from all formal core pixels','layoutGuidancePadding':'four source-reference columns edge-clamped beyond right boundary for reference only','finalCorePixelsNotPadded':True,'finalArtUpscaled':False,'sourceRightEdgeInspection':{'sourceEdgeRegionXYXY':[1251,ey0,1254,ey1],'minRGB':edge.min(axis=(0,1)).tolist(),'maxRGB':edge.max(axis=(0,1)).tolist(),'allBlackPixels':int(np.all(edge==0,axis=2).sum()),'visualReview':'pending'}}
    neighbors={}
    for direction,identity in [('north','r09_c16'),('west','r10_c15')]:
        other=next(i for i in full['tiles'] if i['id']==identity)
        neighbors[direction]={'tile':identity,'globalRect':other['finalPixelRect'],'file':str(R/identity/'output'/f'{identity}.png'),'sha256':None,'bindingStatus':'pending','role':'actual complete 4096 tile core; global intersection pixels only after explicit SHA binding'}
    plan={'tile':tile['id'],'globalRect':tile['finalPixelRect'],'worldRect':tile['worldRect'],'productionPlan':str(plan_source),'productionPlanSha256':sha(plan_source),'layoutSource':str(source),'layoutSourceSha256':sha(source),'layoutSourceBox':box,'globalBox':global_box,'sourceGuide':str(target),'guideSha256':sha(target),'neighbors':neighbors,'northBindingStatus':'pending','preparedAtUtc':now,'status':'layout_reference_prepared_structure_pending','referenceEnlargementOnly':True,'formalAccepted':False,'nativeGrid':[4,4],'core':1024,'halo':115,'boundaryPolicy':border,'geometryStatus':'confirmed layout crop only; local structure review pending','dayFestivalGeometryAligned':False,'navigationAccepted':False,'generationGuards':{'nativeTopRowRequires':'bound complete north r09_c16 SHA','westNeighbor':'pending; do not invent missing west context; native bottom row allowed'}}
    save(T/'plan.json',plan)
    save(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'createdAtUtc':now,'derivedFrom':[{'file':str(source),'sha256':sha(source)}],'operation':'reference-only enlarged global layout crop with clamped right-edge guidance beyond map bounds','sourceBox':box,'globalBox':global_box,'pixels':[1254,1254],'allowedInFinal':False,'countsAsHDArt':False,'boundaryPolicy':border})
    print(json.dumps(plan))
if __name__=='__main__': main()
