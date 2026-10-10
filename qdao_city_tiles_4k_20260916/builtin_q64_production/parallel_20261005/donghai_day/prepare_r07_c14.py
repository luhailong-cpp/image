"""Reference-only preparation for the tile immediately north of r08_c14."""
from pathlib import Path
from PIL import Image
import numpy as np
import json, hashlib, math
from datetime import datetime, timezone
R = Path(__file__).resolve().parent
P = R.parents[3]
T = R / 'r07_c14'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path, value): Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def main():
    assert not (T/'plan.json').exists(), 'Existing plan retained'
    for name in ['guides','prompts','native','output','qa']: (T/name).mkdir(parents=True,exist_ok=True)
    handoff=json.loads((R/'handoff.json').read_text(encoding='utf-8-sig'))
    plan_source=Path(handoff['plan']['file'])
    assert sha(plan_source)==handoff['plan']['sha256']
    full=json.loads(plan_source.read_text(encoding='utf-8-sig'))
    tile=next(x for x in full['tiles'] if x['id']=='r07_c14')
    x,y,w,h=tile['finalPixelRect']
    assert [x,y,w,h]==[53248,24576,4096,4096]
    source=Path(handoff['layout']['file'])
    assert sha(source)==handoff['layout']['sha256']
    global_box=[x-115,y-115,x+w+115,y+h+115]
    target=T/'guides/local-layout.png'
    with Image.open(source) as image:
        image.load(); assert image.size==(1254,1254)
        rgb=np.array(image.convert('RGB'))
        extended=Image.fromarray(rgb)
        box=[v*1254/65536 for v in global_box]
        extended.transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(target)
        ey0,ey1=math.floor(box[1]),math.ceil(box[3])
        edge=rgb[ey0:ey1,-3:]
    now=datetime.now(timezone.utc).isoformat()
    border={'mapBounds':[0,0,65536,65536],'requestedGlobalBox':global_box,'extendsBeyondMap':False,'referenceOnly':True,'finalCorePixelsNotPadded':True,'finalArtUpscaled':False}
    neighbors={}
    for direction,identity in [('south','r08_c14'),('east','r07_c15'),('west','r07_c13')]:
        other=next(i for i in full['tiles'] if i['id']==identity)
        neighbors[direction]={'tile':identity,'globalRect':other['finalPixelRect'],'file':str(R/identity/'output'/f'{identity}.png'),'sha256':None,'bindingStatus':'pending','role':'actual complete 4096 tile core; global intersection pixels only after explicit SHA binding'}
    plan={'tile':tile['id'],'globalRect':tile['finalPixelRect'],'worldRect':tile['worldRect'],'productionPlan':str(plan_source),'productionPlanSha256':sha(plan_source),'layoutSource':str(source),'layoutSourceSha256':sha(source),'layoutSourceBox':box,'globalBox':global_box,'sourceGuide':str(target),'guideSha256':sha(target),'neighbors':neighbors,'southBindingStatus':'pending','preparedAtUtc':now,'status':'layout_reference_prepared_structure_pending','referenceEnlargementOnly':True,'formalAccepted':False,'nativeGrid':[4,4],'core':1024,'halo':115,'boundaryPolicy':border,'geometryStatus':'confirmed layout crop only; local structure review pending','dayFestivalGeometryAligned':False,'navigationAccepted':False,'generationGuards':{'nativeBottomRowRequires':'bound complete south r08_c14 SHA','westNeighbor':'pending; do not invent missing west context; native top row allowed'}}
    save(T/'plan.json',plan)
    save(Path(str(target)+'.generation.json'),{'file':str(target),'sha256':sha(target),'createdAtUtc':now,'derivedFrom':[{'file':str(source),'sha256':sha(source)}],'operation':'reference-only enlarged global layout crop at exact global extent','sourceBox':box,'globalBox':global_box,'pixels':[1254,1254],'allowedInFinal':False,'countsAsHDArt':False,'boundaryPolicy':border})
    print(json.dumps(plan))
if __name__=='__main__': main()
