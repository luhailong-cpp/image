from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
Z=Path(__file__).resolve().parent
fi=lambda p:dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
p=Z/'right-current-selection-20261012.json';d=json.loads(p.read_text(encoding='utf8'));before={k:json.dumps(v,sort_keys=True) for k,v in d['tiles'].items() if k!='r05_c05'}
t=d['tiles'].setdefault('r05_c05',{'matrix':[[None]*4 for _ in range(4)],'assembled4k':False,'internalClosurePassed':False,'formalAccepted':False,'authorization':'Root assigned only r05_c05 on 2026-10-16 after confirming no prior native/inflight target.','northNeighbor':'r04_c05 reserved to other worker; no unapproved north native anchor','westNeighbor':{'image':fi(Z/'tiles/connected-r05-r06-cross-v3/r05_c04_paving-north-v1_4096.png'),'record':fi(Z/'tiles/connected-r05-r06-cross-v3/r05_c04_paving-north-v1_4096.cross-native-repair.json'),'policy':'actual current east115 formal pixels only, no outside-core halo'}})
for stem in sys.argv[1:]:
 parts=stem.split('_');assert parts[:2]==['r05','c05'];r=int(parts[2][1:])-1;c=int(parts[3])-1
 im=Z/'native'/f'{stem}.png';g=json.loads(im.with_suffix('.png.generation.json').read_text())
 assert g['sha256']==fi(im)['sha256'] and g['nativeWidth']==g['nativeHeight']==1254
 t['matrix'][r][c]=parts[4]
t['cells']=[]
for r,row in enumerate(t['matrix'],1):
 for c,a in enumerate(row,1):
  if a is None:continue
  stem=f'r05_c05_s{r:02d}_{c:02d}_{a}';im=Z/'native'/f'{stem}.png'
  t['cells'].append({'stem':stem,'image':fi(im),'generationRecord':fi(im.with_suffix('.png.generation.json')),'receipt':fi(Z/'receipts'/f'{stem}.receipt.json'),'selection':'provisional_pending_whole_tile_internal_QA'})
t['selectedCount']=len(t['cells']);t['requiredCount']=16;d['updatedAtUtc']=datetime.now(timezone.utc).isoformat()
assert all(before[k]==json.dumps(d['tiles'][k],sort_keys=True) for k in before)
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'state':fi(p),'r05_c05_selected':t['selectedCount']}))

