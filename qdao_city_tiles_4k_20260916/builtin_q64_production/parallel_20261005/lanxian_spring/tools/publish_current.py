"""Select verified current pixels without claiming whole-city or client acceptance."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,numpy as np,shutil
B=Path(__file__).resolve().parents[1];T=B/'r08_c10';now=datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p):
    p=Path(p);im=Image.open(p)
    return {'file':str(p),'sha256':sha(p),'pixels':list(im.size)}
old=T/'selected';out=T/'selected-v2';out.mkdir(exist_ok=True)
rp=T/'repairs/final-color-patches';record=read(rp/'processing.json')
assert sha(old/'core4096.png')==record['sourceSha256']
assert sha(rp/'repair-core4096.png')==record['repairSha256']
assert sha(rp/'alpha4096.png')==record['alphaSha256']
previous=np.array(Image.open(old/'core4096.png'));new=np.array(Image.open(rp/'repair-core4096.png'));mask=np.array(Image.open(rp/'alpha4096.png'))>0
assert np.array_equal(previous[~mask],new[~mask])
ext=np.array(Image.open(old/'extended4326.png'));ext[115:4211,115:4211]=new
Image.fromarray(ext).save(out/'extended4326.png');shutil.copyfile(rp/'repair-core4096.png',out/'core4096.png')
Image.fromarray(new).resize((1254,1254),Image.Resampling.LANCZOS).save(out/'preview1254.png')
combined=np.array(Image.open(old/'combined-mask-4326.png'))>0;combined[115:4211,115:4211]|=mask
Image.fromarray(combined.astype('uint8')*255).save(out/'combined-mask-4326.png')
assert np.array_equal(np.array(Image.open(out/'extended4326.png'))[115:4211,115:4211],np.array(Image.open(out/'core4096.png')))
review={'reviewedAtUtc':now,'reviewer':'root with independent agents','qualifiedComplete4KCandidate':True,'formalAccepted':False,'clientValidated':False,'scopedChecks':['Final1254 overview viewed; central front and back1254 crops viewed1:1; cap old highlight speckles removed.','All seasonal edits remain restricted to existing surfaces; protected foliage, trunks, floor and white stone verified by source comparisons.','Four west common-edge segments and corners viewed by c10_top; stone strokes locally repaired; north/east/south external neighbors still pending.','Final pillar/leaf rectangular tone corrections actually viewed in before/after original-scale QA; mask outside pixel exact.','No upscaling in production; core and halo exact corresponding pixels.'],'knownMinorLimitations':['About1-2px west stroke residual and material-frequency variation remain.','Original small3-4px pillar-base contour step retained under same-geometry constraint.'],'remainingAcceptance':['Unbuilt neighboring tiles and full corner network','Whole-city navigation and client integration'],'evidence':[str(T/'shared-geometry/west-edge-repair/visual-review.json'),str(T/'spring-edits/central/composition-record.json'),str(T/'spring-edits/southwest/visual-review.json'),str(rp/'processing.json')]}
wr(out/'visual-review.json',review)
m=read(old/'delivery.manifest.json')
m.update({'updatedAtUtc':now,'status':'qualified_complete_4k_candidate_pending_remaining_neighbors_and_client_acceptance','qualifiedComplete4KCandidate':True,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False,'previousCompositionRecord':str(old/'delivery.manifest.json'),'previousCompositionRecordSha256':sha(old/'delivery.manifest.json'),'finalPolishRecord':str(rp/'processing.json'),'finalPolishRecordSha256':sha(rp/'processing.json'),'finalReview':str(out/'visual-review.json'),'outputs':{n:info(out/n) for n in ['core4096.png','extended4326.png','preview1254.png','combined-mask-4326.png']}})
wr(out/'delivery.manifest.json',m)
selection=read(B/'current-selection.json');tiles=[x for x in selection['currentCandidates'] if x['tile'] not in ['r08_c10','r09_c10']]
tiles.append({'tile':'r08_c10',**info(out/'core4096.png'),'halo':info(out/'extended4326.png'),'deliveryManifest':str(out/'delivery.manifest.json'),'qualifiedComplete4KCandidate':True,'formalAccepted':False})
nxt=B/('r09_c10/selected-v2' if (B/'r09_c10/selected-v2/delivery.manifest.json').exists() else 'r09_c10/selected')
if (nxt/'core4096.png').exists() and (nxt/'extended4326.png').exists():
    md=nxt/'delivery.manifest.json';done=read(md) if md.exists() else {}
    tiles.append({'tile':'r09_c10',**info(nxt/'core4096.png'),'halo':info(nxt/'extended4326.png'),'deliveryManifest':str(md) if md.exists() else None,'qualifiedComplete4KCandidate':done.get('qualifiedComplete4KCandidate',False),'formalAccepted':False,'status':done.get('status','complete_pixels_final_review_in_progress')})
selection.update({'updatedAtUtc':now,'currentCandidates':tiles,'candidateCount':len(tiles),'formalAccepted':0,'wholeCityComplete':False,'runtimePublished':False});wr(B/'current-selection.json',selection)
for name in ['progress.json','current-work.json']:
    d=read(B/name)
    for key in ['nativeDetailPatchesGenerated','nativeDetailPatchesAvailable','nativeDetailPatchesByTile','reusedSharedNativePatches','generatedLocalRepairImages','newRegionalReferences','candidatePixelCoverage','completePixelCandidatesPartiallyReviewed','completePixelCandidatesUnreviewed']:d.pop(key,None)
    d.update({'updatedAtUtc':now,'status':'partial_city_shared_geometry_production','currentTile':'r09_c10','currentPhase':'final_review_and_next_tile_preparation','newComplete4KCandidates':len(tiles)-3,'currentCandidateCount':len(tiles),'remainingCoverageTiles':256-len(tiles),'formalAccepted':0,'wholeCityComplete':False,'runtimePublished':False,'currentSelection':'current-selection.json','nextAction':'Finish r09_c10 local review and cleanup; continue adjacent missing tiles with shared day geometry.','supersededWorkflow':'Independent c10 regional and4native candidates replaced by exact shared day geometry; legacy native preparation scripts no longer used for c10.'})
    wr(B/name,d)
preview=Image.new('RGB',(1600,800))
for i,x in enumerate(tiles[-2:]):
    with Image.open(x['file']) as im:preview.paste(im.convert('RGB').resize((800,800),Image.Resampling.LANCZOS),(800*i,0))
preview.save(B/'current-preview.png');wr(B/'current-preview.png.generation.json',{'file':str(B/'current-preview.png'),'sha256':sha(B/'current-preview.png'),'role':'side_by_side_selected_tile_preview_not_spatial_map_not_final_art','sources':tiles[-2:],'operation':'4096 to800 downsample only','formalAccepted':False})
print(json.dumps({'candidateCount':len(tiles),'c10':info(out/'core4096.png'),'formalAccepted':0},ensure_ascii=False))
