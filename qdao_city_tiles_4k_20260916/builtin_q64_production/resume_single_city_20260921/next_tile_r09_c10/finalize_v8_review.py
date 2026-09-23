from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import hashlib,json
P=Path(__file__).resolve().parent;ART=next(p for p in P.parents if (p/'config/image-generation.json').exists());Q=P/'qa/external-v8';V=P/'repairs/versions/external-v8'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def relative(p):return Path(p).resolve().relative_to(ART).as_posix()
def ref(p):return {'file':relative(p),'sha256':sha(p),'pathBase':'art_root'}
idx=json.loads((Q/'evidence-index.json').read_text(encoding='utf-8'))
for item in idx['files']+idx['neighbors']:
 assert sha(item['file'])==item['sha256']
 with Image.open(item['file']) as im:im.verify()
with Image.open(V/'r09_c10.png') as im:
 assert im.format=='PNG' and im.size==(4096,4096) and im.mode in ('RGB','RGBA')
 assert im.mode=='RGB' or im.getextrema()[3]==(255,255)
for ver in ['external-v6','external-v7','external-v8']:
 d=P/'repairs/versions'/ver;r=json.loads((d/'repair.json').read_text(encoding='utf-8'))
 for key in ['sourceCandidate','sourceRecord','prepared','generationRecord','originalNativeOutput']:
  assert sha(r[key]['file'])==r[key]['sha256'],(ver,key)
 assert sha(d/'repair-native-1254.png')==r['originalNativeOutput']['sha256']
review={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'next_tile_art','status':'scoped_local_continuity_passed_not_production_accepted','candidate':ref(V/'r09_c10.png'),'record':ref(V/'repair.json'),'evidenceIndex':ref(Q/'evidence-index.json'),'reviewMethod':'Actual original-resolution viewing of all 15 evidence images; overview viewed for placement only. No scaled preview substituted for seam inspection.','reviewedChecks':[{'check':'all 3 internal vertical seams, complete4096 length','passed':True},{'check':'all 3 internal horizontal seams, complete4096 length','passed':True},{'check':'all 9 internal four-source intersections','passed':True},{'check':'full4096 left boundary against real r09_c09 v6 core','passed':True},{'check':'full4096 bottom boundary against real r10_c10 existing core','passed':True},{'check':'left x215 and bottom y3881 treatment returns','passed':True},{'check':'both native1254 repair regions and their return boundaries','passed':True},{'check':'true r09_c09/r09_c10/r10_c09/r10_c10 southwest four-tile junction','passed':True},{'check':'southwest combined treatment return region','passed':True}],'observations':['No remaining visible hard boundary, doubled outline or broken bevel in inspected scoped seams and intersections.','Bottom v6/v7 tapered duplicate was removed in v8; left two targeted bevel steps were removed in v7 and retained in v8.','Native material stays crisp, rounded and bright; no UI content from the attached confirmed style reference entered the map.'],'scopedLocalContinuityPassed':True,'scopeExclusions':['Top and right neighbor joins remain unreviewed until their actual adjoining cores exist.','Other three tile-level four-tile junctions remain unreviewed.','Full 256-tile city production acceptance and client runtime acceptance are not claimed.','Backend model and quality remain unverified because tool disclosed no model/quality fields.'],'openFailuresInReviewedScope':[],'productionAccepted':False,'visualAcceptancePassed':False,'runtimePublished':False,'actualModel':None,'actualQuality':None,'backendModelVerified':False,'retainedFailedVersions':['external-v5','external-v6','external-v7'],'originalSourceCountsThisChild':{'detailSelected':16,'detailRejectedRetained':1,'nativeRepairOutputs':6,'styleReferenceOnly':1,'totalOriginalGeneratedPng':24},'newNativeRepairOutputsThisContinuation':3,'sourceNeighborFilesUnchanged':idx['neighbors'],'nativeArtEnlarged':False,'postprocessing':'Native-size assembly; recorded bounded <=8px subpixel registration/local color matching for seam repair; original PNG bytes retained.'}
path=Q/'visual-review.json'
with path.open('x',encoding='utf-8') as f:json.dump(review,f,ensure_ascii=False,indent=2)
pointer={'file':relative(V/'r09_c10.png'),'sha256':sha(V/'r09_c10.png'),'pathBase':'art_root','status':review['status'],'record':ref(V/'repair.json'),'qa':ref(path),'scopedLocalContinuityPassed':True,'productionAccepted':False,'runtimePublished':False,'extendedContext':ref(V/'extended-context.png')}
with (P/'latest-candidate.json').open('x',encoding='utf-8') as f:json.dump(pointer,f,ensure_ascii=False,indent=2)
print(json.dumps(pointer,ensure_ascii=False,indent=2))
