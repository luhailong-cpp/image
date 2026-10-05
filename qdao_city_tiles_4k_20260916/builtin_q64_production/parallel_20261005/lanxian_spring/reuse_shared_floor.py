from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil
from PIL import Image

BASE=Path(__file__).resolve().parent
DAY=BASE.parent/'lanxian_day/r08_c09/native'
DEST=BASE/'r08_c09/native'
DEST.mkdir(parents=True,exist_ok=True)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

h=read(BASE/'handoff.json')
assert h['readyForProduction']
for x in h['currentCandidates']:
    assert sha(Path(x['file']))==x['sha256']

copied=[]
for row in range(1,5):
    for col in range(1,5):
        key=f'r{row:02d}_c{col:02d}'
        if key in {'r04_c03','r04_c04'}: continue
        source=DAY/f'{key}.png'; record=DAY/f'{key}.png.generation.json'
        target=DEST/source.name
        if target.exists() or not source.exists() or not record.exists(): continue
        original=read(record)
        digest=sha(source)
        if digest!=original.get('sha256'): continue
        with Image.open(source) as im:
            im.load()
            assert im.size==(1254,1254)
        shutil.copyfile(source,target)
        write(Path(str(target)+'.generation.json'),{
            'schemaVersion':1,'assetId':'lanxian_spring','tile':'r08_c09','patchId':key,
            'file':str(target),'sha256':digest,'width':1254,'height':1254,'format':'PNG',
            'role':'shared_day_spring_structure_native_pixels_no_new_AI_call',
            'generatedAt':original.get('generatedAt'),'ingestedAt':datetime.now(timezone.utc).isoformat(),
            'actualModel':original.get('actualModel'),'actualQuality':original.get('actualQuality'),
            'unverifiedReason':original.get('unverifiedReason','Source host did not disclose model or quality.'),
            'derivedFrom':[{'file':str(source),'sha256':digest,'generationRecord':str(record),'generationRecordSha256':sha(record),'generationRecordSnapshot':original}],
            'operation':'Byte-identical native detail reuse for shared paving/foliage; no resizing, recoloring or new AI. Spring decorations handled on existing tree-planter surfaces in r04_c03/c04.',
            'qa':{'accepted':False,'status':'pending_full_seam_and_cross_appearance_review'},
            'crossAppearanceGeometryAccepted':False
        })
        copied.append(key)
native=list(DEST.glob('r??_c??.png'))
now=datetime.now(timezone.utc).isoformat()
for name in ['current-work.json','progress.json']:
    state=read(BASE/name)
    state.update(updatedAtUtc=now,status='active_native_production',readyForProduction=True,baselineCurrent=True,currentTile='r08_c09',currentPhase='spring_conversion_and_shared_floor_reuse',nativeDetailPatchesAvailable=len(native),newComplete4KCandidates=0,formalAccepted=0,wholeCityComplete=False)
    state['reusedSharedNativePatches']=len([p for p in native if read(Path(str(p)+'.generation.json')).get('role')=='shared_day_spring_structure_native_pixels_no_new_AI_call'])
    state['nativeDetailPatchesGenerated']=len(native)-state['reusedSharedNativePatches']
    state['nextAction']='Finish r08_c09 native pieces, assemble without scaling, inspect every seam and repair any concrete mismatch.'
    state.pop('blockingCondition',None)
    write(BASE/name,state)
print(json.dumps({'copied':copied,'available':len(native),'complete4KTiles':0}))
