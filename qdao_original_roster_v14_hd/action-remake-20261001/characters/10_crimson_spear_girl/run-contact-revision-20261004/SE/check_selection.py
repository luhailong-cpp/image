from pathlib import Path
from PIL import Image
import json,hashlib,sys
root=Path(__file__).parents[2]
allsha=set()
directions=sys.argv[1:] or ['SE']
for direction in directions:
 work=root/f'run-contact-revision-20261004/{direction}'
 sel=json.loads((work/'selection.json').read_text())['slots']
 rows=[]
 for n in range(1,17):
  slot=f'run/{direction}/{n:02d}';p=root/sel.get(slot,f'runtime/{slot}.png')
  im=Image.open(p);im.load();sha=hashlib.sha256(p.read_bytes()).hexdigest()
  assert im.mode=='RGBA' and im.size in[(1024,1024),(1254,1254)]
  assert sha not in allsha,('duplicate',slot);allsha.add(sha)
  alpha=im.getchannel('A');assert alpha.getextrema()[0]==0
  edges=[alpha.crop((0,0,im.width,1)),alpha.crop((0,im.height-1,im.width,im.height)),alpha.crop((0,0,1,im.height)),alpha.crop((im.width-1,0,im.width,im.height))]
  assert max(e.getextrema()[1] for e in edges)<32,('edge',slot)
  record=Path(str(p)+'.generation.json');assert record.exists(),('record',slot)
  rec=json.loads(record.read_text(encoding='utf-8-sig'))
  rows.append({'slot':slot,'file':p.relative_to(root).as_posix(),'sha256':sha,'size':list(im.size),'mode':im.mode,'alpha32BoundaryClear':True,'generationRecord':record.relative_to(root).as_posix()})
 (work/'selection-technical-check.json').write_text(json.dumps({'status':'pass','count':16,'allUnique':True,'frameMs':75,'cycleMs':1200,'noPoseInterpolation':True,'rows':rows},indent=2),encoding='utf-8')
print(json.dumps({'selected':16*len(directions),'unique':len(allsha),'technical':'pass','artApproval':'pending integrated normal-speed loop'}))
