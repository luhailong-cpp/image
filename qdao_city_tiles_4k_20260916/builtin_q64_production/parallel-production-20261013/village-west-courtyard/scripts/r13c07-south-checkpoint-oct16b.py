from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
B=Path(__file__).resolve().parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def js(p,v):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
q=B/'qa/r13-c07-south-final-inspection-oct16b-v2';m=read(q/'manifest.json')
observations=[]
for c in m['crops']:
    assert sha(c['path'])==c['sha256']
    observations.append(dict(c,reviewed=True,accepted=True,viewMethod='view_image original native pixels',note='Native water ripple scale and color transition continuous; no rectangular patch edge at source splice or actual core join.' if c['id'].startswith('band') else 'Changed lower internal seam remains continuous at native scale.'))
qa={'tile':'r13_c07','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inspection':pin(q/'manifest.json'),'candidate':m['candidate'],'context':m['context'],'anchor':m['anchor'],'observations':observations,'reviewedNativeCrops':10,'acceptedNativeCrops':10,'southEdgeAccepted':True,'internalAcceptedCount':32,'internalTotal':33,'wholeTileInternalAccepted':False,'formalAccepted':False,'pending':[{'id':'vertical-r01-c03','contextBox':[3185,470,3250,535],'note':'Previously observed triangular water fragment, two AI attempts without improvement; root north repair owns further review.'}],'unchangedInternalCropCount':len(m['reusedInternalCrops']),'reusedInternalCrops':m['reusedInternalCrops'],'acceptanceIsVisualNotReplay':True}
js(q/'visual-qa-v1.json',qa)
oldq=B/'qa/r13-c07-south-final-inspection-oct16b-v1';om=read(oldq/'manifest.json')
js(oldq/'visual-qa-v1.json',{'inspection':pin(oldq/'manifest.json'),'reviewedIds':['band-05','band-06','band-07'],'accepted':False,'formalAccepted':False,'issue':{'crop':'band-07','contextBox':[3072,4096,3100,4140],'note':'Rectangular overwritten prior overlap moved splice to context row4096. Failed v1 preserved; corrected by unified generation+anchor side mask in v2.'},'supersededBy':pin(q/'visual-qa-v1.json')})
record={'tile':'r13_c07','status':'south-passed-west-repair-next-north-in-parallel','formalAccepted':False,'dimensions':[4096,4096],'assembly':m['assembly'],'candidate':m['candidate'],'context':m['context'],'southQA':pin(q/'visual-qa-v1.json'),'internalQA':pin(B/'qa/r13-c07-internal-inspection-oct16b-v1/visual-qa-v1.json'),'pending':['north local internal fragment and north actual core join (root owns)','west actual core join (this worker owns)','east actual core join (neighbor pin available, pending)'],'route':'builtin','actualModel':None}
js(B/'records/r13c07-south-checkpoint-oct16b-v1.json',record)
west=B/'repairs/r13c06-south-external-oct16-v1/S04-assembly-v4';w=read(west/'assembly.json')
assert sha(west/'assembly.json')=='977f3bedd49d48575b68cfdaa24d175f2b1136df49d85fb203cb4410091134cd'
own=np.asarray(Image.open(m['candidate']['path']).convert('RGB'));a=np.asarray(Image.open(w['candidate']['path']).convert('RGB'))
assert sha(w['candidate']['path'])=='f3898b6a0f268487e1409edd2ee084c23517c4eed416fdbeb8f271b835752824'
out=B/'qa/r13-c07-west-actualcorejoin-oct16b-v1';out.mkdir(exist_ok=False);join=np.concatenate((a[:,-345:],own[:,:345]),axis=1);crops=[]
for i,y in enumerate([0,1024,2048,3072,679,1703,2727],1):
    height=1024 if i<=4 else 690;p=out/f'band-{i:02d}.png'
    Image.fromarray(join[y:y+height]).save(p);crops.append(dict(pin(p),id=f'band-{i:02d}',coreY=y,scale=1,actualCoreJoinImageX=345,reviewed=False))
js(out/'manifest.json',{'ownCandidate':m['candidate'],'westCandidate':w['candidate'],'westContext':w['context'],'crops':crops,'formalAccepted':False})
print(json.dumps({'checkpoint':pin(B/'records/r13c07-south-checkpoint-oct16b-v1.json'),'southQA':pin(q/'visual-qa-v1.json'),'westInspection':pin(out/'manifest.json')}))
