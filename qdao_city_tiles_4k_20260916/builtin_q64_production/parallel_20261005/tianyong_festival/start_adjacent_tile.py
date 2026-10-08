"""Move the production cursor to an empty adjacent tile after a complete native tile."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timezone
import argparse, hashlib, json, os
import numpy as np
from PIL import Image
from commit_manifest import tile_origin, image_record, checked_ref, require, info, read, write

TASK=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tile',required=True)
    p.add_argument('--checkpoint-sha',required=True)
    p.add_argument('--review',required=True,type=Path)
    a=p.parse_args()
    cp_path=TASK/'source-checkpoint.json'; cp=read(cp_path)
    require(info(cp_path)['sha256']==a.checkpoint_sha,'Checkpoint changed')
    current=image_record(cp['fragment'])
    require(current['box']==[0,0,4096,4096] and np.all(current['pixels'][:,:,3]==255),'Current tile is incomplete')
    review=read(a.review)
    require(review.get('fullyPaintedNativeTileReviewed') is True and not review.get('openInternalFindings'),'Current tile still needs internal review')
    require(review.get('source',{}).get('sha256')==cp['fragment']['sha256'],'Review is for another image')
    origin=tile_origin(a.tile)
    below=f'r{int(a.tile[1:3])+1:02d}_c{int(a.tile[5:7]):02d}'
    tile_origin(below)
    candidates={v['tile']:deepcopy(v) for v in cp['candidateSet']}
    require(a.tile not in candidates,'Target already exists; use its real source instead')
    require(below in candidates,'No actual lower-neighbor candidate exists')
    for v in candidates.values():
        rec=image_record(v)
        require(rec['box']==[0,0,4096,4096] and np.all(rec['pixels'][:,:,3]==255),'Cannot switch while another source has missing pixels')
        v['partialFragment']=False;v['fullyPainted']=True
    out=TASK/a.tile/'current'/'v000'
    require(not out.exists(),'Initialization already exists')
    lock=TASK/'.commit-manifest.lock'
    with lock.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps({'action':'start_adjacent_tile','tile':a.tile,'pid':os.getpid()}))
    try:
        out.mkdir(parents=True)
        write(out/'source-checkpoint-input.json',cp)
        blank=out/(a.tile+'-fragment.png');Image.new('RGBA',(4096,4096),(0,0,0,0)).save(blank)
        src={**info(blank),'tile':a.tile,'pixels':[4096,4096],'tileLocalLTRB':[0,0,4096,4096],'partialFragment':True,'fullyPainted':False,'nativeScale':1,'formalAccepted':False,'generationRecord':str(blank)+'.generation.json'}
        write(Path(str(blank)+'.generation.json'),{**src,'operation':'Empty transparent coordinate scaffold, zero generated or painted pixels','newModelCalls':0,'coveredNativeTilePixels':0,'actualModel':None,'actualQuality':None,'formalAccepted':False})
        candidates[a.tile]=src
        candidate_list=[candidates[k] for k in sorted(candidates)]
        write(out/'candidate-set.json',{'candidates':candidate_list,'formalAccepted':False,'wholeCityComplete':False,'previousCompletedTileReview':info(a.review)})
        next_cp={**cp,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'version':'v000','fragment':src,'bottom':candidates[below],'coupledNeighbors':{k:v for k,v in candidates.items() if k not in [a.tile,below]},'candidateSet':candidate_list,'candidateSetRecord':info(out/'candidate-set.json'),'previousCompletedTile':cp['fragment'],'previousCompletedTileReview':info(a.review),'evidence':[info(out/'source-checkpoint-input.json'),info(a.review)],'formalAccepted':False,'geometryAndNavigationAcceptance':False}
        write(out/'source-checkpoint.json',next_cp)
        progress=read(TASK/'progress.json')
        progress.update(updatedAtUtc=next_cp['createdAtUtc'],activeTile=a.tile,checkpointVersion='v000',coveredNativeTilePixels=0,tileCoverageFraction=0,currentFragmentPixels=[4096,4096],currentFragmentTileLocalLTRB=[0,0,4096,4096],candidateSet=str(out/'candidate-set.json'),completeCandidateCount=len(candidate_list)-1,nextAction='Apply reviewed neighboring native manifests and continue contiguous expansion',wholeCityComplete=False,formalAccepted=False)
        write(out/'progress.json',progress);write(out/'current-work.json',progress)
        Image.new('RGBA',(1024,1024),(0,0,0,0)).save(out/'current-preview.png')
        write(out/'current-preview.png.generation.json',{'file':str(TASK/'current-preview.png'),'sha256':info(out/'current-preview.png')['sha256'],'derivedFrom':[src],'operation':'Empty preview for newly selected tile; not artwork','formalAccepted':False})
        require(info(cp_path)['sha256']==a.checkpoint_sha,'Checkpoint changed during preparation')
        for name in ['progress.json','current-work.json','current-preview.png','current-preview.png.generation.json','source-checkpoint.json']:
            temp=TASK/('.'+name+'.cursor-pending');require(not temp.exists(),'Pending cursor file already exists')
            temp.write_bytes((out/name).read_bytes());os.replace(temp,TASK/name)
        print(json.dumps({'activeTile':a.tile,'bottomTile':below,'completeCandidateCount':len(candidate_list)-1,'checkpoint':info(cp_path),'formalAccepted':False}))
    finally:
        lock.unlink()
if __name__=='__main__':main()
