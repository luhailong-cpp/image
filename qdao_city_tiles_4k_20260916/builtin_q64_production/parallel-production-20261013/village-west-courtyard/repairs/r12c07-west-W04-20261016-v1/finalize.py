from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import numpy as np, json, hashlib
R=Path(__file__).parent; B=R.parent.parent; Q=B/'qa/r12c07-west-W04-20261016-v1'; C=Q/'candidate-v1'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
def save(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
j=json.loads((C/'assembly.json').read_text(encoding='utf-8'))
e=np.asarray(Image.open(j['base']['path']).convert('RGB')); c=np.asarray(Image.open(j['context']['path']).convert('RGB')); w=np.asarray(Image.open(j['westAnchor']['path']).convert('RGB'))
focus=[]
for kind,a in [('before',e),('after',c)]:
 for name in ['top-focus','top-junction']:
  p=C/f'{name}-{kind}-native.png'; expected=a[3000:3350,0:460] if name=='top-focus' else np.concatenate([w[3000:3350,3866:4211],a[3000:3350,115:460]],axis=1)
  rr={**rec(p),'nativeScale':1,'cropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(p))!=expected,axis=2).sum()),'visuallyReviewed':not (name=='top-focus' and kind=='before')}
  if name=='top-focus':rr['eastContextBox']=[0,3000,460,3350]
  else:rr.update({'westContextBox':[3866,3000,4211,3350],'eastContextBox':[115,3000,460,3350],'joinLocalX':345})
  focus.append(rr)
reviews=[]
for rr in j['nativeQACrops']:
 rr=rr.copy();rr.update({'visuallyReviewed':True,'nativeScale':1})
 if rr['label']=='top':rr.update({'status':'pending_at_W03_W04_halo_junction','finding':'旧 W03 细水纹与 W04 西邻原生粗水纹在顶部形成短斜向尺度/色调转折。未把源选择重放零误差当作视觉通过。'})
 else:rr.update({'status':'local_pass','finding':{'center':'岩体轮廓、泡沫与内侧水纹连续，未见原来的纵向硬切。','left':'原生西邻水纹与岩体接入连贯，未见长直切线。','right':'生成水纹向 R19 内部水面过渡，未见突兀竖线。','bottom':'上下文下缘水纹连续，未见新增水平硬切。'}[rr['label']]})
 reviews.append(rr)
actual=j['actualCoreQA'].copy();actual.update({'visuallyReviewed':True,'nativeScale':1,'status':'local_pass_for_W04_core','finding':'真实 core join x=345，覆盖整个 W04 核心高 1024 与向内 690px。原全高竖向切线消失，岩体表面、泡沫与水纹在真实接缝处连贯。'})
review={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'W04_core_local_pass_top_junction_pending','formalAccepted':False,'nativeScale':1,'selectedCandidate':j['context'],'assembly':rec(C/'assembly.json'),'fixedBase':j['base'],'westAnchor':j['westAnchor'],'aiAttemptCountForW04':1,'actualModel':'not returned','visualQANotInferredFromReplay':True,'nativeFourEdgesAndCenter':reviews,'actualCoreJoin':actual,'extraFocusCrops':focus,'pending':[{'id':'W04-TOP-W03-JUNCTION','eastContextBox':[0,3072,260,3187],'globalBox':[24461,48013,24721,48128],'focusEastContextBox':[0,3095,230,3160],'finding':'上方旧 W03 直缝约在 context y3117 收口，短斜向粗细水纹/色调转折仍可见。范围位于 W04 的顶部 halo 与旧 W03 核心末端交接；W04 核心从 y3187 开始。','recommendation':'保留本次 W04 核心改善；此交接与 W03 既存问题一并保留 pending，不以本次改善重置 W03 原两次无改善记录。'}],'attemptPolicyEvidence':rec(B/'qa/r12c07-west-pair-20261016-v1/old-r05-input-audit-v1.json'),'proof':j['proof'],'method':'两个互斥 uint8 二值 mask；同一外部 DP 选择同时约束 donor 和 generation，没有在装配后贴回 anchor；无混色、缩放、模糊。','scope':'仅 y>=3072, x<998；全块尚未 formal accepted。'}
save(Q/'review-v1.json',review)
layers=[{'id':1,'source':j['donor'],'originInContext':[0,3072],'mask':j['donorMask'],'upstream':j['westAnchor'],'upstreamContextBox':[4096,3072,4326,4326],'upstreamAssembly':rec(Path(j['westAnchor']['path']).parent/'assembly.json')},{'id':2,'source':j['native'],'originInContext':[-256,3072],'mask':j['generationMask'],'receipt':j['generationReceipt']}]
plan={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'fixedBase':j['base'],'baseAssembly':j['baseAssembly'],'layers':layers,'sourceIds':j['sourceIds'],'selectedAssembly':rec(C/'assembly.json'),'review':rec(Q/'review-v1.json'),'replayScript':rec(R/'replay.py'),'compatibleNewBaseRequirement':{'contextBox':[0,3072,998,4326],'differentPixelsToR19Required':0},'order':'Initialize from compatible newer base; apply disjoint donor/gen masks. Leave all other pixels exactly the newer base.','reviewedCandidate':j['context'],'proof':{'verifyOnlyExecuted':True,'inputRoiDifferentPixelsToR19':0,'donorCropDifferentPixels':0,'selectedPixelsDifferentToReviewedCandidate':0,'unselectedPixelsDifferentToInputBase':0,'changesAboveY3072':0,'fullContextDifferentToReviewedCandidate':0,'maskOverlapPixels':0,'donorSelectedPixels':207249,'generationSelectedPixels':853605}}
save(R/'replay-plan-v1.json',plan)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':review['status'],'formalAccepted':False,'context':j['context'],'candidate4096':j['candidate'],'assembly':rec(C/'assembly.json'),'review':rec(Q/'review-v1.json'),'replayPlan':rec(R/'replay-plan-v1.json'),'replayScript':rec(R/'replay.py'),'sourceIds':j['sourceIds'],'layers':layers,'westAnchorReadonly':j['westAnchor'],'fixedBase':j['base'],'request':j['request'],'generationReceipt':j['generationReceipt'],'actualModel':'not returned','attemptCount':1,'pending':review['pending'],'proof':j['proof']}
save(R/'delivery-manifest-v1.json',manifest)
print(json.dumps({'manifest':rec(R/'delivery-manifest-v1.json'),'review':rec(Q/'review-v1.json'),'replayPlan':rec(R/'replay-plan-v1.json'),'replayScript':rec(R/'replay.py'),'status':manifest['status']},ensure_ascii=False))
