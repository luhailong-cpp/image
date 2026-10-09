"""Read-only independent verification of the applied joint source migration."""
from pathlib import Path
import datetime,hashlib,json,sys
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent;W=R/'r10_c11';C=R/'r10_c13'
sys.path.insert(0,str(R/'tools/multi_edge'));import engine
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def arr(p):return np.asarray(Image.open(p).convert('RGB'))
def ck(x):assert Path(x['file']).is_file() and sha(x['file'])==x['sha256'],x['file']
def same(im,p):assert np.array_equal(np.asarray(im),arr(p)),str(p)
out=D/'independent-after-audit.json';assert not out.exists()
result=read(D/'migration-applied.json');pre=read(D/'migration-preflight.json');migration=read(D/'applied-source-migration.json')
checked=[]
for field in ['canonicalAfter','metadataAfter','imageAfter','c12All27AppliedQAReproduced']:
 for item in result[field]:ck(item);checked.append(dict(list=field,**item))
for p,h in pre['protected'].items():assert sha(p)==h,p
j=read(D/'migration-journal.json');assert j['status']=='complete';ck(j['result']);ck(j['afterAudit'])
for x in read(D/'text-history/index.json')['snapshots']:ck(x['snapshot'])
e=T/'output/r10_c12.png';p14=W/'native/p14.png';cp=C/'output/r10_c13-candidate.png'
assert sha(e)=='4dc21b33dea8fa9a35e2c5a556e8495ecc9cda3e173457fb060682dd1b4a438b'
assert sha(p14)=='96f4fb8808feedc00234386fb61d273436636d15ab1bb8549908ffb52634bebb'
wp=read(W/'plan.json');cplan=read(C/'plan.json');manifest=read(T/'output/manifest.json');cmanifest=read(C/'output/manifest.json')
assert wp['eastCandidateSha256']==sha(e)==cplan['westCandidateSha256']
assert manifest['sha256']==sha(e) and manifest['scopedLocalSeamsPassed'] and not manifest['formalAccepted']
assert read(T/'progress.json')['sha256']==sha(e)
assert cmanifest['neighbors']['west']['sha256']==sha(e);ck(cmanifest['plan']);ck(cmanifest['neighborRevalidation'])
assert sha(cp)=='c6c7176ea72228aca772c78a17fe8e3b5fc699904f46205d62ae482f420d1a5b'
for m in [manifest,cmanifest]:
 for x in m['qa']:
  ck(x)
  for src in x.get('sources',[]):ck(src)
for x in read(C/'qa/final-local-review.json')['independentReviews']:ck(x)
for x in read(C/'neighbor-revalidation.json'):
 assert sha(x['source'])==x['currentSourceSha256']
 im=Image.open(x['source']).convert('RGB').crop(x['cropXYXY']);assert hashlib.sha256(np.asarray(im).tobytes()).hexdigest()==x['currentCropPixelSha256']==x['frozenCropPixelSha256']
review=read(T/'qa/final-local-review.json');by={Path(x['file']).stem:x for x in review['items']};c12qa=[]
assert len(by)==27
n=Path(manifest['northSource'])
for name,im,op,roles in engine.qa_images(Image.open(e).convert('RGB'),{'north':Image.open(n).convert('RGB')},'NW',256):
 x=by[name];ck(x);same(im,x['file']);assert x['actuallyViewed'] and x['nativeScale']==1 and x['verdict'] in ['scoped_pass','current_pixels_inspected_neighbor_unverified'];c12qa.append(ref(x['file']))
neighbors={role:Image.open(cplan[key]).convert('RGB') for role,key in [('north','northCandidate'),('west','westCandidate'),('northwest','northWestCandidate')]};c13qa=[]
for name,im,op,roles in engine.qa_images(Image.open(cp).convert('RGB'),neighbors,'NW',256):
 if name.startswith('four-tile-'):continue
 name=name.replace('return-plus256','return-256');p=C/'qa/native-candidate'/(name+'.png');same(im,p);c13qa.append(ref(p))
