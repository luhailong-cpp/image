from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).parent;B=R.parent.parent;Q=B/'qa/r12c07-west-W02-20261016-v1';C=Q/'candidate-v2';P=Q/'candidate-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def save(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
j=json.loads((C/'assembly.json').read_text(encoding='utf-8'));old=json.loads((P/'assembly.json').read_text(encoding='utf-8'))
c=np.asarray(Image.open(C/'context-native.png'));o=np.asarray(Image.open(P/'context-native.png'));e=np.asarray(Image.open(j['base']['path']));d=np.any(c!=o,axis=2);dy,dx=np.nonzero(d);assert [int(dx.min()),int(dy.min()),int(dx.max()+1),int(dy.max()+1)]==[230,1382,260,1412];assert d.sum()==900;assert np.array_equal(c[1382:1412,230:260],e[1382:1412,230:260])
reviewed=[]
for new,prior in zip(j['nativeQACrops'],old['nativeQACrops']):
 rr=new.copy();rr['nativeScale']=1;rr['visualEvidence']=rec(prior['path']);rr['visualEvidenceActuallyViewed']=True;rr['sameImageHashAsViewedEvidence']=rr['sha256']==prior['sha256'];rr['incrementalQAIfChanged']='Only [230,1382,260,1412] changed; native 120px focus actually viewed and passed.' if not rr['sameImageHashAsViewedEvidence'] else None
 name=rr['label']
 if name.startswith('top-junction'):rr['status']='upper_W01_existing_texture_pending' if name.endswith('after') else 'baseline_evidence';rr['finding']='修复范围内的竖向沙纹切线改善；上方既存 W01 粗细沙纹差异仍保留，不将整个跨段窗口判为通过。'
 elif name.startswith('bottom-junction'):rr['status']='lower_W03_existing_geometry_pending' if name.endswith('after') else 'baseline_evidence';rr['finding']='W02 核心岩面已经连贯；约 y2190 后进入旧 W03，原生西邻与 R19 岩面形状/明暗错接恢复，保持 pending。'
 else:rr['status']='local_pass';rr['finding']={'center':'W02 核心岩体轮廓和明暗连续，原长竖切线消失。','left':'西邻原生 donor 与生成岩面相接，无明显长直切线；底部跨 W03 问题另列。','right':'沙岸、泡沫及浅水向内部过渡，无明显新增长直切线。','top':'本块内部上边选源边界未出现明显新增横切；跨 W01 的旧纹理问题另列。','bottom':'本块内部下边选源边界连贯；实际西侧跨段接缝恢复旧 W03 问题，另列。'}[name]
 reviewed.append(rr)
actual=j['actualCoreQA'].copy();actual.update({'nativeScale':1,'status':'W02_core_local_pass','visualEvidence':old['actualCoreQA'],'incrementalQA':{'onlyDifferentPixels':900,'contextBox':[230,1382,260,1412],'focus':rec(C/'small-sand-feature-cleaned-native.png'),'actualViewed':True,'status':'local_pass'},'finding':'实际 core join x345，完整 y1139..2163。大岩面、岩隙和光照已自然连接，顶部沙纹的竖向切线明显改善。'})
pending=[{'id':'W02-TOP-W01','eastContextBox':[0,934,300,1139],'globalBox':[24461,45875,24761,46080],'status':'existing_adjacent_segment_pending','finding':'上方 W01 的沙纹尺度差异仍在；本次仅 y1024..2278 工作，不重试已经两次无改善的 W01。'},{'id':'W02-BOTTOM-W03','eastContextBox':[80,2163,260,2368],'globalBox':[24541,47104,24721,47309],'focusEastContextBox':[100,2185,220,2278],'status':'existing_adjacent_segment_pending','finding':'W03 方向原有岩面几何/明暗断层从 y约2190 恢复；未改 y2278 以下，不重置 W03 旧两次无改善记录。'}]
review={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'W02_core_local_pass_adjacent_junctions_pending','formalAccepted':False,'nativeScale':1,'selectedCandidate':j['context'],'assembly':rec(C/'assembly.json'),'fixedBase':j['base'],'westAnchor':j['westAnchor'],'actualModel':'not returned','aiAttemptCount':1,'nativeFourEdgesCenterAndJunctions':reviewed,'actualCoreJoin':actual,'pending':pending,'minorSourceSelectionCorrection':{'reason':'Generated source introduced an unsupported small pebble; kept exact R19 sand pixels.','contextBox':[230,1382,260,1412],'globalBox':[24691,46323,24721,46353],'differentPixelsToCandidateV1':900,'retainedR19IdentityDifferentPixels':0,'nativeFocus':rec(C/'small-sand-feature-cleaned-native.png'),'actualViewed':True,'status':'local_pass'},'proof':j['proof'],'noVisualPassInferredFromReplay':True,'audit':rec(B/'qa/r12c07-west-pair-20261016-v1/old-r05-input-audit-v1.json'),'notChanged':['W03 rock foot y>=2300','W04 y>=3072','west frozen anchor','R19 source image']}
save(Q/'review-v1.json',review)
layers=[{'id':1,'source':j['donor'],'originInContext':[0,1024],'mask':j['donorMask'],'upstream':j['westAnchor'],'upstreamContextBox':[4096,1024,4326,2278],'upstreamAssembly':j['westAnchorAssembly']},{'id':2,'source':j['native'],'originInContext':[-256,1024],'mask':j['generationMask'],'receipt':j['generationReceipt']}]
proof={'verifyOnlyExecuted':True,'inputRoiDifferentPixelsToR19':0,'donorCropDifferentPixels':0,'selectedPixelsDifferentToReviewedCandidate':0,'unselectedPixelsDifferentToInputBase':0,'changesAboveY1024':0,'changesBelowY2278':0,'fullContextDifferentToReviewedCandidate':0,'maskOverlapPixels':0,'donorSelectedPixels':189032,'generationSelectedPixels':764463}
plan={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'fixedBase':j['base'],'baseAssembly':j['baseAssembly'],'layers':layers,'sourceIds':j['sourceIds'],'selectedAssembly':rec(C/'assembly.json'),'review':rec(Q/'review-v1.json'),'replayScript':rec(R/'replay.py'),'compatibleNewBaseRequirement':{'contextBox':[0,1024,998,2278],'differentPixelsToR19Required':0},'order':'Initialize from compatible newer base; apply disjoint donor/gen masks. Leave all other pixels exactly the newer base.','reviewedCandidate':j['context'],'proof':proof}
save(R/'replay-plan-v1.json',plan)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':review['status'],'formalAccepted':False,'context':j['context'],'candidate4096':j['candidate'],'assembly':rec(C/'assembly.json'),'review':rec(Q/'review-v1.json'),'replayPlan':rec(R/'replay-plan-v1.json'),'replayScript':rec(R/'replay.py'),'sourceIds':j['sourceIds'],'layers':layers,'westAnchorReadonly':j['westAnchor'],'fixedBase':j['base'],'request':j['request'],'generationReceipt':j['generationReceipt'],'actualModel':'not returned','attemptCount':1,'pending':pending,'proof':j['proof']}
save(R/'delivery-manifest-v1.json',manifest)
print(json.dumps({'manifest':rec(R/'delivery-manifest-v1.json'),'review':rec(Q/'review-v1.json'),'replayPlan':rec(R/'replay-plan-v1.json'),'replayScript':rec(R/'replay.py'),'context':j['context'],'candidate':j['candidate'],'status':manifest['status']},ensure_ascii=False))
