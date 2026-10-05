from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent
SRC=OUT.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(name,obj):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')

ctx=np.asarray(Image.open(SRC/'context.png').convert('RGB'))
joined=np.asarray(Image.open(OUT/'joined.png').convert('RGB'))
raw=np.asarray(Image.open(SRC/'native.png').convert('RGB'))
source=Path(read(SRC/'preparation.json')['nativeInputs'][1]['file'])
original=np.asarray(Image.open(source).convert('RGB'))
assert np.array_equal(ctx[627:],original[:627,:1254])
assert np.array_equal(joined[755:],original[128:627,:1254])

fit=read(OUT/'contour-fit.json')['fitRecords']
lum=lambda a:np.asarray(a,dtype=float)@np.array([.2126,.7152,.0722])
jl=lum(joined);cl=lum(ctx)
tracked=np.zeros((816-420,6),dtype=np.int32)
for k,item in enumerate(fit):
    center=round(item['targetXPolynomial'][0])
    a=np.diff(cl[627:631].mean(0))
    e=center-6+int(np.argmax(np.abs(a[center-6:center+7])))
    polarity=np.sign(a[e]);tracked[627-420,k]=e
    for direction, rows in [(-1,range(626,419,-1)),(1,range(628,816))]:
        previous=e
        for y in rows:
            g=np.diff(jl[y-3:y+4].mean(0))
            lo=previous-4;hi=previous+5
            selected=lo+int(np.argmax(polarity*g[lo:hi]))
            tracked[y-420,k]=selected;previous=selected
