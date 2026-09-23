"""Select a reviewed W/NW revision; preserve prior selection evidence in text."""
from pathlib import Path
import argparse, json, hashlib, subprocess, sys, re
from datetime import datetime, timezone

R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('generation');p.add_argument('--reason',required=True);a=p.parse_args()
m=re.fullmatch(r'(NW|W)(\d{2})-walk-v(\d+)',a.generation)
if not m:raise SystemExit('Only W/NW walking revision selections are authorized')
d,n=m.group(1),int(m.group(2));assert 1<=n<=16
g=R/'15-generation'/a.generation
res=subprocess.run([sys.executable,str(R/'15-tools/archive_frame.py'),'--generation-dir',str(g),'--source',str(g/'raw.png'),'--request-json',str(g/'request.json'),'--receipt-json',str(g/'receipt.json'),'--direction',d,'--kind','walk','--frame',str(n),'--process'],capture_output=True,text=True,encoding='utf-8')
if res.returncode:raise SystemExit(res.stderr)
rr=json.loads(res.stdout);final=Path(rr['processed']);operation=rr['processing']
assert rr['processedInspection']['structurallyEligible']
raw_sha=hashlib.sha256((g/'raw.png').read_bytes()).hexdigest()
slot=f'walk/{d}/{n:02d}.png';target=R/'15-delivery-preview/runtime'/slot
for other in (R/'15-delivery-preview/runtime').rglob('*.png.generation.json'):
    if other==target.with_name(target.name+'.generation.json'):continue
    if json.loads(other.read_text(encoding='utf-8'))['derivedFrom']['sha256']==raw_sha:raise SystemExit('source reused')
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
side=target.with_name(target.name+'.generation.json');prior=json.loads(side.read_text(encoding='utf-8')) if side.exists() else None
if prior:assert prior['sha256']==sha(target) and prior['character']=='15_water_dragon_scholar_boy'
now=datetime.now(timezone.utc).isoformat()
record={'schemaVersion':1,'character':'15_water_dragon_scholar_boy','slot':slot,'file':target.name,'sha256':sha(final),'selectedAt':now,'selectionAuthorization':'user authorized pose correction; scoped W/NW revision selector','selectionNote':a.reason,'derivedFrom':{'path':str(g/'raw.png'),'sha256':raw_sha,'generationRecord':str(g/'raw.png.generation.json')},'operation':operation,'actualModel':None,'actualQuality':None,'artReview':'pending_manual_cycle_review','clientValidation':'not_performed'}
history=R/'15-review'/'W-NW-selection-history.jsonl';history.parent.mkdir(exist_ok=True)
with history.open('a',encoding='utf-8') as f:f.write(json.dumps({'time':now,'slot':slot,'reason':a.reason,'oldSelection':prior,'newSelection':record},ensure_ascii=False)+'\n')
target.parent.mkdir(parents=True,exist_ok=True)
temp=target.with_name(target.name+'.next');temp.write_bytes(final.read_bytes());temp.replace(target)
tempj=side.with_name(side.name+'.next');tempj.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');tempj.replace(side)
print(slot,a.generation,record['sha256'])
