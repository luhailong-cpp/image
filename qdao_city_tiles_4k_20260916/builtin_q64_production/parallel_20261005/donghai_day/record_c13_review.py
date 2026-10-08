"""Record actual visual inspection results; this script does not inspect images."""
from pathlib import Path
import assembly as n
ROOT=Path(__file__).resolve().parent
Q=ROOT/'r08_c13/qa/current-west-joint'
manifest=n.load_json(Q/'manifest.json')
expected={'r08_c12':'69baa04bc59853455e76fd11d9a88e3b4b85c8470bac67245546cfa7139caf99','r08_c13':'28c5a083e0f2f823508b43ed7e0cc9b48b423cfe9b645b2316c11b3127d7afc8'}
for out in manifest['outputs']:
 n.require(n.sha(out['file'])==out['sha256']==expected[out['tile']],'Review target changed')
inspections=[]
for item in manifest['qa']:
 n.require(n.sha(item['file'])==item['sha256'],'QA pixels changed')
 inspections.append(dict(item,visualInspection='pass for visible edge continuity',method='actual view_image of initial 10 native-pixel sheets; unchanged sheets carried by identical SHA; changed right insertion and horizontal sheets actually reopened after local edits'))
review={'reviewedAtUtc':n.utc_now(),'reviewer':'finish_joint13 visual inspection via view_image','reviewScope':'Complete c12/c13 shared edge, entire left/right strip insertions, three horizontal repair overlaps, four insertion corners, and each subsequent local edit including its perimeter. Tile-internal seams outside this scope remain covered by the existing source tile reviews.','outputs':manifest['outputs'],'qa':inspections,'resolvedIssues':[{'id':'C12-C13-COMMON-EDGE','detail':'Discontinuous paving, timber/rope shapes, banner motifs and shadow across original x4096 join repaired with s1..s4 native edits.'},{'id':'C13-RIGHT-INSERTION-STONE-01','detail':'Small offset grout contours at right insertion corrected; bounded native integration.'},{'id':'C13-RIGHT-INSERTION-STONE-02','detail':'Hard paint transition introduced at upper local edit perimeter softened by a second bounded native edit.'},{'id':'C13-RIGHT-INSERTION-STONE-03','detail':'Lower two gray/warm grout transitions treated with native local edit; contours continuous. Painted facets and small local hue variations retained.'}],'localReviewImages':[{'file':str(ROOT/f'r08_c13/repairs/right-insertion-stone-{i:02}/qa/context.png'),'sha256':n.sha(ROOT/f'r08_c13/repairs/right-insertion-stone-{i:02}/qa/context.png'),'actuallyViewed':True,'pixelScale':1} for i in (1,2,3)],'openActionableDefectsInReviewedScope':[],'visualSeamReviewPassed':True,'c12WestRepairsPreserved':True,'outsideEveryAuthorizedEditRectPixelEquality':True,'nativeSourcesNotResized':True,'actualModel':None,'actualQuality':None,'formalAccepted':False,'wholeCityComplete':False,'navigationValidated':False,'clientAcceptance':False}
n.save_json(ROOT/'r08_c13/qa/west-joint-review.json',review)
print({'review':str(ROOT/'r08_c13/qa/west-joint-review.json'),'outputs':manifest['outputs']})
