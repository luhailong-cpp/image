import json, hashlib, re
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

BASE=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
PROD=BASE/'island-game-20261009'
REVIEW=BASE/'parallel-review-20261013/island-game-20261009'
OUT=REVIEW/'resume-20261016/west'
OUT.mkdir(parents=True,exist_ok=True)
def now():return datetime.now(timezone.utc).isoformat()
def norm(p):return str(p).replace('\\','/')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(n,d):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
oldraw=read(REVIEW/'resume-v03/west/source-delta.json')
old=read(REVIEW/'resume-v03/west/summary.json')
late=read(REVIEW/'resume-v03/west-late/summary.json')
oldtiles={t['tileId']:t for t in old['tiles']}
oldtiles.update({t['tileId']:t for t in late['tiles']})
oldsource={t['tileId']:{(s['subrow'],s['subcolumn']):s for s in t.get('selectedSources',[])} for d in oldraw['zones'].values() for t in d['tiles']}
metadata=[]
def snap(z,n):
 p=PROD/z/n;data=p.read_bytes();save('snapshots/'+z+'/'+n,json.loads(data.decode('utf-8-sig')))
 metadata.append({'path':norm(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'readAtUtc':now()})
 return json.loads(data.decode('utf-8-sig'))
start=now()
nw=snap('northwest','current-adopted-20261012.json')
nr=snap('northwest','root-current-selection-20261012.json')
nri=snap('northwest','right-current-selection-20261012.json')
nwst=snap('northwest','west-current-selection-20261012.json')
sw=snap('southwest','current-native-map.json')
sources={t:{rc:{'path':s['path'],'expectedSha256':s['sha256']} for rc,s in ss.items()} for t,ss in oldsource.items()}
def cells(t,cs):
 ss={}
 for c in cs:
  m=re.search(r'_s(\d+)_(\d+)_',c['stem'])
  if m:ss[(int(m[1]),int(m[2]))]={'path':norm(c.get('image',{}).get('path',PROD/'northwest/native'/f"{c['stem']}.png")),'expectedSha256':c.get('image',{}).get('sha256')}
 sources[t]=ss
for t,d in nw.get('partialTiles',{}).items():
 if d.get('cells'):cells(t,d['cells'])
for j in [nr,nri]:
 for t,d in j['tiles'].items():cells(t,d.get('cells',[]))
for d in nwst.get('partialTiles',[]):
 if 'selectedNative' in d:cells(d['tileId'],d['selectedNative'])
 elif 'selectedNativeStems' in d:cells(d['tileId'],[{'stem':s} for s in d['selectedNativeStems']])
for t,m in sw.items():
 if re.fullmatch(r'r\d\d_c\d\d',t) and isinstance(m,list):sources[t]={(r,c):{'path':norm(PROD/'southwest/native'/f'{s}.png'),'expectedSha256':None} for r,row in enumerate(m,1) for c,s in enumerate(row,1) if s}
candidates={**{t['tileId']:t['image']|{'qaRecord':t} for t in nw['tiles']},**sw['candidateArtifacts']}
cache={}
def info(p):
 p=norm(p)
 if p not in cache:
  q=Path(p);st=q.stat()
  with Image.open(q) as im:dims=list(im.size)
  cache[p]={'path':p,'sha256':sha(p),'dimensions':dims,'bytes':st.st_size,'mtimeNs':st.st_mtime_ns}
 return cache[p]
tiles=[];changedcores=[];changedcandidates=[]
for r in range(1,15):
 z='northwest' if r<8 else 'southwest'
 for c in range(1,8):
  tid=f'r{r:02}_c{c:02}';ot=oldtiles[tid];ss=[]
  for rc,s in sorted(sources.get(tid,{}).items()):
   d=info(s['path'])|{'subrow':rc[0],'subcolumn':rc[1]};o=oldsource.get(tid,{}).get(rc)
   d['change']='added' if not o else 'unchanged' if o['sha256']==d['sha256'] else 'changed'
   d['recordedHashMatches']=s['expectedSha256'] in (None,d['sha256']);ss.append(d)
   if d['change']!='unchanged':changedcores.append({'tileId':tid,**d})
  ca=candidates.get(tid);ci=info(ca['path']) if ca else None
  t={'zone':z,'tileId':tid,'coreCount':len(ss),'selectedSources':ss,'fullCoverage':len(ss)==16,'adopted':bool(ca),'file':ci['path'] if ci else None,'sha256':ci['sha256'] if ci else None,'dimensions':ci['dimensions'] if ci else None,'formalAccepted':False,'candidateSourceChanged':bool(ci and ci['sha256']!=ot.get('sha256')),'selectedCoreDelta':len(ss)-ot['coreCount'],'candidateStatusRecord':ca,'priorEvidence':norm(REVIEW/('resume-v03/west-late/summary.json' if tid in {x['tileId'] for x in late['tiles']} else 'resume-v03/west/summary.json'))}
  if ci and t['candidateSourceChanged']:changedcandidates.append({'tileId':tid,'current':ci,'baselineFile':ot.get('file'),'baselineSha256':ot.get('sha256')})
  if not ci and len(ss)==16 and all(s['change']=='unchanged' for s in ss) and ot.get('file'):
   di=info(ot['file']);t.update(file=di['path'],sha256=di['sha256'],dimensions=di['dimensions'],diagnosticOnly=True)
  t['priorEvidenceReusable']=not t['candidateSourceChanged'] and all(s['change']=='unchanged' for s in ss)
  tiles.append(t)
selectedpaths={s['path'] for t in tiles for s in t['selectedSources']}
cutoff=datetime.fromisoformat(late['completedAtUtc']).timestamp();unselected=[]
for z in ['northwest','southwest']:
 for p in (PROD/z/'native').glob('*.png'):
  if p.stat().st_mtime>cutoff and norm(p) not in selectedpaths:
   unselected.append({'zone':z,'file':norm(p),'bytes':p.stat().st_size,'mtimeUtc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'selected':False,'classification':'post-baseline saved native file not in frozen effective selection'})
summary={'status':'frozen_prepared','startedAtUtc':start,'frozenAtUtc':now(),'baseline':[norm(REVIEW/'resume-v03/west/summary.json'),norm(REVIEW/'resume-v03/west-late/summary.json')],'metadata':metadata,'tiles':tiles,'changedSelectedCores':changedcores,'changedCandidates':changedcandidates,'postBaselineUnselectedNativeFiles':unselected,'formalAcceptedCount':0,'generationCalls':0,'productionWrites':False,'gitOperations':False}
summary['totals']={'tileCount':len(tiles),'selectedCoreCount':sum(t['coreCount'] for t in tiles),'fullCoverageCount':sum(t['fullCoverage'] for t in tiles),'partialCount':sum(0<t['coreCount']<16 for t in tiles),'emptyCount':sum(t['coreCount']==0 for t in tiles),'adopted4kCount':sum(t['adopted'] for t in tiles),'missingCoreCount':98*16-sum(t['coreCount'] for t in tiles)}
summary['zones']={z:{'selectedCoreCount':sum(t['coreCount'] for t in tiles if t['zone']==z),'fullCoverageCount':sum(t['fullCoverage'] for t in tiles if t['zone']==z),'partialCount':sum(0<t['coreCount']<16 for t in tiles if t['zone']==z),'emptyCount':sum(t['coreCount']==0 for t in tiles if t['zone']==z)} for z in ['northwest','southwest']}
save('prepared.json',summary)
print(json.dumps({'totals':summary['totals'],'zones':summary['zones'],'changedCandidates':changedcandidates,'changedSelectedCores':[{k:d[k] for k in ['tileId','subrow','subcolumn','path','change']} for d in changedcores],'postBaselineUnselectedNativeCount':len(unselected)},ensure_ascii=False,indent=2))
