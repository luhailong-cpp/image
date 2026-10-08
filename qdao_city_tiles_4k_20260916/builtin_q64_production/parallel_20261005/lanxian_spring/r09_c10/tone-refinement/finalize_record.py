from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent; T=O.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=json.loads((O/'processing.json').read_text()); q=json.loads((O/'qa/scope-and-metrics.json').read_text())
a=np.array(Image.open(T/'selected/extended4326.png')); b=np.array(Image.open(O/'extended4326.png'))
f=np.load(O/'additive-rgb-field4326.npz')['field']; delta=np.load(O/'actual-rgb-delta4326.npz')['delta']
allowed=np.array(Image.open(O/'allowed-support4326.png'))>0; changed=np.array(Image.open(O/'changed-mask4326.png'))>0
assert np.array_equal(np.clip(np.rint(a.astype(np.float32)+f),0,255).astype(np.uint8),b)
assert np.array_equal(delta.astype(np.int16),b.astype(np.int16)-a.astype(np.int16))
assert np.array_equal(changed,np.any(delta!=0,axis=2))
assert np.array_equal(a[~allowed],b[~allowed])
assert np.array_equal(a[:179],b[:179])
assert np.array_equal(b[115:4211,115:4211],np.array(Image.open(O/'core4096.png')))
for name,h in p['source'].items(): assert sha(T/'selected'/name)==h
viewed=['preview1254.png']+[f'qa/{axis}-{s}-{kind}-1to1.png' for axis in ['vertical','horizontal'] for s in [1024,2048,3072] for kind in ['seam','returns']]+[f'qa/{k}-after.png' for k in ['bridge-cross','water-v3072','bridge-h3072','bridge-v3072']]+[f'qa/north-{i}-after.png' for i in range(1,5)]+['qa/red-post-y1024-unchanged.png','qa/foliage-y3072-detail.png']
record={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewMethod':'Actual tool-rendered pixels; full4096 overview downsample1254 for composition, all six full4326 seam lengths and all12return boundaries as native1:1 strip atlases, selected512/768 bridge-water closeups and joined north border. No magnification represented as native generation.','reviewedImages':[{'file':x,'sha256':sha(O/x)} for x in viewed],'decision':'Recommend this candidate for bridge/water/internal tone refinement; parent chooses published selected path. No claim that all inherited geometry or all native red seams were redrawn.','visualFindings':{'bridge':'Gray-stone vertical/horizontal rectangular tone steps substantially reduced; contours, carvings, arches, stone courses and existing texture retained.','water':'x3072/y3072 color steps reduced without moving reflections or waterline. No pink patches or blur observed.','pavingAndFoliage':'Existing paving and leaf structure retained; estimated biases separated by material.','returnEdges':'All12normal320px fade returns reviewed at1:1; no new rectangular cutoff observed.','north':'Four adjacent1024px segments actually viewed. Full115halo plus first64core rows byte exact; neighbor selected-v2 overlap metrics unchanged.','seasonalEntities':'Original seasonal cap masks excluded and byte exact. Saturated red/gold surfaces also excluded from correction.'},'unresolvedInheritedGeometryOrExcludedSeams':[{'coreInspectBoxLTRB':[900,964,1120,1084],'feature':'Upper red lamp shaft crossing core y1024, near x1084 right silhouette','observation':'Small horizontal red tone step and apparent1–3pixel outline kink inherited from native day assembly. Red surface is excluded and unchanged.','status':'Not hidden or repaired by tone correction. A dedicated local surface/outline repair is required if this isolated seam must be removed; not a bridge or water contour mismatch.','qaFile':'qa/red-post-y1024-unchanged.png'}],'exactVerification':{'sourceHashesUnchanged':True,'savedFloatFieldReconstructsFinalExactly':True,'savedInt8DeltaReconstructsFinalExactly':True,'changedMaskEqualsActualChangedPixels':True,'outsideAllowedSupportByteExact':True,'northHaloAnd64CoreRowsByteExact':True,'coreExactCenterOfExtended':True,'geometryWarp':None,'imageBlur':False,'productionResampling':None,'upscale':False,'cumulativeActualRGBMaxAbs':np.max(np.abs(delta.astype(np.int16)),axis=(0,1)).tolist()},'outerStrips':q['outerStrips'],'northBoundary':q['northBoundary'],'seamMetrics':q['seamMetrics'],'formalAccepted':False,'clientValidated':False}
write(O/'qa/final-review.json',record)
p['visualQA']={'record':'qa/final-review.json','status':'reviewed_recommend_tone_candidate_with_separate_inherited_red_note'}
write(O/'processing.json',p)
index=[]
for imfile in sorted(O.rglob('*.png')):
 rel=imfile.relative_to(O).as_posix()
 if rel=='extended4326.png' or 'mask' in rel or 'labels' in rel or 'support' in rel:
  refs=[{'file':str(T/'selected/extended4326.png'),'sha256':p['source']['extended4326.png'],'generationRecord':str(T/'selected/extended4326.png.generation.json')}]
 elif rel.endswith('before.png'):
  refs=[{'file':str(T/'selected/core4096.png'),'sha256':p['source']['core4096.png']}]
 else:
  refs=[{'file':str(O/'extended4326.png'),'sha256':sha(O/'extended4326.png')}]
 if rel.startswith('qa/north-'):
  north=T.parent/'r08_c10/selected-v2/core4096.png';refs.append({'file':str(north),'sha256':sha(north)})
 with Image.open(imfile) as im:size=list(im.size);mode=im.mode
 index.append({'file':rel,'sha256':sha(imfile),'pixels':size,'mode':mode,'newAIGeneration':False,'derivedFrom':refs,'operation':'technical mask or QA crop/atlas; see scripts and qa/scope-and-metrics.json' if ('mask' in rel or 'labels' in rel or rel.startswith('qa/')) else ('preview-only LANCZOS downsample' if 'preview' in rel else 'bounded same-coordinate RGB field'),'sourceModelEvidence':'Inherited model records through selected/extended4326.png.generation.json; no new AI call.'})
write(O/'derived-image-index.json',{'createdAtUtc':record['reviewedAtUtc'],'images':index})
print(json.dumps({'coreSha256':sha(O/'core4096.png'),'extendedSha256':sha(O/'extended4326.png'),'review':str(O/'qa/final-review.json'),'allExactChecksPassed':True},indent=2))
