import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

now = datetime.now(timezone.utc).isoformat()
selection = read(ROOT / 'selection/run-SW.json')
review_path = ROOT / 'review-parts/run-SW.json'
review = read(review_path)
observations = {
    1: ('right', True, '右前靴已压平，右膝较16进入加载；左腿仍屈膝后收。右膝、胫骨和鞋尖共同朝前偏左，未出现独立踝外旋。'),
    2: ('right', True, '右膝明显屈曲，右脚跟与前掌共同承重，躯干前倾进入缓冲；左脚仍后收。鞋面朝向随胫骨，未将两腿变窄当作脚向修正。'),
    3: ('right', True, '右脚在髋下保持全掌承重，左膝前驱、右膝仍保留屈曲；右靴鞋面向前下且无整片鞋底朝镜头。与02的屈膝缓冲姿态不同。'),
    4: ('right', False, '右腿进入后段支撑，左腿前驱；膝踝鞋面仍相连。此帧虽可读为支撑，为保守计数不纳入四帧最小承重段。'),
    5: ('right', False, '右腿后伸、前掌蹬离，左膝领先；后脚踝沿腿向前下，不计入完整四帧承重段。'),
    6: ('none', False, '双腿屈曲收起，左膝在前、右腿在后；短飞行，不算接地。'),
    7: ('none', False, '左腿伸向下个接触点，鞋底大片朝向镜头且未压平；为下落，不算接地。'),
    8: ('left', True, '左前靴由07的展示鞋底转为鞋面向前、靴底压平的初接触；左膝微屈，右腿屈膝后收。'),
    9: ('left', True, '左脚加载时保持靴底平面，左膝比08更收屈、髋稍前移；右脚后收位置和左臂摆位独立变化。'),
    10: ('left', True, '左膝进一步屈曲缓冲，靴面沿胫骨朝前偏左，鞋跟与前掌承重；右脚后收。没有横撇或锁膝。'),
    11: ('left', True, '左脚在髋下承重，左膝仍有弯曲，右膝已明显前驱；靴底仍平，没有提前提踵凑满第四张。'),
    12: ('left', False, '左腿进入后段支撑，右膝前驱；仍保持膝踝连续。为保守计数不纳入四帧最小承重段。'),
    13: ('left', False, '左后靴明确提踵，前掌蹬离；脚尖跟随小腿前下，无踝突然外翻。不计入四帧承重段。'),
    14: ('none', False, '右膝领先、双腿收起形成短飞行；不算接地。'),
    15: ('none', False, '右腿向前下伸展，前靴仍保持下落姿态；保守不计接触，等待16明确初接触。'),
    16: ('right', True, '右前脚初接触，鞋尖朝前偏左、鞋底开始落平；右膝微屈而非锁直，左腿收后。下一帧01继续加载，形成跨循环连续段。'),
}
frames = []
for n in range(1, 17):
    item = next(f for f in selection['frames'] if f['frame'] == n)
    path = ROOT / item['file']
    record_path = ROOT / item['generationRecord']
    record = read(record_path)
    im = Image.open(path)
    support, counted, observation = observations[n]
    facts = {
        'frame': n, 'slot': f'run/SW/{n:02d}', 'file': item['file'], 'sha256': sha(path),
        'width': im.width, 'height': im.height, 'mode': im.mode,
        'alphaExtrema': list(im.getchannel('A').getextrema()),
        'sourceNativeSize': item['sourceNativeSize'],
        'generationRecord': item['generationRecord'], 'generationRecordSha256': sha(record_path),
        'selectionShaMatches': sha(path) == item['sha256'],
        'generationRecordShaMatchesSelection': sha(record_path) == item['generationRecordSha256'],
        'existingSourceRecordRetained': True, 'pixelsChangedThisReview': False,
        'observedSupportFoot': support, 'countedInMinimumFourContactSegment': counted,
        'visualObservation': observation,
        'staticToeKneeAnkleCheck': 'passed', 'reviewMethod': 'original_runtime_png_view_image_and_contact_sheet',
    }
    assert im.size == (1024, 1024) and im.mode == 'RGBA'
    assert min(item['sourceNativeSize']) >= 1024
    assert facts['selectionShaMatches'] and facts['generationRecordShaMatchesSelection']
    frames.append(facts)
    existing = next(f for f in review['frames'] if f['slot'] == facts['slot'])
    assert existing['sha256'] == facts['sha256']
    existing['fourContactStaticReview20261004'] = {
        'reviewedAt': now, 'sha256': facts['sha256'], 'counted': counted,
        'observedSupportFoot': support, 'evidence': observation,
        'staticToeKneeAnkleCheck': 'passed', 'dynamicPlaybackPassed': False,
    }

