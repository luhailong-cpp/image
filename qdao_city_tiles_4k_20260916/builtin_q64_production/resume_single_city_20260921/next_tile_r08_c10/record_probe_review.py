"""Record scoped observed review for the one generated probe; no image changes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
P=Path(__file__).resolve().parent
B=P/'probe-r04_c02-20260923T125732Z'
def rec(p):return {'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def dump(p,o):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
pre=json.loads((B/'preflight.json').read_text(encoding='utf-8'))
refs=[]
for r in pre['references']:
    current=rec(Path(r['file']));assert current['sha256']==r['sha256'];refs.append(current)
image=P/'native/r04_c02.probe-20260923T125732Z.png'
layout=json.loads((P/'layout-record.json').read_text(encoding='utf-8'))
qa=B/'qa'
review={
  'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
  'tile':'r08_c10','patch':'r04_c02','reviewer':'Codex checkpoint_merge visual inspection',
  'candidate':rec(image),'nativePixels':[1254,1254],
  'reviewedEvidence':[rec(qa/n) for n in ['halo-comparison-generated-top-neighbor-bottom.png','hypothetical-core-to-bottom-seam-native.png','generated-y1139-context-native.png']],
  'viewedWholeImage':'actual image_gen return displayed at 1254x1254; native PNG byte copy, no resize',
  'referenceHashesUnchangedAfterCall':True,'references':refs,
  'bottomExactPair':{'newProbe':rec(image),'selectedNeighbor':{'file':layout['sources']['bottom']['file'],'sha256':layout['sources']['bottom']['sha256']},'neighborContext':refs[3],
     'generatedCoreLastRowsLTRB':[0,1011,1254,1139],'neighborFirstRowsLTRB':[0,0,1254,128],
     'generatedOverlapLTRB':[0,1139,1254,1254],'neighborOverlapLTRB':[0,0,1254,115],
     'status':'failed_visual_continuity'},
  'localObservations':{
    'nativeDetail':'Clean broad ivory faces, restrained rounded bevels and crisp edges. No cloudy or flaky surface visible in this inspected probe.',
    'primaryComposition':'Three gray upper insets, broad center ivory panel and curved framing follow original master composition. This is a local visual observation, not pixel-exact geometric or navigation acceptance.',
    'wholeBottomContextCopied':False,
    'inventedHorizontalJointAtY1139Observed':False,
    'boundaryFailure':'Hypothetical native seam visibly jumps: the probe gray curved band is warmer/lighter than the selected bottom slate band, and floral-relief petals/outline do not continue at matching positions. Bottom115 overlay comparison also shows shape mismatch.',
    'partialLocalUse':'Useful only as clean material and local rendering probe; not eligible as a seamless selected production patch in its current state.'
  },
  'locallySelectableForAssembly':False,
  'materialExplorationUseful':True,
  'bottomContinuityPassed':False,
  'internalSeamsAndJunctions':'not checked; other 15 patches are not generated',
  'leftRightTopExternalEdges':'not checked; this is a partial native patch',
  'tile4kCandidateProduced':False,'wholeTileReady':False,'wholeCityGeometryAccepted':False,
  'formalArtAcceptancePassed':False,'clientRuntimeAccepted':False,
  'actualModel':None,'actualQuality':None,
  'nextStep':'Stop this one-call batch. Root reviews this probe and row8 overall before any new generation.',
  'retention':'Keep this sole in-progress probe and current QA evidence for root review. It is not selected or a final game resource; deletion/next selection awaits root review within authorized retention policy.'
}
dump(B/'local-review.json',review)
handoff={
  'tile':'r08_c10','patch':'r04_c02','nativeImage':rec(image),
  'generationRecord':rec(Path(str(image)+'.generation.json')),
  'request':rec(B/'actual-request.json'),'receipt':rec(B/'tool-receipt.json'),
  'rootLayoutObservation':rec(B/'root-layout-observation.json'),
  'localReview':rec(B/'local-review.json'),
  'builtinCallCount':1,'actualModel':None,'actualQuality':None,
  'locallySelectableForAssembly':False,'bottomContinuityPassed':False,
  'nativeSizeMatchesRequested':True,'wholeTileReady':False,
  'sharedJSONWritten':False,'generationStoppedAsRequested':True
}
dump(B/'handoff-probe.json',handoff)
text='''# r08_c10 / r04_c02 单次原生探片

仅调用一次宿主管理内置 image_gen，实际生成并按原字节保存 1254×1254 PNG：`../native/r04_c02.probe-20260923T125732Z.png`。SHA `1129a25b56ca3d4946c27b38a88108c5700a3411371947cb1f2db7468233873c`。无缩放、无像素修改。

亲看整张返回图和三张原像素接边检查图：材质干净，未见碎纹／云斑；上方三灰嵌板、中央象牙铺地和弧框延续原城构图。没有把底邻 512 高上下文整体抄进目标，也没有在算法 y=1139 处新增贯穿横缝。

**底边未通过，当前不可选入无缝拼接。** 与 external-v8 原像素接边时，灰色弧带明暗／边界及浮雕花瓣位置有跳变。证据 `qa/hypothetical-core-to-bottom-seam-native.png` 中 y=128 为实际假想拼接边；`qa/halo-comparison-generated-top-neighbor-bottom.png` 对照同一世界区域。以上只用于检查，不是加工后的游戏图。

这张暂时只作为材质与局部画法探片，保留给主任务审看。16 格中另外 15 格未生成；整块候选 0，正式美术／导航／客户端实机验收均未通过。未更改共享 JSON。按指令停止这一小批，不再尝试第二次。

真实调用前后 clock 时间为 2026-09-23 12:59:25 UTC 至 13:00:53 UTC。逐图记录、当次配置、实际请求、4 张参考图 SHA、原样文本回执与来源路径均已保存。配置目标 gpt-image-2.5-sunburst / max；工具没有 model/quality 参数且未返回具体型号／质量，actualModel 和 actualQuality 均为 null。

`root-layout-observation.json` 只记录主任务对首片的局部布局观察，不代表整个 c10 或整城几何验收。完整索引见 `handoff-probe.json`，观察见 `local-review.json`。
'''
(B/'README.md').write_text(text,encoding='utf-8')
print(json.dumps(handoff,ensure_ascii=False,indent=2))
