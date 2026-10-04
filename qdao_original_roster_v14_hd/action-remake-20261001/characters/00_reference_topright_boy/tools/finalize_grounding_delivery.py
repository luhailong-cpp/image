"""Bind reviewed native art to this delivery; does not approve dynamic playback."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
BASE = 'review/grounding-fourframes/'


def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def write(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


def main():
    now = datetime.now(timezone.utc).isoformat()
    selected = read('selected-new.json')
    runs = [r for r in selected if r['action'] == 'run']
    assert len(runs) == 128
    reviewed = {}
    for name in ('E-independent.json', 'NE-independent.json', 'W-independent.json',
                 'N-NW-independent-static-review.json', 'S-SE-SW-independent-static-review.json'):
        report = read(BASE + name)
        groups = report.get('directions', {report.get('direction'): report})
        for direction, group in groups.items():
            selection = group['selection']
            path = selection['path'] if isinstance(selection, dict) else selection
            expected_sha = selection['sha256'] if isinstance(selection, dict) else group['selectionSha256']
            assert sha(path) == expected_sha, (direction, 'stale independent selection')
            for key in ('confirmedHardDefects', 'requiredNewEdits', 'hardStaticDefectsRemaining', 'hardStaticDefects', 'hardFindings'):
                assert not group.get(key), (direction, key, group[key])
            by_frame = {int(f['frame']): f for f in group['frames']}
            assert len(by_frame) == 16
            for row in [r for r in runs if r['direction'] == direction]:
                evidence = by_frame[row['frame']]
                assert row['sourceSha256'] == evidence['sourceSha256'] == sha(row['source'])
                assert row['source'] == evidence['source']
                if 'observedSupportFoot' in evidence:
                    assert evidence['observedSupportFoot'] == row['supportFoot']
            reviewed[direction] = {'report': BASE + name, 'reportSha256': sha(BASE + name),
                                   'selection': path, 'selectionSha256': expected_sha,
                                   'staticHardDefectsRemaining': [], 'dynamicVerified': False}
    assert set(reviewed) == set(DIRS)
    manifest = read('manifest.json')
    by_file = {f['file']: f for f in manifest['frames']}
    assert len(by_file) == 196
    for row in runs:
        f = by_file[f"frames/run/{row['direction']}/{row['frame']:02d}.png"]
        assert f['derivedFrom']['sha256'] == row['sourceSha256']
        assert f['frameDurationMs'] == 75
        assert f['sha256'] == sha(f['file'])

    # Preserve prior observations as text; bind every current run note to its actual source.
    notes = read('review/visual-notes.json')
    historical = notes.setdefault('historicalSnapshots', [])
    old_run = {k:v for k,v in notes['frames'].items() if k.startswith('run/')}
    if old_run:
        historical.append({'archivedAt': now, 'reason': 'Superseded by current independently reviewed selection', 'frames': old_run})
    notes['frames'] = {k:v for k,v in notes['frames'].items() if not k.startswith('run/')}
    for row in runs:
        key = f"run/{row['direction']}/{row['frame']:02d}.png"
        notes['frames'][key] = {'status': 'static_reviewed_dynamic_pending',
                                'source': row['source'], 'source_sha256': row['sourceSha256'],
                                'supportFoot': row['supportFoot'], 'positionPair': row['positionPair'],
                                'message': row['observation'],
                                'evidence': reviewed[row['direction']]['report'].removeprefix('review/'),
                                'dynamicVerified': False}
    notes['actions']['run'] = [{'status': 'native_grounding_repaired_static_reviewed_dynamic_pending',
        'message': '八方向128帧已按每脚前侧2→中间前段2→中间后段2→后侧2选入独立原生姿态，16×75ms=1200ms。支撑身份、鞋朝向、左手持葫芦与右空手静态复核无剩余明确硬伤；实际动态及客户端未验收。',
        'evidence': 'grounding-fourframes/current-static-delivery.json'}]
    notes['updatedAt'] = now
    write('review/visual-notes.json', notes)

    plan = [{'frames': [i, i+1], 'supportFoot': 'right' if i<9 else 'left',
             'positionPair': ((i-1)%8)//2+1,
             'position': ('front_landing','middle_early','middle_late','rear_push_off')[((i-1)%8)//2],
             'durationMs': 150} for i in range(1,17,2)]
    state = {'atUtc': now, 'status': 'native_repairs_exported_static_reviewed_dynamic_pending',
             'selectedSha256': sha('selected-new.json'), 'manifestSha256': sha('manifest.json'),
             'runFrames': 128, 'totalFrames': 196, 'normalFrameMs': 75, 'cycleMs': 1200,
             'perDirectionContactFrames': {d:{'right':list(range(1,9)), 'left':list(range(9,17)),
                                             'positionPairs':plan, **reviewed[d]} for d in DIRS},
             'confirmedStaticHardDefectsRemaining': [], 'dynamicVisualPlaybackVerified': False,
             'clientIntegrated': False,
             'limitations': ['逐帧可见支撑姿态不等于世界地面接触测量。',
                             '正常尺寸的脚底滑动、摆臂连续、首尾及跨方向切换未实际播放验收。',
                             '客户端位移速度、根点与地面尚未联合校准。',
                             '受击/普攻/施法交付范围为E/W，未扩展为八方向。']}
    write(BASE + 'current-static-delivery.json', state)
    contract = read(BASE + 'contract.json')
    contract['historicalMinimumOnlyPlan'] = {k:contract.pop(k) for k in ('minimumConsecutiveContactFrames','minimumContactMs') if k in contract}
    contract.update(status=state['status'], updatedAt=now, activeFramePlan=plan,
                    allocationInterpretation='每脚8帧：前侧2→中间前段2→中间后段2→后侧2；中间合计4帧。每对均为两张独立姿态，不复制延长。',
                    latestClarification='直脚着地两帧，再旁边点两帧，依次过渡',
                    currentEvidence='current-static-delivery.json',
                    currentSelectionSha256=state['selectedSha256'])
    write(BASE + 'contract.json', contract)
    foot = read('review/foot-heading-review-current.json')
    foot.update(scopeStatus='historical_review_superseded_by_grounding_delivery',
                supersededBy='grounding-fourframes/current-static-delivery.json',
                supersededAt=now)
    write('review/foot-heading-review-current.json', foot)

    banner = '> 2026-10-04最新：八方向跑步128帧接地与手脚修订已合入196张导出；每脚前侧2→中间4→后侧2，各相邻位置两张独立姿态，正常16×75ms=1200ms。逐图及独立静态复核完成；实际动态与客户端未验收。当前交付见[DELIVERY.md](DELIVERY.md)。'
    for name in ('STATUS.md','MERGE_HANDOFF.md'):
        path = ROOT / name
        text = path.read_text(encoding='utf-8-sig')
        lines = text.splitlines()
        lines = [banner if line.startswith('> 2026-10-04最新：') else line for line in lines]
        text = '\n'.join(lines)+'\n'
        text = text.replace('196个动作槽位齐全：八方向跑步128帧，E/W受击12帧、普攻24帧、施法32帧。已完成本轮定位到的手脚及14槽脚向修订，并调整离线正常节奏；数量、静态修复与实际动态/客户端验收分开统计。',
                            '196张资源已落盘：八方向跑步128帧，E/W受击12帧、普攻24帧、施法32帧。当前以四个相邻位置各两帧的完整原生选表为准；旧14槽脚向修订记录仅为历史。')
        text = text.replace('当前196槽资源已收齐，本轮14槽明确脚掌外撇的原生修复已合入。',
                            '当前196槽资源已收齐，八方向128帧的新接地选表已合入。')
        path.write_text(text, encoding='utf-8')

    rows = '\n'.join(f'| {d} | 01–02 | 03–04、05–06 | 07–08 | 09–10 | 11–12、13–14 | 15–16 |' for d in DIRS)
    delivery = f'''# 金发带道童 · 当前素材交付

本角色196张1024×1024透明PNG已导出。八方向跑步的脚向、支撑身份、左手持葫芦与右空手已完成逐图及独立静态复核，未剩明确静态硬伤；本页不宣称客户端或整段动态已验收。

- [打开全部动作预览](review/index.html)：正常速度、¼慢放、暂停、逐帧、方向与动作切换。
- [直接看正常跑步动画（E）](review/animations/run-E-normal.webp) · [全部动画文件](review/animations/)。
- [正式PNG目录](frames/) · [逐帧清单](manifest.json) · [SHA256](SHA256SUMS.txt)。
- [当前静态复核与来源绑定](review/grounding-fourframes/current-static-delivery.json)。

跑步一圈16帧，每帧75ms，共1200ms。每只脚前侧2帧、中间4帧、后侧2帧；中间拆成相邻的两组2帧，均为独立姿态，无复制停帧或插值。下表为静态图中可见的支撑帧，左右以角色自身为准，侧位置沿跑向推进。

| 方向 | 右前侧 | 右中间 | 右后侧 | 左前侧 | 左中间 | 左后侧 |
| --- | --- | --- | --- | --- | --- | --- |
{rows}

受击、普攻、施法均保留当前E/W两方向版本，分别12、24、32帧；本轮没有扩展为八方向战斗动作。正常帧时长分别40、30、45ms。其他角色（包括月影少女）未在本任务修改或验收。

## 验证边界

当前128张跑步原生图均有逐图来源记录、独立选表和静态复核。正式导出仅每方向固定整画布变换，无逐帧脚底吸附、裁切配准、镜像或补帧。技术报告检查图片、来源、唯一性及预览时序，播放器逻辑验证不等于观看动画。

尚未通过：正常显示尺寸实际播放下的接地/摆臂/首尾连续性，以及客户端位移、滑步和世界地面校准。当前1200ms节奏已写入离线交付，客户端未接入。透明单帧无法单独证明世界地面接触高度。

配置目标为gpt-image-2.5-sunburst/max；内置工具未披露的实际模型/质量仍为未确认，详见各图记录。生成与拒稿文字证据保留，图片按当前引用及项目素材保留规则清理。

交付记录更新：{now}。
'''
    (ROOT/'DELIVERY.md').write_text(delivery,encoding='utf-8')
    (ROOT/'SHA256SUMS.txt').write_text(''.join(f"{f['sha256']}  {f['file']}\n" for f in manifest['frames']),encoding='utf-8')
    print(json.dumps({'status':state['status'],'reviewedRunFrames':128,'exportedFrames':196},ensure_ascii=False))


if __name__ == '__main__':
    main()
