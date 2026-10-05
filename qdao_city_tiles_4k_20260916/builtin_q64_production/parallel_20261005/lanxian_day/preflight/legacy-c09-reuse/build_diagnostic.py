from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parent
REPO = next(p for p in OUT.parents if (p / 'config/image-generation.json').exists())
BASE = REPO / 'qdao_city_tiles_4k_20260916/builtin_q64_production'
WEST = BASE / 'lanxian_day/triple_r08_c06_c08/output_v2/r08_c08.png'
PATCH = BASE / 'lanxian_day/r08_c09/native/r01_c01.png'
HANDOFF = OUT.parents[1] / 'handoff.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
west = Image.open(WEST).convert('RGB')
patch = Image.open(PATCH).convert('RGB')
assert west.size == (4096, 4096) and patch.size == (1254, 1254)
assert sha(WEST) == '7e1f9c16f740cf19a9566d6a1efdedf36d1809c0841a2588a49b61f029bb1fa2'
assert sha(PATCH) == '52dd3413b2fa93e930b1c7d8126ea86a2a46eab38aa93b7aebc9b5b151e9917c'
views = []
for start, end, name in [(0, 1024, 'common-edge-y0000-1024.png'), (1024, 1139, 'common-edge-y1024-1139.png'), (0, 1139, 'common-edge-all1139.png')]:
    canvas = Image.new('RGB', (512, end-start))
    boxes = [[3840,start,4096,end],[115,start+115,371,end+115]]
    canvas.paste(west.crop(boxes[0]),(0,0))
    canvas.paste(patch.crop(boxes[1]),(256,0))
    path=OUT/name
    canvas.save(path)
    views.append({'file':str(path),'sha256':sha(path),'pixels':list(canvas.size),'westSourceBoxXYXY':boxes[0],'patchSourceBoxXYXY':boxes[1],'seamCanvasX':256,'resized':False,'blended':False})
a=west.crop((3981,0,4096,1139))
b=patch.crop((0,115,115,1254))
overlap=Image.new('RGB',(230,1139))
overlap.paste(a,(0,0));overlap.paste(b,(115,0))
o=OUT/'same-world-overlap-side-by-side.png';overlap.save(o)
views.append({'file':str(o),'sha256':sha(o),'pixels':list(overlap.size),'westSourceBoxXYXY':[3981,0,4096,1139],'patchSourceBoxXYXY':[0,115,115,1254],'layout':'two alternate drawings of the same 115px world strip, west at x0; legacy patch at x115','resized':False,'blended':False})
aa=np.array(a).astype(np.int16);bb=np.array(b).astype(np.int16)
delta=np.abs(aa-bb)
result={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Legacy c09 r01_c01 west edge against historical c08, only y0:1139. Not current handoff approval.','formalAccepted':False,'wholeTileAccepted':False,'sources':{'west':{'file':str(WEST),'sha256':sha(WEST),'pixels':list(west.size)},'legacyPatch':{'file':str(PATCH),'sha256':sha(PATCH),'pixels':list(patch.size)}},'handoffAtDiagnostic':{'file':str(HANDOFF),'sha256':sha(HANDOFF),'readyForProduction':json.loads(HANDOFF.read_text(encoding='utf-8-sig'))['readyForProduction']},'coordinateConvention':{'c09PatchOriginRelativeToTile':[-115,-115],'coreOriginInPatch':[115,115],'c09CoreGlobalOrigin':[32768,28672]},'images':views,'sameWorldOverlapDiagnostics':{'pixelsEqual':bool(np.array_equal(aa,bb)),'meanAbsoluteErrorRGB':delta.mean(axis=(0,1)).tolist(),'meanSignedPatchMinusWestRGB':(bb-aa).mean(axis=(0,1)).tolist(),'numericMetricsAreNotVisualAcceptance':True},'visualReview':'pending_actual_view'}
(OUT/'diagnostic.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'images':len(views),'diagnostic':str(OUT/'diagnostic.json'),'sourcesHashVerified':True,'sameWorldOverlap':result['sameWorldOverlapDiagnostics']},ensure_ascii=False))
