"""Record stopped row-eight work from disk without changing art or plans."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

SESSION = Path(__file__).resolve().parent.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
all_ids = [f'r{r:02}_c{c:02}' for r in range(1, 5) for c in range(1, 5)]
notes = {
 'r08_c07': {
  'selected': ['r04_c01.v2','r04_c02.v2','r04_c03.v2','r04_c04','r03_c01','r03_c02','r03_c03','r03_c04','r02_c01'],
  'rejected': ['r04_c01','r04_c02','r04_c03'],
  'next': ['r02_c02','r01_c01','r02_c03','r02_c04','r01_c02','r01_c03','r01_c04'],
  'instructions': '''先检查 requests/r02_c02.request.json 与 requests/r01_c01.request.json。原执行者此前报告这两个坐标正在生成，但磁盘未保存对应原图或可靠完成回执；本交接没有恢复其返回值，不能算完成。新窗口先核对是否有真实可恢复结果，否则重新调用并保存真实回执。两张现有引导与提示已准备，不要再次执行 prepare 覆盖。

已有选用小片顺序由 plan.json 指定：底排到顶排，排内从左到右。未准备坐标用 make_tile.py prepare <内部坐标> 生成参考，前提是其左／底依赖已保存；已有 guide 不重跑。读取 requests/<坐标>.request.json 作为 image_gen 实际参数。工具完成后先保存 native/<版本>.tool-response.json（真实 output_hint 与 observedCompletionAt），再运行 make_tile.py ingest <内部坐标> <工具返回原图绝对路径> <回执绝对路径>。原图路径必须来自真实响应，不猜测。

make_tile.py 只有 init/prepare/ingest，没有完整 4K assemble。16 片齐备后可参考相邻 r08_c09/native_tools.py 的机械拼接实现另建本目录版本，绑定本块选用来源和全局坐标，不能直接调用其硬编码的 r08_c09 组装入口。'''
 },
 'r08_c08': {
  'selected': ['r01_c01.v2','r01_c02.v2'],
  'rejected': ['r01_c01','r01_c02','r01_c03'],
  'next': ['r01_c03'] + all_ids[3:],
  'instructions': '''plan.json 仍把 r01_c03.png 指作已保存，这是原始执行时的保存状态，不代表材质合格。该片属于旧碎纹批次，按本交接排除，先生成其 clean-material v2；原文件和计划保留。r01_c01.v2 与 r01_c02.v2 是续作选用来源，但仍需拼接后视觉检查，不是正式通过。

改良提示在 prompts/<坐标>.clean-material.prompt.txt；实际已成功 v2 参数和参考输入顺序见 native/r01_c01.v2.tool-response.json、native/r01_c02.v2.tool-response.json。准备新请求前确认第一张为目标几何参考，第二张为已选原像素材质参考，最后一张为 designs 风格成图；不混入 UI 内容。

工具返回后先按现有结构保存 native/<版本>.tool-response.json（request、response.output_hint、observedCompletionAt），再运行 save_native.py <内部坐标> <版本名>，例如新 r01_c03.v2 回执保存后用 save_native.py r01_c03 r01_c03.v2。该脚本只读取真实回执、完整复制原图、写逐图记录和更新选用指针，不进行生图。不要重跑 prepare.py 覆盖现有几何和计划。16 片齐备后另建本块机械组装及 QA，当前目录尚无完成的 4K 组装。'''
 },
 'r08_c09': {
  'selected': ['r01_c01.v2','r01_c02.v2','r01_c03.v2','r01_c04.v2','r02_c01.v2'],
  'rejected': ['r01_c01','r01_c02','r01_c03','r01_c04'],
  'next': all_ids[5:],
  'instructions': '''当前 plan.json 的 outputFile 是各坐标拟用的 v2 路径，不表示 16 张均已生成。磁盘只有首排四张 v2 和 r02_c01.v2，其余 11 张不存在。

从 requests/r02_c02.v2.request.json 开始，逐个读取真实准备好的 request，调用 image_gen。第 1 张是几何引导；第 2 张 references/clean-stone-material-native-crop.png 是 r09_c09 v6 的原像素材质裁切；第 3 张是 designs 成图。旧 v1 用的较大整体参考导致碎纹，不再选用。

真实返回后保存 requests/<版本>.receipt.json，含与对应 request 完全相等的 request、真实 response.output_hint 和 completedAtUtc（宿主观察时间，不是服务器生成时刻），再运行 native_tools.py save <版本名>，例如 native_tools.py save r02_c02.v2。16 个拟选 outputFile 均存在且完成来源记录后才能运行 native_tools.py assemble，再运行 native_tools.py qa 生成原像素板，随后必须实际看板并写真实检查结论。这些命令不会自动提供美术通过；现有 prepare 不重跑覆盖。'''
 }
}

for tile, cfg in notes.items():
    directory = SESSION / ('next_tile_' + tile)
    plan_path = directory / 'plan.json'
    plan = read(plan_path)
    selected = []
    for stem in cfg['selected']:
        p = directory / 'native' / (stem + '.png')
        record = directory / 'native' / (stem + ('.generation.json' if tile == 'r08_c08' else '.record.json'))
        data = read(record)
        assert p.exists() and (data.get('nativeSha256') or data.get('sha256')) == sha(p)
        selected.append({'id': stem.split('.')[0], 'versionStem': stem, 'file': str(p), 'sha256': sha(p),
                         'record': str(record), 'recordSha256': sha(record),
                         'status': 'selected_for_continuation_pending_assembly_and_visual_QA'})
    rejected = []
    for stem in cfg['rejected']:
        p = directory / 'native' / (stem + '.png')
        rejected.append({'file': str(p), 'sha256': sha(p), 'status': 'retained_not_selected',
                         'reason': 'Earlier material-flake/mottle failure or superseded retry from prior session review; no new visual review performed at handoff.'})
    native = sorted((directory / 'native').glob('*.png'))
    assert len(native) == len(selected) + len(rejected)
    selected_ids = {x['id'] for x in selected}
    missing = [x for x in all_ids if x not in selected_ids]
    state = {'schemaVersion': 1, 'createdAtUtc': datetime.now(timezone.utc).isoformat(), 'tile': tile,
             'status': 'stopped_for_user_requested_handoff_incomplete',
             'compiledBy': 'root from existing disk records after subagent response-stream failures; no new generation',
             'selectedPatchCount': len(selected), 'targetPatchCount': 16,
             'retainedNativePngCountIncludingRejected': len(native), 'selectedPatches': selected,
             'rejectedOrSuperseded': rejected, 'missingOrNeedsRegeneration': missing,
             'suggestedNextOrder': cfg['next'], 'plan': {'file': str(plan_path), 'sha256': sha(plan_path)},
             'planUnchangedByHandoff': True,
             'localProducerAgentsInterruptedForHandoff': True, 'newGenerationCallsStartedByThisHandoff': 0,
             'hostSideInFlightCallsVerifiedAbsent': False, 'hostSideInFlightStatus': 'unknown',
             'unresolvedCallMeaning': 'Prior stream failures prevented retrieval/confirmation of outstanding host calls. Existing requests without saved PNG and actual receipt remain incomplete; no cancellation/completion claim is made.',
             'full4KCandidateCreated': False, 'fullInternalSeamReviewPassed': False, 'fullExternalSeamReviewPassed': False,
             'fourTileJunctionReviewPassed': False, 'formalAccepted': False, 'runtimePublished': False,
             'actualModel': None, 'actualQuality': None, 'backendModelVerified': False,
             'styleAndMaterial': 'Keep exact layout; replace flake/mottle/crackle/veins with broad sparse clean Q stone tones. Guide paste material boundaries are not scene geometry. Use native crop material authority and actual designs reference.'}
    with (directory / 'handoff-state.json').open('x', encoding='utf-8') as stream:
        json.dump(state, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    lines = [f'# {tile} 停止制作交接', '',
             f'选用待拼接来源 {len(selected)}/16 张，保留原生 PNG 共 {len(native)} 张，其中 {len(rejected)} 张为不选用旧版。没有完整 4096 候选，没有整块接缝或正式验收通过。', '',
             '本交接由主窗口直接核对磁盘记录汇总。子执行者此前发生响应流中断，主窗口已停止其继续执行；旧宿主生图是否仍在运行无法核实，状态记为 unknown。没有原图及真实完成回执的调用不计完成。新窗口可以先核对是否可恢复结果，再决定补绘，不得伪造回执。', '',
             '## 选用来源（仅续作，不是验收通过）', '', '| 内部坐标 | 文件 | PNG SHA-256 |', '| --- | --- | --- |']
    lines += [f"| {x['id']} | `native/{Path(x['file']).name}` | `{x['sha256']}` |" for x in selected]
    lines += ['', '精确记录及 SHA 见 [handoff-state.json](handoff-state.json)。', '',
              '## 待完成', '', '、'.join('`'+x+'`' for x in missing), '', cfg['instructions'], '',
              '命令使用 `C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`，在本目录运行相应脚本。图像生成必须通过实际 image_gen 工具调用；Python 只用于来源保留、几何参考、组装和检查。', '',
              '## 材质与验收边界', '',
              '以最新干净 v2 的实际提示为参考：第 1 张只约束几何，把整片碎纹、云斑、白脉、细裂纹替换为宽缓稀疏色调；保留真实砖缝、雕刻和道路。x=230/y=1024 等处可能是参考拼贴材质分界，不应画成新的边。风格输入实际使用 designs/guild-ui-v2/source/guild-overview.png，只取画法，不加 UI／文字／道具。', '',
              '新图原生输出为 1254²，核心 1024、halo 115、相邻 overlap 230，拼成 4326 后裁成 4096。不能把布局引导放大后当成品。先查 6 条内部全长缝、9 个内部交点，再查底邻全长与未来左右邻居及真实四块交点；最近镜头、布局和导航未通过。', '',
              '当前 configured model/quality 是目标，实际后端型号和质量未披露，保留 null；服务器生成时刻未披露，宿主观察时间单独记。全部旧版、请求、回执、计划和参考保留。']
    with (directory / 'HANDOFF.md').open('x', encoding='utf-8') as stream:
        stream.write('\n'.join(lines) + '\n')
    print(json.dumps({'tile': tile, 'selected': len(selected), 'retained': len(native), 'missing': len(missing), 'inFlight': 'unknown'}))
