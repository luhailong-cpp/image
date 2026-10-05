"""Place a locally reviewed registered native piece using an explicit checkpoint."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
from PIL import Image
import numpy as np
T=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
info=lambda p:{'file':str(p),'sha256':sha(p)}
def write(p,v):
    p.resolve().relative_to(T)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('registration',type=Path);ap.add_argument('version');ap.add_argument('--checkpoint-sha',required=True);a=ap.parse_args()
    d=a.registration.resolve();d.relative_to(T)
    assert sha(T/'source-checkpoint.json')==a.checkpoint_sha,'Current checkpoint changed; recheck adjacent ownership first'
    review=read(d/'visual-review.json');assert review['localAccepted']
    result=read(d/'result.json');joined=Path(result['output']['file']);assert sha(joined)==result['output']['sha256']
    b=review['tileLocalLTRB'];assert len(b)==4
    p=read(T/'source-checkpoint.json')
    for k in ['fragment','bottom']:assert sha(p[k]['file'])==p[k]['sha256']
    old=Image.open(p['fragment']['file']).convert('RGBA');ob=p['fragment']['tileLocalLTRB'];j=Image.open(joined).convert('RGBA');assert j.size==(b[2]-b[0],b[3]-b[1]);assert j.getextrema()[3]==(255,255)
    box=[min(ob[0],max(0,b[0])),min(ob[1],max(0,b[1])),max(ob[2],min(4096,b[2])),max(ob[3],min(4096,b[3]))]
    out=T/'r08_c10'/'current'/a.version;out.mkdir(parents=True,exist_ok=False)
    new=Image.new('RGBA',(box[2]-box[0],box[3]-box[1]));new.paste(old,(ob[0]-box[0],ob[1]-box[1]))
    cl,ct,cr,cb=max(0,b[0]),max(0,b[1]),min(4096,b[2]),min(4096,b[3]);new.paste(j.crop((cl-b[0],ct-b[1],cr-b[0],cb-b[1])),(cl-box[0],ct-box[1]))
    count=int((np.asarray(new)[:,:,3]==255).sum());before=int((np.asarray(old)[:,:,3]==255).sum())
    fragment=out/'r08_c10-fragment.png';new.save(fragment)
    assert b[3]<=4096 and b[0]>=0 and b[2]<=4096,'External return requires explicit coupled neighbor placement'
    op={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'1:1 placement of a reviewed registered native piece; no enlargement; missing areas remain transparent','derivedFrom':[p['fragment'],info(joined)],'registrationResult':info(d/'result.json'),'visualReview':info(d/'visual-review.json'),'fragment':info(fragment),'bottom':p['bottom'],'tileLocalLTRB':box,'newMissingPixelsFilledInsideTile':count-before,'coveredNativeTilePixels':count,'formalAccepted':False,'complete4KTilesAdded':0,'sourceCheckpointSha':a.checkpoint_sha}
    write(out/'assembly.json',op);write(Path(str(fragment)+'.generation.json'),{'file':str(fragment),'sha256':sha(fragment),'derivedFrom':op['derivedFrom'],'assembly':info(out/'assembly.json'),'newModelCalls':0,'nativeScale':1})
    cp={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'resumeAuthorizedByUser':True,'userInstruction':'继续做完给我','sourcePairVerified':True,'bottom':p['bottom'],'fragment':{**info(fragment),'tileLocalLTRB':box},'evidence':[info(out/'assembly.json'),info(d/'visual-review.json')],'formalAccepted':False,'geometryAndNavigationAcceptance':False}
    write(out/'source-checkpoint.json',cp);write(T/'source-checkpoint.json',cp)
    preview=Image.new('RGBA',(4096,4096));preview.paste(new,(box[0],box[1]));preview.thumbnail((1024,1024));pp=T/'current-preview.png';preview.save(pp)
    write(Path(str(pp)+'.generation.json'),{'file':str(pp),'sha256':sha(pp),'derivedFrom':[info(fragment)],'operation':'Progress preview downsample only, missing pixels transparent','newModelCalls':0})
    progress=read(T/'progress.json');progress.update(updatedAtUtc=datetime.now(timezone.utc).isoformat(),currentFragmentPixels=list(new.size),coveredNativeTilePixels=count,tileCoverageFraction=count/16777216,nativeCallsInThisTask=len(list((T/'r08_c10').glob('*/native.png.generation.json'))))
    write(T/'progress.json',progress);write(T/'current-work.json',{**progress,'lastCommittedPatch':str(d),'lastCommit':str(out/'assembly.json')});print(json.dumps({'sourceCheckpoint':cp,'coverage':count,'newPixels':count-before}))
if __name__=='__main__':main()
