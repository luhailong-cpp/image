from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
T=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'file':str(p),'sha256':sha(p)}
notes=load(T/'row02-observations.json');items=[]
for col in [4,3,2,1]:
 cell=f'r02_c{col:02d}'
 if cell not in notes:continue
 p=T/f'native/{cell}.png';gp=Path(str(p)+'.generation.json');g=load(gp)
 assert sha(p)==g['sha256'] and Image.open(p).size==(1254,1254)
 assert g['actualModel'] is None and g['actualQuality'] is None
 e=g['evidence'];rp=Path(e['toolResultPath']);receipt=load(rp)
 assert sha(rp)==e['toolResultSha256'] and sha(e['sourceOutputPath'])==g['sha256']
 assert sha(g['sourceJob'])==g['sourceJobSha256'] and sha(g['prompt'])==g['promptSha256']
 assert receipt['prompt']==g['submittedParameters']['prompt']
 for r in g['references']:assert sha(r['path'])==r['sha256']
 j=load(g['sourceJob']);d=j['guideDerivation']
 assert sha(d['guide'])==d['guideSha256'] and sha(d['regional'])==d['regionalSha256']
 assert sha(d['context'])==d['contextSha256']
 items.append({'cell':cell,'file':str(p),'sha256':g['sha256'],'pixels':[1254,1254],
  'generationRecord':ref(gp),'receipt':ref(rp),'sourceOutput':ref(e['sourceOutputPath']),
  'actualRequest':ref(T/f'jobs/{cell}.actual-request.json'),'prompt':ref(g['prompt']),
  'sourceJob':ref(g['sourceJob']),'guide':ref(d['guide']),'styleReference':g['references'][1],
  'configSnapshot':g['configSnapshot'],'submittedModel':None,'submittedQuality':None,
  'actualModel':None,'actualQuality':None,'visualReview':notes[cell],
  'allSourceGuideStyleReceiptJobPromptHashesVerifiedAfterViews':True})
out={'schemaVersion':1,'tile':'r09_c08','row':2,'worker':'c09_final_internal','recordedAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'row_complete_pending_full_tile_qa' if len(items)==4 else 'in_progress_waiting_for_ready_north_neighbor',
 'nativeTraversal':['r02_c04','r02_c03','r02_c02','r02_c01'],'completedNative':len(items),'selectedNativeCalls':len(items),
 'rejectedNativeCalls':0,'regionalAlreadyPreparedByRoot':True,'items':items,
 'styleViewedOnceAndActuallyAttachedToEveryCall':True,'allGuidesAndOutputsActuallyViewedForListedCells':True,
 'assemblyPerformed':False,'formalAccepted':False,'qualifiedComplete4KCandidate':False,'clientValidated':False,'wholeCityComplete':False,
 'scopeLimit':'Individual native outputs only; complete-tile internal and external seam review remains required.'}
p=T/'worker-row02.json';p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':str(p),'sha256':sha(p),'completed':len(items)}))
