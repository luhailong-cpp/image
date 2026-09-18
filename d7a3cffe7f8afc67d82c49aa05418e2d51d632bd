from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,sys
root=Path(__file__).resolve().parent
src=Path(sys.argv[1]).resolve()
assert root.resolve() in src.parents
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
data=json.loads(src.read_text(encoding='utf-8-sig'))
cfgfile=root/'builtin_q64_production/current-batch-config.json'
cfg=json.loads(cfgfile.read_text(encoding='utf-8-sig'))
idx={(e['appearance'],e['tile']):e for e in cfg['candidates']}
for item in data['candidates']:
 e=dict(item);f=root/e['file'];assert Image.open(f).size==(4096,4096)
 if e.get('sha256'): assert sha(f)==e['sha256']
 for k in ('qa','assembly'): assert (root/e[k]).is_file()
 w=e['worldRect']
 if 'y' in w and 'z' not in w: e['worldRect']={('z' if k=='y' else k):v for k,v in w.items()}
 idx[(e['appearance'],e['tile'])]=e
cfg['candidates']=list(idx.values())
for rp in data['repairRecords']:
 assert (root/rp).is_file()
 if rp not in cfg['repairRecords']: cfg['repairRecords'].append(rp)
cfg['expectedRepairCount']=len(cfg['repairRecords'])
cfg.setdefault('mergedBatchEvidence',[]).append({'path':src.relative_to(root).as_posix(),'sha256':sha(src),'mergedAtUtc':datetime.now(timezone.utc).isoformat(),'worldAxisNormalization':'input worldRect.y mapped to canonical ground-plane z where needed'})
cfgfile.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'uniqueCandidates':len(idx),'repairRecords':len(cfg['repairRecords']),'batch':str(src)},ensure_ascii=False))
