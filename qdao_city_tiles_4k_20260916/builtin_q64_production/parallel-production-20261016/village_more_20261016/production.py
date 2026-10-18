"""Isolated native village production: integer source crops, no final-art resize."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, shutil
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
BASE = REPO/'qdao_city_tiles_4k_20260916/builtin_q64_production'
MAP = BASE/'fishing-village-game-20261009'
OWNER = MAP/'southwest'
CONTRACT = json.loads((MAP/'production-contract.json').read_text(encoding='utf-8-sig'))
TILES = ['r09_c02', 'r10_c02']
ANCHORS = {
 'r09_c03': OWNER/'qa/block2x2-r09r10c03c04-v1-r09_c03-context-native.png',
 'r10_c03': OWNER/'qa/pair-r10c03-r11c03-v1-r10_c03-context-native.png',
 'r11_c02': OWNER/'qa/pair-r11c02-c03-v1-r11_c02-context-native.png',
}

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False,indent=2)
def origin(t): return ((int(t[5:7])-1)*4096,(int(t[1:3])-1)*4096)
def box(t,p):
 x,y=origin(t); x+=(int(p[2])-1)*1024; y+=(int(p[1])-1)*1024
 return [x-115,y-115,x+1139,y+1139]
def intersection(a,b):
 c=[max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])]
 return c if c[2]>c[0] and c[3]>c[1] else None
def selections(t):
 fs=sorted((ROOT/t).glob('selection-v*.json'))
 return read(fs[-1]) if fs else {'tile':t,'patches':{},'internalReady':False,'formalAccepted':False}
def verify():
 (REPO/'AGENTS.md').read_text(encoding='utf-8-sig')
 split=read(REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json')
 batch=next(b for b in split['batches'] if b['key']=='village_more_20261016')
 assert batch['status']=='allocated_root_reserved' and batch['tiles']==TILES
 assert (REPO/batch['outputDirectory']).resolve()==ROOT
 conflicts=[p for p in ROOT.rglob('*') if p.is_file() and 'CONFLICT' in p.name.upper()]
 assert not conflicts, conflicts
 for t in TILES:
  assert not list((OWNER/'native').glob(t+'*.png')), 'Original owner now has target native source'
 return batch
def prepare(t,p,v='v1'):
 assert t in TILES
 batch=verify(); d=ROOT/t; stem=p+'-'+v
 request=d/'requests'/f'{stem}.json'; assert not request.exists()
 target=box(t,p); scale=1254/57344
 with Image.open(CONTRACT['layoutReference']) as im:
  guide=im.convert('RGB').transform((1254,1254),Image.Transform.EXTENT,[q*scale for q in target],resample=Image.Resampling.NEAREST)
 sources=[]
 for at,ap in ANCHORS.items():
  if not ap.exists(): continue
  x,y=origin(at); ab=[x-115,y-115,x+4211,y+4211]
  inter=intersection(target,ab)
  if inter:
   with Image.open(ap) as im:
    cut=im.crop((inter[0]-ab[0],inter[1]-ab[1],inter[2]-ab[0],inter[3]-ab[1]))
    guide.paste(cut,(inter[0]-target[0],inter[1]-target[1]))
   sources.append({'path':ap.as_posix(),'sha256':sha(ap),'globalSourceBox':ab,'globalOverlapBox':inter,'role':'existing passed same-coordinate native anchor; no source resampling'})
 for ot in TILES:
  for op,info in selections(ot)['patches'].items():
   if ot==t and op==p: continue
   ob=box(ot,op); inter=intersection(target,ob)
   if not inter: continue
   source=Path(info['path'])
   with Image.open(source) as im:
    guide.paste(im.crop((inter[0]-ob[0],inter[1]-ob[1],inter[2]-ob[0],inter[3]-ob[1])),(inter[0]-target[0],inter[1]-target[1]))
   sources.append({'path':source.as_posix(),'sha256':sha(source),'globalSourceBox':ob,'globalOverlapBox':inter,'role':'current adjacent native patch; exact integer crop'})
 guidepath=d/'guides'/f'{stem}-continuity.png'; guidepath.parent.mkdir(parents=True,exist_ok=True); guide.save(guidepath)
 # Separate native reference is a crop at the nearest anchor edge, without resampling.
 first=sources[-1] if sources else None
 nativepath=d/'guides'/f'{stem}-native-reference.png'
 if first:
  sb=first['globalSourceBox']; x=max(0,min(target[0]-sb[0],sb[2]-sb[0]-1254)); y=max(0,min(target[1]-sb[1],sb[3]-sb[1]-1254))
  with Image.open(first['path']) as im: im.crop((x,y,x+1254,y+1254)).save(nativepath)
 refs=[{'path':guidepath.as_posix(),'role':'edit target: enlarged layout ONLY in unfinished area, true native overlap bands are protected'},
       {'path':CONTRACT['layoutReference'],'role':'approved whole-map layout only; keep exact buildings and roads'},
       {'path':nativepath.as_posix(),'role':'adjacent native material, scale and geometry reference; continue the corresponding overlap'},
       {'path':CONTRACT['detailStyleReference'],'role':'independent daylight Daoist Q material and architecture style only'},
       {'path':(REPO/'designs/mail-ui-v1/01-mail-event.png').as_posix(),'role':'approved Daoist Q painterly finish only; no UI or night scene'}]
 for ref in refs: ref['sha256']=sha(ref['path'])
 write(request,{'createdAt':now(),'tile':t,'patch':p,'version':v,'globalContextBox':target,'expectedNativeDimensions':[1254,1254],'nativeCoreBox':[115,115,1139,1139],'references':refs,'nativeSources':sources,'allocation':batch,'actualModel':None,'actualQuality':None,'submittedSelectors':{'model':None,'quality':None,'transparent_background':False},'status':'prepared'})
 print(json.dumps({'request':request.as_posix(),'guide':guidepath.as_posix(),'nativeReference':nativepath.as_posix(),'sources':len(sources),'box':target}))
def ingest(t,p,v,raw):
 d=ROOT/t; stem=p+'-'+v; request=d/'requests'/f'{stem}.json'; req=read(request)
 raw=Path(raw); out=d/'native'/f'{stem}.png'; out.parent.mkdir(parents=True,exist_ok=True); assert not out.exists()
 with Image.open(raw) as im: size=list(im.size); mode=im.mode; metadataKeys=list(im.info)
 shutil.copyfile(raw,out)
 prompt=request.with_suffix('.prompt.txt'); submission=request.with_suffix('.submitted.json')
 receipt={'receivedAt':now(),'sourceDefaultPath':raw.as_posix(),'savedPath':out.as_posix(),'sha256':sha(out),'rawCopyExact':sha(out)==sha(raw),'actualDimensions':size,'mode':mode,'pngMetadataKeys':metadataKeys,'tool':'image_gen__imagegen','route':'builtin','actualModel':None,'actualQuality':None,'modelEvidence':'Built-in tool returned no actual model or quality selector/metadata.','request':request.as_posix(),'requestSha256':sha(request),'prompt':prompt.as_posix(),'promptSha256':sha(prompt),'submission':submission.as_posix() if submission.exists() else None,'status':'candidate_pending_visual_review'}
 write(d/'receipts'/f'{stem}.json',receipt)
 assert size==[1254,1254], 'Preserved raw; wrong native dimensions, not selected'
 print(json.dumps(receipt))
def select(t,p,v,review):
 d=ROOT/t; stem=p+'-'+v; out=d/'native'/f'{stem}.png'; rec=read(d/'receipts'/f'{stem}.json')
 assert out.exists() and rec['actualDimensions']==[1254,1254]
 sel=selections(t); sel['patches'][p]={'path':out.as_posix(),'sha256':sha(out),'review':review,'nativeContextBox':box(t,p),'sourceCoreBox':[115,115,1139,1139]}
 sel.update(updatedAt=now(),internalReady=False,formalAccepted=False)
 num=len(list(d.glob('selection-v*.json')))+1; write(d/f'selection-v{num:03d}.json',sel)
 canvas=Image.new('RGB',(4096,4096))
 for op,info in sel['patches'].items():
  with Image.open(info['path']) as im: canvas.paste(im.convert('RGB').crop((115,115,1139,1139)),((int(op[2])-1)*1024,(int(op[1])-1)*1024))
 q=d/'qa'/f'coverage-v{num:03d}'; q.mkdir(parents=True,exist_ok=False); canvas.save(q/'candidate-4096.png')
 canvas.resize((1024,1024),Image.Resampling.LANCZOS).save(q/'preview-1024.png')
 write(q/'manifest.json',{'createdAt':now(),'tile':t,'selectedPositions':len(sel['patches']),'candidate':(q/'candidate-4096.png').as_posix(),'sha256':sha(q/'candidate-4096.png'),'dimensions':[4096,4096],'complete':len(sel['patches'])==16,'nativePixelsResampled':False,'previewOnlyResampled':True,'internalReady':False,'formalAccepted':False,'selection':(d/f'selection-v{num:03d}.json').as_posix(),'sources':sel['patches']})
 print(json.dumps({'tile':t,'selected':len(sel['patches']),'candidate':(q/'candidate-4096.png').as_posix(),'preview':(q/'preview-1024.png').as_posix()}))

if __name__=='__main__':
 {'prepare':prepare,'ingest':ingest,'select':select}[sys.argv[1]](*sys.argv[2:])
