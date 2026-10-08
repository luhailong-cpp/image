from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,copy
from datetime import datetime,timezone
D=Path(__file__).parent; T=D.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
cp_bytes=(T/'source-checkpoint.json').read_bytes()
cp=json.loads(cp_bytes)
src=cp['bottom']
assert src['tile']=='r08_c10' and src['sha256']=='d8b35c312bcb85c42bd3f2478c6f56a9c8c1aed67e6c7b11e3e79ab5c05e766c'
assert sha(src['file'])==src['sha256']
current=Image.open(src['file']).convert('RGBA')
assert current.size==(4096,4096)
cur=np.array(current)
assert (cur[:,:,3]==255).all()
prev_review_path=T/'full-review-v017/internal-review.json'
prev_review=read(prev_review_path)
previous=prev_review['source']
assert sha(previous['file'])==previous['sha256']
old=np.array(Image.open(previous['file']).convert('RGBA'))
candidate=D/'r08_c10.png'; previous_export=info(candidate)
assert np.array_equal(np.array(Image.open(candidate).convert('RGBA')),old),'Existing snapshot differs from reviewedv017; stop instead of replacing unknown changes.'
north_path=T/'r07_c10/review-lower-two-rows-v1/visual-review.json'; north=read(north_path)
assert north['localVisualAccepted'] and north['nativePixelInspection'] and not north['blockingFindings']
assert hashlib.sha256(cur.tobytes()).hexdigest()==north['derivedSouthPixelSha256']
composed=old.copy(); region=np.zeros((4096,4096),bool); return_proofs=[]
for item in north['returnApplicationProofs']:
 p=item['patch']
 if p['destinationTile']!='r08_c10':continue
 assert sha(item['manifest']['file'])==item['manifest']['sha256']
 assert sha(p['asset']['file'])==p['asset']['sha256']
 x1,y1,x2,y2=p['destinationTileLTRB'];assert y1==0 and y2==61
 asset=np.array(Image.open(p['asset']['file']).convert('RGBA'))
 assert asset.shape==(y2-y1,x2-x1,4)
 composed[y1:y2,x1:x2]=asset;region[y1:y2,x1:x2]=True
 return_proofs.append({'manifest':item['manifest'],'asset':p['asset'],'destinationTileLTRB':p['destinationTileLTRB'],'nativeScale':1})
assert len(return_proofs)==4
assert np.array_equal(composed,cur),'Current source is not the exact four ordered reviewedreturns.'
diff=np.any(old!=cur,axis=2)
assert not diff[~region].any()
assert np.array_equal(old[61:],cur[61:])
left_path=T/'r08_c10/full-review-v017/external-left-review.json';left=read(left_path)
assert left['localVisualAccepted'] and left['leftSharedBoundaryAccepted']
south_path=Path(left['southReference']['file'])
assert sha(south_path)==left['southReference']['sha256']
assert read(south_path)['localVisualAccepted']
assert np.array_equal(old[-256:],cur[-256:])
latest=read(T/'source-checkpoint.json')
assert latest['bottom']['sha256']==src['sha256'],'Bottom source changed during verification.'
(D/'source-checkpoint-snapshot.json').write_bytes(cp_bytes)
proof={'verifiedAtUtc':now,'operation':'Refresh lossless candidate snapshot after four reviewed north returns; no new generation, no resize, no image backup, no image deletion.','previousSource':previous,'previousExport':previous_export,'currentSource':src,'sourceCheckpoint':info(D/'source-checkpoint-snapshot.json'),'northBoundaryReview':info(north_path),'previousInternalReview':info(prev_review_path),'orderedNorthReturns':return_proofs,'returnUnionTileLocalLTRB':[0,0,4096,61],'changedPixels':int(diff.sum()),'changedPixelsOutsideNorthReturns':int(diff[~region].sum()),'rows61Through4095PixelIdenticalToV017':True,'allStandardHorizontalInternalSeamsUnchanged':True,'remainingVerticalInternalSeamSegmentsUnchanged':'All x1024/2048/3072 below y61; top61px are part of the reviewed north return band.','reconstructedFromFourReturnsExactlyEqualsCurrentSource':True,'currentRgbaPixelSha256':hashlib.sha256(cur.tobytes()).hexdigest(),'northReviewRgbaPixelSha256ExactlyMatchesCurrent':True,'south256RowsPixelIdenticalToV017':True,'sourceDimensions':[4096,4096],'opaquePixels':16777216,'formalAccepted':False,'rootSourceCheckpointModified':False}
write(D/'north-update-proof.json',proof)
current.convert('RGB').save(candidate)
assert np.array_equal(np.array(Image.open(candidate).convert('RGBA')),cur),'Lossless export pixel verification failed.'
tile=copy.deepcopy(src);tile.update(info(candidate));tile['generationRecord']=str(D/'r08_c10.png.generation.json')
previous_generation=read(D/'r08_c10.png.generation.json')
gen={'derivedAtUtc':now,'file':str(candidate),'sha256':sha(candidate),'pixels':[4096,4096],'nativeScale':1,'operation':'Lossless RGB export of current fully covered native composite after reviewed four top61-row returns; no resizing or generation','derivedFrom':[src],'sourceCheckpoint':info(D/'source-checkpoint-snapshot.json'),'previousInternalReview':info(prev_review_path),'northBoundaryReview':info(north_path),'northUpdateProof':info(D/'north-update-proof.json'),'previousExportRecord':previous_generation,'newModelCalls':0,'actualModel':None,'actualQuality':None,'actualModelReason':'Native tool did not expose model or quality; individual source records preserve actual evidence','fullyPainted':True,'formalAccepted':False}
write(D/'r08_c10.png.generation.json',gen)
source_candidates=[copy.deepcopy(v) for v in cp['candidateSet'] if not v.get('partialFragment',False)]
assert len(source_candidates)==12 and len({v['tile'] for v in source_candidates})==12
for i,v in enumerate(source_candidates):
 if v['tile']=='r08_c10':source_candidates[i]=tile
