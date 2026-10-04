from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
root=Path(__file__).resolve().parent
selection=json.loads((root/'selection.json').read_text(encoding='utf8'))
selected={(root/e['path']).resolve() for e in selection['entries']}
for e in selection['entries']:
 p=(root/e['path']).resolve(); assert p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']
reasons={'SE-left-load-v1':'superseded by selected straight-spear margin repair v3','SE-right-compress-v1':'rejected: disproportionate170px body/head drop','SE-left-mid-margin-v2':'rejected: bent spear shaft','SE-right-flight-v1':'rejected: requested right advance but left leg stays leading','SE-right-precontact-v1':'unselected left-front pose despite right-precontact request; existing selected left sources retained'}
out=[]
for stem,reason in reasons.items():
 p=(root/(stem+'.png')).resolve()
 assert p.parent==root and p not in selected
 if not p.exists():continue
 h=hashlib.sha256(p.read_bytes()).hexdigest();rpath=Path(str(p)+'.generation.json');r=json.loads(rpath.read_text(encoding='utf8'));assert h==r['sha256']
 r['review']={'status':'rejected or superseded','reason':reason};r['imageRetention']='PNG removed after current selections verified; prompt/source/model/SHA records retained'
 rpath.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');p.unlink();out.append(dict(file=p.name,sha256=h,reason=reason))
log=root/'retired-images.json';old=json.loads(log.read_text(encoding='utf8')).get('entries',[]) if log.exists() else[]
log.write_text(json.dumps(dict(updatedAt=datetime.now(timezone.utc).isoformat(),entries=old+out),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out))
