from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent;T=ROOT/'r09_c09';Q=T/'qa'
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def rgb(im):return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
core=T/'candidate/core4096.png';ext=T/'candidate/extended4326.png';im=Image.open(core).convert('RGB')
assert im.size==(4096,4096) and Image.open(ext).size==(4326,4326)
assert Image.open(ext).convert('RGB').crop((115,115,4211,4211)).tobytes()==im.tobytes()
reports=[Q/'final-internal-review.json',Q/'final-neighbor-review.json'];a,b=[load(p) for p in reports]
assert sha(reports[0])=='2e019aafd469dbce3591f52f1aa7969e8147d2d8cc76033a89f828a5875bcff2'
assert sha(reports[1])=='b58713772b63aca1253f6525c803c0c3365f7474921bcdf71669b460b68af1cc'
assert not a['requiresRepair'] and not b['requiresRepair']
assert a['source']['sha256']==b['candidateSource']['sha256']==sha(core)
expected=[]
manifests=[Q/'qa.manifest.json',Q/'guide-bands/manifest.json',Q/'external-north.manifest.json',Q/'external-east.manifest.json']
for p in manifests:expected+=load(p)['checks']
checks=a['checks']+b['items'];assert len(checks)==len(expected)==93
assert len({str(Path(c['file']).resolve()).lower() for c in checks})==93
assert {str(Path(c['file']).resolve()).lower() for c in checks}=={str(Path(c['file']).resolve()).lower() for c in expected}
for c in expected:assert sha(c['file'])==c['sha256']
for c in a['checks']:
 crop=Image.open(c['file']).convert('RGB');assert sha(c['file'])==c['sha256'] and rgb(crop)==c['decodedRgbSha256']
 assert crop.tobytes()==im.crop(c['targetCoreBox']).tobytes() and not c['requiresRepair']
 if not c['newlyActuallyViewed']:
  e=c['inheritance'];assert sha(e['reviewFile'])==e['reviewFileSha256'] and sha(e['earlierCropFile'])==e['earlierCropSha256']
  assert Image.open(e['earlierCropFile']).convert('RGB').tobytes()==crop.tobytes() and e['earlierActuallyViewed']
for c in b['items']:
 crop=Image.open(c['file']).convert('RGB');assert sha(c['file'])==c['sha256'] and rgb(crop)==c['rawRGBSha256'] and not c['requiresRepair']
 rebuilt=Image.new('RGB',tuple(c['pixels']))
 for m in c['pixelMappings']:
  assert sha(m['source'])==m['sourceSha256'];part=Image.open(m['source']).convert('RGB').crop(m['sourceBoxXYXY']);assert rgb(part)==m['rawRGBSha256']
  rebuilt.paste(part,tuple(m['destinationBoxXYXY'][:2]))
 assert rebuilt.tobytes()==crop.tobytes()
 if not c['actuallyViewedByThisReviewer']:
  e=c['inheritedEvidence'];assert sha(e['review'])==e['reviewSha256'] and sha(e['file'])==e['sha256']
  assert Image.open(e['file']).convert('RGB').crop(e['sourceBoxXYXY']).tobytes()==crop.tobytes()
jp=Q/'northeast-four-tile-junction.manifest.json';j=load(jp);joint=Image.open(j['output']['file']).convert('RGB');assert sha(j['output']['file'])==j['output']['sha256']
rebuild=Image.new('RGB',(1024,1024))
for m in j['pixelMappings']:
 assert sha(m['file'])==m['sha256'];part=Image.open(m['file']).convert('RGB').crop(m['sourceBoxXYXY']);assert rgb(part)==m['cropRawRGBSha256'];rebuild.paste(part,tuple(m['destinationXY']))
assert rebuild.tobytes()==joint.tobytes()
preview=T/'candidate/preview1024.png'
out={'schemaVersion':1,'tile':'r09_c09','reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCore':ref(core),'sourceExtended':ref(ext),'reports':[ref(p) for p in reports],'exportManifests':[ref(p) for p in manifests],'coverage':{'exportedTotal':93,'coveredScopes':93,'allExportedScopesCoveredByActualViewsAndByteIdentity':True,'finalStageNewOriginalPixelViews':40,'earlyStageOriginalPixelViews':46,'originalPixelImagesActuallyViewedForStandardScopesAcrossTeam':86,'exactSubscopesWithoutRedundantView':7,'additionalRootOriginalPixelViews':1,'totalOriginalPixelImagesViewedAcrossTeam':87,'totalScopesIncludingRootJunction':94,'interpretation':'31 early internal and15 early neighbor images;14 final internal and26 final neighbor; seven own-edge scopes are exact halves of earlier neighbor boards. One additional root four-tile junction view.'},'requiresRepair':False,'overview':{**ref(preview),'actuallyViewed':True,'method':'tools.view_image(detail=original) of1024 downsample, overview only','observations':'Existing upper curved planter, low ivory rail and posts, lower cropped blank red/gold lantern and rounded canopy retain intended placement. No obvious isolated new object or rectangular assembly boundary in overview. Low-contrast broad stone facets are visible.'},'additionalRootChecks':[{'kind':'northeast_four_tile_junction','image':j['output'],'manifest':ref(jp),'actuallyViewed':True,'method':'tools.view_image(detail=original),1024x1024 integer four-corner board','requiresRepair':False,'observation':'Pillar face and bevel, low railing, foliage and paving grooves cross the two center axes continuously at the shown four-tile junction; no visible doubled contour, clipped foliage or sharp rectangular tonal boundary requires repair in this scope.','notEveryPixelFormalAcceptance':True}],'minorObservations':a['minorObservations']+b['minorObservations'],'remaining':{'westAndSouthNeighborContinuity':'Future neighbors incomplete; own-edge views are not adjacency acceptance.','otherFourTileJunctions':'Remain unverified until surrounding tiles exist.','formalClientWholeCity':'All remain unaccepted/unvalidated/incomplete.'},'noImageProcessingInReview':True,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False}
dest=Q/'root-final-review.json';assert not dest.exists();dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(dest),'sha256':sha(dest),'coveredStandardScopes':93,'additionalRootScope':1,'requiresRepair':False}))