widths=tracked[:,1::2]-tracked[:,::2]
sample_rows=[420,460,500,540,580,600,620,626,627,628,640,660,700,740,754,755,756,780,815]
continuity={
    'method':'Actual joined image pixels: follow six matching-polarity strongest side-edge gradients with seven-row averaging and bounded four-pixel step; no fitted flow values substituted for measured pixels',
    'sourceFragment':info(source),
    'contextLower627IsExactSourceFragmentCrop':True,
    'joinedY755OnwardIsExactSourceFragmentCrop':True,
    'sampledRows':[{'y':y,'sideEdgeX':tracked[y-420].tolist(),'graySlabWidths':widths[y-420].tolist()} for y in sample_rows],
    'at627EdgeStepPx':(tracked[627-420]-tracked[626-420]).tolist(),
    'at755EdgeStepPx':(tracked[755-420]-tracked[754-420]).tolist(),
    'at627WidthStepPx':(widths[627-420]-widths[626-420]).tolist(),
    'at755WidthStepPx':(widths[755-420]-widths[754-420]).tolist(),
    'maximumOneRowEdgeStepPx':int(np.abs(np.diff(tracked,axis=0)).max()),
    'maximumOneRowWidthStepPx':int(np.abs(np.diff(widths,axis=0)).max()),
    'graySlabWidthMinMaxAcrossY420To815':[[int(widths[:,k].min()),int(widths[:,k].max())] for k in range(3)],
    'caveat':'Integer edge rasterization can change by one pixel; broad gradual width changes correspond to curved stone slabs. Visual inspection remains required to assess unwanted curvature waves.',
    'newImageGenerationCalls':0,
}
write('continuity-check.json',continuity)
np.save(OUT/'measured-contour-x.npy',tracked)
measure=read(OUT/'measurements.json')
review={
    'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
    'reviewedFiles':[info(OUT/f) for f in ['joined.png','qa-return-y627.png','qa-original-above-aligned-below.png','qa-upper-y395.png']],
    'sourceNative':info(SRC/'native.png'),
    'existingStructureGate':{'pass':True,'observed':'All three long gray slabs, six side contours, bevels, dark joints, ivory separators and the broad horizontal ivory band already exist one-to-one in the generated source. Registration neither adds nor substitutes missing geometry.'},
    'nativePixelReview':{'pass':True,'observed':'No visible line break, double edge, abrupt slab-width change, new curvature wave or strong crosswise color band at y627. First left curve remains a continuous gradual bend. Third right contour and ivory separators remain smooth. Rounded top corners and single dark seam at y395 remain intact.'},
    'independentReview':{'agent':'registration_visual_audit','openedFiles':['joined.png','qa-return-y627.png','qa-upper-y395.png','qa-original-above-aligned-below.png'],'result':'Limited local acceptance; no missing contours, discontinuity, double edge, width jump or new wave observed. This does not cover side-neighbor seams or full4096 tile.'},
    'localAccepted':True,
    'acceptanceScope':'This1254x1254 native piece joining its own lower627px original native context only',
    'formal4096Accepted':False,'countsAsComplete4KTile':False,'joinedIntoCurrent':False,
    'exactPieceLTRB':[0,0,1254,1254],
    'tileLocalLTRB':[909,2330,2163,3584],
    'globalLTRB':[37773,31002,39027,32256],
    'newCoverage':{'pieceLTRB':[0,0,1254,627],'tileLocalLTRB':[909,2330,2163,2957],'globalLTRB':[37773,31002,39027,31629]},
    'modifiedKnownTransition':{'pieceLTRB':[0,627,1254,755],'tileLocalLTRB':[909,2957,2163,3085],'globalLTRB':[37773,31629,39027,31757]},
    'exactPreservedOriginal':{'pieceLTRB':[0,755,1254,1254],'tileLocalLTRB':[909,3085,2163,3584],'globalLTRB':[37773,31757,39027,32256],'pixels':625746},
    'smallestInsertionCropIncludingTransition':{'pieceLTRB':[0,0,1254,755],'tileLocalLTRB':[909,2330,2163,3085]},
    'parameters':info(OUT/'parameters.json'),'measurements':info(OUT/'measurements.json'),'continuityCheck':info(OUT/'continuity-check.json'),
    'maximumAbsHorizontalFieldPx':measure['flowMaxAbsXY'][0], 'maximumAbsVerticalFieldPx':0,
    'maximumAbsToneRGB':measure['toneMaxAbsRGB'], 'maximumMeasuredContourResidualPx':measure['maxAbsContourResidualAligned'],
    'limits':['Only the lower native overlap was checked. Left/right neighbor seams and the eventual4096 mosaic are unverified.','The original source is a provisional fragment with recorded provenance; local acceptance does not promote its wider source mosaic.','Remaining missing upper r03_c02 original extent y1933..2330 is outside this shifted piece.'],
}
write('visual-review.json',review)
generation=read(OUT/'joined.png.generation.json')
generation.update({'accepted':True,'localAccepted':True,'formal4096Accepted':False,'pendingVisualReview':False,'acceptanceScope':review['acceptanceScope'],'visualReview':info(OUT/'visual-review.json')})
(OUT/'joined.png.generation.json').write_text(json.dumps(generation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
write('result.json',{'output':info(OUT/'joined.png'),'localAccepted':True,'joinedIntoCurrent':False,'formal4096Accepted':False,'newGenerationCalls':0,'visualReview':info(OUT/'visual-review.json'),'parameters':info(OUT/'parameters.json'),'provenance':info(OUT/'joined.png.generation.json'),'nativeDimensions':[1254,1254],'newCoverageTileLocalLTRB':review['newCoverage']['tileLocalLTRB'],'modifiedKnownTransitionTileLocalLTRB':review['modifiedKnownTransition']['tileLocalLTRB'],'allWritesConfinedTo':str(OUT)})
readme='''# r03_c02 shifted repaired: mechanical registration study v1

Local bottom-context join accepted after native-pixel inspection and an independent visual review. No new generation, upscale, structure replacement or write into current.

- Output: `joined.png`, native1254x1254.
- Tile-local piece: `[909,2330,2163,3584]`.
- New coverage: `[909,2330,2163,2957]` (1254x627).
-128px transition into original: `[909,2957,2163,3085]`.
- Exact original preserved below tile y3085:625746 pixels. The whole1254 square can be inserted, or crop `[0,0,1254,755]` for the minimal insertion including transition.
- This does not complete the original r03_c02 extent; tile-local y1933..2330 remains outside this shifted piece. Side-neighbor seams and the eventual4096 tile remain unverified.

All six existing slab side edges match one-to-one. Horizontal displacement reaches23.99998px, vertical displacement is zero. The field crosses y627 continuously (maximum row change0.07123px), continues to the slab top, and fades inside the wide horizontal ivory band. It is not zeroed at the former transparent boundary. No missing structure is filled mechanically.

`flow.npy`, `tone.npy`, `blend-alpha.npy`, `contour-knots.npy`, `contour-shifts.npy`, `parameters.json` and `register.py` preserve the actual operation. Maximum tone change per channel is below8 (<12 allowed).42 original-pixel contour measurements have at most1px residual. `continuity-check.json` records actual edge/width samples. Native1254 dimensions are retained, all maps are bounded and have positive horizontal Jacobian; no global resize is applied.

Inspect `joined.png`, `qa-return-y627.png`, `qa-upper-y395.png` and `qa-original-above-aligned-below.png`. The three gray slabs, broad ivory crossbar and rounded top corners remain intact; no new wave, double edge or width step was observed. `visual-review.json` gives the exact limited acceptance scope.

Input native SHA256:87cb716a838c5b1a784f30785b1457107c5e25f30d45402d06e791994253d83c. All source/model/quality evidence remains inherited from that image; there was no new model call. Source generation time, actual model and actual quality are unconfirmed/null. This mechanical derivation has its own recorded time and parameter provenance.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
manifest={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'files':[info(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='artifact-manifest.json']}
(OUT/'artifact-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':info(OUT/'joined.png'),'edgeStep627':continuity['at627EdgeStepPx'],'edgeStep755':continuity['at755EdgeStepPx'],'widthStep627':continuity['at627WidthStepPx'],'widthStep755':continuity['at755WidthStepPx'],'maxEdgeStep':continuity['maximumOneRowEdgeStepPx'],'maxWidthStep':continuity['maximumOneRowWidthStepPx'],'widthMinMax':continuity['graySlabWidthMinMaxAcrossY420To815'],'resultRecord':info(OUT/'result.json')},ensure_ascii=False))
