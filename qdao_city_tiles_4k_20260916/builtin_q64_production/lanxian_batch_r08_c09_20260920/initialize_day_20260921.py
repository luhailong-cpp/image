from pathlib import Path
import json,hashlib
from PIL import Image
P=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production');B=P/'lanxian_batch_r08_c09_20260920';D=P/'lanxian_day/r08_c09'
assert not D.exists();D.mkdir()
for n in ['guides','prompts','native','regional-reference','output','qa']:(D/n).mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
entry=next(t for t in j(P.parent/'q64_production_plans/lanxian_day.json')['tiles'] if t['id']=='r08_c09')
neighbor=P/'lanxian_day/triple_r08_c06_c08/output_v2/r08_c08.extended.png'
preview=D/'regional-reference/west-c08-context-preview.png';Image.open(neighbor).convert('RGB').resize((1254,1254),Image.Resampling.LANCZOS).save(preview)
plan={'schemaVersion':1,'status':'regional_geometry_calibration_in_progress','route':'builtin_image_gen','configuredProduct':'ChatGPT Images 2.5','configuredModelTarget':'gpt-image-2.5-sunburst','configuredQualityTarget':'max','actualBackendModel':None,'actualQualityPreset':None,'backendModelVerified':False,'wholeCityPixels':[65536,65536],'wholeCityGrid':{'rows':16,'columns':16},'deliveryTilePixels':[4096,4096],'worldRect':{'x':50,'z':0,'width':300,'height':300},'sampleTile':{'id':'r08_c09','row':8,'column':9,'worldRect':entry['worldRect']},'samplePixelRectInWholeCity':[32768,28672,36864,32768],'nativeGrid':{'rows':4,'columns':4},'core':1024,'halo':115,'assembledBeforeOuterCrop':[4326,4326],'patches':[],'guidePreparation':{'status':'pending_regional_geometry_acceptance','guideOnly':True},'leftNeighborBoundary':{'tile':'r08_c08','file':str(neighbor),'sha256':sha(neighbor),'coreConstraintPixels':115,'sourceXYXY':[4096,0,4211,4326]},'regionalInputs':[{'path':str(B/'guides/day-regional-layout-only.png'),'sha256':sha(B/'guides/day-regional-layout-only.png'),'role':'provisional_target_layout_crop_with_crisp_left33px_geometry_constraint'},{'path':str(preview),'sha256':sha(preview),'role':'exact_selected_west_neighbor_at_preview_scale_style_and_curve_continuation_authority'}],'formalTileAcceptance':False,'runtimePublished':False,'finalArtUpscaled':False}
(D/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(D))
