"""One-shot prepared registered-halo reference, explicitly not output artwork."""
from pathlib import Path
from datetime import datetime,timezone
from io import BytesIO
import hashlib,json
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;P=D.parent;R=P.parents[3]
B=D/'probe-aligned-halo-v2'
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):return {'file':str(p),'sha256':sha(p.read_bytes())}
def dump(p,o):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
def loadim(p):
 raw=p.read_bytes();im=Image.open(BytesIO(raw));im.load();return im.convert('RGB'),rec(p)
B.mkdir(exist_ok=False)
audit=json.loads((D/'audit.json').read_text(encoding='utf-8'))
metrics={}
for name in ['master','plaza','bottom']:
 a=np.asarray(Image.open(D/(name+'-same-global-halo-native-review.png')).convert('L'),dtype=float);rows=[]
 for y in [10,57,100]:
  line=a[max(0,y-4):min(115,y+5)].mean(axis=0);line=np.convolve(line,np.ones(9)/9,mode='same');g=np.gradient(line);picks={}
  for label,l,r,sign in [('flower_to_frame_rise',650,850,1),('ivory_to_slate_fall',920,1120,-1),('slate_to_ivory_rise',1090,1240,1)]:
   x=l+int(np.argmax(g[l:r]*sign));picks[label]={'x':x,'globalX':37773+x,'slope':round(float(g[x]),2)}
  rows.append({'haloY':y,'globalY':32768+y,'features':picks})
 metrics[name]=rows
diff=[]
for m,n in zip(metrics['master'],metrics['bottom']):
 for feature in m['features']:diff.append(abs(m['features'][feature]['x']-n['features'][feature]['x']))
observation={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'static same-global halo only','sources':audit['comparisonImages'],'viewed':[audit['stackedComparison'],audit['contactComparison']],
 'method':'Review images at original analysis size; supporting 9-row mean luma profiles smoothed with a9px box kernel, strongest signed gradient within three declared structural-edge windows. This samples only three major edges; it is not full image registration or art acceptance.',
 'supportingEdgeSamples':metrics,'masterBottomSampleAbsShiftPixels':diff,'maxSampleShift':max(diff),
 'visualObservation':'Primary curved bands correspond; observed edge offsets 1..12 native pixels are consistent with different low-resolution outlines and rounded native bevels. Floral relief detail is not geometrically established from the blurred master and remains an explicit output-continuity risk.',
 'decision':'one_registered_halo_native_probe_allowed_under_root_bounded_instruction',
 'notAnAcceptance':True,'wholeTileReady':False,'navigationAccepted':False,'generationCallsSoFar':0}
dump(B/'static-layout-observation.json',observation)
master,mrec=loadim(P/'guides/r04_c02.master-layout-only.png')
halo,hrec=loadim(D/'bottom-same-global-halo-native-review.png')
assert master.size==(1254,1254) and halo.size==(1254,115)
canvas=master.copy();canvas.paste(halo,(0,1139))
assert canvas.crop((0,0,1254,1139)).tobytes()==master.crop((0,0,1254,1139)).tobytes()
assert canvas.crop((0,1139,1254,1254)).tobytes()==halo.tobytes()
guide=B/'registered-reference-only.png'
with guide.open('xb') as f:canvas.save(f,format='PNG')
dump(B/'registered-reference-only.derived.json',{'output':rec(guide),'pixels':[1254,1254],'sources':[mrec,hrec,audit['selectedBottom']],
 'operation':'Keep original master guide rows0:1139 exactly, paste exact current-bottom native source box[909,0,2163,115] at target[0,1139,1254,1254], no resizing, no blending or stroke.',
 'globalPatchLTRB':audit['nativePatchGlobalLTRB'],'knownHaloGlobalLTRB':audit['sharedHaloGlobalLTRB'],
 'coreChangedFromMasterReference':False,'neighborPixelsInsertedAbove1139':0,
 'topReferenceBytesSha256':sha(master.crop((0,0,1254,1139)).tobytes()),'bottomReferenceBytesSha256':sha(halo.tobytes()),
 'role':'generation_geometry_reference_only_not_candidate','referenceBoundaryIsNotStoneSeam':True,'mayEnterFinalArtwork':False})
refs=[{'index':1,**rec(guide),'role':'registered original-master geometry plus exact bottom115 neighbor halo; reference only'},
 {'index':2,**rec(P/'references/clean-stone-native768.png'),'role':'clean native stone material only'},
 {'index':3,**rec(R/'designs/gameplay-ui/04-guild.png'),'role':'primary confirmed project drawing style'},
 {'index':4,**rec(P/'references/r04_c02.bottom-neighbor-native-context.png'),'role':'bottom context only; top115 align target bottom115, rest never copied'}]
