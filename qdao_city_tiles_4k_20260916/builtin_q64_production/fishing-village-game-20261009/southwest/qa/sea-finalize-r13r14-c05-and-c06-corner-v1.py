import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent
ref=lambda p:{'path':Path(p).as_posix(),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rgb(r):
 p=Path(r['path']);assert ref(p)['sha256']==r['sha256'];return np.asarray(Image.open(p).convert('RGB')).copy()
def write(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2)
 return ref(p)
def png(p,a):
 assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(np.asarray(Image.open(p)),a);return dict(ref(p),size=[a.shape[1],a.shape[0]])
def diffbox(a,b):
 y,x=np.where(np.any(a!=b,axis=2));return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]
t=read(Q/'pair-r13c05-r14c05-v3-trace.json');v2=read(Q/'pair-r13c05-r14c05-v2-trace.json');old=read(Q/'pair-r14c05-r14c06-v2-trace.json')
r13=rgb(t['tiles'][0]['context']);r14=rgb(t['tiles'][1]['context']);r13stable=rgb(ref(Q/'pair-r12c05-r13c05-v1-r13_c05-context-native.png'));assert np.array_equal(r13[:230],r13stable[:230])
reused=[]
for i in [0,1,3,4]:
 assert t['qa'][i]['sha256']==v2['qa'][i]['sha256'];reused.append(t['qa'][i])
va={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'passed_native_pair_visual_qa','trace':ref(Q/'pair-r13c05-r14c05-v3-trace.json'),'qaViewedNative':t['qa'],'sharedWindowsPassed':5,'unchangedQaReusedFromViewedV2':reused,'repairViewedNative':[r['after'] for r in t['repairs']],'findings':['Five native shared seam windows passed. Water, foam and rounded rocks connect without source zigzag.','Three native strip repairs resolve rock plane discontinuities; one small subsequent junction repair resolves remaining bright wedge.','All four boundaries of all repair masks and affected internal vertical edge segments were covered by the native1254 repair windows and native shared windows. No blur, scale change or object displacement introduced.'],'validation':t['validation'],'preservation':{'r13_c05_north230ExactToR12R13Accepted':True,'r13ChangedContextBox':diffbox(r13,r13stable),'r14ChangedContextBox':diffbox(r14,rgb(old['tiles'][0]['context']))},'formalAcceptance':False,'remainingExternalJoins':['r13_c05 east to reserved r13_c06 under coordinator','r14_c06 north corner halo to reserved r13_c06; checked separately in propagated pair audit']}
va_ref=write(Q/'pair-r13c05-r14c05-v3-art-audit-v1.json',va)
base=rgb(old['context']);out=base.copy();out[:,:4326]=r14
assert np.array_equal(out[:,:4326],r14);assert np.array_equal(out[:,4326:],base[:,4326:])
c06old=rgb(old['tiles'][1]['context']);c06=out[:,4096:];assert np.array_equal(r14[:,-230:],c06[:,:230]);assert np.array_equal(c06[:,-230:],c06old[:,-230:]);east=rgb(ref(Q/'pair-r14c06-r14c07-v3-r14_c06-context-native.png'));assert np.array_equal(c06[:,-230:],east[:,-230:])
pre='pair-r14c05-r14c06-v3';ids=np.ones(out.shape[:2],np.uint8);ids[:,:4326]=0
npy=Q/(pre+'-source-ids.npy');assert not npy.exists();np.save(npy,ids);assert np.array_equal(np.load(npy),ids)
tr={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'native_pair_corner_propagated_pending_visual_qa','axis':'horizontal','inputs':[t['tiles'][1]|{'context':t['tiles'][1]['context']},old['tiles'][1]|{'context':old['tiles'][1]['context']}],'provenance':[ref(Q/'pair-r13c05-r14c05-v3-trace.json'),va_ref,ref(Q/'pair-r14c05-r14c06-v2-trace.json'),ref(Q/'pair-r14c05-r14c06-v2-art-audit-v1.json')],'script':ref(Path(__file__)),'globalContextBox':old['globalContextBox'],'method':'exact integer adoption of updated c05 context into existing horizontal pair; c06 overlap takes the same c05 pixels','sourcePixelIdentity':True,'nativePixelsResampled':False,'context':png(Q/(pre+'-context-native.png'),out),'sourceIds':ref(npy),'sourceLegend':{'0':t['tiles'][1]['context'],'1':old['tiles'][1]['context']},'tiles':[],'qa':[],'validation':{'allFinalPixelsExactlyMatchRecordedSource':True,'noResize':True,'noFeather':True,'noColourCorrection':True,'noDrawing':True,'overlap230Exact':True,'c06East230ExactToAcceptedC06C07V3':True},'changedC06ContextBox':diffbox(c06,c06old),'formalAcceptedCount':0}
for item,a in [(old['tiles'][0],r14),(old['tiles'][1],c06)]:
 tr['tiles'].append({'tile':item['tile'],'context':png(Q/(pre+'-'+item['tile']+'-context-native.png'),a),'contextBox':item['contextBox'],'candidate':png(Q/(pre+'-'+item['tile']+'-candidate-4096.png'),a[115:4211,115:4211]),'coreBox':item['coreBox']})
for i,item in enumerate(old['qa'],1):
 l,y,r,b=item['contextBox'];p=png(Q/(pre+f'-shared-part{i:02d}-100pct.png'),out[y:b,l:r]);tr['qa'].append(dict(p,contextBox=item['contextBox'],globalBox=item['globalBox'],exactPixelIdentityToV2=p['sha256']==item['sha256']))
tr['cornerQa']={'contextBox':[3584,0,4838,1254],'image':png(Q/(pre+'-north-corner-100pct.png'),out[:1254,3584:4838])}
tr_ref=write(Q/(pre+'-trace.json'),tr)
print(json.dumps({'verticalAudit':va_ref,'propagatedTrace':tr_ref,'tiles':tr['tiles'],'changedC06ContextBox':tr['changedC06ContextBox']}))