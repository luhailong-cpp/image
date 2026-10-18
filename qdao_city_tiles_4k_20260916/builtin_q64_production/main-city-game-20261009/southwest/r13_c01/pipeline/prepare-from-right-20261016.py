from pathlib import Path
from types import SimpleNamespace
from datetime import datetime,timezone
import json,hashlib,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[2];sys.path.insert(0,str(B))
from native_pipeline import Pipeline,pid,read
tile,row,col,attempt,prefix=sys.argv[1:];row=int(row);col=int(col)
allowed={f'r{r:02d}_c{c:02d}' for r in range(13,17) for c in range(1,5)}
assert tile in allowed and row in range(1,5) and col in range(1,5)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
allocation=B/'pipeline-tools/internal-lower-left-allocation-20261016-v01.json'
assert sha(allocation)=='0109ebd54188f4f41fbba75d5ee18aeaf5402f53e5519fbb7f563cd755a4aad6'
class ReversePipeline(Pipeline):
 def neighbor(self,row,col,side):
  rr,cc=(row,col-1) if side=='left' else (row-1,col)
  if rr>=1 and cc>=1 and self.selected_record(self.tile,rr,cc,optional=True) is None:
   self.warn('same_tile_neighbor_unavailable_reverse_independent_order',sourceTile=self.tile,patch=pid(rr,cc),side=side,note='Actual right-to-left production; no invented native anchor, original approved layout retained.')
   return None
  return super().neighbor(row,col,side)
p=ReversePipeline(tile);base_attempt=attempt+'-base'
args=SimpleNamespace(row=row,col=col,attempt=base_attempt,content_prefix=None,content_prefix_file=None,anchor_left=None,anchor_top=None)
p.prepare(args)
T=B/tile;patch=pid(row,col);base=T/'pipeline/prompts'/f'{patch}.{base_attempt}.request.json';r=read(base)
seed=Path(r['references'][0]['file']);request=T/'pipeline/prompts'/f'{patch}.{attempt}.request.json';prompt=request.with_name(f'{patch}.{attempt}.prompt.txt');target=T/'pipeline/guides'/f'{patch}.{attempt}.continuity-seed.png'
assert not any(x.exists() for x in (request,prompt,target))
from PIL import Image
im=Image.open(seed).convert('RGB');assert im.size==(1254,1254)
tilecol=int(tile.split('_c')[1]);righttile=tile if col<4 else f'r{int(tile[1:3]):02d}_c{tilecol+1:02d}';rightcol=col+1 if col<4 else 1
sel=p.selected_record(righttile,row,rightcol,optional=True)
assert sel is not None, 'No actual right neighbor to justify right-seeded production'
right,entry=p.native_record(righttile,row,rightcol,sel)
assert entry['coordinates']['contextWorldBox'][0]==r['coordinates']['contextWorldBox'][0]+1024
assert entry['coordinates']['contextWorldBox'][1]==r['coordinates']['contextWorldBox'][1]
rightcrop=(0,0,230,1254);im.paste(right.crop(rightcrop),(1024,0))
top_present=any('top' in x.get('role','') for x in r.get('neighborSources',[]))
if top_present:im.paste(Image.open(seed).crop((0,0,1254,230)),(0,0))
im.save(target)
neighbor={'file':entry['nativeFile'],'sha256':entry['nativeSha256'],'role':'exact selected right native strip, provisional geometry/material anchor only; not passed QA','generationRecord':entry['recordFile'],'generationRecordSha256':entry['recordSha256'],'sourceTile':righttile,'sourcePatch':entry['id'],'selectionEvidence':entry['selectionEvidence'],'sourceCrop':list(rightcrop),'sourceWorldBox':[entry['coordinates']['contextWorldBox'][0],entry['coordinates']['contextWorldBox'][1],entry['coordinates']['contextWorldBox'][0]+230,entry['coordinates']['contextWorldBox'][3]],'sourceResampling':False}
der={'file':str(target),'sha256':sha(target),'pixels':[1254,1254],'category':'mechanical continuity guidance only; never final game artwork','sourceResampling':False,'base':{'file':str(seed),'sha256':sha(seed)},'nativeRightSource':neighbor,'pasteTargetBox':[1024,0,1254,1254],'upperNativePriority':top_present,'formalAccepted':False}
dp=Path(str(target)+'.derivation.json');dp.write_text(json.dumps(der,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r['references'][0]={'file':str(target),'sha256':sha(target),'role':'edit target: approved coarse layout with exact real native RIGHT230 and top when available; no resampling; not final art'}
r['neighborSources'].append(neighbor)
quiet=B/'pipeline-tools/local-continuation-audit-20261011/r12-firstrow/ref-stone-context.png'
r['references']=r['references'][:4]+[{'file':str(quiet),'sha256':sha(quiet),'role':'quiet stone finish only; copy no extra geometry, seams or red scraps'}]
r['prompt']=prefix+'\nRIGHT CONTINUITY: Sharp right230 strip in Image1 is real native neighbor, extend its material and every intersecting line leftward with no artificial x1024 divider. Image5 is quiet stone finish ONLY; copy no grid, geometry or red scraps.\n\n'+r['prompt']
prompt.write_text(r['prompt'],encoding='utf-8')
r.update(promptFile=str(prompt),promptSha256=sha(prompt),referenced_image_paths=[x['file'] for x in r['references']],preparedAtUtc=datetime.now(timezone.utc).isoformat(),contentBaseRequest={'file':str(base),'sha256':sha(base)},allocationEvidence={'file':str(allocation),'sha256':sha(allocation)},rightSeedDerivation={'file':str(dp),'sha256':sha(dp)},cornerTreatment={'priority':'upper when actual native top present','pasteOrder':['right','upper only when real source exists'],'bothSourcesPresent':top_present,'blendingOrResampling':False},actualModel=None,actualQuality=None)
request.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(request),'seed':str(target),'rightSource':neighbor,'nativeTopPresent':top_present,'internalAccepted':False,'formalAccepted':False},ensure_ascii=False))
