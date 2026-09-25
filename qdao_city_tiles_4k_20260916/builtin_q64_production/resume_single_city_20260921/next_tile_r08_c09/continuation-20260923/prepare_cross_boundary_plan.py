"""Prepare a reviewable coupled repair; no model call or candidate mutation."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
H=Path(__file__).resolve().parent
T=H.parent
S=T.parent
A=S.parent.parent
P=A.parent
V=H/'versions/bottom-material-v2-20260923T094331634966Z'
R=V/'complete-review-20260923T113829791462Z/visual-review.json'
N=S/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png'
STYLE=P/'designs/gameplay-ui/04-guild.png'
MAT=T/'references/clean-stone-material-native-crop.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p)}
def relinfo(p):return {'file':Path(p).relative_to(A).as_posix(),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,obj):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)
assert sha(V/'r08_c09.png')=='dbaf9d7e02a8bcccf958d81e0bf5e506c4d558dff553d5abb759abdbc3320cd5'
assert sha(N)=='5ce3e9099c4292a3c2d2b854bcc6d2cfd3b8858bb6960bc8e7966699ade4742c'
assert sha(STYLE)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
review=read(R)
pointer={'schemaVersion':1,'selectedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c09','appearance':'tianyong_festival','candidate':{**relinfo(V/'r08_c09.png'),'pixels':[4096,4096]},'record':relinfo(V/'repair.json'),'assembly':relinfo(H/'versions/hard-core-20260923T070734660600Z/assembly.json'),'review':relinfo(R),'status':'selected_complete_work_in_progress_candidate_bottom_edge_failed_not_production_accepted','internalFullSeamsReviewed':6,'internalJunctionsReviewed':9,'externalFullEdgesReviewed':1,'externalFullEdgesPassed':0,'externalEdgesPending':3,'externalFourTileJunctionsPending':4,'bottomEdgeStatus':'failed_material_continuity_segments_1_4_segment_3_material_pending','actualModel':None,'actualQuality':None,'backendModelVerified':False,'accepted':False,'formalArtAcceptancePassed':False,'clientRuntimeAccepted':False,'sourceArtUpscaled':False,'selectionReason':review['selectionRecommendation']['reason']}
write(T/'latest-candidate.json',pointer)
O=H/('cross-boundary-plan-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));O.mkdir()
config=read(P/'config/image-generation.json');write(O/'config-snapshot.json',config)
a=np.asarray(Image.open(V/'r08_c09.png').convert('RGB'));b=np.asarray(Image.open(N).convert('RGB'))
entries=[]
for num,x,left,right in [(1,0,0,1024),(3,1933,2048,3072),(4,2842,3072,4096)]:
    q=O/f'patch-{num:02}';q.mkdir()
    context=np.concatenate([a[3469:,x:x+1254],b[:627,x:x+1254]],axis=0)
    Image.fromarray(context).save(q/'context-native-1254.png')
    # Original concatenated context: shared boundary at local y627.
    # Editable c08 final192 rows and r09 first448; return feathers are32 pixels.
    yy=np.arange(1254,dtype=np.float32)[:,None]
    alpha=np.minimum(np.clip((yy-435)/32,0,1),np.clip((1075-yy)/32,0,1))
    alpha=alpha*alpha*(3-2*alpha)
    mask=np.repeat(np.rint(alpha*255).astype(np.uint8),1254,axis=1)
    Image.fromarray(mask).save(q/'planned-allowed-mask.png')
    instruction='Preserve the now-correct polished gold bevel near x477..497 at the shared boundary without any kink, duplicated highlight, shift or widening. Reduce cloudy stone in the adjoining cream slab and carved relief only; do not simplify or deform flower relief geometry.' if num==3 else 'Remove dense irregular cloudy/mineral veining on the lower-side cream stone; use the clean upper material as the finish target. Preserve every stone joint, gold edge, dark ring contour and relief exactly.'
    prompt=f'''Use case: precise-object-edit. A 1254x1254 native game-art crop; exact same framing, camera, geometry and original-pixel scale. IMAGE 1 is the sole geometry and composition authority. It combines r08_c09 above and r09_c09 below, meeting at y=627. Repair BOTH sides as one continuous painted material; the tile boundary is not a slab joint and must not become a visible horizontal line.
Only local rows y=435..1074 may change. Preserve rows y<435 and y>=1075 and all object geometry. Within editable rows, retain crisp rounded bevels and perfectly aligned contours. {instruction}
Use broad quiet warm-ivory gradients, bright clean rounded Daoist Q painting. No mottled clouds, flakes, mineral veins, speckles, mosaic texture, added joints, blur, fog stripes, global recolor, or new objects. Blend the material change into existing quiet tones at both outer ends without a flat horizontal fade stripe; within the last 64 editable lower rows retain only faint tonal continuity needed to meet the original bottom material. Geometric shapes and sharp highlights stay locked.
IMAGE 2 is the approved design art for clean bright rounded finish only: do not import its UI, people, letters, icons or layout. IMAGE 3 is native clean stone material reference only, not geometry. Do not rotate, rescale, reposition or straighten the artwork. Return one opaque native square image without labels or collage.'''
    (q/'planned-prompt.txt').write_text(prompt,encoding='utf-8')
    request={'prompt':prompt,'referenced_image_paths':[str(q/'context-native-1254.png'),str(STYLE),str(MAT)]}
    write(q/'planned-request.json',request)
    item={'id':f'patch-{num:02}','status':'prepared_not_submitted','modelCallsPerformed':0,'request':info(q/'planned-request.json'),'prompt':info(q/'planned-prompt.txt'),'context':info(q/'context-native-1254.png'),'mask':info(q/'planned-allowed-mask.png'),'references':[info(p) for p in request['referenced_image_paths']],'nativePixels':[1254,1254],'originalCombinedContextLTRB':[x,3469,x+1254,4723],'boundaryLocalY':627,'ownedXRange':[left,right],'allowedR08YRange':[3904,4096],'allowedR09YRange':[0,448],'topAndBottomReturnPixels':32,'sideFeatherPixels':0,'registration':'none','resampling':'none','sourceArtUpscaled':False,'actualModel':None,'actualQuality':None,'configSnapshot':config}
    write(q/'prepared.json',item);entries.append({'id':item['id'],'prepared':info(q/'prepared.json'),'request':item['request']})
ledger=read(S/'current-coverage-ledger.json')
affected={'priorReferencesAreHistoricalOnlyAfterAnyNewPairVersion':True,'r09OlderLeftAndRightPassesRequireFreshVersionReview':['r09_c08|r09_c09','r09_c09|r09_c10'],'affectedSeams':[e for e in ledger['seams'] if 'r09_c09' in e['tiles']],'affectedJunctions':[e for e in ledger['junctions'] if 'r09_c09' in e['tiles']]}
write(O/'prior-evidence-invalidation-plan.json',affected)
plan={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'prepared_only_not_submitted_not_applied','purpose':'Coupled clean-material repair across r08_c09 bottom and r09_c09 top, retaining geometry and crisp gold contour. Prior r09 immutability was the earlier batch application limit; this plan creates a separate r09 version without overwriting v6.','maximumProposedNativeCalls':3,'modelCallsPerformed':0,'sourceR08':info(V/'r08_c09.png'),'sourceR08Record':info(V/'repair.json'),'sourceR08Review':info(R),'sourceR09':info(N),'sourceR09Record':info(N.parent/'repair.json'),'style':info(STYLE),'material':info(MAT),'configSnapshot':config,'patches':entries,'segment2':'not edited; existing local bottom continuity retained only if identical pixel evidence is verified','allowedChanges':{'r08_c09':{'xRanges':[[0,1024],[2048,4096]],'yRange':[3904,4096]},'r09_c09':{'xRanges':[[0,1024],[2048,4096]],'yRange':[0,448]}},'application':'Create a unique pair version. Apply exact1254-native pixels by recorded mask and owned x intervals, no resize, alignment, warp, color correction, or old-source overwrite. Verify both source SHA immediately before operation and exact pixel equality outside masks afterward.','capabilityRule':'Recheck the live builtin tool before execution; currently exposes prompt/referenced_image_paths/num_last_images_to_include only. Do not submit model/quality fields or claim backend values. Record actual request and clock around every call, native result receipt and source SHA. Planned request is not proof of submission.','qaRequired':['Both resulting4096x4096 PNGs, source/current SHA and actual assembly record','Both changed masks and exact RGB equality outside masks','All6 internal full seams and9 intersections of both tiles; directly re-view changed lower/top vertical portions, link unchanged evidence only after exact pixel equality','Full shared4096 edge in four1024 segments with512 pixels on each side; inspect x2410..2430 gold tangent at1:1','Both top/bottom repair returns and all their intersections with x1024,2048,3072, including the segment2 boundaries','Fresh full left/right edges of r09 vs fixed r09_c08/r09_c10, because top448 pixels change; old local pass evidence cannot automatically carry over','Check all external neighbors and four-tile intersections involving both new versions. Top pair junctions involving r08_c08/r08_c10 remain pending if full candidates are absent. Lower old r09/r10 junction evidence may be rebound only after actual involved pixels and adjacent SHA are identical','Review broader material style; do not accept displaced mismatch at the lower return simply because the original shared edge improves'], 'priorEvidenceInvalidation':info(O/'prior-evidence-invalidation-plan.json'),'completionCriteria':'Only select new pair if real visual QA improves failed material boundary without new geometry, return seams or neighbor failures. Formal city/runtime gates remainfalse.','sharedJsonWritesPerformed':False,'nativeSourceRetention':'Prepared context PNGs are current design inputs until attempted/retired. Keep selected r08 and old r09 candidates while planning; root owns scoped retention decisions.','script':info(Path(__file__))}
write(O/'plan.json',plan)
(O/'PLAN.md').write_text('''# 跨边界返修草案（仅准备）\n\n以当前 r08_c09 v2 与 r09_c09 repair_v6 的原像素拼成参考；拟对第 1、3、4 段最多生图 3 次，同步清理 r08 最后 192 行与 r09 最前 448 行的指定区间。第 2 段保持原像素。所有几何、浮雕、金边切线保持，旧 r09 不覆盖，输出为独立双图版本。\n\n已保存逐片实际尺寸参考、掩码、计划提示词、计划请求和 SHA；这些请求尚未提交，没有生成回执，也没有模型调用。执行前重查入口能力和引用 SHA。\n\n必须重验完整共边、两侧回接缝、两图内部全缝与交点，以及 r09 左右边被修改的顶部区域；旧版本的左/右局部通过记录不可直接继承。旧 r09 底边及底部四块交点如像素逐一相等，可保留为历史已检查范围并绑定新 SHA，但不能冒充新实机或整城验收。\n\n材质改善若只把问题从共边移至下回接位置，仍应判失败。完整执行及 QA 要求见 plan.json。\n''',encoding='utf-8')
assert sha(N)==plan['sourceR09']['sha256'] and sha(V/'r08_c09.png')==plan['sourceR08']['sha256']
print(json.dumps({'latestCandidate':info(T/'latest-candidate.json'),'plan':info(O/'plan.json'),'directory':str(O),'modelCallsPerformed':0},ensure_ascii=False))
