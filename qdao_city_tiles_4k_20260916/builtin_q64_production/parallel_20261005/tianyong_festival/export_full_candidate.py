"""Export a fully painted 4K candidate, never imply full-city/game acceptance."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

TASK = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p, v): Path(p).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def ref(p): return {'file': str(Path(p).resolve()), 'sha256': sha(p)}
def checked_image(v):
    if sha(v['file']) != v['sha256']: raise ValueError('Source changed: '+v['file'])
    im=Image.open(v['file']).convert('RGBA')
    if im.size != (4096,4096): raise ValueError('Candidate is not4096-square: '+v['file'])
    return im
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--checkpoint-sha', required=True)
    p.add_argument('--review', type=Path, required=True)
    a=p.parse_args()
    cp_path=TASK/'source-checkpoint.json'
    if sha(cp_path)!=a.checkpoint_sha: raise ValueError('Checkpoint changed')
    cp=read(cp_path); src=cp['fragment']; tile=src['tile']
    im=checked_image(src); pixels=np.asarray(im)
    if not np.all(pixels[:,:,3]==255): raise ValueError('Missing or partial-alpha pixels remain; cannot export full candidate')
    review=read(a.review)
    if review.get('source',{}).get('sha256')!=src['sha256']: raise ValueError('Review belongs to another image')
    if review.get('fullyPaintedNativeTileReviewed') is not True: raise ValueError('Whole native tile not reviewed')
    if review.get('openInternalFindings'): raise ValueError('Internal findings remain unresolved')
    if review.get('formalAccepted') is not False: raise ValueError('This exporter is only for candidates')
    candidates=[]
    in_progress=[]
    for v in cp['candidateSet']:
        current=checked_image(v)
        if v['tile']==tile: continue
        arr=np.asarray(current)
        if not np.all((arr[:,:,3]==0)|(arr[:,:,3]==255)): raise ValueError('Partial alpha in candidate: '+v['tile'])
        if not np.all(arr[:,:,3]==255):
            in_progress.append({**v,'partialFragment':True,'fullyPainted':False,'actualCoveredNativePixels':int(np.count_nonzero(arr[:,:,3]==255))})
            continue
        candidates.append(v)
    if len({v['tile'] for v in candidates}) != len(candidates): raise ValueError('Duplicate tile coordinates')
    out=TASK/'candidates'/tile
    if out.exists(): raise ValueError('Candidate output already exists; never overwrite silently')
    out.mkdir(parents=True)
    final=out/(tile+'.png'); im.convert('RGB').save(final)
    if not np.array_equal(np.asarray(Image.open(final).convert('RGBA')),pixels): raise ValueError('Export changed pixels')
    now=datetime.now(timezone.utc).isoformat()
    gen={'derivedAtUtc':now,'file':str(final),'sha256':sha(final),'pixels':[4096,4096],'nativeScale':1,'operation':'LosslessRGB export of fully covered native composite; no resizing or generation','derivedFrom':[src],'sourceCheckpoint':ref(cp_path),'newModelCalls':0,'actualModel':None,'actualQuality':None,'actualModelReason':'Native tool did not expose model or quality; individual source records preserve actual evidence','fullyPainted':True,'formalAccepted':False}
    write(str(final)+'.generation.json',gen)
    entry={**src,**ref(final),'pixels':[4096,4096],'partialFragment':False,'fullyPainted':True,'nativeScale':1,'generationRecord':str(final)+'.generation.json','formalAccepted':False}
    candidates.append(entry); candidates.sort(key=lambda v:v['tile'])
    write(out/'candidate-set.json',{'createdAtUtc':now,'candidates':candidates,'completeCandidateCount':len(candidates),'inProgress':in_progress,'targetTiles':256,'formalAcceptedCount':0,'formalAccepted':False,'wholeCityComplete':False,'review':ref(a.review),'sourceCheckpoint':ref(cp_path),'coordinateDuplicates':False})
    write(out/'delivery-status.json',{'createdAtUtc':now,'tile':entry,'review':ref(a.review),'candidateSet':ref(out/'candidate-set.json'),'completeCandidateCount':len(candidates),'remainingUnpaintedTileCount':256-len(candidates),'wholeCityComplete':False,'formalAccepted':False,'clientAccepted':False,'pendingChecks':review.get('pendingExternalChecks',[])})
    if sha(cp_path)!=a.checkpoint_sha: raise ValueError('Checkpoint changed during export; export not registered')
    print(json.dumps({'output':str(final),'sha256':sha(final),'completeCandidateCount':len(candidates),'formalAccepted':False,'rootCheckpointModified':False},ensure_ascii=False))
if __name__=='__main__': main()
