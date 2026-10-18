from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;name=sys.argv[1]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rp=T/'receipts'/(name+'.receipt.json');qp=T/'prompts'/(name+'.request.json');rec=read(rp);req=read(qp)
src=Path(rec['sourceOutputPath']);dest=T/'native/repairs'/(name+'.png');dest.parent.mkdir(exist_ok=True)
assert not dest.exists()
with Image.open(src) as im:assert im.size==(1254,1254) and im.format=='PNG'
shutil.copy2(src,dest); plan=read(T/'qa/resume-20261016/repair-plan-v1.json')
item=next(x for x in plan['repairs'] if x['id']==req['repairId'])
j={'file':str(dest),'sha256':sha(dest),'tool':'image_gen','route':'builtin','generatedAt':datetime.now(timezone.utc).isoformat(),'sourceOutputPath':str(src),'nativeSize':[1254,1254],'width':1254,'height':1254,'format':'PNG','actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin returned no model or quality metadata.','prompt':str(T/'prompts'/(name+'.prompt.txt')),'request':str(qp),'evidence':str(rp),'references':[{'file':p,'sha256':sha(p),'role':req['referenceRoles'][i]} for i,p in enumerate(req['referenced_image_paths'])],'repairTarget':item,'baseCandidate':plan['baseCandidate'],'resized':False,'status':'native_local_repair_composed_QA_pending'}
Path(str(dest)+'.generation.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'native':str(dest),'sha256':j['sha256']}))

