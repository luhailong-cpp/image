from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
PROJECT = ROOT.parent

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

handoff = read(BASE/'handoff.json')
now = datetime.now(timezone.utc).isoformat()
audit = []
for item in [handoff['plan'], handoff['layout'], *handoff['baselineCandidates']]:
    p = Path(item['file'])
    entry = {'file':str(p), 'exists':p.exists(), 'expectedSha256':item['sha256']}
    if p.exists():
        entry['sha256']=sha(p)
        entry['shaMatches']=entry['sha256']==entry['expectedSha256']
        if p.suffix=='.png':
            with Image.open(p) as im:
                im.load()
                entry['pixels']=list(im.size)
    audit.append(entry)
assert all(e.get('shaMatches') for e in audit), 'handoff source missing or hash changed'
config=read(PROJECT/'config/image-generation.json')
write(BASE/'preflight/source-audit.json', {'checkedAtUtc':now, 'sources':audit, 'handoffReady':handoff['readyForProduction'], 'sourceDirectoriesReadOnly':True})
write(BASE/'preflight/official-model-check.json', {'checkedAtUtc':now, 'configSnapshot':config, 'sources':['https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','https://developers.openai.com/api/docs/guides/image-generation'], 'finding':'Official fetched model page lists Sunburst as most capable model and supports max. Current builtin schema has no model or quality selector. Root config remains unchanged in this isolated task.', 'submittedParameters':{'model':None,'quality':None}, 'actualModel':None, 'actualQuality':None})
write(BASE/'preflight/geometry-navigation.json', {'checkedAtUtc':now, 'firstMissingTile':'r08_c09','finalPixelRectXYWH':[32768,28672,4096,4096], 'worldRect':{'x':200,'z':150,'width':18.75,'height':18.75},'commonGeometryRequirement':'Spring detail must preserve verified day structure at the same coordinates. Independent spring appearance overview is not a geometry source. Old r08_c09 day regional mother and guides are missing; wait for current day geometry.', 'dayGeometryStatusFile':str(BASE.parent/'lanxian_day/current-work.json'), 'legacyNativePatch':{'file':str(ROOT/'builtin_q64_production/lanxian_day/r08_c09/native/r01_c01.png'), 'sha256':'52dd3413b2fa93e930b1c7d8126ea86a2a46eab38aa93b7aebc9b5b151e9917c', 'pixels':[1254,1254], 'role':'existing detail fragment, not whole tile; current day selection pending'}, 'navigation':{'code':'D:/work/mmorpg-client/Assets/Scripts/World/Tianyong/FestivalRegionMap.cs','sharedMaskPath':'World/FestivalRegions/lanxian/walkmask','grid':[150,150], 'worldUnitsPerCell':2, 'spawn':[200,0,180], 'localMaskPresent':False,'pixelNavigationValidation':'not performed: local mask missing'}, 'formalAccepted':False})
common={'schemaVersion':1,'appearance':'lanxian_spring','updatedAtUtc':now,'readyForProduction':handoff['readyForProduction'],'status':'awaiting_current_day_geometry' if handoff['readyForProduction'] else 'preflight_waiting_for_handoff','targetTiles':256,'targetTilePixels':[4096,4096],'wholeCityPixels':[65536,65536],'baselineCandidateCount':len(handoff['baselineCandidates']),'baselineCurrent':handoff.get('baselineCurrent',False),'formalAccepted':0,'newComplete4KCandidates':0,'nativeDetailPatchesGenerated':0,'wholeCityComplete':False,'runtimePublished':False,'route':'builtin_image_gen','paidApiAllowed':False,'sourceAudit':'preflight/source-audit.json'}
for filename in ['progress.json','current-work.json']:
    if not (BASE/filename).exists() or read(BASE/filename).get('nativeDetailPatchesGenerated',0)==0:
        out=dict(common)
        if filename=='current-work.json':
            out.update(currentTile='r08_c09',requiredNativePatches=16,core=1024,halo=115,currentPhase='handoff_gate' if not handoff['readyForProduction'] else 'shared_geometry',nextAction='Re-read handoff every <=30s; once ready verify final source SHA and use current day shared geometry for adjacent spring detail.')
        write(BASE/filename,out)
preview=Image.new('RGB',(1536,512),(46,51,48))
draw=ImageDraw.Draw(preview)
sources=[]
for i,item in enumerate(handoff['baselineCandidates']):
    with Image.open(item['file']) as im:
        preview.paste(im.resize((512,512),Image.Resampling.LANCZOS),(i*512,0))
    sources.append({'file':item['file'],'sha256':item['sha256']})
preview.save(BASE/'current-preview.png')
write(BASE/'current-preview.png.generation.json',{'file':str(BASE/'current-preview.png'),'sha256':sha(BASE/'current-preview.png'),'derivedFrom':sources,'operation':'Downsample three inherited 4K candidates to 512 squares for preview only; no new production pixels.','formalAccepted':False})
print(json.dumps({'handoffReady':handoff['readyForProduction'],'sourceShaMatches':True,'status':common['status']}))
