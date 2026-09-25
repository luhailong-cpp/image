"""Persist the actual manual review; no original/shared file is modified."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,re
from PIL import Image
HERE=Path(__file__).resolve().parent
V=HERE/'versions/bottom-material-v2-20260923T094331634966Z'
O=V/'complete-review-20260923T113829791462Z'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def check(e):
    assert Path(e['file']).is_file() and sha(e['file'])==e['sha256'],e
    return dict(e)
repair=read(V/'repair.json')
assert sha(V/'r08_c09.png')=='dbaf9d7e02a8bcccf958d81e0bf5e506c4d558dff553d5abb759abdbc3320cd5'
assert sha(V/'repair.json')=='63b6b907e25faba1c69fe33e31fcaf3213aa1fda3093b1f25fab8e0683af46db'
check(repair['neighbor'])
verification=read(O/'verification-and-crops.json')
receipts=[]
for source in repair['sources']:
    gen=read(check(source['generationRecord'])['file'])
    for k in ['prompt','request','evidence','editBefore','originalNativeOutput']:check(gen[k])
    for r in gen['references']:check(r)
    request=read(gen['request']['file']);receipt=read(gen['evidence']['file'])
    assert request==receipt['request']
    assert request['prompt']==Path(gen['prompt']['file']).read_text(encoding='utf-8')
    assert request['referenced_image_paths']==[r['file'] for r in gen['references']]
    assert 'model' not in request and 'quality' not in request
    native=check(source['native'])
    assert Image.open(native['file']).size==(1254,1254)
    assert native['sha256']==gen['originalNativeOutput']['sha256']
    returned=re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint']).group(1)
    assert Path(returned)==Path(gen['originalNativeOutput']['file'])
    assert gen['generatedAt'] is None and gen['actualModel'] is None and gen['actualQuality'] is None
    assert gen['observedCompletionAt']==receipt['completedAtUtc']
    receipts.append({'native':native,'generation':source['generationRecord'],'request':gen['request'],'receipt':gen['evidence'],'nativeBytesEqualReturnedCache':True,'referenceCurrentBytesVerified':True,'startedAtUtc':receipt['startedAtUtc'],'observedCompletedAtUtc':receipt['completedAtUtc'],'actualModel':None,'actualQuality':None,'generatedAt':None})
qa=V/'qa'
viewed=[O/f'full-{axis}-{i:02}.png' for axis in ['v','h'] for i in [1,2,3]]
viewed += [O/'nine-junctions.png',*(O/f'wide-lower-v-{i:02}.png' for i in [1,2,3]),O/'four-returns.png',O/'six-return-junctions.png']
viewed += [qa/f for f in ['wide-bottom-01.png','wide-bottom-04.png','focus-gold-joint.png','bottom-edge-02.png','bottom-edge-03.png']]
record={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c09','candidate':info(V/'r08_c09.png'),'repair':info(V/'repair.json'),'neighbor':repair['neighbor'],'reviewMethod':'Human-visible assistant inspection using view_image detail=original. All evidence listed here was actually viewed. Full seams use four non-overlapping 1024-long segments of a 512-pixel-wide native strip, assembled without resampling; vertical strips rotated exactly 90 degrees only for display. Three lower vertical seams additionally checked in 1024x1024 native context. Overview is reference-only and not acceptance evidence.','sourceVerification':info(O/'verification-and-crops.json'),'provenanceVerification':receipts,'viewedNativePixelEvidence':[info(p) for p in viewed],'internalSeams':[],'internalJunctions':[],'repairReturns':[],'externalEdges':{},'externalFourTileJunctions':{'status':'pending_not_checked','count':4},'formalAccepted':False,'productionAccepted':False,'clientRuntimeAccepted':False,'wholeCityArtGatePassed':False,'layoutNavigationAndCameraGate':'not independently compared to full layout/navigation in this review','actualModel':None,'actualQuality':None,'newGenerationCallsDuringThisReview':0}
for axis in ['v','h']:
    for n in [1,2,3]:
        e={'id':f'{axis}{n}','axis':'vertical' if axis=='v' else 'horizontal','coordinate':n*1024,'span':[0,4096],'status':'scoped_local_continuity_pass','reviewed':True,'evidence':info(O/f'full-{axis}-{n:02}.png'),'finding':'No obvious cut grout, duplicated relief, broken gold edge or straight artificial tone boundary observed along the full seam.'}
        if axis=='v':
            e['supplement']=info(O/f'wide-lower-v-{n:02}.png')
            e['priorLowerTonalConcern']='Fresh wide context does not reproduce a definite straight color strip at the internal x boundary. This resolves that specific earlier pending observation locally; it does not accept all broad stone texture or the external boundary.'
        record['internalSeams'].append(e)
for y in [1024,2048,3072]:
    for x in [1024,2048,3072]:record['internalJunctions'].append({'centerXY':[x,y],'scopePixels':[512,512],'status':'scoped_local_continuity_pass','reviewed':True,'evidence':info(O/'nine-junctions.png'),'finding':'No visible crossing mismatch or isolated square intersection patch observed.'})
for n in [1,2,3,4]:record['repairReturns'].append({'segment':n,'xRange':[(n-1)*1024,n*1024],'status':'scoped_local_continuity_pass','reviewed':True,'evidence':info(O/'four-returns.png'),'finding':'No new obvious discontinuous contour or horizontal return stripe. Segment 2 is inherited unchanged from v1.'})
record['repairReturnJunctions']={'count':6,'status':'scoped_local_continuity_pass','reviewed':True,'evidence':info(O/'six-return-junctions.png'),'finding':'No obvious new cut or rectangular patch at the intersections of repair returns and internal x boundaries.'}
record['maskVerification']={'outsideAllowedMaskPixelsUnchanged':verification['outsideAllowedMaskPixelsUnchanged'],'changedPixels':verification['changedPixels'],'fixedNeighborCurrentShaVerified':True,'sourceCandidateShaVerified':True,'allInternalJunctionsUnchanged':repair['allInternalJunctionsUnchanged'],'method':'Exact RGB byte comparison against v1 where allowed-mask is zero; fixed neighbor file hash verified before and after review.'}
record['externalEdges']={'top':{'status':'pending_not_checked'},'left':{'status':'pending_not_checked'},'right':{'status':'pending_not_checked'},'bottom':{'status':'failed_material_continuity','wholeEdgePassed':False,'neighbor':repair['neighbor'],'segments':[
{'segment':1,'xRange':[0,1024],'status':'failed_material_continuity','evidence':info(qa/'wide-bottom-01.png'),'finding':'The edited upper region is substantially cleaner, but fixed lower r09_v6 retains conspicuous irregular cloudy marbling. Native wide context shows an abrupt change in texture character at y4096. Geometry appears continuous; material gate fails.'},
{'segment':2,'xRange':[1024,2048],'status':'scoped_local_continuity_pass','evidence':info(qa/'bottom-edge-02.png'),'finding':'In the reviewed native 128-pixel bands above/below the boundary, no obvious outline or abrupt tone step is visible. This limited segment pass cannot accept the full edge.'},
{'segment':3,'xRange':[2048,3072],'status':'pending_material_review','evidence':info(qa/'bottom-edge-03.png'),'focusEvidence':info(qa/'focus-gold-joint.png'),'goldJoinStatus':'scoped_local_geometry_pass','finding':'The prior x2410..2430 gold-bevel kink is not visibly reproduced at original pixel scale. Tone/texture in the cream relief area and consistency with the failed neighboring external segments remain pending; no whole segment pass is claimed.'},
{'segment':4,'xRange':[3072,4096],'status':'failed_material_continuity','evidence':info(qa/'wide-bottom-04.png'),'finding':'The upper slabs and ring are clean, while the fixed lower half has dense cloudy/mineral veining. The broad native context still shows a visible material transition at y4096. Geometry appears connected; material gate fails.'}
]}}
record['selectionRecommendation']={'selectAs':'best_current_complete_work_in_progress_candidate','formalAccepted':False,'reason':'Compared with v1, upper-side excess clouds in bottom segments 1/4 are reduced and the prior gold-edge concern is locally improved. Fixed old neighbor prevents the complete bottom boundary from satisfying the clean-material constraint. Select only as unfinished candidate, retaining explicit external failure/pending states.','boundedGenerationDecision':'No new calls issued during this review: repeating a clean-only upper edit while requiring immutable cloudy lower pixels cannot establish a clean matching material gate. Next work should address the coupled cross-tile material decision rather than count another attempted generation as success.','doNotRewriteHistoricalReviews':True}
for e in record['viewedNativePixelEvidence']:check(e)
check(record['candidate']);check(record['neighbor'])
p=O/'visual-review.json';assert not p.exists();p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
md='''# r08_c09 v2 原像素复核\n\n选用建议：保留本版为当前完整在制候选，正式美术验收与客户端实机验收均为未通过。\n\n已实际查看 6 条完整内部缝（512 像素宽、4096 全长）、9 个内部交点，并补查三条内部竖缝下段的 1024×1024 宽上下文。未发现明确的几何断线或直线色带；以上仅局部接缝连续性通过。4 段返修回接缝和 6 个回接交点未见新增断裂。\n\n外部底边第 1、4 段仍失败：本版上侧已减轻碎纹，固定 r09_c09 repair_v6 下侧仍有明显云斑／矿物纹，原像素宽图可见材质跳变。第 2 段局部连续性通过；第 3 段金边疑点本次未重现，但乳白浮雕材质与相邻失败段的一致性待定。其余 3 条外边与 4 个外部四块交点未检查。\n\n3 张 v2 原生返修图的请求、提示词、逐图记录、真实回执、参考 SHA 与实际返回缓存的 PNG 原字节已复核。候选 mask 外与 v1 完全一致，固定旧邻居 SHA 未变。实际后端型号／质量仍为 null；未把配置目标或提示词当成型号证据。本复核没有再次生图。\n\n保留记录中的历史原图链接与 SHA；后续按用户新清理政策删除源图片时应追加清理文字说明，不改写历史证据。\n'''
(O/'visual-review.md').write_text(md,encoding='utf-8')
print(json.dumps({'candidate':record['candidate'],'repair':record['repair'],'review':info(p),'recommendation':record['selectionRecommendation'],'formalAccepted':False},ensure_ascii=False))
