from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
checked={};bad=[];invalid=[]
def walk(v,record,at=''):
 if isinstance(v,dict):
  name=v.get('file');h=v.get('sha256')
  if isinstance(name,str) and isinstance(h,str) and len(h)==64:
   p=Path(name)
   if p.is_absolute():
    key=(str(p),h)
    if key not in checked:
     if not p.exists():bad.append({'record':str(record),'at':at,'file':str(p),'expectedSha256':h,'reason':'missing'})
     elif sha(p)!=h:bad.append({'record':str(record),'at':at,'file':str(p),'expectedSha256':h,'actualSha256':sha(p),'reason':'hash mismatch'})
     checked[key]=True
  for k,w in v.items():walk(w,record,at+'/'+k)
 elif isinstance(v,list):
  for i,w in enumerate(v):walk(w,record,at+'/'+str(i))
for p in P.rglob('*.json'):
 if p.name.endswith('audit.json'):continue
 try:walk(json.loads(p.read_text(encoding='utf-8-sig')),p)
 except Exception as e:invalid.append({'file':str(p),'error':str(e)})
ai=[]
for name in ['repair-v1.png','repair-v2.png','repair-v3.png','top-local.png','lower-west-local.png','root-lower-bevel-v12.png','three-endpoints-v14.png','upper-middle-v19.png']:
 p=P/name;g=Path(str(p)+'.generation.json');v=json.loads(g.read_text());im=Image.open(p)
 ai.append({'image':ref(p),'generation':ref(g),'nativeSize':list(im.size),'native1254':im.size==(1254,1254),'route':v.get('route'),'actualModel':v.get('actualModel'),'actualQuality':v.get('actualQuality'),'hasUnverifiedReason':bool(v.get('unverifiedReason'))})
report={'recordedAt':datetime.now(timezone.utc).isoformat(),'scope':str(P),'checkedUniqueFileHashPairs':len(checked),'mismatches':bad,'invalidJSON':invalid,'aiSources':ai,'allAvailableReferencedHashesMatch':not bad and not invalid,'candidate':ref(P.parent.parent/'output/r09_c15-candidate.png'),'candidateUnchanged957':sha(P.parent.parent/'output/r09_c15-candidate.png')=='957194bcbf888cac88f8b0a3d79d055f8ce69a76846590f174eee7e6f8b9e456','visualApproval':False,'independentProposal':ref(P/'proposal-v19.json')}
(P/'source-chain-audit-v19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'pairs':len(checked),'bad':bad,'invalid':invalid,'audit':ref(P/'source-chain-audit-v19.json')}))