assert len(c13qa)==27
p=C/'qa/four-tile-corner.png';g=read(str(p)+'.generation.json');q=Image.new('RGB',(1024,1024))
for src,box,xy in zip(g['derivedFrom'],g['operation']['sourceCropLTRB'],[(0,0),(512,0),(0,512),(512,512)]):
 ck(src);q.paste(Image.open(src['file']).convert('RGB').crop(box),xy)
same(q,p);c13qa.append(ref(p))
for p in sorted((C/'qa/external-details').glob('west-unrotated-*.png')):
 g=read(str(p)+'.generation.json');q=Image.new('RGB',tuple(g['pixels']))
 for src in g['sources']:ck(src);q.paste(Image.open(src['file']).convert('RGB').crop(src['cropLTRB']),src['pasteXY'])
 same(q,p);c13qa.append(ref(p))
assert len(c13qa)==32
for rec in migration['c13ConsumedPixels']:
 im=Image.open(e).convert('RGB').crop(rec['cropLTRB']);assert hashlib.sha256(np.asarray(im).tobytes()).hexdigest()==rec['oldPixelSha256']==rec['newPixelSha256']
g=read(str(p14)+'.generation.json');assert g['sha256']==sha(p14) and g['actualModel'] is None and g['actualQuality'] is None;ck(g['previousCurrentGeneration']);ck(g['originalImagegenRequest']);ck(g['sourceVersionMigration'])
for x in g['derivedFrom']:ck(x);ck(x['generation'])
expected=[wp['tile']['finalPixelRect'][0]-115+3072,wp['tile']['finalPixelRect'][1]-115,1254,1254];assert g['globalPatchXYWH']==expected and not g['sourceUpscaled'] and not g['resizedAfterGeneration'];assert g['nativeWorkflow']['wavefront']=='NE'
ctx=np.asarray(Image.open(W/'native/p14-current-context.png').convert('RGBA'));pa=arr(p14);mask=ctx[:,:,3]>0;assert np.array_equal(pa[mask],ctx[:,:,:3][mask])
same(Image.open(e).convert('RGB').crop((0,0,115,4096)),W/'references/east-native115.png')
# Re-run the production limited registration against actual current N/E/NE support.
neighbors={role:arr(wp[key]) for role,key in [('north','northCandidate'),('east','eastCandidate'),('northeast','northEastCandidate')]}
l=engine.Layout();canvas,covered,seeds=engine.seed_neighbors(l,neighbors);x,y=l.origin(0,3);context=canvas[y:y+l.patch,x:x+l.patch].copy();known=covered[y:y+l.patch,x:x+l.patch].copy();edges=engine.active_edges(l,0,3,'NE',neighbors);owner=engine.owner_mask(known,edges,l)
merged,flow,tone,reg=engine.register_native(context,pa,known,owner,edges,l,max_shift=6.,tone_cap=18.,return_depth=256)
assert np.array_equal(merged,pa),'Current p14 is changed by production registration';assert reg['foldedAppliedPixels']==0
report=dict(auditedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),mode='read_only_independent_current_state_verification',script=ref(Path(__file__)),migrationResult=ref(D/'migration-applied.json'),canonical=[ref(e),ref(p14),ref(cp)],checkedRecordedEntries=checked,allCurrentCanonicalMetadataQAShaValid=True,c12QAReproduced=c12qa,c13QAReproduced=c13qa,c13QAReproducedCount=32,c13Source115320512PixelHashesUnchanged=True,protectedCount=len(pre['protected']),allProtectedUnchanged=True,c11CurrentEastSource=ref(e),p14CurrentGeneration=ref(str(p14)+'.generation.json'),p14OriginalRequest=ref(W/'native/p14.request.json'),p14ContextExact=True,p14ProductionRegistrationPixelIdentical=True,p14ProductionRegistration=reg,frozenAtAndAssembliesUntouched=True,historicalReferencesRemainHistorical=True,currentDocumentWrites=False,productionImageWrites=False,rootProgressWrites=False,newImageGeneration=False,issueCount=0,issues=[],scopedPass=True,formalAccepted=False)
out.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));print(json.dumps(dict(file=str(out),sha256=sha(out),c12QA=len(c12qa),c13QA=len(c13qa),protected=len(pre['protected']),issues=0),indent=2))
