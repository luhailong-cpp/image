"""Commit a visually reviewed native patch together with its changed lower-neighbor band."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
from PIL import Image
import numpy as np
from checkpoint_candidates import carry
TASK=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
info=lambda p:{'file':str(p),'sha256':sha(p)}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('patch_dir',type=Path);ap.add_argument('version');a=ap.parse_args()
    d=a.patch_dir.resolve();d.relative_to(TASK)
    review=read(d/'visual-review.json');assert review['localAccepted']
    req=read(d/'request.json');prep=read(d/'preparation.json');prev=read(TASK/'source-checkpoint.json')
    for s in prep['nativeInputs']:assert sha(s['file'])==s['sha256']
    old=Image.open(prev['fragment']['file']).convert('RGBA');oldbox=prev['fragment']['tileLocalLTRB']
    old_covered=int((np.asarray(old)[:,:,3]==255).sum())
    b=req['tileLocalCropLTRB'];xmin=min(oldbox[0],max(0,b[0]));ymin=min(oldbox[1],max(0,b[1]));xmax=max(oldbox[2],min(4096,b[2]));ymax=max(oldbox[3],min(4096,b[3]))
    out=TASK/'r08_c10'/'current'/a.version;out.mkdir(parents=True,exist_ok=False)
    new=Image.new('RGBA',(xmax-xmin,ymax-ymin),(0,0,0,0));new.paste(old,(oldbox[0]-xmin,oldbox[1]-ymin))
    joined=Image.open(d/'joined.png').convert('RGBA')
    cl,ct,cr,cb=max(0,b[0]),max(0,b[1]),min(4096,b[2]),min(4096,b[3])
    new.paste(joined.crop((cl-b[0],ct-b[1],cr-b[0],cb-b[1])),(cl-xmin,ct-ymin))
    covered=int((np.asarray(new)[:,:,3]==255).sum())
    fragment=out/'r08_c10-fragment.png';new.save(fragment)
    bottom=Path(prev['bottom']['file'])
    if b[3]>4096:
        lower=Image.open(bottom).convert('RGB');lower.paste(joined.convert('RGB').crop((cl-b[0],4096-b[1],cr-b[0],1254)),(cl,0))
        bottom=out/'r09_c10.png';lower.save(bottom)
    operation={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'1:1 placement of reviewed joined native fragment and any coupled lower-neighbor return band; explicit transparent missing areas; no enlargement','derivedFrom':[prev['fragment'],prev['bottom'],info(d/'joined.png')],'patchAssembly':info(d/'assembly.json'),'visualReview':info(d/'visual-review.json'),'fragment':info(fragment),'bottom':info(bottom),'tileLocalLTRB':[xmin,ymin,xmax,ymax],'newMissingPixelsFilledInsideTile':covered-old_covered,'coveredNativeTilePixels':covered,'complete4KTilesAdded':0,'formalAccepted':False}
    write(out/'assembly.json',operation)
    for p in [fragment]+([bottom] if bottom.parent==out else []):write(Path(str(p)+'.generation.json'),{'file':str(p),'sha256':sha(p),'derivedFrom':operation['derivedFrom'],'assembly':info(out/'assembly.json'),'operation':operation['operation'],'newModelCalls':0})
    if not (TASK/'source-checkpoint-initial.json').exists():write(TASK/'source-checkpoint-initial.json',prev)
    checkpoint={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'resumeAuthorizedByUser':True,'userInstruction':'继续做完给我','sourcePairVerified':True,'bottom':info(bottom),'fragment':{**info(fragment),'tileLocalLTRB':[xmin,ymin,xmax,ymax]},'evidence':[info(out/'assembly.json'),info(d/'visual-review.json')],'formalAccepted':False,'geometryAndNavigationAcceptance':False}
    checkpoint=carry(prev,checkpoint,out)
    write(out/'source-checkpoint.json',checkpoint);write(TASK/'source-checkpoint.json',checkpoint)
    preview=Image.new('RGBA',(4096,4096),(0,0,0,0));preview.paste(new.convert('RGBA'),(xmin,ymin));preview.thumbnail((1024,1024))
    pp=TASK/'current-preview.png';preview.save(pp)
    write(Path(str(pp)+'.generation.json'),{'file':str(pp),'sha256':sha(pp),'derivedFrom':[info(fragment)],'operation':'Transparent missing-area canvas downsampled only for progress preview; not complete artwork','newModelCalls':0})
    native_count=len(list((TASK/'r08_c10').rglob('native.png.generation.json')))
    progress={'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'tianyong_festival','status':'native_expansion_in_progress','targetTiles':256,'activeTile':'r08_c10','nativeCallsInThisTask':native_count,'newCompleteTileCount':0,'formalAccepted':0,'wholeCityComplete':False,'clientAccepted':False,'currentFragmentPixels':[new.width,new.height],'coveredNativeTilePixels':covered,'tileCoverageFraction':covered/16777216,'sourceCheckpoint':str(TASK/'source-checkpoint.json'),'currentPreview':str(pp),'nextAction':'Continue adjacent missing native patch; inspect all affected joins.'}
    write(TASK/'progress.json',progress);write(TASK/'current-work.json',{**progress,'lastCommittedPatch':req['patch'],'lastCommit':str(out/'assembly.json')})
    print(json.dumps(checkpoint))
if __name__=='__main__':main()