candidate_set={'updatedAtUtc':now,'candidates':source_candidates,'completeCandidateCount':12,'targetTiles':256,'formalAcceptedCount':0,'formalAccepted':False,'wholeCityComplete':False,'previousInternalReview':info(prev_review_path),'northBoundaryReview':info(north_path),'sourceCheckpoint':info(D/'source-checkpoint-snapshot.json'),'coordinateDuplicates':False,'snapshotScope':'Twelve complete candidate coordinates at this export; partial active tile excluded. Read root progress.json and source-checkpoint.json for current production.'}
write(D/'candidate-set.json',candidate_set)
status={'updatedAtUtc':now,'tile':tile,'sourceImage':src,'previousInternalReview':info(prev_review_path),'northBoundaryReview':info(north_path),'northUpdateProof':info(D/'north-update-proof.json'),'candidateSet':info(D/'candidate-set.json'),'completeCandidateCount':12,'remainingUnpaintedTileCount':244,'wholeCityComplete':False,'formalAccepted':False,'clientAccepted':False,'internalReviewApplicability':'Full v017 internal review remains applicable to unchanged rows61..4095; changed top61 rows are covered by the exact-source north-boundary review. Original review is not rewritten.','boundaryStatus':{'left':{'locallyAccepted':True,'review':info(left_path),'note':'Original complete left-boundary acceptance applies below61; changed upper61 and northwest available corner covered by north review.'},'south':{'locallyAccepted':True,'review':info(south_path),'pixelsUnchanged':True},'north':{'locallyAccepted':True,'review':info(north_path),'note':'Full4096 shared border and r08 return endy61 reviewed; r07_c09 missing area excluded.'},'east':{'locallyAccepted':False,'reason':'r08_c11 and required eastern corner neighbours are not available.'}},'pendingChecks':[{'scope':'east boundary and missing neighbour corner areas','status':'pending actual neighbouring assets and native seam review'},{'scope':'nearest-camera client runtime and cross-tile movement','status':'pending'},{'scope':'whole-city256 tiles, full adjacency review, geometry and navigation','status':'pending'}],'activeProduction':{'progressFile':str(T/'progress.json'),'checkpointFile':str(T/'source-checkpoint.json'),'readDynamically':True},'snapshotRole':'Current complete r08_c10 candidate export, separate from changing active fragment. This file is not formal map delivery.'}
write(D/'delivery-status.json',status)
print(json.dumps({'candidate':info(candidate),'currentSource':src['file'],'proof':info(D/'north-update-proof.json'),'changedPixels':int(diff.sum()),'outsideTop61Changed':int(diff[61:].sum()),'candidateCount':12,'formalAccepted':False}))
