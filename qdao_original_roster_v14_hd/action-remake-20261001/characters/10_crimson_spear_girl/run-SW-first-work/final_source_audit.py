from pathlib import Path
from PIL import Image
import json,hashlib,datetime
base=Path(__file__).parent.parent
summary={}
for directory,expected in [('run-W-work',16),('run-NW-work',16),('run-SW-first-work',5)]:
 d=base/directory;s=json.loads((d/'selection.json').read_text(encoding='utf8'));rows=[]
 assert len(s['slots'])==expected
 for slot,rel in s['slots'].items():
  p=base/rel;mfile=p.with_name(p.name+'.generation.json');m=json.loads(mfile.read_text(encoding='utf8'));im=Image.open(p);digest=hashlib.sha256(p.read_bytes()).hexdigest()
  assert im.size==(1254,1254) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
  assert digest==m['sha256'] and m['actualModel'] is None and m['actualQuality'] is None
  assert (d/m['prompt']).exists()
  m['status']='native_static_reviewed_dynamic_pending'
  m['visualReview']={'status':'static-reviewed','selectedSlot':slot,'document':'REVIEW_20261003.md','dynamicValidation':False}
  mfile.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
  rows.append({'slot':slot,'source':rel,'sha256':digest,'nativeSize':[1254,1254],'rgba':True,'durationMs':75,'actualModel':None,'actualQuality':None})
 assert len({r['sha256'] for r in rows})==expected
 t=json.loads((d/'timing-grounding.json').read_text(encoding='utf8'));assert t['cycleMs']==1200 and t['frameMs']==75 and not t['phaseWeightsApplied']
 if expected==16:assert t['frameDurationsMs']==[75]*16
 summary[directory]={'selected':expected,'unique':expected,'verified':True}
 (d/'final-source-audit.json').write_text(json.dumps({'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidateOnly':True,'dynamicValidation':False,'frames':rows,'cycleMs':1200,'frameMs':75},indent=2),encoding='utf8')
print(json.dumps(summary))

