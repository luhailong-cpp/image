"""Exact-frame planning crops and native-neighbor layout inspection; no production pixels."""
from pathlib import Path
import sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from production import read,write,sha,now,deriv
F=ROOT/'r09_c15';R=F/'references';G=F/'guides';Q=F/'qa'
def ref(p):return dict(file=str(p),sha256=sha(p))
def main():
    assert not (G/'index.json').exists()
    src=R/'structure-water-fixed.png';plan=read(F/'plan.json');west=Path(plan['westCandidate'])
    assert sha(src)=='8712b0f32c5ca1b02ce3ffaa2726268801fc99bd39b3dfa4c09228eb3937f384'
    assert sha(west)==plan['westCandidateSha256']
    G.mkdir(exist_ok=True);Q.mkdir(exist_ok=True)
    im=Image.open(src).convert('RGB');assert im.size==(1254,1254)
    im=im.resize((4326,4326),Image.Resampling.LANCZOS);ext=R/'planning-extended4326.png';im.save(ext)
    deriv(ext,[src],dict(kind='planning_enlargement_only',sourcePixels=[1254,1254],outputPixels=[4326,4326],coreLTRB=[115,115,4211,4211],globalRectXYWH=[57229,32653,4326,4326],productionPixels=False))
    rows=[]
    for r in range(1,5):
      for c in range(1,5):
        box=[(c-1)*1024,(r-1)*1024,(c-1)*1024+1254,(r-1)*1024+1254];p=G/f'p{r}{c}.png';im.crop(box).save(p)
        deriv(p,[ext],dict(kind='planning_only_integer_crop',sourceBoxLTRB=box,productionPixels=False))
        rows.append(dict(id=f'p{r}{c}',**ref(p),sourceBoxLTRB=box,globalCoreXYWH=[57344+(c-1)*1024,32768+(r-1)*1024,1024,1024]))
    for r in range(1,5):
      for c in range(1,4):assert Image.open(G/f'p{r}{c}.png').crop((1024,0,1254,1254)).tobytes()==Image.open(G/f'p{r}{c+1}.png').crop((0,0,230,1254)).tobytes()
    for r in range(1,4):
      for c in range(1,5):assert Image.open(G/f'p{r}{c}.png').crop((0,1024,1254,1254)).tobytes()==Image.open(G/f'p{r+1}{c}.png').crop((0,0,1254,230)).tobytes()
    write(G/'index.json',dict(createdAt=now(),tile='r09_c15',guideCount=16,productionPixels=False,finalUseForbidden=True,nativeContextMustOverridePlanningEdges=True,source=ref(ext),guides=rows,all24Overlaps230PixelsIdentical=True))
    candidate=im.crop((115,115,4211,4211));w=Image.open(west).convert('RGB');items=[]
    for s in range(4):
      v=Image.new('RGB',(1024,1024));v.paste(w.crop((3584,s*1024,4096,(s+1)*1024)),(0,0));v.paste(candidate.crop((0,s*1024,512,(s+1)*1024)),(512,0));p=Q/f'west-layout-segment{s+1}.png';v.save(p)
      deriv(p,[west,ext],dict(kind='native_neighbor_and_upscaled_planning_seam',neighborCropLTRB=[3584,s*1024,4096,(s+1)*1024],planningCoreCropLTRB=[0,s*1024,512,(s+1)*1024],joinX=512,productionPixels=False));items.append(dict(**ref(p),joinX=512,planningOnly=True))
    day=Image.open(Path(plan['sharedDayStructure']['file'])).convert('RGB');night=Image.open(src).convert('RGB');comparison=Image.new('RGB',(2508,1254));comparison.paste(day,(0,0));comparison.paste(night,(1254,0));p=Q/'shared-night-structure-comparison.png';comparison.save(p);deriv(p,[Path(plan['sharedDayStructure']['file']),src],dict(kind='full_resolution_planning_side_by_side',productionPixels=False));items.append(dict(**ref(p),planningOnly=True))
    write(Q/'structure-index.json',dict(createdAt=now(),tile='r09_c15',planningOnly=True,formalAccepted=False,items=items))
    plan.update(stage='structure_and_guides_ready_for_root_review',rootReviewPending=True,nightStructure=ref(src),planningExtended4326=ref(ext),guideIndex=str(G/'index.json'),guideIndexSha256=sha(G/'index.json'),nativePatchCount=0);write(F/'plan.json',plan)
    write(F/'progress.json',dict(updatedAt=now(),tile='r09_c15',stage='structure_and_16_guides_waiting_root_review',nativeDetailPatches=0,planningGuides=16,completePixelCandidateTiles=0,formalAccepted=0,wholeCityComplete=False))
    print('16 planning guides; 24 overlaps exact; 5 structure QA files. No native images generated.')
if __name__=='__main__':main()
