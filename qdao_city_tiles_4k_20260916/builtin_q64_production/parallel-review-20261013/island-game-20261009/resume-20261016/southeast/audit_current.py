from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re, copy
from PIL import Image
OUT=Path(__file__).parent
ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
PROD=BASE/'island-game-20261009/southeast'
REVIEW=BASE/'parallel-review-20261013/island-game-20261009'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d): (OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
start=now(); checks={}; docs={}
def capture(p):
 p=Path(p); a=p.stat(); b=p.read_bytes(); z=p.stat()
 checks[str(p)]={'file':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'mtimeNs':a.st_mtime_ns,'stableDuringRead':a.st_mtime_ns==z.st_mtime_ns and a.st_size==z.st_size}
 return b
for p in sorted(PROD.glob('*.json')):
 if p.name.startswith(('progress','selection','selected-native','current-zone-counts','production-resume','left-batch-state','resume-right')): docs[p.name]=json.loads(capture(p).decode('utf-8-sig'))
write('metadata-snapshot.json',{'startedAtUtc':start,'capturedAtUtc':now(),'documents':docs,'checks':list(checks.values()),'instructions':{str(p):sha(p) for p in [ROOT/'AGENTS.md',ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json']}})
old=read(REVIEW/'resume-v03/southeast/summary.json'); oldtiles={t['tileId']:t for t in old['tiles']}
tiles={tid:{'tileId':tid,'worldBox':x['worldBox'],'coreCount':0,'fullCoverage':False,'adopted':False,'file':None,'sha256':None,'formalAccepted':False,'internalPassedAsRecorded':False,'baselineCoreCount':x['coreCount']} for tid,x in oldtiles.items()}
for x in docs['progress.json']['currentAdoptedCandidates']:
 t=tiles[x['tile']];t.update(coreCount=16,fullCoverage=True,adopted=True,file=x['candidate'],sha256=x['sha256'],internalPassedAsRecorded=x['internalPassed'],productionRecord=x)
wall=docs['production-resume-wall-20261013.json']; left=docs['progress-r14_c11.json']; right=docs['progress-r13_c13.json']
for tid,file,h,authority,usable in [('r08_c10',wall['fullCandidate'],wall['fullCandidateSha256'],'production-resume-wall-20261013.json',wall['selectedCoreCount']),('r14_c11',left['candidate'],left['candidateSha256'],'progress-r14_c11.json',len(left['selectedVersions'])),('r13_c13',right['fullCoverageCandidate'],right['candidateSha256'],'progress-r13_c13.json',len(right['selectedVersions']))]:
 tiles[tid].update(coreCount=16,fullCoverage=True,file=file,sha256=h,authority=str(PROD/authority),usableSelectedCoreCount=usable,internalPassedAsRecorded=bool(tid=='r08_c10' and wall['internalAccepted']))
for tid,versions in [('r08_c13',docs['progress-r08_c13.json']['workingVersions']),('r13_c10',docs['progress-r13_c10.json']['selectedVersions']),('r14_c13',docs['progress-r14_c13.json']['selectedVersions'])]:
 ss=[]
 for coord,v in versions.items():
  p=PROD/'native'/f'{tid}_p{coord}_{v}.png';capture(p)
  with Image.open(p) as im: size=list(im.size)
  assert size==[1254,1254]
  ss.append({'coordinate':coord,'version':v,'file':str(p),'sha256':checks[str(p)]['sha256'],'dimensions':size})
 tiles[tid].update(coreCount=len(ss),selectedNativeCores=ss,usableSelectedCoreCount=len(ss))
ims={}; changed=[]
for tid,t in tiles.items():
 t['missingCoreCount']=16-t['coreCount']
 if t['file']:
  capture(t['file']); assert checks[t['file']]['sha256']==t['sha256']
  im=Image.open(t['file']).convert('RGB');assert im.size==(4096,4096);ims[tid]=im;t['dimensions']=[4096,4096]
  t['baselineSha256']=oldtiles[tid]['sha256']; t['baselineHashUnchanged']=t['sha256']==oldtiles[tid]['sha256']
  if not t['baselineHashUnchanged']:changed.append(tid)
for tid in changed:
 # Current manifests and review files are captured only for changed candidates.
 p=Path(tiles[tid]['file']+'.generation.json')
 if p.exists(): docs[str(p.relative_to(PROD))]=json.loads(capture(p).decode('utf-8-sig'))
extra=['qa/r12_c13-material-v04-20261013/root-internal-review.json','qa/r12_c13-material-v04-20261013/source-pixel-proof.json','qa/r14_c14-resume-20261013-v01/root-internal-review.json','qa/r14_c14-resume-20261013-v01/source-proof.json','qa/r13_c13-right-full-20261013-v01/actual-review.json','qa/r14_c11-resume-20261013-v01/left-visual-review.json']
for n in extra:
 if (PROD/n).exists(): docs[n]=json.loads(capture(PROD/n).decode('utf-8-sig'))
write('supplemental-snapshot.json',{'capturedAtUtc':now(),'documents':{k:v for k,v in docs.items() if '/' in k},'checks':list(checks.values())})
# Exact core replay for new complete candidates without overlays.
replays=[]
for tid,mf in [('r08_c10','selected-native-r08_c10-wall-recover-20261013-v02.json'),('r13_c13','selected-native-r13_c13-right-full-20261013-v01.json'),('r14_c14','selected-native-r14_c14-resume-20261013-v01.json')]:
 m=docs[mf]; pieces=[]
 for s in m['sources']:
  capture(s['file']);assert checks[s['file']]['sha256']==s['sha256']
  coord=re.search(r'_p(\d)(\d)_',s['file']);r,c=map(int,coord.groups());box=[(c-1)*1024,(r-1)*1024,c*1024,r*1024]
  with Image.open(s['file']) as src: equal=src.convert('RGB').crop((115,115,1139,1139)).tobytes()==ims[tid].crop(box).tobytes()
  assert equal;pieces.append({'file':s['file'],'sha256':s['sha256'],'destinationBox':box,'pixelsMatch':equal})
 replays.append({'tileId':tid,'candidateSha256':tiles[tid]['sha256'],'sources':pieces,'exactCoreReplay':True,'coveredPixels':16777216})
# Existing prior evidence is carried only when exact candidate inputs did not change.
reuse=[]
for name in ['shared-edge-reuse.json','additional-evidence-reuse.json']:
 prev=read(REVIEW/'resume-v03/southeast'/name)
 reuse.append({'evidence':str(REVIEW/'resume-v03/southeast'/name),'sha256':sha(REVIEW/'resume-v03/southeast'/name),'details':prev})
write('source-replay.json',{'newCandidateReplays':replays})
cuts=[];boards=[]
def cut(tid,name,box,kind='internal'):
 q=OUT/'cuts'/tid/(name+'.png');q.parent.mkdir(parents=True,exist_ok=True);im=ims[tid].crop(box);im.save(q)
 rec={'id':name,'tileId':tid,'file':str(q),'sha256':sha(q),'box':list(box),'dimensions':list(im.size),'kind':kind,'sourceSha256':tiles[tid]['sha256'],'pixelExact':True,'actuallyViewed':False};cuts.append(rec);return rec
def board(items,name,cols,rows=None):
 w=max(x['dimensions'][0] for x in items);h=max(x['dimensions'][1] for x in items); rows=rows or (len(items)+cols-1)//cols
 im=Image.new('RGB',(w*cols,h*rows),(45,45,45));placements=[]
 for i,x in enumerate(items):
  pos=[i%cols*w,i//cols*h];im.paste(Image.open(x['file']),(pos[0],pos[1]));placements.append({'id':x['id'],'file':x['file'],'position':pos,'dimensions':x['dimensions']})
 p=OUT/(name+'.png');im.save(p);boards.append({'file':str(p),'sha256':sha(p),'dimensions':list(im.size),'scale':1,'placements':placements,'actuallyViewed':False})
for tid in ['r08_c10','r14_c14']:
 vs=[];hs=[];js=[]
 for r in range(1,5):
  for c in range(1,4):vs.append(cut(tid,f'v-r{r}-c{c}',[c*1024-256,(r-1)*1024,c*1024+256,r*1024]))
 for r in range(1,4):
  for c in range(1,5):hs.append(cut(tid,f'h-r{r}-c{c}',[(c-1)*1024,r*1024-256,c*1024,r*1024+256]))
 for r in range(1,4):
  for c in range(1,4):js.append(cut(tid,f'j-r{r}-c{c}',[c*1024-256,r*1024-256,c*1024+256,r*1024+256]))
 for name,a,n in [('vertical',vs,4),('horizontal',hs,2)]:
  board(a[:8],tid+'-'+name+'-1',n);board(a[8:],tid+'-'+name+'-2',n)
 board(js,tid+'-junctions',3)
# r12 v04 changed ownership bounds and old unresolved sail joint.
r12=docs['qa/r12_c13-material-v04-20261013/root-internal-review.json']; named=[]
for x in r12['changedEvidenceViewed']+r12['newBoundariesViewed']:
 named.append(cut('r12_c13',x['id'],x['box'],'changed_region'))
board(named[:5],'r12_c13-changed-seams',2)
board(named[5:9],'r12_c13-new-ownership-boundaries',2)
board(named[9:],'r12_c13-whole-material',1)
board([cut('r12_c13','previous-sail-batten',[2816,3474,3328,3986],'prior_issue_recheck')],'r12_c13-sail-batten',1)
# Preserve not-passed producer issues and verify representative actual pixels.
board([cut('r13_c13','spar-join',[2816,0,3328,1024],'not_passed_sample'),cut('r13_c13','water-guide',[768,1024,1280,2048],'not_passed_sample'),cut('r14_c11','water-north-guide',[1024,0,2048,512],'not_passed_sample'),cut('r14_c11','middle-water',[1536,1792,2560,2304],'not_passed_sample')],'known-unpassed-current-samples',2)
def worldcrop(box,tids):
 im=Image.new('RGB',(box[2]-box[0],box[3]-box[1]));count=0
 for tid in tids:
  tb=tiles[tid]['worldBox'];b=[max(tb[0],box[0]),max(tb[1],box[1]),min(tb[2],box[2]),min(tb[3],box[3])]
  if b[0]<b[2] and b[1]<b[3]:im.paste(ims[tid].crop((b[0]-tb[0],b[1]-tb[1],b[2]-tb[0],b[3]-tb[1])),(b[0]-box[0],b[1]-box[1]));count+=(b[2]-b[0])*(b[3]-b[1])
 assert count==im.width*im.height
 return im
edges=[]
for a,b in [('r08_c10','r08_c11'),('r11_c13','r12_c13'),('r12_c12','r12_c13'),('r12_c13','r13_c13'),('r13_c12','r13_c13'),('r13_c11','r14_c11'),('r14_c11','r14_c12')]:
 aa=tiles[a]['worldBox'];bb=tiles[b]['worldBox'];vertical=aa[2]==bb[0];items=[]
 for i in range(4):
  box=[aa[2]-256,aa[1]+1024*i,aa[2]+256,aa[1]+1024*(i+1)] if vertical else [aa[0]+1024*i,aa[3]-256,aa[0]+1024*(i+1),aa[3]+256]
  im=worldcrop(box,[a,b]);q=OUT/'cuts'/(a+'-'+b+f'-{i+1}.png');q.parent.mkdir(exist_ok=True);im.save(q)
  rec={'id':f'{a}-{b}-{i+1}','file':str(q),'sha256':sha(q),'dimensions':list(im.size),'kind':'external_delta','worldBox':box,'tiles':[a,b],'pixelExact':True,'actuallyViewed':False};cuts.append(rec);items.append(rec)
 board(items,a+'-'+b+'-edge',4 if vertical else 2);edges.append({'tiles':[a,b],'segments':[x['id'] for x in items],'status':'pending_visual'})
for tids,cx,cy in [(['r12_c12','r12_c13','r13_c12','r13_c13'],49152,49152),(['r13_c11','r13_c12','r14_c11','r14_c12'],45056,53248)]:
 box=[cx-256,cy-256,cx+256,cy+256];im=worldcrop(box,tids);q=OUT/'cuts'/f'cross-{cx}-{cy}.png';im.save(q);rec={'id':q.stem,'file':str(q),'sha256':sha(q),'dimensions':list(im.size),'worldBox':box,'tiles':tids,'pixelExact':True,'actuallyViewed':False,'kind':'external_junction_delta'};cuts.append(rec);board([rec],q.stem,1)
write('crop-manifest.json',{'cuts':cuts,'boards':boards,'edges':edges,'operation':'exact integer crops and paste only, original source RGB, no resize/blend/generation'})
write('evidence-reuse.json',{'priorEvidence':reuse,'unchangedFullCandidateCount':sum(t.get('baselineHashUnchanged',False) for t in tiles.values()),'sourceHashRechecked':True})
# Saved but unselected native versions are not promoted by existence.
chosen=set()
for t in tiles.values():
 for x in t.get('selectedNativeCores',[]):chosen.add(x['file'])
for tid in ['r13_c10','r14_c13','r08_c13']:
 pass
unselected=[]
for tid in ['r13_c10','r14_c13','r08_c13']:
 for p in sorted((PROD/'native').glob(tid+'_p*.png')):
  if str(p) not in chosen:unselected.append({'tileId':tid,'file':str(p),'sha256':sha(p),'countedAsSelected':False})
write('saved-unselected.json',{'sources':unselected,'notPromotedByFileExistence':True})
counts={'targetTiles':49,'fullCoverage':sum(t['fullCoverage'] for t in tiles.values()),'adoptedFullCoverage':sum(t['adopted'] for t in tiles.values()),'partialTiles':sum(0<t['coreCount']<16 for t in tiles.values()),'emptyTiles':sum(t['coreCount']==0 for t in tiles.values()),'candidateCoverageCores':sum(t['coreCount'] for t in tiles.values()),'usableSelectedCoreCount':sum(t.get('usableSelectedCoreCount',t['coreCount']) for t in tiles.values()),'formalAccepted':0}
counts['unadoptedFullCandidates']=counts['fullCoverage']-counts['adoptedFullCoverage'];counts['missingNativeCores']=784-counts['candidateCoverageCores'];counts['missingFullTiles']=49-counts['fullCoverage']
write('summary.json',{'schemaVersion':4,'zone':'southeast','status':'visual_pending','snapshotStartedAtUtc':start,'snapshotCompletedAtUtc':now(),'counts':counts,'tiles':list(tiles.values()),'changedFullCandidates':changed,'baseline':str(REVIEW/'resume-v03/southeast/summary.json'),'generationPerformed':False,'aiEditPerformed':False,'productionModified':False,'sharedGitTouched':False,'formalAccepted':0})
write('source-checks.json',{'checks':list(checks.values()),'allStableDuringRead':all(x['stableDuringRead'] for x in checks.values())})
print(json.dumps({'counts':counts,'changed':changed,'cutCount':len(cuts),'boards':[str(Path(x['file']).name) for x in boards]},ensure_ascii=False))
