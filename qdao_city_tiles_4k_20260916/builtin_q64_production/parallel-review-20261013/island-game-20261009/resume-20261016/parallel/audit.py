import json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import numpy as np

ROOT=Path('D:/work/image')
BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
PROD=BASE/'parallel-production-20261013'
OUT=Path(__file__).parent
OLD=BASE/'parallel-review-20261013/island-game-20261009/resume-v03/parallel'
OUT.mkdir(parents=True,exist_ok=True)
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def path(p):
 p=Path(p);return p if p.is_absolute() else ROOT/p
def read(p):return json.loads(path(p).read_text(encoding='utf-8-sig'))
def info(p):
 p=path(p);return {'file':p.as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def save(n,d):
 p=OUT/n;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2,default=lambda v:int(v) if isinstance(v,np.integer) else str(v)),encoding='utf-8')
def pos(st):
 m=re.search(r'(r\d+_c\d+)_[ps](\d+)_(\d+)',st)
 return (m[1],int(m[2]),int(m[3])) if m else None
def image(p):return Image.open(path(p)).convert('RGB')
started=now();baseline=read(OLD/'summary.json');bs=read(OLD/'snapshot.json')
split=read(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')
keys=['island-west-residences','island-east-residences','island-northwest-east-extension']
batches=[b for b in split['batches'] if b['key'] in keys]
metadata={};native={};tilebatch={};selected={};holds=[];warnings=[]
def md(p):
 p=path(p);k=p.as_posix()
 if k not in metadata:metadata[k]={'source':info(p),'content':read(p)}
 return metadata[k]['content']
for b in batches:
 for t in b['tiles']:tilebatch[t]=b['key']
 for p in sorted(path(b['outputDirectory']).glob('native/*.png')):
  po=pos(p.stem)
  if not po:continue
  with Image.open(p) as im:dim=list(im.size)
  native[p.stem]={'id':p.stem,'tileId':po[0],'subrow':po[1],'subcolumn':po[2],'batch':b['key'],'dimensions':dim,**info(p)}
def select(st,expected=None):
 n=native[st]
 assert n['dimensions']==[1254,1254]
 if expected:assert n['sha256']==expected
 selected[pos(st)]=st
# Retain only the r02_c02 explicit selections: this unchanged row has two holds.
for t in baseline['tiles']:
 if t['tileId']=='r02_c02':
  for row in t['selectedCoreMatrix']:
   for v in row:
    if v:select(v['id'],v['sha256'])
w=PROD/keys[0]
for prefix in ['c02-north-progress','c03-progress','c04-progress']:
 fs=sorted(w.glob(prefix+'-v*.json'))
 d=md(fs[-1])
 for v in d.get('selectedSources',d.get('selected',[])):
  select(v['stem'],v.get('sha256',v.get('raw',{}).get('sha256')))
  q=v.get('quickReview',v.get('qa'))
  if q:md(q['path'])
# Keep source-coordinate holds out of selected count; the r02_c03 assembly deliberately contains s04_04 anyway.
d=md(w/'qa/c02-geometry-review/continue-repair-result-v01.json')
for h in d['hold']:
 po=pos(h['coordinate']);selected.pop(po,None);holds.append(h)
for v in d['continuationSelected']:select(v['stem'],v['sha256'])
for f in sorted((PROD/keys[1]/'selections').glob('*')):
 ss=sorted(f.glob('selection-v*.json'))
 if ss:
  d=md(ss[-1])
  for v in d['selected'].values():
   select(v['id'],v['sha256'])
   if v.get('review'):md(v['review'])
e=PROD/keys[2];ea=md(e/'qa/native-audit-v1.json');overrides=md(e/'selected-revisions.json');md(e/'progress.json')
for v in ea['records']:
 if not v.get('selected'):continue
 st=Path(v['path']).stem;coord=st.rsplit('_',1)[0]
 if coord in overrides:st=coord+'_'+overrides[coord]
 select(st)
 if st!=Path(v['path']).stem:md(e/'receipts'/(st+'.json'))
tiles=[]
for t,b in sorted(tilebatch.items()):
 ns=[n for n in native.values() if n['tileId']==t];ss=[n for n in ns if selected.get(pos(n['id']))==n['id']]
 matrix=[[None]*4 for _ in range(4)]
 for n in ss:matrix[n['subrow']-1][n['subcolumn']-1]={k:n[k] for k in ['id','file','sha256']}
 tiles.append({'tileId':t,'batch':b,'coreCount':len(ss),'fullCoverage':len(ss)==16,'adopted':False,'file':None,'sha256':None,'savedUniqueCoreCount':len({pos(n['id']) for n in ns}),'savedVersionCount':len(ns),'selectedCoreMatrix':matrix,'formalAccepted':False,'currentCandidates':[]})
candidates=[];replay=[];boards=[];crops=[]
def board(name,panels):
 im=Image.new('RGB',(2048,2048),(22,22,22));entries=[]
 for i,v in enumerate(panels):
  a=v['im'];wide=a.width>=a.height
  x=(i%2)*1024 if wide else (i%8)*256
  y=(i//2)*256 if wide else (i//8)*1024
  if a.size==(512,512):x=(i%4)*512;y=(i//4)*512
  assert x+a.width<=2048 and y+a.height<=2048
  im.paste(a,(x,y));entries.append({k:v[k] for k in v if k!='im'}|{'destination':[x,y,x+a.width,y+a.height]})
 p=OUT/(name+'.png')
 if p.exists():assert image(p).tobytes()==im.tobytes()
 else:im.save(p)
 boards.append({'name':name,**info(p),'panels':entries})
def candidate(t,f,rec,kind,sources):
 im=image(f);assert im.size==(4096,4096)
 d={'tileId':t,'kind':kind,**info(f),'dimensions':[4096,4096],'record':info(rec),'adopted':False,'formalAccepted':False,'sources':sources,'currentEffectiveSourceMismatch':[],'status':'pending_visual_review'}
 for n in sources:
  po=pos(Path(n['file']).stem);cur=selected.get(po)
  if cur!=Path(n['file']).stem:d['currentEffectiveSourceMismatch'].append({'coordinate':list(po),'candidateId':Path(n['file']).stem,'selectedId':cur})
 candidates.append(d);next(x for x in tiles if x['tileId']==t)['currentCandidates'].append({k:d[k] for k in ['file','sha256','kind']})
 return d,im
for rec in sorted(w.glob('tiles/*.assembly.json')):
 d=md(rec);t=d['tileId'];src=[{**info(v['path']),'sourceId':v['sourceId'],'kind':v.get('kind')} for v in d['sources']]
 c,im=candidate(t,d['output']['path'],rec,'production_candidate_with_dp_overlap_seam',src);assert c['sha256']==d['output']['sha256']
 p=path(d['provenance']['path']);assert sha(p)==d['provenance']['sha256'];ids=np.load(p)['tile_source_id'];arr=np.asarray(im);mismatch=0;pixels=0
 for v in src:
  yy,xx=np.where(ids==v['sourceId']);a=np.asarray(image(v['file']));sx=xx+115-(v['sourceId']%4)*1024;sy=yy+115-(v['sourceId']//4)*1024
  assert sx.min()>=0 and sy.min()>=0 and sx.max()<1254 and sy.max()<1254
  mismatch+=np.count_nonzero(np.any(arr[yy,xx]!=a[sy,sx],axis=1));pixels+=len(xx)
 assert mismatch==0 and pixels==4096**2
 c['rawPixelReplay']={'pixels':pixels,'mismatchPixels':mismatch,'sourceIndexPlane':info(p)};replay.append({'tileId':t,**c['rawPixelReplay']})
 for axis in ['v','h']:
  panels=[]
  for line in range(1,4):
   for seg in range(4):
    box=[line*1024-128,seg*1024,line*1024+128,(seg+1)*1024] if axis=='v' else [seg*1024,line*1024-128,(seg+1)*1024,line*1024+128]
    panels.append({'id':f'{t}-{axis}{line}-s{seg+1}','tileId':t,'tileBox':box,'im':im.crop(box)})
  board(t+'-'+axis+'-internal-100pct',panels)
 panels=[]
 for y in range(1,4):
  for x in range(1,4):
   box=[x*1024-256,y*1024-256,x*1024+256,y*1024+256]
   panels.append({'id':f'{t}-cross{x}{y}','tileId':t,'tileBox':box,'im':im.crop(box)})
 board(t+'-crossings-100pct',panels)
for rec in sorted(e.glob('tiles/*.json')):
 d=md(rec);t=d['tile'];src=[{**info(v['source']),'crop':v['crop'],'destination':v['destination']} for v in d['sources']]
 c,im=candidate(t,rec.with_suffix('.png'),rec,'production_hard_join_candidate',src);assert c['sha256']==d['sha256']
 for v in src:
  x,y=v['destination'];assert im.crop((x,y,x+1024,y+1024)).tobytes()==image(v['file']).crop(v['crop']).tobytes()
 c['rawPixelReplay']={'pixels':4096**2,'mismatchPixels':0};replay.append({'tileId':t,**c['rawPixelReplay']})
 q=md(e/f'qa/{t}/internal-review-complete-v1.json');assert q['candidateSha256']==c['sha256']
 c['producerQa']={k:q[k] for k in ['internalStatus','geometryStatus','findings','reviewedSeamCount']}
 c['producerQa']['allRecordedCropHashesUnchanged']=all(sha(v['path'])==v['sha256'] for v in q['inputs'])
 c['status']='known_surface_repairs_pending'+('_stale_current_source' if c['currentEffectiveSourceMismatch'] else '')
rec=PROD/keys[1]/'candidates/r02_c12-provisional-v001.png.derivation.json'
d=md(rec);src=[{**info(v['file']),'crop':v['coreCrop'],'destination':v['tileLocalPaste'][:2]} for v in d['sources']]
c,im=candidate(d['tileId'],d['file'],rec,'provisional_contains_one_unselected_failed_core',src);assert c['sha256']==d['sha256']
for v in src:
 x,y=v['destination'];assert im.crop((x,y,x+1024,y+1024)).tobytes()==image(v['file']).crop(v['crop']).tobytes()
c['rawPixelReplay']={'pixels':4096**2,'mismatchPixels':0};replay.append({'tileId':c['tileId'],**c['rawPixelReplay']});c['status']=d['status']
# Minimal new invalidated current-source edges: r04_c05 s04_02 a02.
po=('r04_c05',4,2);cur=selected[po];a=native[cur];panels=[]
for name,pob,boxa,boxb,axis in [('north',('r04_c05',3,2),[115,115,1139,243],[115,1011,1139,1139],'h'),('west',('r04_c05',4,1),[115,115,243,1139],[1011,115,1139,1139],'v'),('east',('r04_c05',4,3),[1011,115,1139,1139],[115,115,243,1139],'v')]:
 b=native[selected[pob]];ia=image(a['file']).crop(boxa);ib=image(b['file']).crop(boxb)
 out=Image.new('RGB',(1024,256) if axis=='h' else (256,1024))
 if name in ['north','west']:out.paste(ib,(0,0));out.paste(ia,(0,128) if axis=='h' else (128,0))
 else:out.paste(ia,(0,0));out.paste(ib,(128,0))
 p=OUT/(cur+'-'+name+'-100pct.png')
 if p.exists():assert image(p).tobytes()==out.tobytes()
 else:out.save(p)
 crops.append({'id':cur+'-'+name,'sources':[a,b],**info(p),'status':'pending_visual_review'})
# Reuse only old checks whose actual source hashes still match.
v=read(OLD/'visual-review.json');reuse=[]
for edge in v['edges']:
 valid=all(sha(s['file'])==s['sha256'] for s in edge['sources'])
 reuse.append({'id':edge['id'],'status':edge['status'],'finding':edge['finding'],'sourceHashesUnchanged':valid,'evidence':edge['output']})
# Four useful full candidate neighbor boundaries; source files pinned from old already selected images.
neighbor=dict(bs['neighbors']);ims={c['tileId']:image(c['file']) for c in candidates if c['tileId'] in ['r01_c04','r02_c03','r02_c04']}
for t in ['r03_c03','r03_c04']:ims[t]=image(neighbor[t]['file'])
external=[]
for a,b,axis in [('r01_c04','r02_c04','h'),('r02_c03','r02_c04','v'),('r02_c03','r03_c03','h'),('r02_c04','r03_c04','h')]:
 ps=[]
 for seg in range(4):
  if axis=='h':
   aa=ims[a].crop([seg*1024,3968,(seg+1)*1024,4096]);bb=ims[b].crop([seg*1024,0,(seg+1)*1024,128]);out=Image.new('RGB',(1024,256));out.paste(aa,(0,0));out.paste(bb,(0,128))
  else:
   aa=ims[a].crop([3968,seg*1024,4096,(seg+1)*1024]);bb=ims[b].crop([0,seg*1024,128,(seg+1)*1024]);out=Image.new('RGB',(256,1024));out.paste(aa,(0,0));out.paste(bb,(128,0))
  ps.append({'id':f'{a}-{b}-s{seg+1}','tiles':[a,b],'segment':seg+1,'im':out})
 board(a+'-'+b+'-external-100pct',ps)
counts={'tileCount':len(tiles),'selectedCoreCount':sum(t['coreCount'] for t in tiles),'fullCoverageTileCount':sum(t['fullCoverage'] for t in tiles),'partialTileCount':sum(0<t['coreCount']<16 for t in tiles),'emptySelectedTileCount':sum(t['coreCount']==0 for t in tiles),'savedNativeVersionCount':len(native),'savedUniqueCoreCount':sum(t['savedUniqueCoreCount'] for t in tiles),'savedCompleteGridCount':sum(t['savedUniqueCoreCount']==16 for t in tiles),'adoptedTileCount':0,'formalAcceptedCount':0,'existing4096CandidateCount':len(candidates)}
save('snapshot.json',{'startedAtUtc':started,'frozenAtUtc':now(),'baseline':info(OLD/'summary.json'),'rules':[info(ROOT/'AGENTS.md'),info(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')],'counts':counts,'tiles':tiles,'native':list(native.values()),'metadata':list(metadata.values()),'selectionMap':{'|'.join(map(str,k)):v for k,v in selected.items()},'holds':holds,'candidates':candidates,'replayedCandidatePixels':replay,'reusedChecks':reuse,'boards':boards,'newCrops':crops,'neighbors':neighbor,'newNativeIdsSinceBaseline':sorted(set(native)-{n['id'] for n in bs['native']})})
print(json.dumps({'counts':counts,'tiles':[{k:t[k] for k in ['tileId','coreCount','savedUniqueCoreCount','savedVersionCount']} for t in tiles],'boards':[b['file'] for b in boards],'newCrops':[v['file'] for v in crops]},ensure_ascii=False,indent=2))
