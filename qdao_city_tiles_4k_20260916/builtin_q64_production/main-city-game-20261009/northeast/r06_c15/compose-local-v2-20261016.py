from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/resume-20261016';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(Q/'repair-plan-v1.json');base=Image.open(plan['baseCandidate']['file']).convert('RGB');out=base.copy();mask=Image.new('L',base.size,0);records=[]
rois={'panel':[180,450,610,930],'roof':[90,470,1139,800],'wallrail':[200,400,1120,900],'upperroof':[130,380,1170,840]}
for item in plan['repairs']:
 id=item['id'];p=T/'native/repairs'/(id+'-local-v2-20261016.png');roi=rois[id];x,y=item['origin'];box=[x+roi[0],y+roi[1],x+roi[2],y+roi[3]]
 out.paste(Image.open(p).convert('RGB').crop(roi),box[:2]);mask.paste(255,tuple(box))
 records.append({'id':id,'file':str(p),'sha256':sha(p),'origin':item['origin'],'roi':roi,'destinationBox':box,'historicalPlusCurrentAIAttempts':2,'nativeSize':[1254,1254],'resized':False})
p=T/'candidates/r06_c15.local-repairs-v2-20261016.png';assert not p.exists();out.save(p)
for item in plan['repairs']:
 x,y=item['origin'];out.crop((x,y,x+1254,y+1254)).save(Q/(item['id']+'-composed-v2.png'))
diff=ImageChops.difference(out,base);diff.paste((0,0,0),(0,0),mask);assert diff.getbbox() is None
j={'tile':'r06_c15','candidate':str(p),'candidateSha256':sha(p),'pixels':[4096,4096],'baseCandidate':plan['baseCandidate'],'repairs':records,'operation':'Native integer crop/paste only; no resizing/blending/feathering/color correction','outsideRepairRectsIdentical':True,'status':'awaiting-composed-QA','internalPassed':False,'formalAcceptedCount':0}
(Q/'composition-v2.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'candidate':str(p),'sha256':sha(p)},ensure_ascii=False))

