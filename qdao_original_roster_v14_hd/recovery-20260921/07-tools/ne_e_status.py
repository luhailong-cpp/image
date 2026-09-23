"""Snapshot only07 NE/E selected slots and truthful visual-review status."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image
from finalize_current import metrics

HERE = Path(__file__).resolve().parent
ROOT = HERE / 'candidate/07_moon_shadow_assassin_girl'
OUT = HERE / 'ne-e-review'
rows = []
for direction in ['NE', 'E']:
    for slot in [f'idle/{direction}.png'] + [f'walk/{direction}/{n:02}.png' for n in range(1, 17)]:
        p = ROOT / slot
        m = json.loads(Path(str(p) + '.generation.json').read_text(encoding='utf-8-sig'))
        im = Image.open(p)
        rows.append({'slot': slot, 'attempt': m['attempt'], 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                     'sourceSha256': m['derivedFrom']['sha256'], 'sourcePresent': Path(m['derivedFrom']['path']).is_file(),
                     'nativeSize': m['nativeMetrics']['size'], 'mode': im.mode, 'metrics': metrics(im),
                     'outputShaMatchesSidecar': hashlib.sha256(p.read_bytes()).hexdigest() == m['outputSha256']})
now = datetime.now(timezone.utc).isoformat()
record = {'character': '07_moon_shadow_assassin_girl', 'observedAt': now, 'scope': ['NE','E'],
          'rows': rows, 'walkCount': 32, 'idleCount': 2,
          'uniqueSelectedSourceHashes': len({r['sourceSha256'] for r in rows}),
          'sourcePresentCount': sum(r['sourcePresent'] for r in rows),
          'allOutput1024RGBA': all(r['metrics']['size'] == [1024,1024] and r['mode']=='RGBA' for r in rows),
          'allOutputShaVerified': all(r['outputShaMatchesSidecar'] for r in rows),
          'offlineVisualPass': False, 'clientIntegration': False,
          'remaining': ['E near/far leg reversal and transitions are actively being redrawn; current file count is not acceptance.',
                        'After final selections refresh preview and rerun complete 30ms light/dark normal/enlarged seam review.']}
(OUT / 'review-record.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
handoff = HERE / 'NE_E_HANDOFF.md'
old = handoff.read_text(encoding='utf-8-sig')
marker = '\n<!-- HISTORICAL_NE_E_HANDOFF -->\n'
history = old.split(marker, 1)[1] if marker in old else old
lines = ['# 07 月影少女 NE / E 当前交接', '', f'更新时间（UTC）：{now}', '',
         '**仍在制作，两个方向均未宣布完整离线验收通过；未做客户端接入。**', '',
         '- 当前实际文件：NE、E 各16张行走和1张独立站立，共34张1024透明PNG。',
         f'- 当前34张输出SHA全部匹配记录：{record["allOutputShaVerified"]}；记录的原生来源SHA互不重复：{record["uniqueSelectedSourceHashes"]}/34。',
         '- 原生来源尺寸均1254×1254。历史清理删除的raw只能按文字/清理证据追溯，不代表可重新读像素。新生成raw保留在07-generation各attempt目录。',
         '- NE已修02/03比例、06尺寸、07/08比例与脚踝相位、13/14前摆与15反侧蹬离；旧13-v3只迁至12一槽，见ne-reassignment-20260923.json。',
         '- E04是旧1024候选的0.9647812166488794整幅等比缩小，来源SHA及旧记录在ne-e-review/E04-scale-20260923.json；没有伪称新AI原生图。',
         '- E01/09、03/11经双人复核发现近远腿未清楚交换，正在修E06前摆至13承重过渡。E09-r20260923a/b/c/d/f不选；e是正确近腿抬膝的姿势参考，不能同时计入多个槽。',
         '- NE07-r20260923a/b、NE08-r20260923a的头比修正过度，不选；当前07c/08b重新以NE09正常比例作实际参考，未用自动头宽缩放。',
         '- 内置工具未披露实际型号/质量，actualModel/actualQuality为null。未调用收费API。',
         '- 预览页：ne-e-review/index.html；深浅GIF各16×30ms=480ms（最终选槽后需再重建）。IAB曾实播深浅512及部分1024/接缝，后续修改不能沿用旧验收。',
         '', '## 当前逐槽选择（以此表及实际sidecar为准）', '', '| 槽 | 实际来源attempt | 输出SHA256 |', '|---|---|---|']
lines += [f'| {r["slot"]} | {r["attempt"]} | {r["sha256"]} |' for r in rows]
lines += ['', '## 恢复第一步', '',
          '先读本表及各attempt/result.json，处理已经成功但未导出的唯一raw；再完成E反侧腿过渡，不重复生成或把拒稿计为完成。生成入口现可用，当前不是工具额度阻塞。',
          '', '以下是旧交接，仅保留历史；库存、选择与保留规则以本节和最新用户要求为准。']
handoff.write_text('\n'.join(lines) + marker + history, encoding='utf-8')
print(json.dumps({k:record[k] for k in ['walkCount','idleCount','uniqueSelectedSourceHashes','sourcePresentCount','allOutput1024RGBA','allOutputShaVerified']}))