configraw=(R/'config/image-generation.json').read_bytes();assert configraw==(P/'config-snapshot.json').read_bytes()
(B/'config-snapshot.json').write_bytes(configraw)
prompt='''Use case: precise-object-edit.
Create ONE opaque square native 1254 x 1254 terrain painting for tile r08_c10 patch r04_c02. Produce new native detail; this is a geometry-control reference, never a final upscaled source.

IMAGE 1 is the exact registered target canvas. From y=0 through y=1138 it is the original-city layout: keep the three gray inset panels at the top, broad central ivory paving slab, curved framing bands, and floral relief in the lower left at their existing positions and scale. Its bottom 115 rows (y=1139..1254) are the exact current lower-neighbor scene at the SAME world coordinates. That band was deliberately registered to provide native contours/material where both regions overlap. The two source resolutions/finishes differ. Repaint the canvas as one continuous native scene, not a collage. Preserve the real floral outlines and gray/ivory band crossings shown in the registered lower band and continue them smoothly upward into the corresponding master shapes. Keep macro geometry; only reconcile local outline/bevel/relief detail.

CRITICAL: y=1139 is an invisible tile-coordinate boundary, NOT a real horizontal joint, border, step, highlight or shadow. Do not draw any horizontal line or material stripe to explain the change in reference sharpness there. Never shift the neighboring band upward to y=1024. The only confirmed lower-neighbor area is precisely the bottom115 rows, and the rest of the target is newly painted master-based terrain. Match the lower band's actual slate-gray values and floral contact contours, not merely its palette. No sudden cutoff of petals at the coordinate boundary.

IMAGE 2 is only clean native surface-rendering guidance: calm smooth warm ivory, broad soft shading, restrained rounded bevels, crisp clean joints. Do not copy its composition, gold inlays, slab arrangement or ornaments.
IMAGE 3 is the primary confirmed project painting/finish reference: bright, clean, rounded, full-bodied Daoist Q/chibi hand-painted polish. Do not import UI, text, characters or props.
IMAGE 4 is a separate1254 x 512 original-pixel strip of the current lower neighbor for contextual understanding. ONLY its TOP115 rows correspond to IMAGE1's BOTTOM115 rows; the rest is below this output. Never squeeze the entire strip into the target, never copy its full composition, and never replace the top/center gray panels with its flowers or diagonal bands.

Keep image1 framing, scale and open paving layout. Algorithm x/y=115,1024,1139 are not stone divisions. No new road, building, entrance, stair, ornaments, vegetation, object, text, watermark, grid or border. Keep stone faces smooth and quiet: no flakes, cloudy blotches, marble veins, cracks, speckles, grain, white frosting, thick halos, plastic shine or blur. Output exactly one native1254 x1254 image, entirely newly rendered detail, and maintain continuous shapes and material across the invisible y1139 boundary.'''
request={'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs]}
dump(B/'actual-request.json',request);(B/'actual-prompt.txt').write_text(prompt+'\n',encoding='utf-8')
preflight={'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin_host_managed','maximumCalls':1,
 'clockToolEvidence':{'current_time':'2026-09-23 13:28:58 UTC','source':'actual clock__curr_time return'},
 'capabilityObserved':{'submittedFields':['prompt','referenced_image_paths'],'modelParameterAvailable':False,'qualityParameterAvailable':False,'sizeParameterAvailable':False},
 'configSnapshot':json.loads(configraw),'configFile':rec(B/'config-snapshot.json'),'actualRequest':rec(B/'actual-request.json'),'prompt':rec(B/'actual-prompt.txt'),'references':refs,
 'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host builtin selectors and response backend metadata not provided.',
 'staticReview':rec(B/'static-layout-observation.json'),'registeredGuideRecord':rec(B/'registered-reference-only.derived.json'),
 'requestedNativePixels':[1254,1254],'nativeCoreCropLTRB':[115,115,1139,1139],'outputMayUseReferencePixels':False,
 'wholeTileReady':False,'formalArtAcceptancePassed':False,'navigationChanged':False,'sharedJSONWritten':False}
dump(B/'preflight.json',preflight)
print(json.dumps({'probeDirectory':str(B),'maxStaticEdgeOffsetPixels':max(diff),'guide':rec(guide),'onlyHaloY':[1139,1254],'references':refs},ensure_ascii=False,indent=2))
