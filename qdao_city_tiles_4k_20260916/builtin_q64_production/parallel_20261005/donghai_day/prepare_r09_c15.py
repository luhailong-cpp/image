"""Prepare reference-only layout and explicit neighboring-native bindings."""
import hashlib, json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

R=Path(__file__).resolve().parent
T=R/'r09_c15'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    assert not T.exists(), 'Inspect existing task rather than overwrite it'
    handoff=json.loads((R/'handoff.json').read_text(encoding='utf-8-sig'))
    production=Path(handoff['plan']['file']); layout=Path(handoff['layout']['file'])
    assert sha(production)==handoff['plan']['sha256'] and sha(layout)==handoff['layout']['sha256']
    full=json.loads(production.read_text(encoding='utf-8-sig'))
    tile=next(i for i in full['tiles'] if i['id']=='r09_c15')
    x,y,w,h=tile['finalPixelRect']; assert [x,y,w,h]==[57344,32768,4096,4096]
    for folder in ['guides','prompts','native','output','qa']: (T/folder).mkdir(parents=True,exist_ok=True)
    global_box=[x-115,y-115,x+w+115,y+h+115]
    assert all(0<=v<=65536 for v in global_box)
    target=T/'guides/local-layout.png'
    with Image.open(layout) as im:
        im.load(); assert im.size==(1254,1254)
        box=[v*1254/65536 for v in global_box]
        im.convert('RGB').transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(target)
    neighbors={}
    for direction,identity in [('north','r08_c15'),('east','r09_c16'),('west','r09_c14'),('south','r10_c15')]:
        other=next(i for i in full['tiles'] if i['id']==identity)
        neighbors[direction]={'tile':identity,'globalRect':other['finalPixelRect'],'file':str(R/identity/'output'/f'{identity}.png'),'sha256':None,'bindingStatus':'pending','role':'actual complete tile core, used only after explicit hash binding'}
    external=[]
    for row in (2,3,4):
        f=R/'r09_c16/native'/f'r{row:02d}_c01.png'
        rec=Path(str(f)+'.generation.json'); data=json.loads(rec.read_text(encoding='utf-8-sig'))
        assert data['sha256']==sha(f) and data['width']==data['height']==1254
        external.append({'file':str(f),'sha256':sha(f),'record':str(rec),'recordSha256':sha(rec),'tile':'r09_c16','row':row,'column':1,'globalRectXYXY':[61440-115,32768-115+(row-1)*1024,61440+1139,32768+1139+(row-1)*1024],'role':'bound actual native east-neighbor context; not a complete east tile'})
    now=datetime.now(timezone.utc).isoformat()
    plan={'tile':'r09_c15','globalRect':tile['finalPixelRect'],'worldRect':tile['worldRect'],'productionPlan':str(production),'productionPlanSha256':sha(production),'layoutSource':str(layout),'layoutSourceSha256':sha(layout),'layoutSourceBox':box,'globalBox':global_box,'sourceGuide':str(target),'guideSha256':sha(target),'neighbors':neighbors,'externalNativeBindings':external,'northBindingStatus':'pending','preparedAtUtc':now,'status':'layout_reference_prepared_structure_pending','referenceEnlargementOnly':True,'formalAccepted':False,'nativeGrid':[4,4],'core':1024,'halo':115,'boundaryPolicy':{'entireContextInsideMap':True,'paddingApplied':False,'finalArtUpscaled':False},'geometryStatus':'layout crop only, structure pending actual review','dayFestivalGeometryAligned':False,'navigationAccepted':False,'generationGuards':{'nativeTopRowRequires':'bound complete north r08_c15 SHA','eastNativeContext':'rows2..4 col1 explicit immutable SHA bindings, no assumption of complete tile'}}
    save(T/'plan.json',plan)
    save(str(target)+'.generation.json',{'file':str(target),'sha256':sha(target),'createdAtUtc':now,'derivedFrom':[{'file':str(layout),'sha256':sha(layout)}],'operation':'reference-only enlarged global layout crop; no padding','sourceBox':box,'globalBox':global_box,'pixels':[1254,1254],'allowedInFinal':False,'countsAsHDArt':False})
    print(json.dumps(plan))

if __name__=='__main__': main()
