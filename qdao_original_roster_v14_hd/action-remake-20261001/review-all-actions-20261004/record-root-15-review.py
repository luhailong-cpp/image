import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent
snapshot = json.loads((root / 'root-15/source-evidence.json').read_text(encoding='utf-8-sig'))
frames = snapshot['frames']
now = datetime.now(timezone.utc).isoformat()
changed = []
for frame in frames:
    current = hashlib.sha256(Path(frame['path']).read_bytes()).hexdigest()
    if current != frame['sha256']:
        changed.append({'action': frame['action'], 'direction': frame['direction'], 'frame': frame['frame'], 'reviewed_sha256': frame['sha256'], 'current_sha256': current})
report = {
    'schema_version': 1,
    'character_id': '15_water_dragon_scholar_boy',
    'reviewed_at_utc': now,
    'reviewer': 'root',
    'scope': 'Actual visual review of all 28 current full/hand and leg/foot contact sheets, plus identity portrait; static only.',
    'static_groups_reviewed': 14,
    'static_frames_reviewed': 196,
    'snapshot': 'root-15/source-evidence.json',
    'source_snapshot_at_utc': snapshot['createdAtUTC'],
    'source_changed_after_snapshot': changed,
    'changed_frame_reinspection': [{'sequence': 'attack/W', 'frame': 3, 'sha256': '2ec7fb8912f0808d3f813a53378ddd168680617a39a83c53578b746ffb02a5a2', 'actually_viewed_current_single_frame': True, 'observation': '新图已单帧实看；仍为右手后上举持扇、左手前伸，手腕握持与腿脚方向未确认新增硬伤；不代表相邻动作动态通过。'}],
    'manifest_sha_mismatches_at_snapshot': sum(not f['shaMatches'] for f in frames),
    'identity': '右手水龙扇，左手空闲，左胯玉佩；实际查看当前身份画像。',
    'confirmed_additional_art_errors': [],
    'dynamic_checks_dispatched': [
        {'sequence': 'run/N', 'transition': '10→11', 'observation': '扇由腰侧到肩侧的幅度较大，须核定身侧过渡。'},
        {'sequence': 'run/E', 'transition': '03→04', 'observation': '持扇臂/空手前后位置及胸肩转角变化较大。'},
        {'sequence': 'run/W', 'transition': '03→04', 'observation': '胸前到背肩视角的摆臂躯干过渡须连播核定。'},
        {'sequence': 'run/NW', 'transition': '02→03', 'observation': '扇由前侧到背肩的身侧/遮挡过渡须核定。'}
    ],
    'retained_observations': [
        '未确认需要新增重画的明显腿脚横扭、断握或左右持扇归属硬伤；不等于所有隐藏关节已看清或动态通过。',
        'N/S/NW/SW支撑相位15/16→01/02→03/04→05/06，07换足；NE/E/SE/W为16/01→02/03→04/05→06/07，08换足。已核对当前MERGE_HANDOFF，禁止强制01–08模板。',
        '正常抬跟露底和同一支撑鞋由身体前方行至后方不能独立作为横扭/换足证据。',
        '战斗六组全身及腿脚均已查看，暂无明确额外手脚或换手断握新增问题。'
    ],
    'timing': {'run': {'frames': 16, 'frame_ms': 75, 'cycle_ms': 1200}, 'hit_frame_ms': 40, 'attack_frame_ms': 30, 'cast_frame_ms': 45},
    'character_window_message_succeeded': True,
    'dynamic_acceptance': 'not_confirmed',
    'user_acceptance': 'not_confirmed',
    'source_images_modified_by_reviewer': False
}
(root / '15-static-review-20261005.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
prelim_path = root / 'preliminary-findings-20261005.json'
prelim = json.loads(prelim_path.read_text(encoding='utf-8-sig'))
for finding in prelim['findings']:
    if finding['character_id'] == '08_alchemy_prodigy_boy':
        finding.update(observation='NW07→08原换脚疑点已排除：实际同足跨16/01→02/03→04/05→06/07，08是正常换足边界。窗口独立仍在修E02握瓶手缺少身侧过渡。', status='initial_phase_suspicion_resolved_retain_correct_phase', static_groups_reviewed=14, static_frames_reviewed=196)
    if finding['character_id'] == '10_crimson_spear_girl':
        finding.update(observation='E/W04→05及12→13原提前换脚判断已降为待核：不能凭最低鞋或屏幕位置确认解剖换足，裙摆遮髋，需窗口真实标足追踪。NE09→10及NW10→11保留动态衔接核对，暂无确定换手/脱杆。', status='tentative_anatomical_tracking_and_dynamic_check_required')
prelim['updated_utc'] = now
prelim_path.write_text(json.dumps(prelim, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'reviewed_groups':14, 'reviewed_frames':196, 'source_changes_after_snapshot':changed, 'report':str(root/'15-static-review-20261005.json')}, ensure_ascii=False))