assert len({f['sha256'] for f in frames}) == 16
segments = [
    {'foot': 'right', 'frames': [16, 1, 2, 3], 'count': 4, 'crossesLoopBoundary': True,
     'phases': ['initial_contact', 'loading', 'knee_flexion_compression', 'mid_support'], 'durationMs': 300},
    {'foot': 'left', 'frames': [8, 9, 10, 11], 'count': 4, 'crossesLoopBoundary': False,
     'phases': ['initial_contact', 'loading', 'knee_flexion_compression', 'mid_support'], 'durationMs': 300},
]
audit = {
    'reviewedAt': now, 'action': 'run', 'direction': 'SW',
    'scope': '每只脚每次落地至少连续4张独立、可辨接触/缓冲/承重；全部16张膝踝与鞋掌朝向复核。',
    'minimumFourContactStaticStatus': 'passed_preserve_existing_frames',
    'decision': '两脚各有4张明确连续接触/承重帧。保留16张已认可图，不作无必要AI重画。',
    'imagegenCallsThisReview': 0, 'runtimeFilesChanged': [],
    'timing': {'frameDurationsMs': [75] * 16, 'cycleMs': 1200, 'uniform': True, 'extraLoopPauseMs': 0},
    'method': '先实看preview/qa/run-SW-contact.png，再逐张实看16张runtime原图；根据膝屈、踝角、鞋底承重朝向、前后腿和重心关系判断，不使用最低像素、旧相位标签或SHA差异作为动作成立证据。SHA仅绑定本次实际观察版本。',
    'contactSegments': segments,
    'excludedFromMinimumCount': {'late_support': [4, 12], 'forefoot_push_off': [5, 13], 'flight_or_descent': [6, 7, 14, 15]},
    'identityObserved': '棕高马尾、玉叶金饰、绿眼、绿白金短袍短靴；左手握完整长竹弓、右手空手、箭筒解剖右肩。',
    'staticFootDirectionResult': '16张未发现需要重画的明确鞋掌外撇、踝外翻或承重锁膝。',
    'groundCalibration': '未标定；不把历史y=940或任何最低像素视作实际世界地面。',
    'stillUnverified': ['1200ms正常速度的浏览器/客户端动态实播观感', '客户端世界地面、根点、角色位移与步频/滑步匹配'],
    'localBrowserAttempted': False, 'dynamicPlaybackPassed': False, 'clientModified': False,
    'sourceMetadataPolicy': '没有新图；原有模型/质量/来源记录保留，未按当前配置回填历史实际型号。',
    'frames': frames,
}
audit_rel = 'audit/run-SW-four-contact-20261004.json'
write(ROOT / audit_rel, audit)
review['fourContactStaticReview20261004'] = {k: v for k, v in audit.items() if k != 'frames'}
review['fourContactStaticReview20261004']['audit'] = audit_rel
review['updatedAt'] = now
review['wholeSequenceDynamicStatus'] = 'not_performed_by_this_reviewer'
seq = next(s for s in review['sequences'] if s['action'] == 'run' and s['direction'] == 'SW')
seq['fourContactStaticReview20261004'] = {'status': 'passed_preserve_existing_frames', 'contactSegments': segments, 'audit': audit_rel, 'reviewedAt': now}
seq['status'] = 'needs_review'
write(review_path, review)
print(json.dumps({'audit': audit_rel, 'frames': len(frames), 'changedPngCount': 0, 'contactSegments': segments, 'technicalValidation': 'passed', 'sequenceStatus': 'needs_review_dynamic'}, ensure_ascii=False))
