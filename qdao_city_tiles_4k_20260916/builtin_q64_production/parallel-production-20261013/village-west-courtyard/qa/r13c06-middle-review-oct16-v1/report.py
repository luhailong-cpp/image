from pathlib import Path
from PIL import Image
import hashlib,json,datetime,numpy as np
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
i=json.loads((R/'inputs-v1.json').read_text())
source=Path(i['source']);assert sha(source)==i['sha256']
im=Image.open(source)
assert sha(i['assembly'])==i['assemblySha256']
assert sha(i['sourceIdMap'])==i['sourceIdMapSha256']
checked=[]
for c in i['crops']:
    p=Path(c['path']);assert sha(p)==c['sha256']
    assert np.array_equal(np.asarray(Image.open(p)),np.asarray(im.crop(c['contextBox'])))
    checked.append({**c,'viewed':True,'viewDetail':'original','cropPixelIdentity':True,'visualStatus':'passed-reviewed-scope','note':'Native visual inspection found coherent water shapes across the reviewed original seam and selection boundaries; no conspicuous straight cutoff, color step or new zigzag contour.'})
rec={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'/root/resume_r12c06_oct16','tile':'r13_c06','status':'passed-specified-middle-internal-scope','formalAccepted':False,'source':{'path':str(source),'sha256':sha(source),'dimensions':list(im.size)},'assembly':{'path':i['assembly'],'sha256':i['assemblySha256']},'sourceIdMap':{'path':i['sourceIdMap'],'sha256':i['sourceIdMapSha256']},'globalContextBox':i['globalContextBox'],'reviewedContextCoreScope':[115,1536,4211,2560],'mainScope':i['scope'],'changedOverlapScope':i['changedOverlapScope'],'scopeNote':'Read-only W13 snapshot review of y1536..2560, including changed y1536..1766 overlap. Does not repeat or extend the prior y<1536 review. No y>=2560 pixels or external joins accepted. Result transfers only when pixels inside this scope remain identical.','originalVerticalSeams':{'x':[1139,2163,3187],'yRange':[1536,2560],'status':'passed-reviewed-scope'},'originalSecondHorizontalSeam':{'y':2163,'xRange':[115,4211],'segments':4,'status':'passed-reviewed-scope'},'nativeCropsActuallyViewed':19,'crops':checked,'boundaryDiagnosticMethod':'Eight spatially separated high-contrast source-ID boundary points were additionally cropped and visually inspected; numerical boundary score was used only to select inspection locations, never to infer visual pass. All selection boundaries are also contained in the four native full-coverage windows.','actualSelectionBoundaryChecks':i['boundaryRegions'],'findings':[],'pending':['North/west/east external joins','Lower area y>=2560','Whole-tile formal acceptance','Any subsequently changed pixels in reviewed scope'],'artworkMutated':False,'aiGenerationUsed':False,'gitOperations':False,'proof':{'sourceHashUnchanged':True,'cropHashMismatches':0,'cropPixelIdentityMismatches':0,'sourceIdHashUnchanged':True}}
with (R/'review-v1.json').open('x',encoding='utf-8') as f:json.dump(rec,f,ensure_ascii=False,indent=2)
print(json.dumps({'report':str(R/'review-v1.json'),'sha256':sha(R/'review-v1.json'),'status':rec['status'],'sourceSha256':sha(source)},ensure_ascii=False))
