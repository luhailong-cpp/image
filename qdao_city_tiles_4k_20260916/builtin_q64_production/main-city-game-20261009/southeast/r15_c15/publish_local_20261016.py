from pathlib import Path
from PIL import Image
import json,hashlib,datetime,numpy as np,shutil
T=Path(__file__).resolve().parent;R=T/'review/resumed-local-repairs-20261016'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(p,j):assert not p.exists();p.write_text(json.dumps(j,indent=2,ensure_ascii=False),encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
M=read(R/'selection-manifest.json');V=read(R/'verification.json')
B=Image.open(M['base']['path']).convert('RGB');N=Image.open(M['candidate']['path']).convert('RGB')
assert N.size==(4096,4096) and sha(M['candidate']['path'])==M['candidate']['sha256']
oldqa=T/'review/assembly-008f4b817c43676ebb32/visual-qa-before-repairs.json'
reused=[];locallyRechecked=[]
for axis in ['v','h']:
 for pos in [1024,2048,3072]:
  for q in range(4):
   a,b=q*1024,(q+1)*1024;box=[pos-200,a,pos+200,b] if axis=='v' else [a,pos-200,b,pos+200]
   equal=np.array_equal(np.asarray(B.crop(box)),np.asarray(N.crop(box)))
   (reused if equal else locallyRechecked).append({'name':f'{axis}{pos}-q{q}','box':box,'pixelsUnchanged':equal})
junctions=[]
for x in [1024,2048,3072]:
 for y in [1024,2048,3072]:
  box=[x-450,y-450,x+450,y+450];assert np.array_equal(np.asarray(B.crop(box)),np.asarray(N.crop(box)))
  junctions.append({'center':[x,y],'pixelsUnchanged':True})
qa={'tile':'r15_c15','reviewedAt':now,'reviewer':'/root/seam_resume','candidate':M['candidate'],'verification':ref(R/'verification.json'),'baseVisualQA':ref(oldqa),'method':'Reuse unchanged native-sized base QA after exact pixel comparison; visually inspect generated south v2 native and five 1:1 final repair/mask/join crops. No metric-only aesthetic judgement.','reviewedLocalCrops':['south-repair-after','west-repair-real-join','west-mask-right-boundary','west-mask-upper-boundary','west-mask-lower-boundary'],'internalSeamQA':'passed','internalArtQA':'passed_after_local_native_repair','externalNeighborSeamQA':{'north':'structure_pass_finish_pending','west':'structure_pass_finish_pending','east':'own_edge_unchanged_neighbor_joint_review_pending','south':'S01_repaired_neighbor_joint_review_pending'},'reusedUnchangedSeamSegments':reused,'segmentsWithChangedOuterPortionReviewedInLocalCrops':locallyRechecked,'reusedUnchangedJunctions':junctions,'findings':[{'id':'S01','status':'resolved_local_visual_pass','box':[2120,3840,2340,4096],'selectedRepair':'south-post-v2-20261013','description':'Additional narrow column removed. Existing broad post retained. Normal wall cap on right joins post at original height without v1 step. Mask boundary has no new geometry break.','nativeAttempts':2,'unselectedRepair':'south-post-v1-20261013'},{'id':'W01','status':'resolved_local_visual_pass','box':[0,2375,95,2430],'selectedRepair':'west-grout-v1-20261013','description':'Orphan horizontal grout removed on child side; true vertical and long slab joints retained. Top, right, bottom mask boundaries visually continuous.','nativeAttempts':1},{'id':'N02','status':'pending_not_passed','severity':'nonblocking_finish','box':[950,0,2300,150],'description':'North red/gold cylinder and pavement retain brightness and fine texture transition. Base child top200 and current north neighbor bottom200 exactly equal old QA inputs; carry forward previous finding.'},{'id':'N03','status':'pending_not_passed','severity':'nonblocking_finish','box':[3450,0,3910,120],'description':'North lotus petals retain shading transition across core cut; silhouette continuous. Unchanged QA evidence reused.'},{'id':'W02','status':'pending_not_passed','severity':'nonblocking_finish','box':[0,1500,170,2750],'description':'Fine blue-grey stone grain/value still changes on vertical core boundary, visible in new west real-join crop. W01 structural repair does not clear this finish finding.'}],'eastLast115Unchanged':True,'northFirst200Unchanged':True,'actualModel':None,'formalAccepted':False,'remainingChecks':['Independent root review of local fixes','Actual east core join with r15_c16','Actual south core join with r16_c15','Deferred north/west material finish']}
write(R/'visual-qa.json',qa)
for name in ['progress.json','candidate/latest-assembly.json']:
 dst=R/('before-'+Path(name).name);assert not dst.exists();shutil.copyfile(T/name,dst)
sourcecount=len(list((T/'native').glob('*.png')))+len(list((T/'repairs').glob('*/native.png')))
latest={'schemaVersion':2,'tile':'r15_c15','publishedAt':now,'status':'internal_pass_external_finish_and_neighbor_review_pending','candidate':dict(M['candidate'],size=[4096,4096]),'context':dict(M['context'],size=[4326,4326]),'manifest':ref(R/'selection-manifest.json'),'visualQA':ref(R/'visual-qa.json'),'verification':ref(R/'verification.json'),'baseAssembly':M['baseAssembly'],'previousSelection':ref(R/'before-latest-assembly.json'),'selectedNativeRepairs':['south-post-v2-20261013','west-grout-v1-20261013'],'activeNativeCount':16,'activeRepairNativeCount':2,'actualNativeOutputCount':sourcecount,'internalArtQA':qa['internalArtQA'],'internalSeamQA':'passed','externalNeighborSeamQA':qa['externalNeighborSeamQA'],'remainingQA':[f for f in qa['findings'] if f['status']=='pending_not_passed'],'formalAccepted':False,'actualModel':None,'haloAuthority':False}
(T/'candidate/latest-assembly.json').write_text(json.dumps(latest,indent=2,ensure_ascii=False),encoding='utf-8')
p=read(T/'progress.json');p.update({'status':latest['status'],'updatedAt':now,'candidate':M['candidate']['path'],'context':M['context']['path'],'candidateSha256':M['candidate']['sha256'],'contextSha256':M['context']['sha256'],'assemblyManifest':str(R/'selection-manifest.json'),'visualQA':ref(R/'visual-qa.json'),'verification':ref(R/'verification.json'),'currentVersion':'south-v2-west-v1-20261016','actualNativeOutputCount':sourcecount,'activeRepairNativeCount':2,'internalArtQA':qa['internalArtQA'],'internalSeamQA':'passed','externalNeighborSeamQA':qa['externalNeighborSeamQA'],'remainingQA':latest['remainingQA'],'formalAccepted':False,'nextStep':'Review real east/south core joins; keep N02/N03/W02 finish pending; do not repeat accepted unchanged internal QA.'})
(T/'progress.json').write_text(json.dumps(p,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({'candidate':M['candidate'],'context':M['context'],'qa':ref(R/'visual-qa.json'),'selection':ref(T/'candidate/latest-assembly.json'),'actualNativeOutputCount':sourcecount,'unchangedSeamSegments':len(reused),'changedSeamSegmentOuterParts':locallyRechecked,'unchangedJunctions':len(junctions),'formalAccepted':False}))
