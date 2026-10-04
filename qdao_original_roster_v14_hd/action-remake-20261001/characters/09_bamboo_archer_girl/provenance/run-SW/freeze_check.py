import json,hashlib,datetime
from pathlib import Path
from PIL import Image
base=Path(__file__).resolve().parents[2]
report={'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[]}
for group,count in [('run-SW',16),('combat-W',34)]:
 p=base/'selection'/f'{group}.json';selection=json.loads(p.read_text(encoding='utf-8-sig'))
 rows=selection['frames'];assert len(rows)==count
 rows.sort(key=lambda r:({'hit':0,'attack':1,'cast':2,'run':3}[r['action']],r['frame']))
 review=json.loads((base/'review-parts'/f'{group}.json').read_text(encoding='utf-8-sig'))
 review_rows={r['slot']:r for r in review['frames']}
 assert len(review_rows)==count
 for row in rows:
  file=base/row['file'];sha=hashlib.sha256(file.read_bytes()).hexdigest();image=Image.open(file)
  recp=base/row['generationRecord'];recsha=hashlib.sha256(recp.read_bytes()).hexdigest();rec=json.loads(recp.read_text(encoding='utf-8-sig'))
  slot=f"{row['action']}/{row['direction']}/{row['frame']:02}"
  assert sha==row['sha256']==rec['sha256']==review_rows[slot]['sha256']
  assert recsha==row['generationRecordSha256']
  assert image.mode=='RGBA' and image.size==(1024,1024) and min(rec['nativeSize'])>=1024
  report['checks'].append({'slot':slot,'sha256':sha,'status':'passed','size':[1024,1024],'mode':'RGBA','nativeSize':rec['nativeSize'],'generationRecordSha256':recsha})
 p.write_text(json.dumps(selection,ensure_ascii=False,indent=2),encoding='utf-8')
report['result']='50 selected images, generation records and review SHAs match; native >=1024, export1024 RGBA. This does not assert whole sequence visual approval.'
(base/'provenance/run-SW/frozen-selection-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(report['result'])
