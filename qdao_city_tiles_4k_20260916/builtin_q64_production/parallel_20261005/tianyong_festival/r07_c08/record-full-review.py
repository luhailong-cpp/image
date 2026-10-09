from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
N=Path(__file__).parent;T=N.parent;D=N/'full-review-native-v1'
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
i=read(D/'native-crop-index.json')
findings={
'full-11.png':'Planter arc, grounded leaf shadow, paired diagonal courses and quiet slab surfaces remain continuous across top-row and row2 transitions.',
'full-12.png':'Long carved cloud panel, rounded upright rails, gray plinth and oblique slab edges remain coherent; actual panel butt joint is preserved.',
'full-13.png':'Upper course and sparse staggered cream paving remain clean. Repaired stray tapered groove is absent and middle slab face is uninterrupted.',
'full-21.png':'Broad oblique paving grid, narrow paired rail and lower channel have smooth single contour crossings through internal patch transitions.',
'full-22.png':'Cloud panel termination, short end block and diagonal rail junction are physically connected to broad ivory course and recessed gray channel.',
'full-23.png':'Upper slab field, paired curved rails, channel and framed slate panels continue through middle-row transitions without disconnected geometry.',
'full-31.png':'Lower-left cream framing, shallow emblem and large gray slab remain connected. Broad diagonal tonal plane on gray slab is canonical painterly shading, not a crack, extra joint or rectangular crop seam.',
'full-32.png':'Large gray fields and crossing narrow ivory frame remain continuous. Corrected r03c02 finite return removes misplaced old bevel; no repeated line remains.',
'full-33.png':'Cloud relief column, dark slab rows, ivory dividers and lower curved course meet with stable contours and consistent scale.',
'east-1.png':'Upper full east boundary: coarse sparse slab grid and upper course join actual r07c09 with no stepped or doubled edges.',
'east-2.png':'Middle east boundary: cream rails, recessed channel and vertical frame joint connect across x4096; differing slab tones occur at actual stone butt joints.',
'east-3.png':'Lower east boundary: upright frame, dark slab rows and curved bottom course join continuously. Right-side inherited texture is confined to its existing material fields and does not disconnect geometry.',
'south-1.png':'Entire left south segment: diagonal narrow frame and gray slab edges connect to actual r08c08 across y4096.',
'south-2.png':'Middle south segment: broad courses, butt joint and lower decorative plate edges continue across y4096.',
'south-3.png':'Right south segment: curved border and cloud relief field connect into authentic r08c08 without line step.',
'corner-northwest.png':'Existing own384-square is clean. Three absent neighbor quadrants remain transparent and are not accepted by inference.',
'corner-northeast.png':'Known own/east lower quadrants connect smoothly along top course; unknown north quadrants pending.',
'corner-southwest.png':'Three authentic visible quadrants form continuous ivory diagonal framing and gray slab intersection. Unknown r07c07 quadrant pending.',
'corner-southeast.png':'All four actual-source quadrants form continuous ivory course, framed cloud relief and lower gold border; no cross-corner break.'
}
assert len(i['crops'])==19 and set(findings)=={Path(c['file']).name for c in i['crops']}
for c in i['crops']:assert sha(c['file'])==c['sha256']
pending=[{'neighbor':'r06_c08','edge':'north','status':'await actual native neighbor'},{'neighbor':'r07_c07','edge':'west','status':'await actual native neighbor'},{'neighbors':['r06_c07','r06_c09'],'scope':'northern diagonal corner quadrants','status':'unknown actual source'},{'scope':'complete city256 tiles and nearest-camera runtime','status':'outside local image review'}]
r={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r07_c08','fullyPaintedNativeTileReviewed':True,'source':i['sources']['r07_c08'],'sourceIndex':ref(D/'native-crop-index.json'),'fullNativeCoveragePixels':16777216,'nativeScale':1,'method':'Actual view_image(detail=original) inspection of all19 indexed crops: nine overlapping1536-square windows, three east strips and three south strips with384px on each side, and four known-corner composites. No visual acceptance inferred from numeric metrics.','noReviewUpscaling':True,'openInternalFindings':[],'formalAccepted':False,'pendingExternalChecks':pending,'eastActualRootBoundaryReviewed':True,'southActualRootBoundaryReviewed':True,'knownCornerPartsReviewed':True,'crops':[dict(c,actuallyViewed=True,visualPass=True,finding=findings[Path(c['file']).name]) for c in i['crops']],'modelQualityDisclosure':'Builtin actual model and quality undisclosed/null; each generated/edited source retains separate provenance.','rootStateModified':False}
save(D/'visual-review.json',r)
root=read(T/'source-checkpoint.json');latest={v['tile']:v for v in root['candidateSet']}
checks=[]
for tile,box in [('r07_c08',[0,0,4096,4096]),('r07_c09',[0,0,384,4096]),('r08_c08',[0,0,4096,384]),('r08_c09',[0,0,384,384]),('r08_c07',[3712,0,4096,384])]:
 a=i['sources'][tile];b=latest[tile]
 for v in [a,b]:assert sha(v['file'])==v['sha256']
 A=np.array(Image.open(a['file']).convert('RGBA').crop(box));B=np.array(Image.open(b['file']).convert('RGBA').crop(box))
 diff=int(np.any(A!=B,axis=2).sum());assert diff==0,(tile,diff)
 checks.append({'tile':tile,'reviewedSource':a,'rootSource':b,'roi':box,'pixelExact':True,'differentPixels':0})
save(D/'root-checkpoint-at-final-verification.json',root)
report={k:v for k,v in r.items() if k not in ['crops','sourceIndex']}
report.update(source=latest['r07_c08'],visualReview=ref(D/'visual-review.json'),exactRootPixelChecks=checks,rootCheckpoint=ref(D/'root-checkpoint-at-final-verification.json'),method='All19 frozen native crops actually inspected; entire4096-square root tile and all reviewed neighboring strips/corner ROIs subsequently proven pixel-exact to frozen reviewed sources. This identity check does not replace visual inspection.')
save(D/'root-reviewed-v016.json',report)
print(json.dumps({'review':ref(D/'visual-review.json'),'rootReport':ref(D/'root-reviewed-v016.json'),'rootSource':latest['r07_c08'],'checks':[{'tile':x['tile'],'exact':x['pixelExact']} for x in checks]}))
