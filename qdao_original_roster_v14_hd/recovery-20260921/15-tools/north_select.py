from pathlib import Path
import json,hashlib,subprocess,sys,shutil
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1];rt=R/'15-delivery-preview/runtime/walk';log=[]
for d,n in [('N',2),('NE',6),('NE',8)]:
 g=R/'15-generation'/f'{d}{n:02}-walk-v2'
 cmd=[sys.executable,str(R/'15-tools/archive_frame.py'),'--generation-dir',str(g),'--source',str(g/'raw.png'),'--request-json',str(g/'request.json'),'--receipt-json',str(g/'receipt.json'),'--direction',d,'--kind','walk','--frame',str(n),'--process']
 p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8');assert p.returncode==0,p.stderr
 target=rt/d/f'{n:02}.png';side=target.with_suffix('.png.generation.json');old=json.loads(side.read_text(encoding='utf-8'))
 prior=R/'15-review'/f'{d}{n:02}-superseded-selection-v1.json';prior.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf-8')
 new=json.loads((g/'raw.png.generation.json').read_text(encoding='utf-8'))
 proc=json.loads(p.stdout)['processing'];final=g/'processing-fixed088-v1/final.png';shutil.copyfile(final,target)
 rec=dict(old);rec.update(sha256=hashlib.sha256(target.read_bytes()).hexdigest(),selectedAt=datetime.now(timezone.utc).isoformat(),selectionAuthorization='User requested gait and proportion fixes; N/NE worker selected independently generated revision',selectionNote='Supersedes earlier rejected pose/scale; final offline acceptance recorded separately',derivedFrom={'path':str(g/'raw.png'),'sha256':hashlib.sha256((g/'raw.png').read_bytes()).hexdigest(),'generationRecord':str(g/'raw.png.generation.json')},operation=proc,supersedesSelectionRecord=str(prior))
 side.write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8');log.append({'slot':str(target),'oldSource':old['derivedFrom'],'newSource':rec['derivedFrom']})
# Two independently generated poses are reordered, never duplicated or transformed.
a=rt/'N/06.png';b=rt/'N/07.png';ab=a.read_bytes();bb=b.read_bytes();sa=json.loads(a.with_suffix('.png.generation.json').read_text());sb=json.loads(b.with_suffix('.png.generation.json').read_text())
a.write_bytes(bb);b.write_bytes(ab)
for target,record,original in [(a,sb,'07'),(b,sa,'06')]:
 record.update(slot=f'walk/N/{target.name}',file=target.name,selectedAt=datetime.now(timezone.utc).isoformat(),sequenceRemap={'originalRequestedFrame':original,'reason':'Order real mid-swing before terminal forward swing; no image transformation or reuse','originalGenerationRecord':record['derivedFrom']['generationRecord']})
 target.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
log.append({'swap':['N/06','N/07'],'pixelTransform':False})
(R/'15-review/N-NE-selection-corrections.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
