from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;Q=T/'qa/resume-20261016';read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(Q/'repair-plan-v1.json');base=Image.open(plan['baseCandidate']['file']).convert('RGB');out=base.copy();mask=Image.new('L',base.size,0);records=[]
rois={'floor-join':[235,180,1100,1254],'leaf-notch':[350,360,900,840],'window-strip':[30,360,790,680]}
for item in plan['repairs']:
 id=item['id']
 if id not in rois:continue
 ver=2 if id=='floor-join' else 1;p=T/'native/repairs'/(id+'-local-v'+str(ver)+'-20261016.png');roi=rois[id];x,y=item['origin'];box=[x+roi[0],y+roi[1],x+roi[2],y+roi[3]]
 out.paste(Image.open(p).convert('RGB').crop(roi),box[:2]);mask.paste(255,tuple(box));records.append({'id':id,'file':str(p),'sha256':sha(p),'origin':item['origin'],'roi':roi,'destinationBox':box,'attempts':ver})
p=T/'candidates/r07_c16.local-repairs-best-v2-20261016.png';assert not p.exists();out.save(p)
for item in plan['repairs']:
 if item['id'] not in rois:continue
 x,y=item['origin'];out.crop((x,y,x+1254,y+1254)).save(Q/(item['id']+'-best-v2.png'))
diff=ImageChops.difference(out,base);diff.paste((0,0,0),(0,0),mask);assert diff.getbbox() is None
j={'tile':'r07_c16','candidate':str(p),'candidateSha256':sha(p),'pixels':[4096,4096],'baseCandidate':plan['baseCandidate'],'repairs':records,'operation':'native integer crop/paste only; no resize/blur/feather/color processing','outsideRepairRectsIdentical':True,'rejectedRepairs':[{'id':'wall-joints','attempts':2,'reason':'Both generated repairs shift lower masonry phase and move cut to the repair lower edge; baseline retained and same point deferred.'}],'internalPassed':False,'formalAcceptedCount':0}
(Q/'composition-best-v2.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'candidate':str(p),'sha256':sha(p)},ensure_ascii=False))

