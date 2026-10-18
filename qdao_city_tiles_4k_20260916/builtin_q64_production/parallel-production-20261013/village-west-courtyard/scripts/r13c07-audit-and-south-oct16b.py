from pathlib import Path
import json,hashlib,datetime
from PIL import Image
B=Path(__file__).resolve().parent.parent
D=B/'qa/r13-c07-internal-inspection-oct16b-v1'
S=B/'qa/r13-c07-south-actualcorejoin-oct16b-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,j):
 with p.open('x',encoding='utf-8') as f:json.dump(j,f,indent=2);f.write('\n')
m=read(D/'inspection-manifest.json');assert sha(Path(m['context']['path']))==m['context']['sha256']
rows=[]
for c in m['nativeCrops']:
 assert sha(Path(c['path']))==c['sha256']
 bad=c['id']=='vertical-r01-c03'
 kind='Rock/foam contours and mineral planes remain continuous; no pasted boundary identified.' if ('r01' in c['id']) else 'Water ripple phases, highlights and foam fields continue naturally through the inspected join.'
 rows.append({**c,'reviewed':True,'reviewedAtNativePixels':True,'accepted':not bad,'status':'pending-local-repair' if bad else 'passed','finding':'Retained small sharp triangular water fragment at context [3185,470,3250,535]; two earlier attempts did not improve it. No whole-tile acceptance.' if bad else kind})
pending=B/'repairs/r13c07-internal-seams-oct16/rock-top-c03-v02.not-selected-qa.json'
audit={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':'r13_c07','inspectionManifest':ref(D/'inspection-manifest.json'),'assembly':m['assembly'],'context':m['context'],'candidate':m['candidate'],'nativeCropsReviewed':33,'nativeCropsAccepted':32,'crops':rows,'sourceReplay':m['sourceReplay'],'internalQa':'pending-one-local-water-fragment','wholeTileInternalAccepted':False,'formalAccepted':False,'pending':[{'id':'north-third-vertical-water-triangle','contextBox':[3185,470,3250,535],'attemptsAtPoint':2,'status':'deferred-after-two-no-improvement-attempts','evidence':ref(pending)}],'externalQa':'pending'}
write(D/'visual-qa-v1.json',audit)
ledger=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest/current-tile-ledger.json')
south=next(t for t in read(ledger)['tiles'] if t['tile']=='r14_c07')
np=Path(m['candidate']['path']);sp=Path(south['current4096']['path']);cp=Path(south['nativeContext']['path'])
assert sha(np)==m['candidate']['sha256'] and sha(sp)==south['current4096']['sha256'] and sha(cp)==south['nativeContext']['sha256']
n=Image.open(np).convert('RGB');s=Image.open(sp).convert('RGB');sc=Image.open(cp).convert('RGB');assert n.size==s.size==(4096,4096) and sc.size==(4326,4326)
assert sc.crop((115,115,4211,4211)).tobytes()==s.tobytes()
S.mkdir(exist_ok=False)
join=Image.new('RGB',(4096,690));join.paste(n.crop((0,3751,4096,4096)),(0,0));join.paste(s.crop((0,0,4096,345)),(0,345))
crops=[]
for i,(x0,x1) in enumerate([(0,1024),(1024,2048),(2048,3072),(3072,4096),(679,1369),(1703,2393),(2727,3417)]):
 p=S/f'south-actualcorejoin-{i+1:02d}.png'
 with p.open('xb') as f:join.crop((x0,0,x1,690)).save(f,format='PNG')
 crops.append({'id':f'south-actualcorejoin-{i+1:02d}',**ref(p),'globalBox':[24576+x0,52903,24576+x1,53593],'size':[x1-x0,690],'joinY':345,'reviewed':False})
write(S/'manifest.json',{'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'edge':'r13_c07 south / r14_c07 north','ownCandidate':ref(np),'neighborCandidate':ref(sp),'neighborContext':ref(cp),'neighborLedger':ref(ledger),'method':'actual 4096 core join at globalY53248; integer crop and paste only; no resampling or RGB rewrite','coreMatchesNeighborContext':True,'crops':crops,'formalAccepted':False,'status':'pending-visual-QA'})
print(json.dumps({'internalAudit':ref(D/'visual-qa-v1.json'),'southManifest':ref(S/'manifest.json')}))
