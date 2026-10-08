"""Select a native tile using any real adjacent anchor, preserving all work in progress."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime,timezone
import argparse,os,uuid,json
import numpy as np
from PIL import Image
from commit_manifest import read,write,info,require,image_record,tile_origin

T=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--tile',required=True);p.add_argument('--anchor-tile',required=True)
 p.add_argument('--anchor-side',required=True,choices=['north','south','west','east'])
 p.add_argument('--checkpoint-sha',required=True);p.add_argument('--review',type=Path)
 p.add_argument('--allow-incomplete-cursor-switch',action='store_true')
 p.add_argument('--validate-only',action='store_true');a=p.parse_args()
 cp_path=T/'source-checkpoint.json';cp=read(cp_path);require(info(cp_path)['sha256']==a.checkpoint_sha,'Checkpoint changed')
 origin=tile_origin(a.tile);anchor_origin=tile_origin(a.anchor_tile)
 dx,dy={'north':(0,-4096),'south':(0,4096),'west':(-4096,0),'east':(4096,0)}[a.anchor_side]
 require(anchor_origin==[origin[0]+dx,origin[1]+dy],'Anchor is not adjacent in specified direction')
 require(cp['fragment']['tile']!=a.tile,'Already selected')
 candidates={};covered={}
 for v in cp['candidateSet']:
  require(v['tile'] not in candidates,'Duplicate tile');r=image_record(v)
  require(r['box']==[0,0,4096,4096],'Selection requires full coordinate scaffold')
  n=int(np.count_nonzero(r['pixels'][:,:,3]==255));covered[v['tile']]=n
  candidates[v['tile']]={**deepcopy(v),'fullyPainted':n==4096**2,'partialFragment':n!=4096**2}
 require(a.anchor_tile in candidates and covered[a.anchor_tile]==4096**2,'A complete actual adjacent anchor is required')
 current_tile=cp['fragment']['tile'];current=candidates[current_tile]
 require(current['sha256']==cp['fragment']['sha256'],'Fragment disagrees with candidate set')
 reviewed=None
 if current['fullyPainted']:
  require(a.review is not None,'Complete current tile requires its whole-native review')
  review=read(a.review);require(review.get('fullyPaintedNativeTileReviewed') is True and not review.get('openInternalFindings'),'Full review is incomplete')
  require(review.get('source',{}).get('sha256')==current['sha256'],'Review belongs to a different image');reviewed=info(a.review)
 else:require(a.allow_incomplete_cursor_switch,'Explicit incomplete cursor switch is required; work is preserved')
 new=a.tile not in candidates
 require(new or not candidates[a.tile]['fullyPainted'],'Target is already complete')
 require(not (T/'.commit-manifest.lock').exists(),'Another commit is running')
 if a.validate_only:
  print(json.dumps({'valid':True,'writesPerformed':False,'newScaffold':new,'target':a.tile,'preservedCandidates':len(candidates)}));return
 token=uuid.uuid4().hex;out=T/'cursor-switches'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+a.tile+'-'+token[:6])
 lock=T/'.commit-manifest.lock'
 with lock.open('x',encoding='utf-8') as stream:stream.write(json.dumps({'action':'select_native_tile','tile':a.tile,'pid':os.getpid()}))
 try:
  out.mkdir(parents=True);write(out/'source-checkpoint-input.json',cp)
  if new:
   blank=out/(a.tile+'-empty.png');Image.new('RGBA',(4096,4096),(0,0,0,0)).save(blank)
   src={**info(blank),'tile':a.tile,'pixels':[4096,4096],'tileLocalLTRB':[0,0,4096,4096],'nativeScale':1,'fullyPainted':False,'partialFragment':True,'formalAccepted':False,'generationRecord':str(blank)+'.generation.json'}
   write(Path(src['generationRecord']),{**src,'operation':'Empty coordinate scaffold; zero artwork pixels','newModelCalls':0,'coveredNativeTilePixels':0,'actualModel':None,'actualQuality':None})
   candidates[a.tile]=src;covered[a.tile]=0
  src=candidates[a.tile];candidate_list=[candidates[k] for k in sorted(candidates)]
  below=f'r{int(a.tile[1:3])+1:02d}_c{int(a.tile[5:7]):02d}';bottom=candidates.get(below)
  now=datetime.now(timezone.utc).isoformat();full=sum(n==4096**2 for n in covered.values())
  write(out/'candidate-set.json',{'createdAtUtc':now,'candidates':candidate_list,'formalAccepted':False,'wholeCityComplete':False})
  nxt={**cp,'createdAtUtc':now,'version':'cursor-selection','fragment':src,'anchor':candidates[a.anchor_tile],'anchorSide':a.anchor_side,'bottom':bottom,'coupledNeighbors':{k:v for k,v in candidates.items() if k not in [a.tile,a.anchor_tile]},'candidateSet':candidate_list,'candidateSetRecord':info(out/'candidate-set.json'),'previousActiveTile':current,'previousCompletedTileReview':reviewed,'evidence':[info(out/'source-checkpoint-input.json')]+([reviewed] if reviewed else []),'formalAccepted':False,'geometryAndNavigationAcceptance':False,'complete4KTilesAdded':max(0,full-11)}
  write(out/'source-checkpoint.json',nxt)
  progress=read(T/'progress.json');progress.update(updatedAtUtc=now,activeTile=a.tile,checkpointVersion='cursor-selection',coveredNativeTilePixels=covered[a.tile],tileCoverageFraction=covered[a.tile]/4096**2,currentFragmentPixels=[4096,4096],currentFragmentTileLocalLTRB=[0,0,4096,4096],candidateSet=str(out/'candidate-set.json'),completeCandidateCount=full,remainingUnpaintedTileCount=256-full,newCompleteTileCount=max(0,full-11),complete4KTilesAdded=max(0,full-11),nextAction='Apply reviewed manifests against exact current ROI sources',wholeCityComplete=False,formalAccepted=False)
  write(out/'progress.json',progress);write(out/'current-work.json',progress)
  preview=Image.open(src['file']).convert('RGBA');preview.thumbnail((1024,1024),Image.Resampling.LANCZOS);preview.save(out/'current-preview.png')
  write(out/'current-preview.png.generation.json',{'file':str(T/'current-preview.png'),'sha256':info(out/'current-preview.png')['sha256'],'derivedFrom':[src],'operation':'Progress-only downsample; never final artwork','newModelCalls':0,'formalAccepted':False})
  for v in cp['candidateSet']:require(info(v['file'])['sha256']==v['sha256'],'Source changed while selecting')
  require(info(cp_path)['sha256']==a.checkpoint_sha,'Checkpoint changed while selecting')
  for name in ['progress.json','current-work.json','current-preview.png','current-preview.png.generation.json','source-checkpoint.json']:
   temp=T/('.'+name+'-'+token+'.cursor-pending');temp.write_bytes((out/name).read_bytes());os.replace(temp,T/name)
  print(json.dumps({'activeTile':a.tile,'anchorTile':a.anchor_tile,'anchorSide':a.anchor_side,'coveredNativePixels':covered[a.tile],'completeCandidateCount':full,'checkpoint':info(cp_path),'formalAccepted':False}))
 finally:lock.unlink()
if __name__=='__main__':main()
