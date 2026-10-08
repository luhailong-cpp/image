"""Refresh exports only when exact accepted manifest replay explains every changed pixel."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,uuid
import numpy as np
from PIL import Image
from commit_manifest import read,write,info,require,checked_ref,image_record
T=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint-sha',required=True);p.add_argument('manifests',nargs='+',type=Path);a=p.parse_args()
 cp_path=T/'source-checkpoint.json';cp=read(cp_path);require(info(cp_path)['sha256']==a.checkpoint_sha,'Checkpoint changed')
 sources={v['tile']:v for v in cp['candidateSet']};manifests=[];tiles=set()
 for path in a.manifests:
  path.resolve().relative_to(T);m=read(path);require(m.get('localVisualAccepted') is True,'Unreviewed manifest')
  review=read(checked_ref(m['visualReview']));require(review.get('localVisualAccepted') is True,'Unaccepted visual review')
  require(review.get('image',review.get('output',{})).get('sha256')==m['joined']['sha256'],'Review source mismatch');checked_ref(m['joined'])
  manifests.append((info(path),m))
  for patch in m['patches']:
   if (T/'candidates'/patch['destinationTile']/(patch['destinationTile']+'.png')).exists():tiles.add(patch['destinationTile'])
 plans={}
 for tile in sorted(tiles):
  out=T/'candidates'/tile;dest=out/(tile+'.png');oldgen=read(Path(str(dest)+'.generation.json'));oldref=info(dest)
  require(oldgen['sha256']==oldref['sha256'],'Export differs from generation record')
  before=np.asarray(Image.open(dest).convert('RGBA'));result=before.copy();used=[]
  for manifest_ref,m in manifests:
   for patch in m['patches']:
    if patch['destinationTile']!=tile:continue
    asset=np.asarray(Image.open(checked_ref(patch['asset'])).convert('RGBA'));l,t,r,b=patch['destinationTileLTRB']
    require(asset.shape==(b-t,r-l,4),'Asset dimensions disagree');result[t:b,l:r]=asset;used.append({'manifest':manifest_ref,'review':m['visualReview'],'patch':patch})
  current=image_record(sources[tile]);require(current['box']==[0,0,4096,4096] and np.all(current['pixels'][:,:,3]==255),'Current source is incomplete')
  require(np.array_equal(result,current['pixels']),'Manifest replay does not exactly explain current source')
  plans[tile]={'out':out,'dest':dest,'oldgen':oldgen,'oldref':oldref,'pixels':result,'used':used,'changed':int(np.count_nonzero(np.any(before!=result,axis=2)))}
 require(info(cp_path)['sha256']==a.checkpoint_sha,'Checkpoint changed before export refresh')
 now=datetime.now(timezone.utc).isoformat();token=uuid.uuid4().hex;full=[v for v in cp['candidateSet'] if v.get('fullyPainted') and not v.get('partialFragment')];partial=[v for v in cp['candidateSet'] if v not in full]
 for tile,v in plans.items():
  out=v['out'];history=out/'updates';history.mkdir(exist_ok=True);proof=history/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+token[:8]+'.json')
  write(proof,{'updatedAtUtc':now,'tile':tile,'previousExport':v['oldref'],'previousGenerationRecord':v['oldgen'],'currentSource':sources[tile],'sourceCheckpoint':info(cp_path),'reviewedPatches':v['used'],'exactReplayEqualsCurrentSource':True,'changedPixelCount':v['changed'],'noImageBackupCreated':True,'formalAccepted':False})
  temp=out/('.'+tile+'-'+token+'.png');Image.fromarray(v['pixels'][:,:,:3]).save(temp)
  require(np.array_equal(np.asarray(Image.open(temp).convert('RGBA')),v['pixels']),'Saving export changed pixels');os.replace(temp,v['dest'])
  gen={'file':str(v['dest']),'sha256':info(v['dest'])['sha256'],'derivedAtUtc':now,'pixels':[4096,4096],'nativeScale':1,'operation':'Lossless RGB export after exact reviewed native ROI replay; no resize or new generation','derivedFrom':[sources[tile]],'sourceCheckpoint':info(cp_path),'updateProof':info(proof),'newModelCalls':0,'actualModel':None,'actualQuality':None,'actualModelReason':'Actual model and quality not disclosed by host; native source records retain evidence','fullyPainted':True,'formalAccepted':False}
  write(Path(str(v['dest'])+'.generation.json'),gen)
  status=read(out/'delivery-status.json');status.update(updatedAtUtc=now,tile={**sources[tile],**info(v['dest']),'generationRecord':str(v['dest'])+'.generation.json'},completeCandidateCount=len(full),remainingUnpaintedTileCount=256-len(full),formalAccepted=False,clientAccepted=False,wholeCityComplete=False)
  status['reviewAddenda']=status.get('reviewAddenda',[])+[info(proof)];write(out/'delivery-status.json',status)
 for tile,v in plans.items():
  entries=[]
  for src in full:
   dest=T/'candidates'/src['tile']/(src['tile']+'.png')
   entries.append({**src,**info(dest),'generationRecord':str(dest)+'.generation.json'} if src['tile'] in plans else src)
  doc={'updatedAtUtc':now,'candidates':entries,'completeCandidateCount':len(full),'inProgress':partial,'targetTiles':256,'formalAcceptedCount':0,'formalAccepted':False,'wholeCityComplete':False,'sourceCheckpoint':info(cp_path),'coordinateDuplicates':False}
  write(v['out']/'candidate-set.json',doc);status=read(v['out']/'delivery-status.json');status['candidateSet']=info(v['out']/'candidate-set.json');write(v['out']/'delivery-status.json',status)
 print(json.dumps({'refreshed':[{'tile':tile,'file':str(v['dest']),'sha256':info(v['dest'])['sha256'],'changedPixels':v['changed']} for tile,v in plans.items()],'completeCandidates':len(full),'inProgress':len(partial),'rootCheckpointModified':False}))
if __name__=='__main__':main()
