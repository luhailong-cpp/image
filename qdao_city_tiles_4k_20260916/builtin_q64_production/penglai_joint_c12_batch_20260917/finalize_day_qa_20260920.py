"""Validate already reviewed day v2 and emit independent candidate ledger only."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
R=Path('E:/work/image/qdao_city_tiles_4k_20260916');B=R/'builtin_q64_production'; A=B/'penglai_joint_c12_batch_20260917';J=B/'penglai_day/r09_c10_c11_c12_joint';O=J/'output_v2_20260918'; Q=J/'qa_v2_20260918';E=J/'qa_return_edges_20260920'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).relative_to(R).as_posix()
def jread(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
outqa=J/'visual-review-v2-20260920.json';ledger=A/'day-v2-ledger-update-20260920.json';assert not outqa.exists() and not ledger.exists()
asm=jread(O/'assembly.json');im=np.array(Image.open(O/'triple-12288x4096.png'))
tiles=[]
for entry in asm['outputs']:
    p=Path(entry['file']); assert sha(p)==entry['sha256'] and Image.open(p).size==(4096,4096)
    tiles.append(np.array(Image.open(p)))
assert np.array_equal(np.concatenate(tiles,axis=1),im)
old=np.array(Image.open(J/'output/triple-12288x4096.png'));changed=np.zeros(im.shape[:2],bool)
for repair in asm['repairs']:
    for key in ('mask','flow','colorCorrection'):
        item=repair[key]; assert sha(item['path'])==item['sha256']
    assert sha(repair['nativeSource'])==repair['nativeSha256'] and sha(repair['record'])==repair['recordSha256']
    x,y,r,b=repair['registrationSupportLTRB'];mask=np.array(Image.open(repair['mask']['path']))
    changed[y:b,x:r] |= mask>0
assert np.array_equal(old[~changed],im[~changed]) and np.array_equal(old[:,:4096],im[:,:4096])
ext=np.array(Image.open(O/'extended-context.png'));assert np.array_equal(ext[115:4211,115:12403],im)
checkpoint=jread(A/'handoff-checkpoint-20260919.json'); previous=checkpoint['latestUnselectedDay']['visualQaThisTask']
for item in previous['evidence']: assert sha(item['path'])==item['sha256']
viewed=[Q/f'boundary_y{y:04d}.png' for y in (0,1024,2048,2842)]+[Q/(name+'.joined-support.png') for name in ('water-boundary-upper','water-boundary-lower')]+[Q/'repair-overlap-crossing.png']+[Q/f'intersections_y{y}.png' for y in (1024,2048,3072)]+sorted(E.glob('*.png'))
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'penglai_day','version':'output_v2_20260918','status':'local_continuity_review_passed_candidate_only','approvedForRootMerge':True,'sourceTriple':str(O/'triple-12288x4096.png'),'sourceTripleSha256':sha(O/'triple-12288x4096.png'),'assembly':str(O/'assembly.json'),'assemblySha256':sha(O/'assembly.json'),'previousSixFullInternalLines':previous,'newVisualEvidence':[{'path':str(p),'sha256':sha(p),'viewedAtOriginalPixels':True} for p in viewed],'visualFindings':'All 4 c11/c12 boundary slices, both joined-support crops, all 8 actual paste-ROI return edges, overlap crossing and all 9 internal junctions viewed at original pixels. Stone joints, rail contour and arch are continuous. Cyan water reflection paths cross the actual ROI edges without a definitive cut, duplicate contour or hard brightness stripe. Subtle local painterly reflection differences remain within continuous water. No further native repair required for this local review. The lower ROI bottom lies on the unverified outer map edge y4096; inspected its interior extent, future neighbor remains outstanding.','mechanical':{'threeTiles4096Square':True,'splitIdentity':True,'outerCropIdentity':True,'zeroMaskPixelsUnchanged':True,'c10Unchanged':True,'repairSourceAndFieldHashesVerified':True},'resamplingDisclosure':asm['sourceResampling'],'newNativeImagesGenerated':0,'wholeCityAccepted':False,'formallyAccepted':False,'runtimePublished':False,'remainingAcceptance':['other external neighbors','cross-appearance microgeometry','full 256-tile city','foreground and navigation','Unity nearest camera movement seasonal switch device performance']}
outqa.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
candidates=[]
for item in asm['outputs']:
    col=int(item['tile'][-2:]);p=Path(item['file'])
    candidates.append({'appearance':'penglai_day','displayName':'蓬莱仙岛日景','tile':item['tile'],'file':rel(p),'sha256':sha(p),'assembly':rel(O/'assembly.json'),'qa':rel(outqa),'pixels':[4096,4096],'finalPixelRectXYWH':[(col-1)*4096,32768,4096,4096],'worldRect':{'x':50+(col-1)*18.75,'z':131.25,'width':18.75,'height':18.75},'status':'candidate_local_continuity_reviewed_not_runtime_accepted','accepted':False,'runtimePublished':False})
data={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'batch':'penglai_day_c12_local_qa_20260920','status':'ready_for_root_merge','candidates':candidates,'repairRecords':[],'newUniqueCandidates':1,'replacementCandidates':2,'newNativeSources':0,'sourceAccountingNote':'32 c12 base native sources and both historical day native repairs are already in the 20260919 source-only merge; do not count again.','qa':str(outqa),'runtimePublished':False,'formalAcceptance':False}
ledger.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');print(str(ledger))
