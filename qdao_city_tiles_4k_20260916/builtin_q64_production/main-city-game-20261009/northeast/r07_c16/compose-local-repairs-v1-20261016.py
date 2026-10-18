from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/resume-20261016';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(Q/'repair-plan-v1.json');base=Image.open(plan['baseCandidate']['file']).convert('RGB');out=base.copy();changed=Image.new('L',base.size,0)
rois={'floor-join':[235,180,1100,1254],'wall-joints':[0,0,1254,1254],'leaf-notch':[350,360,900,840],'window-strip':[30,360,790,680]}
records=[]
for item in plan['repairs']:
 id=item['id'];p=T/'native/repairs'/(id+'-local-v1-20261016.png');im=Image.open(p).convert('RGB');roi=rois[id];x,y=item['origin'];box=[x+roi[0],y+roi[1],x+roi[2],y+roi[3]]
 out.paste(im.crop(roi),box[:2]);changed.paste(255,tuple(box))
 records.append({'id':id,'file':str(p),'sha256':sha(p),'origin':item['origin'],'roi':roi,'destinationBox':box,'nativeSize':[1254,1254],'resized':False})
d=T/'candidates';d.mkdir(exist_ok=True);p=d/'r07_c16.local-repairs-v1-20261016.png';assert not p.exists();out.save(p)
for item in plan['repairs']:
 id=item['id'];x,y=item['origin'];out.crop((x,y,x+1254,y+1254)).save(Q/(id+'-composed-v1.png'))
 if id=='wall-joints':
  for label,b in [('north',[x,y-150,4096,y+150]),('south',[x,y+1104,4096,y+1404]),('west',[x-150,y,x+150,y+1254])]:
   out.crop(b).save(Q/(id+'-'+label+'-boundary-v1.png'))
diff=ImageChops.difference(out,base);outside=diff.copy();outside.paste((0,0,0),(0,0),changed);assert outside.getbbox() is None
j={'tile':'r07_c16','candidate':str(p),'candidateSha256':sha(p),'pixels':[4096,4096],'baseCandidate':plan['baseCandidate'],'repairs':records,'operation':'Integer native crop and paste only; no resizing, blending, feathering or color correction.','outsideRepairRectsIdentical':True,'status':'awaiting-composed-boundary-QA','internalPassed':False,'formalAcceptedCount':0}
(Q/'composition-v1.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(j,ensure_ascii=False))

