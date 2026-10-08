from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
out=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ix=out/'crop-index.json';idx=json.loads(ix.read_text(encoding='utf-8'))
r={
 'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'reviewer':'external_review',
 'scope':'Frozen r07_c10 lower two generated rows: complete native coverage x0..4095/y1933..4095, standard and actual internal join boundaries, final coupled south seam after all four row04 bottom returns and c01 southwest return',
 'sourceCheckpoint':idx['localCheckpoint'],'rootBaseCheckpoint':idx['rootCheckpoint'],
 'sourceImage':idx['fragment'],'cropIndex':{'file':str(ix),'sha256':sha(ix)},
 'nativePixelInspection':True,'nativeScale':1,'localVisualAccepted':True,'wholeTileAccepted':False,'formalAccepted':False,
 'newModelCalls':0,'sourceImagesModified':False,'rootStateModified':False,
 'coverage':idx['coverage'],
 'reviewedImages':idx['crops'],
 'returnApplicationProofs':idx['returnApplications'],
 'derivedSouthPixelSha256':idx['derivedSouthPixelSha256'],
 'derivedSouthwestPixelSha256':idx['derivedSouthwestPixelSha256'],
 'findings':[
  {'id':'complete-painted-area','finding':'All 8,859,648 opaque pixels in the required lower-two-row region are covered by six overlapping1536x1536 native crops, all viewed. The ivory paving, narrow borders, recessed grey channel, and partial relief retain a consistent clean rounded painted finish. No unpainted hole, accidental duplicate edge, rectangular material step or obvious native patch seam was found.'},
  {'id':'internal-joins','finding':'The full-coverage views include all standard x1024/2048/3072 and y2048/3072 lines within the painted region. Three additional native768x768 junction views centre the standard y3072 line and include actual row return boundaries y2957/y3133 and nearby column joins. Existing broad highlight tapers are continuous across the joins; they do not form boundary-aligned cuts or separate disconnected lines. No repair-blocking structural discontinuity found.'},
  {'id':'south-return-order','finding':'Four r08_c10 bottom returns were applied for review in c04,c03,c02,c01 order onto the frozen actual root v017 source, together with the r04_c01 r08_c09 corner return. All five requiredPriorSource destination ROIs exactly matched immediately before application; only manifest asset pixels were pasted at native scale. Sources were not mutated.'},
  {'id':'south-full4096','finding':'Four overlapping native1280x768 views cover the entire4096-pixel r07/r08 shared horizontal edge,384 pixels on each side, after the return composition. Diagonal stone joints, the gray channel, cloud carving and broad ivory profiles remain continuous at y4096 and at the y61 return end in r08. No conspicuous new step, doubled groove, rectangular colour return or break was observed.'},
  {'id':'southwest-partial-junction','finding':'Available southwest junction source was inspected, including the unpublished115-pixel r07_c09 halo, the current r07_c10, and both row8 tiles with required returns. Visible profiles connect smoothly. Unknown r07_c09 pixels remain transparent and are explicitly excluded from acceptance.'}
 ],
 'blockingFindings':[],
 'limitations':[
  'This accepts only the frozen painted lower-two-row region and the described final coupled south border. It does not accept the full r07 tile, missing northern pixels, or left/right external neighbours.',
  'The r07_c09 115-pixel halo is useful for checking the visible corner but is not a root-published neighbour tile.',
  'Formal geometry/navigation and nearest-camera client validation are not performed by this visual review.',
  'Future changed pixels require review of their affected ROI and return boundaries; this record must not be silently applied to a newer image hash.'
 ]
}
p=out/'visual-review.json';p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(p),'sha256':sha(p),'localVisualAccepted':True,'formalAccepted':False,'viewedNativeCrops':len(r['reviewedImages'])},ensure_ascii=False))
