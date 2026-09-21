from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image

ROOT=Path('E:/work/image/qdao_city_tiles_4k_20260916');P=ROOT/'builtin_q64_production'
B=P/'lanxian_batch_r08_c09_20260920'
assert not B.exists(),'Preserve all existing preparation'
B.mkdir();(B/'guides').mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
specs=[]
for appearance in ['lanxian_day','lanxian_spring']:
    pp=ROOT/f'q64_production_plans/{appearance}.json';entry=next(t for t in j(pp)['tiles'] if t['id']=='r08_c09')
    assert not (P/appearance/'r08_c09').exists(),'Do not restart existing production'
    neighbor=P/appearance/'triple_r08_c06_c08/output_v2/r08_c08.extended.png'
    with Image.open(neighbor) as im:assert im.size==(4326,4326)
    specs.append({'appearance':appearance,'tile':entry,'productionPlan':str(pp),'productionPlanSha256':sha(pp),'westNeighbor':str(neighbor),'westNeighborSha256':sha(neighbor),'westHaloSourceXYXY':[4096,0,4211,4326],'westHaloPixels':115,'detailNativeCompleted':0,'detailNativeRequired':16})
source=ROOT/'builtin_q64_all_city_references/lanxian_day/map-native-layout-reference.png'
layout=Image.open(source).convert('RGB');scale=layout.width/65536
box=[(32768-115)*scale,(28672-115)*scale,(36864+115)*scale,(32768+115)*scale]
canvas=layout.transform((4326,4326),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC)
west=Image.open(specs[0]['westNeighbor']).convert('RGB')
canvas.paste(west.crop((4096,0,4211,4326)),(0,0))
f=B/'guides/day-preliminary-layout-only.png';canvas.save(f)
g=B/'guides/day-regional-layout-only.png';canvas.resize((1254,1254),Image.Resampling.BICUBIC).save(g)
result={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'prepared_after_spring_c08_local_qa_awaiting_root_merge','nextTile':'r08_c09','route':'builtin_image_gen','configuredProduct':'ChatGPT Images 2.5','configuredModelTarget':'gpt-image-2.5-sunburst','configuredQualityTarget':'max','actualBackendModel':None,'actualQualityPreset':None,'separateBilledApiAuthorized':False,'steps':['Root merges spring c08 ledger and confirms latest selected neighbor paths/hashes.','Generate one day regional layout/style reference using prepared guide plus current neighbor context; its native result is a regional reference, not a finished4K tile.','Prepare16 overlapping1254px day guides from that shared regional reference; exact115px west native core constraint,24 identical230px guide overlaps.','Generate16 day detail patches preserving every raw source and actual ordered reference list; assemble and inspect full internal/outer seams and nine crossings.','Prepare spring c09 guides from final day c09 native geometry and current spring c08 west115px core constraint. Generate16 spring detail patches and inspect full shared geometry and seams.'],'coordinates':specs,'layoutSource':str(source),'layoutSourceSha256':sha(source),'layoutSourceSize':list(layout.size),'extendedLayoutSourceBox':box,'guides':[{'file':str(f),'sha256':sha(f),'size':[4326,4326]},{'file':str(g),'sha256':sha(g),'size':[1254,1254]}],'guidesAreUpscaledLayoutOnly':True,'guidePixelsMayEnterFinalArtwork':False,'nativeCallsMade':0,'nativeDetailSources':0,'newCandidateCoordinates':0,'formalAcceptance':False,'runtimePublished':False}
(B/'next-adjacent-plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(B/'next-adjacent-plan.json'))
