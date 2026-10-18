import json,hashlib,sys
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
z=Path(__file__).resolve().parent.parent
p,v,src=sys.argv[1:]
dst=z/'native'/f'{p}-{v}.png'
def sha(f): return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def ref(f,role): return {'path':str(Path(f).resolve()).replace('\\','/'),'sha256':sha(f),'role':role}
def write(f,d):
 assert not Path(f).exists()
 Path(f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(dst)==sha(src)
a=Image.open(dst).convert('RGB'); assert a.size==(1254,1254)
planpath=z/'records'/f'{p}-{v}.plan.json'
if not planpath.exists(): planpath=z/'records'/f'{p}.plan.json'
plan=json.loads(planpath.read_text(encoding='utf-8-sig'))
prompt=z/'records'/f'{p}-{v}.prompt.txt'; receipt=z/'records'/f'{p}-{v}.receipt.json'
rr=json.loads(receipt.read_text(encoding='utf-8-sig'))
assert prompt.read_text(encoding='utf-8').strip()==rr['request']['prompt'].strip()
roles={q['path']:q['role'] for q in plan['references']}
plan['references']=[ref(x,roles.get(x,'actual reference')) for x in rr['request']['referenced_image_paths']]
record=dict(plan,file=str(dst),sha256=sha(dst),nativeSize=list(a.size),width=a.width,height=a.height,observedAtUtc=datetime.now(timezone.utc).isoformat(),prompt=ref(prompt,'actual submitted prompt'),receipt=ref(receipt,'actual tool return receipt'),source=ref(src,'host output byte-for-byte copy'),formalAccepted=False,usable=False,visualReview='pending',status='native_candidate_pending_review',nativeResizePerformed=False,metadataResumeReason='Original ingest copied native successfully then detected prompt at wrong directory; metadata completed without touching saved pixels.')
write(str(dst)+'.generation.json',record)
for e in plan['nativeEdgeSources']:
 b=Image.open(e['path']).convert('RGB');bottom='bottom' in e['role']; assert bottom or 'right' in e['role']
 q=Image.new('RGB',(1254,256) if bottom else (256,1254))
 if bottom:q.paste(a.crop((0,1011,1254,1139)),(0,0));q.paste(b.crop((0,115,1254,243)),(0,128))
 else:q.paste(a.crop((1011,0,1139,1254)),(0,0));q.paste(b.crop((115,0,243,1254)),(128,0))
 qp=z/'qa'/f'{p}-{v}-{e["role"]}.png';assert not qp.exists();q.save(qp)
 write(str(qp)+'.derived.json',{'purpose':'native1:1 seam QA','sources':[e,ref(dst,'new native')],'seam':128,'resized':False})
print(json.dumps({'saved':str(dst),'sha256':sha(dst),'nativeSize':list(a.size)}))
