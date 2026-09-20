from pathlib import Path
from PIL import Image
import json, hashlib
import numpy as np
from datetime import datetime, timezone
R=Path(__file__).resolve().parents[2]; C=Path(__file__).resolve().parent; P=C/'r09_c09'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not P.exists(), 'Never overwrite an existing tile workspace'
selected=json.loads((R/'builtin_q64_production/current-batch.json').read_text(encoding='utf-8-sig'))
assert not any(e['appearance']=='tianyong_festival' and e['tile']=='r09_c09' for e in selected['candidates'])
source=R/'builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png'
V=C/'upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5'
left=V/'quad-extended-context.png'; bottom=V/'row10-extended-context.png'
box=[2026.4375,2026.4375,2837.5625,2837.5625]
canvas=Image.open(source).convert('RGB').resize((4326,4326),Image.Resampling.BICUBIC,box=box)
left_cut=Image.open(left).convert('RGB').crop((8192,0,8422,4326))
bottom_cut=Image.open(bottom).convert('RGB').crop((8192,0,12518,230))
assert np.array_equal(np.array(left_cut)[-230:],np.array(bottom_cut)[:,:230]), 'Neighbor corner disagreement'
canvas.paste(left_cut,(0,0));canvas.paste(bottom_cut,(0,4096))
for n in ('native','guides','prompts','output','qa'): (P/n).mkdir(parents=True,exist_ok=True)
canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(P/'layout-input.jpg',quality=92)
Image.open(V/'r09_c08.png').convert('RGB').resize((1254,1254),Image.Resampling.LANCZOS).save(P/'left-style-input.jpg',quality=92)
Image.open(V/'r10_c09.png').convert('RGB').resize((1254,1254),Image.Resampling.LANCZOS).save(P/'bottom-style-input.jpg',quality=92)
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'role':'reference-only layout and neighboring geometry; not delivery artwork','layoutSource':str(source),'layoutSourceSha256':sha(source),'layoutSourceBoxLTRB':box,'nextTile':'r09_c09','guideResized':True,'guidePixels':[1254,1254],'globalPixelRectXYWH':[32768,32768,4096,4096],'worldRect':{'x':200,'z':131.25,'width':18.75,'height':18.75},'cornerOverlapPixelsIdentical':True,'neighborConstraints':[{'edge':'left','source':str(left),'sha256':sha(left),'sourceBoxLTRB':[8192,0,8422,4326],'pasteXY':[0,0]},{'edge':'bottom','source':str(bottom),'sha256':sha(bottom),'sourceBoxLTRB':[8192,0,12518,230],'pasteXY':[0,4096]}],'sourceArtUpscaledForFinal':False}
(P/'layout-record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
plan={'schemaVersion':2,'status':'layout_ready_unified_reference_pending','route':'builtin_image_gen','requestedModel':'gpt-image-2.5-sunburst','requestedQuality':'max','backendModelVerified':False,'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'wholeCityPixels':[65536,65536],'wholeCityGrid':{'rows':16,'columns':16},'deliveryTilePixels':[4096,4096],'sampleTile':{'row':9,'column':9,'worldRect':record['worldRect']},'nativeGrid':{'rows':4,'columns':4},'core':1024,'halo':115,'adjacentOverlap':230,'assembledBeforeOuterCrop':[4326,4326],'samplePixelRectInWholeCity':[32768,32768,36864,36864],'styleReference':'style-reference.png','patches':[],'finalArtUpscaled':False}
(P/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
print(str(P))
