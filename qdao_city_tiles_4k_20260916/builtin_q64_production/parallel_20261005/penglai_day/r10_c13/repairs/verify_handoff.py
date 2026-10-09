from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;T=R.parent
sys.path.insert(0,str(R));import seam_local as s
def bbox(m):
    yy,xx=np.where(m)
    return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
def main():
    south=R/'r10_c13-combined-v11.png';north=R/'r09_c13-north-revised-v8.png'
    raw=T/'tiles/r10_c13-candidate.png';nbase=T.parent/'tiles/current/r09_c13-candidate-v4b.png'
    a=s.arr(south);b=s.arr(north);assert a.shape==b.shape==(4096,4096,3)
    sm=np.any(a!=s.arr(raw),axis=2);nm=np.any(b!=s.arr(nbase),axis=2)
    masks=[]
    for name,m,src,base in [('r10_c13-all-changes-v11.png',sm,south,raw),('r09_c13-north-changes-v8.png',nm,north,nbase)]:
        fp=R/name;Image.fromarray(m.astype('uint8')*255).save(fp);s.h.p.derived(fp,[src,base],{'method':'exact changed pixels binary mask'});masks.append({'file':str(fp),'sha256':s.h.p.sha(fp),'bboxLTRB':bbox(m),'pixelCount':int(m.sum())})
    locked=np.array_equal(a[:,3981:],s.arr(R/'r10_c13-combined-v5.png')[:,3981:]);assert locked,'East115 anchor changed'
    records=[]
    for p in sorted((R/'native').glob('*.png')):
        rec=s.h.p.read(str(p)+'.generation.json');source=Path(rec['toolResultPath']);assert rec['sha256']==s.h.p.sha(p)==s.h.p.sha(source);assert Image.open(p).size==(1254,1254);records.append({'file':str(p),'sha256':rec['sha256'],'sourceVerified':True,'record':str(p)+'.generation.json','actualModel':rec['actualModel'],'actualQuality':rec['actualQuality']})
    eastprop=T.parent/'r09_c14/repairs/west/output/proposal-v1.json';e=s.h.p.read(eastprop);em=np.asarray(Image.open(e['mask']))>0;et=np.zeros((4096,4096),bool);et[:,3469:]=em[:,:627];overlap=nm&et
    fp=R/'r09_c13-southeast-conflict-with-c14-west.png';Image.fromarray(overlap.astype('uint8')*255).save(fp);s.h.p.derived(fp,[north,nbase,Path(e['mask'])],{'method':'binary overlap of current north seam changes with existing c13/c14 west joint mask; requires root corner QA'})
    board=np.concatenate([b[3396:,3396:],s.arr(e['westCandidate'])[3396:,3396:]],axis=1);s.save(board,R/'r09_c13-southeast-conflict-native-review.png',[north,Path(e['westCandidate'])],{'method':'native700x700 current north proposal left versus east-joint proposal right; separate alternatives, not combined'})
    changedlast=np.any(a!=s.arr(R/'r10_c13-combined-v6.png'),axis=2)
    out={'status':'parent_ready_local_internal_and_north_seam_reviewed_global_corners_pending','createdAt':s.h.p.stamp(),'south':{'file':str(south),'sha256':s.h.p.sha(south),'base':str(raw),'baseSha256':s.h.p.sha(raw),'globalOriginXY':[49152,36864],'mask':masks[0]},'north':{'file':str(north),'sha256':s.h.p.sha(north),'base':str(nbase),'baseSha256':s.h.p.sha(nbase),'globalOriginXY':[49152,32768],'mask':masks[1]},'east115LockedToV5':locked,'newAIRepairSources':records,'formalAccepted':False,'clientAccepted':False,'review':{'scale':'native1254 context and six full4096 seam strip stacks; native320px nine intersections','files':['combined-v6-y1024.png','combined-v6-y2048.png','combined-v8-junctions.png','combined-v7-x1024.png','combined-v7-x2048.png','combined-v7-y3072.png','combined-v11-x3072.png','north-combined-shared-v5.png','north-combined-returns-0-v5.png','north-combined-returns-1024-v5.png','north-combined-returns-2048-v7.png','north-combined-returns-2842-v7.png','cap-final-review.png','combined-v11-junctions.png'],'lastChangeComparedWithV6BBox':bbox(changedlast),'findings':['Roof x1024 pigment seam, paving y3072 offset and wall y3072 band repaired with native AI source and exact ownership masks.','Fabric agent three accepted local repairs integrated with exact masks; two canopy stripes and p31 bevels continuous.','North shared edge repainted through golden roof, foliage, table endpoint, stairs and paving; top/bottom/side returns inspected.','The final stair cap uses native ownership from the whole cap source inside joint box [2800,400,2908,780], retaining v9 stair tread and paving outside; both cap bevel and stair tread were visually checked in cap-final-review.png.','Fine local painterly texture changes remain at some ownership returns, without disconnected/doubled contour.','West shared edge and global four-tile corners belong to subsequent integration.']},'conflictWithC14West':{'proposal':str(eastprop),'mask':str(fp),'pixelCount':int(overlap.sum()),'tileBBoxLTRB':bbox(overlap),'globalBBoxLTRB':[49152+bbox(overlap)[0],32768+bbox(overlap)[1],49152+bbox(overlap)[2],32768+bbox(overlap)[3]],'action':'Do not blindly overwrite either proposal. Root must resolve the bottom-right c13 corner jointly with adjacent tiles.'},'rejectedTrials':['internal-v1/v2 minimum-error native overlaps had mismatch in geometry; not used','combined-v4 through v10 superseded by v11; v10 entire result rejected due stair-tread tongue, used only masked cap-face subregion'],'methodLimits':{'geometricShift':0,'imageResample':False,'imageBlur':False,'imageFeather':False,'RGBFields':'Per-stage caps: existing north-tone14; individual AI perimeter10; neighbor-return12 and final fixed-cut direct color return18. Exact float fields stored; these are separate stages, not a single total-cap claim.'}}
    s.h.p.write(R/'handoff-final-v11.json',out);print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()


