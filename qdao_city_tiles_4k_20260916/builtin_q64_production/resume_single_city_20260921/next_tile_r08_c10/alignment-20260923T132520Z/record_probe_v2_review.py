"""Record bounded failed result and local calibration proposal. No new image call."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
D=Path(__file__).resolve().parent;P=D.parent;B=D/'probe-aligned-halo-v2'
def rec(p):return {'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def dump(p,o):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
native=B/'native-r04_c02.png';box=[950,1000,1254,1200]
sources=[P/'guides/r04_c02.master-layout-only.png',P/'guides/r04_c02.plaza-layout-review-only.png',native]
comp=Image.new('RGB',(304,600))
for k,p in enumerate(sources):
 with Image.open(p) as im:im.load();comp.paste(im.crop(box).convert('RGB'),(0,k*200))
q=B/'qa/right-band-originals-v-output.png'
with q.open('xb') as f:comp.save(f,format='PNG')
dump(q.with_suffix('.derived.json'),{'output':rec(q),'sources':[rec(p) for p in sources],'operation':'Exact unresampled crop[950,1000,1254,1200] stacked: original master guide top200, plaza guide middle200, generated output bottom200. Review-only comparison, not generated artwork.','targetGlobalLTRB':[38723,32629,39027,32829],'role':'qa_only','sourceResampledBeforeCrop':[True,True,False]})
pre=json.loads((B/'preflight.json').read_text(encoding='utf-8'))
for r in pre['references']:assert rec(Path(r['file']))['sha256']==r['sha256']
review={
 'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c10','patch':'r04_c02','native':rec(native),'nativePixels':[1254,1254],
 'scope':'one revised registered-halo probe only','exactBottomNeighbor':json.loads((D/'audit.json').read_text(encoding='utf-8'))['selectedBottom'],
 'viewedWholeOutput':'actual image_gen return; saved PNG is byte-identical host copy, not resampled',
 'viewedQA':[rec(B/'qa'/n) for n in ['halo-comparison-generated-top-neighbor-bottom.png','hypothetical-core-to-bottom-seam-native.png','generated-y1139-context-native.png']],
 'additionalQAForRoot':rec(q),
 'coordinateValidation':{'globalPatchLTRB':[37773,31629,39027,32883],'nativeCoreLTRB':[115,115,1139,1139],'trueNeighborTargetLTRB':[0,1139,1254,1254],'sourceNeighborLTRB':[909,0,2163,115],'globalSharedHaloLTRB':[37773,32768,39027,32883],'noNeighborPixelsAbove1139':True,'registeredReferenceMasterCoreUnchanged':True},
 'decision':'failed_bottom_continuity_and_new_local_joint_not_selected',
 'findings':[
  {'kind':'floral_boundary_discontinuity','targetContactY':1139,'globalContactY':32768,'targetXRegion':[0,650],'globalXRegion':[37773,38423],'extentMeaning':'visual problem region, not exact petal feature annotation','observation':'The output floral relief is displaced relative to the known neighbor. At the hypothetical actual seam review y128, petal contours terminate/restart across a straight horizontal cut. Correct halo coordinates did not constrain native shape continuation.'},
  {'kind':'invented_joint_near_reference_transition','targetInspectBoxLTRB':box,'globalInspectBoxLTRB':[38723,32629,39027,32829],'observation':'The right curved band changes from warm light stone to slate with a newly drawn transverse beveled joint near the registered boundary. This was not a real joint in the master geometry and violates the no-invented-grid-boundary requirement.'},
  {'kind':'material_and_macro_composition_only','observation':'Faces are clean and broad; three gray upper insets and central slab composition are retained. These improvements do not compensate for failed boundary continuity.'}
 ],
 'staticMetricLimit':'The preflight nine samples only measured three primary band edges (1..12px differences); they did not register the floral relief. No overall geometry or seam pass was implied.',
 'locallySelectableForAssembly':False,'selectedNativeCount':0,'bottomContinuityPassed':False,'wholeTileReady':False,'formalArtAcceptancePassed':False,'clientRuntimeAccepted':False,
 'nativeCoreExported':False,'guidePixelsEnteredOutputFile':False,'nativeSizeMatchesRequested':True,
 'actualModel':None,'actualQuality':None,'currentExperimentGenerationCalls':1,
 'referenceHashesUnchangedAfterCall':True,'sharedJSONWritten':False,'navigationChanged':False,'oldRejectedProbeRestored':False,
 'nextStep':'Stop this batch. Review local geometry calibration proposal before another generation. Do not rerun this prompt unchanged.',
 'retention':'Current failed probe and QA held only for root review; generation/request/source text retained. Not selected as game art.'
}
dump(B/'local-review.json',review)
proposal={
 'scope':'r08_c10 bottom patch r04_c02 against exact r09_c10 external-v8 SHA; not a navigation change',
 'status':'proposal_only_not_applied',
 'fixedFrames':{'globalPatchLTRB':[37773,31629,39027,32883],'bottomBoundaryGlobalY':32768,'haloTargetY':[1139,1254],'nativeCoreLTRB':[115,115,1139,1139]},
 'problems':[{'globalBoundarySegment':[37773,32768,38423,32768],'issue':'floral silhouette/contour continuation is not anchored despite correct band registration'},{'globalInspectionLTRB':[38723,32629,39027,32829],'issue':'reference material transition is being converted into a real transverse joint'}],
 'calibrationSteps':[
  'Trace a small explicit set of floral contour crossings and curved-band center/edge landmarks from the exact bottom native source on y0..115. Preserve their exact global coordinates and tangent direction; no early paste at1024.',
  'Compare those landmarks to original-master nominal geometry within its limited6144 resolution. Where correspondence is ambiguous, require a reviewed local shape guide; do not treat a material-only native crop as geometry authority.',
  'Prepare a geometry-continuous reference design across the boundary before another call: remove the visual resolution/material cutoff as a geometric cue while keeping confirmed neighbor landmark coordinates fixed. This is reference design only; no guide pixels may enter exported art.',
  'If calibrated floral geometry cannot respect both the original layout and selected neighbor, document the conflict and plan a coordinated boundary-region native revision with root, instead of warping roads/entrances or changing navigation.',
  'Any future output must use only actual native core115:1139 after original-pixel contour and contact review. Require both the y1139 contact and every newly introduced local joint to pass; do not count a preview or a smooth-looking full image as acceptance.'
 ],
 'noFurtherImageCallAuthorizedByThisDocument':True,'sharedOrNavigationChangesApplied':False
}
dump(B/'calibration-proposal.json',proposal)
handoff={'tile':'r08_c10','patch':'r04_c02','status':'revised_probe_failed_not_selected','image':rec(native),'generationRecord':rec(B/'native-r04_c02.png.generation.json'),'request':rec(B/'actual-request.json'),'receipt':rec(B/'tool-receipt.json'),'staticObservation':rec(B/'static-layout-observation.json'),'localReview':rec(B/'local-review.json'),'calibrationProposal':rec(B/'calibration-proposal.json'),'callsThisExperiment':1,'selectedNativeCount':0,'wholeTileReady':False,'actualModel':None,'actualQuality':None,'stopped':True}
dump(B/'handoff.json',handoff)
text='''# r08_c10 / r04_c02 正确 halo 对齐试验：未通过

本轮只生成 1 次。原生输出 1254×1254，SHA `7e5a69ee7aff3bf34aa6f3f0b83b22907fcd8b4f13149ac97279cb6d6f096a37`；原字节保存，没有缩放、贴回或像素修补。它仍未选用，不是 4096 候选。

输入修订已核实：原城 master 引导 y0..1139 保持原样；只将当前 r09_c10 external-v8 的 `[909,0,2163,115]` 原像条带放入目标 `[0,1139,1254,1254]`。没有提前到 y1024，没有底邻像素侵入未知核心。全局共享范围 `[37773,32768,39027,32883]`。该参考画布不是成品。

静态对照的三条主要弧带，9 处边缘样本相差 1–12 个原生像素，允许解释为描边/倒角，因而按指令做一次试验；这不包含浮雕轮廓注册，也不构成几何或美术验收。

结果亲看：`qa/hypothetical-core-to-bottom-seam-native.png` 的 y128 真实接触线仍有花瓣横断层；右侧弧带附近还出现新的横向倒角砖缝，把材质过渡误解成结构分段。故底边失败、选用 native=0、整块 ready=false。没有导出核心作为成品。

问题坐标与精确来源见 `local-review.json`；下一步局部控制点与轮廓校准建议见 `calibration-proposal.json`。不要重复本提示词刷图。新原图与本轮 QA 仅留待主任务审看，旧已删拒图未恢复。共享五份 JSON、导航、其他图块均未修改。

真实调用 clock：2026-09-23 13:31:29 UTC 至 13:32:29 UTC。工具只有 prompt/referenced_image_paths 实参；配置目标仍为 gpt-image-2.5-sunburst / max，但实际型号和质量未披露，actualModel/actualQuality=null。逐图配置、请求、4 张参考 SHA、原样文本回执与来源记录均已保存，索引 `handoff.json`。
'''
(B/'README.md').write_text(text,encoding='utf-8')
print(json.dumps(handoff,ensure_ascii=False,indent=2))
