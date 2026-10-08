"""Write root's actual views; append explicit observed cells before execution."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent.parent
notes={'r01_c03':{
 'north':'Crown contours join coherently. The earlier short bright leaf face is corrected. Paving has a low-contrast material transition at the true north join; no sharp dark rule, geometry step or detached contour seen in this scope. Reassess in the full north strip.',
 'east':'Both existing paving grooves join across the native boundary without a disconnected or duplicated contour; small bevel/shading variation remains.',
 'east-guide':'No distinct rectangular guide-boundary stripe or clipped groove seen; broad low-contrast ivory facets remain.'},
 'r04_c03':{
 'north':'Native groove and clipped red spiral continue across the true native join; no disconnected contour or distinct horizontal exposure band seen.',
 'east':'Quiet ground on the left and broader ivory facets on the older eastern cell differ in texture density. No continuous hard brightness line, rectangular patch frame or severed entity contour seen; retain this material observation for whole-tile overview.',
 'east-guide':'No straight guide-boundary line or newly added floor markings. Ground stays quiet with very gentle diffuse variation.',
 'north-guide':'Red spiral edge and quiet ivory ground cross the guide transition without visible clipping or a horizontal paint stripe.'},
 'r04_c02':{
 'north':'Green leaf lobes and red upright cross the native boundary without an actionable truncated leaf or post offset. Ivory ground has no distinct horizontal stripe.',
 'east':'The shared red spiral, gold ball, post face and ivory ground join with continuous contours and highlights; no duplicated object or cut edge observed.',
 'east-guide':'Red bevels, gold trim and post remain continuous at the guide transition; the blank yellow panel retains no text or symbol.',
 'north-guide':'Existing leaves, red spiral bracket and gold collar continue without a straight guide-cut edge or detached fragment.'}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for cell,observations in notes.items():
 d=R/'r09_c08/ready-cell-qa'/cell; target=d/'root-review.json'
 if target.exists():continue
 m=json.loads((d/'manifest.json').read_text(encoding='utf-8-sig'));items=[]
 for e in m['checks']:
  p=Path(e['file']);assert sha(p)==e['sha256']
  assert hashlib.sha256(Image.open(p).convert('RGB').tobytes()).hexdigest()==e['decodedRgbSha256']
  items.append({**e,'actuallyViewed':True,'reviewStatus':'inspected_pending_full_tile_qa','requiresRepair':False,
   'method':'tools.view_image(detail=original), no display resampling','observation':observations[p.stem]})
 v={'schemaVersion':1,'tile':'r09_c08','cell':cell,'reviewer':'root','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
  'sourceManifest':{'file':str(d/'manifest.json'),'sha256':sha(d/'manifest.json')},'checks':items,
  'requiresRepair':False,'formalAccepted':False,'clientValidated':False,
  'scopeLimit':'Only the listed exact original-pixel scopes. Full tile QA and complete true north strip remain pending.'}
 target.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'file':str(target),'sha256':sha(target),'actualViews':len(items)}))

# Root actually viewed this original512 crop after the listed cells became ready.
# Northern c02's pending repair is contracted to rows<400 and cannot change the
# bottom256 pixels used here. Final QA still must compare exact decoded bytes.
d=R/'r09_c08/ready-intersection-qa/r1_c2'; target=d/'root-review.json'
if not target.exists():
 manifest=d/'manifest.json';m=json.loads(manifest.read_text(encoding='utf-8-sig'));e=m['output'];p=Path(e['file'])
 assert sha(p)==e['sha256']=='5d3fc6b7ba27af8487eaeab3e4be25e122e8de3176bf4f7fc95de6675a0af15b'
 item={**e,'actuallyViewed':True,'requiresRepair':False,'method':'tools.view_image(detail=original)',
  'observation':'Curved ivory planter rim, foliage and ground join across both center axes without an isolated fragment, straight color stripe or displaced contour. Existing foliage colors vary smoothly.'}
 v={'tile':'r09_c08','reviewer':'root','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'checks':[item],
  'sourceManifest':{'file':str(manifest),'sha256':sha(manifest)},'requiresRepair':False,'formalAccepted':False,
  'scopeLimit':'This single original-pixel four-cell intersection only; final candidate must retain exact decoded crop pixels before inheriting this view.'}
 target.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'file':str(target),'sha256':sha(target),'actualViews':1}))

intersection_notes={
 'r1_c3':('5f08138c2b260d35a3c31dfac9cf7bba22fff07b3f24e95794c02f8834452105','Existing shallow groove joins continuously. Broad stone facets do not form a straight cross-shaped exposure boundary.'),
 'r2_c2':('dda30cadbf815d7c7a205744e7bbfa6b4e0710e4831861ce5de1003dbd677ef3','Quiet stone only. Upper broad facets transition into gentler lower material; no continuous horizontal rule or rectangular patch frame identified.'),
 'r2_c3':('2acc5cb1072ec5e4cd293531b2a2c7f2f975aea2935618dfb3cd11ffeb6c2ab7','Ivory facet density differs between cells, but no four-way brightness step or sharp seam-length stripe observed.'),
 'r3_c2':('07322f21446865a2a7194c38243520f760b4351b09bbd04ef691994dbbf131b5','The existing TWO bracket levels are intentional and confirmed against the selected regional composition and r03c02 guide, both actually viewed by root. Post, lower red spiral, gold ball and ivory ground join continuously.'),
 'r3_c3':('5d0086f940255e6cb4aa7db99e4390e279c576b4653a60a68f44eec38422b86b','Single existing groove crosses the vertical center without a disconnection or duplicate. Upper/lower and left/right ivory texture variance remains low contrast without a crisp cross-shaped boundary.')}
for cell,(expected,observation) in intersection_notes.items():
 d=R/'r09_c08/ready-intersection-qa'/cell; target=d/'root-review.json'
 if target.exists():continue
 manifest=d/'manifest.json';m=json.loads(manifest.read_text(encoding='utf-8-sig'));e=m['output'];p=Path(e['file'])
 assert sha(p)==e['sha256']==expected
 item={**e,'actuallyViewed':True,'requiresRepair':False,'method':'tools.view_image(detail=original)','observation':observation}
 v={'tile':'r09_c08','reviewer':'root','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'checks':[item],
  'sourceManifest':{'file':str(manifest),'sha256':sha(manifest)},'requiresRepair':False,'formalAccepted':False,
  'scopeLimit':'This single original-pixel four-cell intersection only; final candidate must retain exact decoded crop pixels before inheriting this view.'}
 target.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'file':str(target),'sha256':sha(target),'actualViews':1}))
