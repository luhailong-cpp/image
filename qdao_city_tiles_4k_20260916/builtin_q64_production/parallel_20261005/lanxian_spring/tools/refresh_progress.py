"""Report exact saved coverage, select the repaired c09, and refresh preview."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
    p=Path(p);tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
now=datetime.now(timezone.utc).isoformat()
h=read(ROOT/'handoff.json')
repair=ROOT/'r08_c09/repairs/join-endpoint/repair-record.json'
r=read(repair)
assert r['maskOutsideCoreByteEqual'] and r['savedPngRereadOutsideMaskEqual'] and r['visualReview']['localRepairAccepted']
core=next(x for x in r['outputs'] if x['pixels']==[4096,4096])
halo=next(x for x in r['outputs'] if x['pixels']==[4326,4326])
assert sha(core['file'])==core['sha256'] and sha(halo['file'])==halo['sha256']
sources=[dict(x) for x in h['baselineCandidates']]
for x in sources:assert sha(x['file'])==x['sha256']
sources.append({'tile':'r08_c09','file':core['file'],'sha256':core['sha256'],'pixels':[4096,4096],'halo':halo,'repairRecord':str(repair),'repairRecordSha256':sha(repair),'seamReview':str(ROOT/'r08_c09/assembly_v2/visual-review.json'),'status':'local_seams_reviewed_remaining_outer_edges_navigation_pending','formalAccepted':False})
write(ROOT/'current-selection.json',{'schemaVersion':1,'appearance':'lanxian_spring','updatedAtUtc':now,'currentCandidates':sources,'candidateCount':len(sources),'formalAccepted':0,'wholeCityComplete':False,'runtimePublished':False,'remainingScope':'Missing tiles, full outer-edge and cross-appearance navigation/client acceptance.'})
tile_counts={}
for tile in ['r08_c09','r08_c10']:
    files=sorted((ROOT/tile/'native').glob('r??_c??.png'))
    for f in files:
        rec=read(str(f)+'.generation.json')
        assert rec['sha256']==sha(f)
    tile_counts[tile]=len(files)
for name in ['progress.json','current-work.json']:
    d=read(ROOT/name)
    d.update({'updatedAtUtc':now,'status':'partial_city_c09_repaired_c10_native_generation','currentTile':'r08_c10','currentPhase':'native_detail_generation','newComplete4KCandidates':1,'currentCandidateCount':len(sources),'formalAccepted':0,'wholeCityComplete':False,'runtimePublished':False,'nativeDetailPatchesAvailable':sum(tile_counts.values()),'nativeDetailPatchesByTile':tile_counts,'nativeDetailPatchesGenerated':3+tile_counts['r08_c10'],'generatedLocalRepairImages':2,'newRegionalReferences':1,'reusedSharedNativePatches':13,'currentSelection':'current-selection.json','completePixelCandidatesUnreviewed':0,'completePixelCandidatesPartiallyReviewed':1,'candidatePixelCoverage':'r08_c09:16/16 native pieces assembled and known seam repaired; north/east/south neighbor and navigation acceptance pending','nextAction':'Generate r08_c10 native pieces, assemble without upscaling, review internal seams and common c09 edge.'})
    write(ROOT/name,d)
preview=Image.new('RGB',(1600,800))
for i,x in enumerate(sources[-2:]):
    with Image.open(x['file']) as im:preview.paste(im.convert('RGB').resize((800,800),Image.Resampling.LANCZOS),(i*800,0))
p=ROOT/'current-preview.png';preview.save(p)
write(str(p)+'.generation.json',{'schemaVersion':1,'role':'downsampled_comparison_preview_not_final_art','generatedAt':now,'file':str(p),'sha256':sha(p),'pixels':[1600,800],'sources':sources[-2:],'operation':'each4096 tile downsampled800 LANCZOS, c08 left and c09 right; no generated detail','formalAccepted':False})
print(json.dumps({'selection':str(ROOT/'current-selection.json'),'preview':str(p),'tileNativeCounts':tile_counts,'candidateCount':len(sources),'formalAccepted':0},ensure_ascii=False))
