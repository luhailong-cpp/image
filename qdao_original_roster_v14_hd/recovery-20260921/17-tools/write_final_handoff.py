"""Write a character-local handoff from an accepted immutable asset manifest."""
from pathlib import Path
from common import RECOVERY, CHAR, DIRS, read, sha, save_new, require, now

out = RECOVERY / '17-delivery-preview/revisions/final-20260923'
manifest = read(out / 'manifest.json')
delivery = read(out / 'delivery.json')
acceptance = read(out / 'acceptance.json')
inventory = read(out / 'inventory-final.json')
require(delivery['all_directions_accepted'] and acceptance['offline_visual_approval'], 'Final approval required')
require(sha(out / 'manifest.json') == delivery['manifest_sha256'], 'Final bytes changed')
link = lambda label, path: f'[{label}]({Path(path).resolve().as_posix()})'
lines = [
    '# 17 灵篆书生 — 最终交接（2026-09-23）', '',
    '本窗口角色为 `17_ghost_script_calligrapher_boy`。最终已完成 **128/128 张真实行走 + 8/8 张独立站立**；8 方向素材与离线预览全部通过本次验收。客户端接入、Unity/引擎播放和正式上线均未执行。完成本角色后停止，不自动续做其他角色。', '',
    '## 成品与预览', '',
    '- '+link('成品目录：136 张 1024×1024 RGBA PNG', out / 'runtime'),
    '- '+link('八方向交互预览（可直接打开本地 HTML）', out / 'index.html'),
    '- '+link('八方向 30ms 循环总览', out / 'preview/eight-directions-30ms-dark.gif'),
    '- '+link('最终交付清单', out / 'delivery.json'),
    '- '+link('逐图来源、请求、回执和精确提示词证据', out / 'source-evidence.json'),
    '- '+link('验收判断与范围', out / 'acceptance.json'), '',
    '| 方向 | 行走 | 独立站立 | 离线结果 | 30ms 深底预览 | 30ms 浅底预览 |',
    '| --- | --- | --- | --- | --- | --- |'
]
for d in DIRS:
    lines.append(f'| {d} | 01–16，16/16 | 1/1 | 通过 | '+link('深底',out/f'preview/{d}-30ms-dark.gif')+' | '+link('浅底',out/f'preview/{d}-30ms-light.gif')+' |')
lines += ['', '## 验收与来源边界', '',
    '- 每张动作来自独立原生 1254×1254 完整单帧，最终导出 1024×1024 真透明 PNG；未用旧 512 图放大，未复制、镜像、插值或扭曲同一姿势补槽。统一缩放与画布锚点归一仅用于各自独立原稿的导出，不创造动作。',
    '- 逐帧检查交替迈腿、支撑/摆动脚、人物比例、装备手持、挂饰、墨灵与透明残边。实际浏览器以 30ms 播放八方向，检查深浅底、512 正常与1024放大，并核对 15→16→01→02 接缝。16 份单方向 GIF 的编码均为16×30ms=480ms，无限循环；未声称浏览器屏幕刷新实测达到精确33.33fps。',
    '- 锚点数值是透明轮廓与上半身轴线的测量约定：x=512±0.5，最低有效透明像素y=942。它不等同于所有可见支撑靴底都精确在同一y；脚底判断另见验收记录。S04靴底y941、挂饰y942的1px差，NE13左支撑靴底y937、右摆脚尖y942的5px画面投影差，均经正常/放大比较后接受，未平移或扭曲姿势修饰测量值。',
    '- 本次修正的代表问题：W02–04腿部前后关系；SE02/03/05及14–16步态、04/07比例；E10腿部深度；S01/06/07比例起伏；NE02/13上半身下沉。N08/N10优先恢复已生成原稿，未重复生成。拒稿和替换版本不计入136张。',
    '- 身份参考为项目原角色4096肖像及其1024输入衍生；实际附入 `designs/jubaozhai-ui/02-characters.png` 等相近用途的已确认风格参考。具体每次附图和哈希见来源证据。',
    '- 使用宿主内置image_gen，无收费API调用。配置目标为gpt-image-2.5-sunburst/max；入口不提供实际model/quality选择或返回值，逐图实际值记为null/host-managed-unverified，不能把配置或提示词当作实际型号证据。',
    '- 历史N向14条提示词档案比真实宿主返回文本多末尾LF；已保留原档并补充真实返回文本。idle-S-v2另有精确提交提示词补充。原请求/回执未伪改，详情见source-evidence。',
    '- 创建时manifest和单图派生记录中的pending/visualApproval=false是历史状态。最终离线批准在acceptance.json中，绑定本节同一manifest SHA；不要把旧创建标志读作最终结论。', '',
    '## 最终选稿与库存', '',
    f'- Manifest SHA256：`{sha(out / "manifest.json")}`。',
    f'- 来源证据 SHA256：`{sha(out / "source-evidence.json")}`。',
    f'- 原稿attempt共{inventory["raw_attempt_count"]}个；选用{inventory["selected_raw_count"]}个，排除{inventory["excluded_raw_count"]}个。最终所选原稿均已导入；缺方向/帧号：无。',
    '- 5个未导入旧raw均已被最终版本替代：idle-N-v1、NE06-v1、NE09-v1、NE09-v2、NE13-v1。它们不是缺槽或必须继续处理的任务。',
    '- 本轮最新指令明确要求保存真实raw及请求/回执，并禁止清理，因此仍保留来源归档；交付runtime目录仅含选中成品PNG及文字元数据。未执行删除、Git提交、推送或Git清理。未改其他角色和共享角色状态。',
    '- 旧动作和00–04未作恢复或修改；本次未改客户端工程。', '',
    '| 方向 | 独立站立版本 | 行走01–16版本 |', '| --- | --- | --- |'
]
bykey = {r['path']:r for r in manifest['files']}
for d in DIRS:
    versions = ', '.join(f'{n:02d}={bykey[f"walk/{d}/{n:02d}.png"]["selected_revision"].rsplit("-",1)[1]}' for n in range(1,17))
    lines.append(f'| {d} | {bykey[f"idle/{d}.png"]["selected_revision"]} | {versions} |')
lines += ['', '## 接手边界', '',
    '素材制作：完成。离线预览验收：完成。客户端接入：未执行。无剩余制图阻塞、无缺帧；下一步如另行安排接入，应从本成品runtime目录读取，按30ms逐帧和同一画布锚点接入后另做客户端验收，本窗口不自动执行。', '']
path = RECOVERY / '17-HANDOFF-20260923.md'
require(not path.exists(), 'Do not overwrite existing handoff')
path.write_text('\n'.join(lines), encoding='utf-8')
save_new(RECOVERY / '17-HANDOFF-20260923.json', {
    'character_id':CHAR, 'recorded_at':now(), 'handoff_md':str(path), 'handoff_sha256':sha(path),
    'runtime':str(out/'runtime'), 'preview':str(out/'index.html'), 'manifest_sha256':sha(out/'manifest.json'),
    'walk_complete':True, 'walk_count':128, 'independent_idle_complete':True, 'independent_idle_count':8,
    'offline_visual_approval':True, 'client_integration':False, 'missing_slots':[], 'blocked':False,
    'unprocessed_selected_raw':[], 'generation_inflight':False, 'continue_next_character':False,
    'source_retention':'retained_per_latest_explicit_task', 'asset_manifest':str(out/'manifest.json'),
    'acceptance':str(out/'acceptance.json'), 'inventory':str(out/'inventory-final.json')
})
print(path)
