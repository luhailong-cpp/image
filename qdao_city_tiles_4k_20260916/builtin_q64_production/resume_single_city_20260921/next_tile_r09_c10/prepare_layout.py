"""Reference-only geometry preparation. No output is delivery artwork."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image

P=Path(__file__).resolve().parent
R=P.parents[2]
C=R/'builtin_q64_production'/'tianyong_festival'
V=C/'upperpair_r09_c07_c08_row10_c07_c10_20260918'/'output_v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name in ('references','guides','native','prompts','qa','output'): (P/name).mkdir(exist_ok=True)
source=R/'builtin_4x4'/'output'/'tianyong_plaza_4k_candidate_v3b.png'
box=[2794.4375,2026.4375,3605.5625,2837.5625]
canvas=Image.open(source).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC,box=box)
bottom=V/'row10-extended-context.png'
bottom_box=[12288,0,16614,230]
assert Image.open(bottom).size[0]>=bottom_box[2]
canvas.paste(Image.open(bottom).convert('RGB').crop(bottom_box),(0,4096))
canvas.save(P/'references'/'layout-with-bottom-constraint.png')
canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(P/'references'/'layout-input.jpg',quality=95)
for src,name in ((source,'source-overview.jpg'),(V/'r10_c10.png','bottom-style-input.jpg'),(C/'r09_c09'/'style-reference.png','left-style-reference.jpg')):
 im=Image.open(src).convert('RGB');im.thumbnail((1254,1254),Image.Resampling.LANCZOS);im.save(P/'references'/name,quality=95)
record={
 'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'role':'Reference-only layout and neighboring geometry. Every raster in references is excluded from final native detail counts.',
 'layoutSource':str(source),'layoutSourceSha256':sha(source),'layoutSourceBoxLTRB':box,
 'nextTile':'r09_c10','guideResized':True,'guidePixels':[1254,1254],
 'globalPixelRectXYWH':[36864,32768,4096,4096],
 'worldRect':{'x':218.75,'z':131.25,'width':18.75,'height':18.75},
 'sourceArtUpscaledForFinal':False,
 'neighborConstraints':[{'edge':'bottom','source':str(bottom),'sha256':sha(bottom),'sourceBoxLTRB':bottom_box,'pasteXY':[0,4096]}],
 'pendingNeighborConstraint':{'edge':'left','tile':'r09_c09','reason':'No selected assembled extended context exists yet. Requires final bottom-left corner agreement before stitching.'},
 'leftReferenceStatus':'r09_c09 style-reference is layout/style only and is not an accepted or selected native assembled candidate.'
}
(P/'layout-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
plan={'schemaVersion':2,'status':'layout_prepared_left_neighbor_pending','route':'builtin_image_gen','requestedModel':'gpt-image-2.5-sunburst','requestedQuality':'max','backendModelVerified':False,'actualModel':None,'actualQuality':None,'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'wholeCityPixels':[65536,65536],'wholeCityGrid':{'rows':16,'columns':16},'deliveryTilePixels':[4096,4096],'tile':{'row':9,'column':10,'worldRect':record['worldRect']},'nativeGrid':{'rows':4,'columns':4},'core':1024,'halo':115,'adjacentOverlap':230,'assembledBeforeOuterCrop':[4326,4326],'samplePixelRectInWholeCity':[36864,32768,40960,36864],'patches':[],'finalArtUpscaled':False,'accepted':False,'runtimePublished':False}
(P/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(json.dumps({'directory':str(P),'layoutSha256':sha(source),'bottomConstraintSha256':sha(bottom),'status':plan['status']},indent=2))
