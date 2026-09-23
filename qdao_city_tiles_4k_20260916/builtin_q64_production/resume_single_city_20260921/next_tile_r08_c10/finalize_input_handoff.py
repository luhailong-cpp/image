"""Finalize preparation-only notes; cannot generate images or update shared state."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

P = Path(__file__).resolve().parent
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):
    return {'file': str(p), 'sha256': sha(p)}
def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

if (P/'HANDOFF.md').exists() or (P/'input-visual-review.json').exists():
    raise SystemExit('Refusing to overwrite completed handoff')
request_path=P/'requests/r04_c02.draft.request.json'
request=load(request_path)
old='Match only the already reviewed crossing positions and material there.'
new='Its existing crossing positions and material are comparison constraints; compatibility with this target crop is pending regional layout review.'
if old not in request['prompt']:
    raise SystemExit('Unexpected draft wording; inspect manually')
request['prompt']=request['prompt'].replace(old,new)
write(request_path,request)
(P/'prompts/r04_c02.draft.prompt.txt').write_text(request['prompt']+'\n',encoding='utf-8')
plan=load(P/'plan.json')
plan['draftRequest']=record(request_path)
write(P/'plan.json',plan)
validation=load(P/'preparation-validation.json')
validation['plan']=record(P/'plan.json')
validation['handoffWordingClarification']='No r08_c10 boundary has been visually accepted; draft explicitly awaits regional layout review.'
write(P/'preparation-validation.json',validation)

seen=[
    ('references/master-core-native384.png','Original master core crop viewed at native 384 pixels. Circular plaza paving and curved ring bands; no new objects authorized.'),
    ('references/plaza-core-native768.png','Nominal plaza crop viewed at native 768 pixels. Broad layout correspondence does not establish geometric identity with master.'),
    ('references/clean-stone-native768.png','Selected r08_c07 native crop: smooth ivory faces, restrained warm joints and rounded bevels. Material only; its gold-line composition must not transfer.'),
    ('guides/r04_c02.master-layout-only.png','Reference enlargement viewed: gray inset panels above a broad ivory slab; curved trim and floral relief below. Single-source geometry guide, no pasted neighbor blocks.'),
    ('guides/r04_c02.plaza-layout-review-only.png','Comparison reference enlargement viewed. Gray panel divisions and bevel details differ from original master; regional reconciliation remains pending.'),
    ('references/r04_c02.bottom-neighbor-native-context.png','Separate original-pixel neighbor strip viewed. Floral relief on left and broad curved ivory/slate paving. Only top 115 rows provide existing bottom halo.'),
    ('review/master-navigation-polygons-review-only.png','Reference-only overlay viewed. No polygon edge is visible inside this crop; this is not navigation or runtime acceptance.'),
]
review={
    'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),
    'tile':'r08_c10','scope':'preparation_inputs_only_no_generated_artwork',
    'viewer':'Codex subagent checkpoint_merge',
    'viewedImages':[dict(record(P/rel),observation=note) for rel,note in seen],
    'canonicalStyleViewed':dict(record(P.parents[3]/'designs/gameplay-ui/04-guild.png'),observation='User-confirmed clean bright rounded Daoist Q style; actual file in draft inputs.'),
    'notViewedAsOriginalWholeImage':['Full master, plaza and bottom image display attempts failed; successful derived native crops and guide images are enumerated above.'],
    'originalMasterGeometryAuthority':True,
    'masterToPlazaGeometryIdentityEstablished':False,
    'bottomBoundaryContinuityPassed':False,
    'leftNeighborIsProvisional':True,
    'allBoundaryAndJunctionReview':'not performed; no new output exists',
    'firstPatch':'r04_c02','nativeOutputTarget':[1254,1254],
    'coreCropLTRB':[115,115,1139,1139],
    'nativeBottomKnownRows':115,'nativeBottomStartsAtTargetY':1139,
    'guidePastedRectangles':0,
    'generationReady':False,'nativeGenerationCount':0,
    'actualModel':None,'actualQuality':None,
    'formalArtAcceptancePassed':False,'clientRuntimeAccepted':False,
    'mustResolveBeforeSubmission':[
        'Root visually reconciles original master guide with nominal plaza redraw and selected external-v8 bottom strip.',
        'Keep r08_c09 provisional until a selected exact-SHA neighbor and its relevant boundary evidence are available.',
        'Recheck current builtin entry; capture fresh configuration, exact request, all reference SHAs, tool receipt and verifiable time.',
        'Only actual new native image output may enter an assembled candidate. No guide, overlay or preview pixels may enter output.'
    ],
    'artifacts':{name:record(P/name) for name in ('plan.json','layout-record.json','preparation-validation.json','prepare_inputs.py','requests/r04_c02.draft.request.json')}
}
write(P/'input-visual-review.json',review)

handoff='''# r08_c10 制作输入交接（尚未生图）

已准备 16 格原生分区计划，单格目标 1254×1254，核心 1024×1024、四边 halo 115；相邻分区重叠 230。所有现有 PNG 仅为设计／材质／布局／检查参考，成品候选 0，正式美术与客户端实机验收 0。没有调用 image_gen、API 或 CLI，也没有更新共享 JSON。

## 坐标与来源

- 全城核心 LTRB：`[36864,28672,40960,32768]`；含 halo：`[36749,28557,41075,32883]`。
- 原城 6144 图核心：`[3456,2688,3840,3072]`。它是几何基准；广场重绘的名义对应范围 `[2816,1280,3584,2048]` 只用于比对，尚未证明逐点几何同一。
- 底邻是当前选用 `r09_c10 external-v8`，SHA `f5a45f15f69104c6f3dfe9f7a855e71f5d142d896cc78ffadbf12b3a57f813e4`。
- 左邻 `r08_c09` 的 `dbaf9d7e...` 仍在返修，记录为 provisional，不作为最终固定边。
- 材质使用选用 r08_c07 的原像素 768 裁片，风格实际附 `designs/gameplay-ui/04-guild.png`。全部完整来源 SHA 见 `layout-record.json` 与各 `.derived.json`。

## 请主任务先看的输入

1. `references/master-core-native384.png` 与 `references/plaza-core-native768.png`：对照原城／局部重绘差异。
2. `guides/r04_c02.master-layout-only.png` 与 `guides/r04_c02.plaza-layout-review-only.png`：首片几何对照。
3. `references/r04_c02.bottom-neighbor-native-context.png`：已选底邻的原像素条带。
4. `references/clean-stone-native768.png`：干净材质参考。

首片选 r04_c02：避开未定左边，先研究底邻约束。其全城范围 `[37773,31629,39027,32883]`；底邻顶端 115 行对应目标 y=1139..1254。1254×512 条带中剩余部分仅供上下文参考，不是多出来的目标重叠。首片灰色嵌板、弧线倒角及花卉浮雕在两版布局之间有局部区别，不能把数值变换通过当作衔接通过。

## 防止机械直线污染

新引导由单一原城源采样，没有邻图矩形拼贴，没有画 4×4 网格。底邻独立附图。x/y=115、1024、1139 是制作坐标，不是砖缝；禁止模型为色块或采样不连续补画水平／垂直分割线。真实构造线只依据原城设计。材质图只取画法，不复制它的金线、台阶或砖块布局。

`requests/r04_c02.draft.request.json` 仅是待审请求，不可视为真实提交。`generationReady=false`；须主任务先核清原城与底邻的几何冲突，再决定是否生图。配置目标是 gpt-image-2.5-sunburst / max；actualModel、actualQuality 均为 null。所有参考放大图、导航覆盖图与预览均不得进入拼接成品。

`preparation-validation.json` 的算术及 24 组分区重叠检查只验证制作计划，不是图像接缝验收。下一步生成后仍需完整检查 6 条内部缝、9 个内部交点及实际相邻外边和四块交点，精确绑定对应 SHA。现阶段这些图像验收全部未检查。
'''
(P/'HANDOFF.md').write_text(handoff,encoding='utf-8')
print(json.dumps({'plan':record(P/'plan.json'),'visualReview':record(P/'input-visual-review.json'),'handoff':record(P/'HANDOFF.md'),'generationReady':False},ensure_ascii=False,indent=2))
