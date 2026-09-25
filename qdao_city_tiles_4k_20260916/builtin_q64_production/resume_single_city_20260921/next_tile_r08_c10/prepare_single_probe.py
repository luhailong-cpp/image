"""Prepare exactly one authorized native probe; this script does not generate."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
from io import BytesIO
import hashlib,json

P=Path(__file__).resolve().parent
R=P.parents[3]
B=P/'probe-r04_c02-20260923T125732Z'
def sha(raw): return hashlib.sha256(raw).hexdigest()
def dump(p,o):
    with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
def rec(p): return {'file':str(p),'sha256':sha(p.read_bytes())}
B.mkdir(exist_ok=False)
plan=json.loads((P/'plan.json').read_text(encoding='utf-8'))
refs=[]
for row in plan['draftInputs']:
    p=Path(row['file']);raw=p.read_bytes();assert sha(raw)==row['sha256'],str(p)
    im=Image.open(BytesIO(raw));im.load()
    refs.append(dict(row,pixels=list(im.size),verifiedAtUtc=datetime.now(timezone.utc).isoformat()))
configraw=(R/'config/image-generation.json').read_bytes()
assert configraw==(P/'config-snapshot.json').read_bytes(),'Batch config changed; inspect before call'
(B/'config-snapshot.json').write_bytes(configraw)
observation={
  'recordedAtUtc':datetime.now(timezone.utc).isoformat(),
  'source':'root agent direct task message, recorded by checkpoint_merge',
  'reviewer':'root',
  'reviewedFiles':[rec(P/'guides/r04_c02.master-layout-only.png'),rec(P/'guides/r04_c02.plaza-layout-review-only.png'),rec(P/'references/r04_c02.bottom-neighbor-native-context.png')],
  'observation':'Root actually compared these three inputs: primary inset-panel and curved-frame structure corresponds; differences concentrate in surface texture, bevel and relief. This single patch is paving, with no road/building/entrance boundary visible.',
  'authorization':'one builtin native probe only, original-master geometry first and selected bottom neighbor separate',
  'scope':'r08_c10 patch r04_c02 only',
  'wholeTileReady':False,'wholeCityGeometryAccepted':False,'navigationAccepted':False,'formalArtAccepted':False,
  'leftNeighbor':'provisional under repair, not a fixed edge'
}
dump(B/'root-layout-observation.json',observation)
prompt='''Use case: precise-object-edit.
Asset: ONE native 1254 x 1254 pixel opaque terrain detail patch, r04_c02 inside city tile r08_c10, for a bright clean rounded Daoist Q/chibi game map.

IMAGE 1 is the exact original-city geometry target. Preserve its camera, crop, relative scale, three gray inset panels across the top, broad warm ivory panel through the middle, curved framing bands and the partial floral relief entering at lower left. The guide is enlarged solely to specify existing shapes. Newly paint all detail at native pixel clarity; do not enlarge, sharpen or reproduce the blurry guide pixels. Keep every structural boundary at its existing location. The result must have IMAGE 1 composition, not the composition of any other reference.

IMAGE 2 is only the original-pixel clean material example: smooth quiet warm ivory surfaces, crisp restrained rounded bevels, broad subtle shading and sparse clean joints. Borrow the clean drawing finish only. Do not copy its slab layout, gold lines, stair-like forms or ornaments.
IMAGE 3 is the primary user-confirmed project painting-style reference: bright, clean, rounded, full-bodied Daoist Q hand-painted polish. Do not import any UI, text, props or people.
IMAGE 4 is a SEPARATE 1254 x 512 pixel original-pixel bottom-neighbor context. Only its TOP 115 rows describe the already-existing continuation corresponding to the BOTTOM 115 rows of the output (target y=1139..1254). Keep x coordinates aligned. Use those rows to guide the existing floral/curved-band continuation and ivory/slate material. The remaining 397 rows are context only and must NEVER be compressed, expanded, copied or re-composed into the output. In particular, do not replace the center/top of IMAGE 1 with IMAGE 4's flowers or diagonal bands. Do not create a step, new horizontal seam, stripe, pasted border or sudden color jump at y=1139.

The target guide contains no pasted neighbor rectangles or grid. Reference edges and algorithm coordinates x/y=115,1024,1139 are NOT stone joints. Never explain a sampling boundary or color patch by inventing a straight horizontal or vertical groove. Preserve real joints already present in IMAGE 1 and make the ground continuous across the crop.

Keep stone faces calm, smooth and clean with restrained broad tonal transitions; soft sculpted depth, crisp native bevels, no glossy plastic. No flakes, cloudy blotches, mottles, marble veins, cracks, speckles, white frosting, gritty grain, noise, blur or thick halos. No new road, building, entrance, stair, ornament, vegetation, object, lettering, UI, watermark or border. Keep open paving open. Output exactly one square 1254 x 1254 image with IMAGE 1 framing.'''
request={'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs]}
dump(B/'actual-request.json',request)
(B/'actual-prompt.txt').write_text(prompt+'\n',encoding='utf-8')
preflight={
  'schemaVersion':1,'preparedAtUtc':datetime.now(timezone.utc).isoformat(),
  'clockToolEvidence':{'current_time':'2026-09-23 12:57:32 UTC','source':'clock__curr_time actual tool return'},
  'tile':'r08_c10','patch':'r04_c02','allowedBuiltinCallCount':1,
  'tool':'image_gen.imagegen','route':'builtin_host_managed',
  'capabilityObserved':{'callableName':'image_gen__imagegen','acceptedFields':['prompt','referenced_image_paths','num_last_images_to_include'],'submittedFields':['prompt','referenced_image_paths'],'modelParameterAvailable':False,'qualityParameterAvailable':False,'sizeParameterAvailable':False},
  'configSnapshot':json.loads(configraw),'configFile':rec(B/'config-snapshot.json'),
  'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,
  'unverifiedReason':'Host-managed builtin entry exposes no model or quality selector; configuration and prompt are not backend evidence.',
  'request':rec(B/'actual-request.json'),'prompt':rec(B/'actual-prompt.txt'),'references':refs,
  'rootLayoutObservation':rec(B/'root-layout-observation.json'),
  'requestedNativePixels':[1254,1254],'expectedCoreCropLTRB':[115,115,1139,1139],
  'sharedJSONWritten':False,'wholeTileReady':False,'formalArtAccepted':False,'clientRuntimeAccepted':False
}
dump(B/'preflight.json',preflight)
print(str(B))
