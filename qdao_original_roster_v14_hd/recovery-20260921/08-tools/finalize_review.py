"""Record completed human-visible offline review against exact selected pixels."""
from pathlib import Path
from datetime import datetime, timezone
import json
from PIL import Image, ImageDraw
from process import RECOVERY, write, sha

here = Path(__file__).resolve().parent
delivery = RECOVERY / '08-delivery-preview'
dest = delivery / 'revisions' / 'final-v1'
manifest = json.loads((dest / 'manifest.json').read_text(encoding='utf-8'))
bindings = json.loads((delivery / 'reviewed-snapshot-bindings.json').read_text(encoding='utf-8'))
bound = {r['slot']: r for b in bindings for r in b['files']}
assert len(bound) == len(manifest['files']) == 136
for row in manifest['files']:
    assert row['sha256'] == bound[row['slot']]['sha256'] == sha(dest / row['path'])
    assert row['source_attempt'] == bound[row['slot']]['source_attempt']

review = {
    'schema': 'qdao-08-offline-visual-acceptance-v1',
    'completedAt': datetime.now(timezone.utc).isoformat(),
    'character_id': '08_alchemy_prodigy_boy', 'revision': 'final-v1',
    'walk_accepted': 128, 'independent_idle_accepted': 8, 'unresolved_visual_blockers': [],
    'visual_approval': True, 'browser_review_performed': True,
    'reviewed_snapshot_bindings': bindings,
    'checks': ['All selected frames reviewed on light and dark contact sheets',
               'Foot and lower-body crops checked at 1:1',
               'Eight directions played in local browser at 30 ms timeline, normal 512 and enlarged 1024 display, both backgrounds',
               'Opposite-leg progression, support foot, body proportions and foot anchoring checked',
               '15 -> 16 -> 01 -> 02 transitions reviewed in contact strips and browser seam mode',
               'Eight independently generated idle images inspected'],
    'notes': ['Rejected duplicate-leading-leg, kick and disproportionate-stride attempts are excluded by explicit selections.',
              'Small generative differences in hair, brocade and ankle rendering remain; no blocking gait or transparent-edge issue observed in accepted selections.',
              'The browser uses time-based frame selection without interpolation; screen refresh can skip displayed frames. Encoded 16 x 30 ms GIF timing is separately audited.'],
    'browser_evidence': 'Actual CUA screenshots and interactions in this task; no captured-video or measured-monitor-timing claim.',
    'client_integration': 'not_performed', 'unity_validation': False, 'formal_client_validation': False,
    'files': [{'slot': r['slot'], 'sha256': r['sha256'], 'source_attempt': r['source_attempt']} for r in manifest['files']],
}
write(dest / 'browser-review.json', review)
manifest.update(status='offline_accepted', visual_approval=True, browser_review_performed=True,
                visual_acceptance_record='browser-review.json', visual_acceptance_sha256=sha(dest / 'browser-review.json'),
                unity_validation=False, formal_client_validation=False,
                retention_policy='Keep final game/design assets and textual provenance; source and intermediate image copies removed only after file audit succeeds.')
for row in manifest['files']:
    row['visual_review'] = 'accepted'
manifest['scripts'] = [{'file': str(here / name), 'sha256': sha(here / name)} for name in ('process.py', 'build.py', 'preview.html')]

for theme, color in [('light', (240,238,228)), ('dark', (30,38,46))]:
    sheet = Image.new('RGB', (2048,1088), color)
    draw = ImageDraw.Draw(sheet)
    for index, direction in enumerate(manifest['directions']):
        im = Image.open(dest / 'runtime' / 'idle' / (direction + '.png')).convert('RGBA').resize((512,512), Image.Resampling.LANCZOS)
        x, y = (index % 4)*512, (index // 4)*544
        sheet.paste(im, (x,y+32), im)
        draw.text((x+12,y+8), direction + ' IDLE', fill='white' if theme=='dark' else 'black')
    file = dest / 'preview' / ('idle-eight-directions-' + theme + '.jpg')
    sheet.save(file, quality=94)
    manifest['contact_sheets'].append({'path':file.relative_to(dest).as_posix(), 'sha256':sha(file), 'review_composite_only':True})
write(dest / 'manifest.json', manifest)
template = (here / 'preview.html').read_text(encoding='utf-8')
(dest / 'index.html').write_text(template.replace('__MANIFEST__', json.dumps(manifest, ensure_ascii=False).replace('</', '<\\/')), encoding='utf-8')
links = ''.join(f'<li>{d}：<a href="preview/{d}-30ms-light.gif">浅底循环</a> · <a href="preview/{d}-30ms-dark.gif">深底循环</a></li>' for d in manifest['directions'])
(dest / 'previews.html').write_text('<!doctype html><meta charset="utf-8"><title>08 八方向预览</title><h1>08 炼丹童子 · 八方向循环</h1><p>每方向16帧，每帧30毫秒，每圈480毫秒。离线检查通过；客户端接入未进行。</p><p><a href="index.html">交互预览：逐帧、放大、深浅底、首尾接缝</a></p><ul>'+links+'</ul>', encoding='utf-8')
(delivery / 'index.html').write_text('<!doctype html><meta charset="utf-8"><title>08 炼丹童子最终交付</title><h1>08 炼丹童子</h1><p>128/128 行走；8/8 独立站立。八方向离线美术检查通过；客户端接入未进行。</p><p><a href="revisions/final-v1/index.html">打开30毫秒/帧交互预览</a></p><p><a href="revisions/final-v1/previews.html">八方向GIF预览</a></p><p><a href="08-HANDOFF.md">最终交接</a></p>', encoding='utf-8')
(dest / 'FINAL-REVIEW.md').write_text('''# 08 炼丹童子最终离线验收

128/128 行走帧、8/8 独立站立图齐全，八方向均通过本任务离线美术检查。最终选择及逐图 SHA 见 manifest.json，浏览器检查范围和已审阅快照绑定见 browser-review.json。最终文件和来源完整性检查另见 file-audit-before-cleanup.json；图片清理后另见 runtime-audit-after-cleanup.json。

- N/NE/E/SE/S/SW/W/NW 每方向16张，独立站立各1张。
- 全部最终 PNG 为1024×1024、RGBA透明底；真实生成原图均为原生1254×1254。
- 不同槽位分别有独立生成请求、回执与原图 SHA；没有通过镜像、复制、插值或姿势形变补帧。技术处理只清低透明度残边、整格等比缩小及统一对齐。
- 浅底与深底、正常512显示与原尺寸1024检查；静态全16帧、脚部原尺寸、交替迈腿/支撑脚、脚底锚点、比例及15→16→01→02衔接均已检查。
- 每方向提供深浅底GIF各1个，16帧×30毫秒=480毫秒无限循环。浏览器按时间选帧，不插值；显示器刷新率可能跳帧，未声称测量了屏幕播放时序。
- 保留少量自然发丝、纹样和踝部绘制变化；本次已选稿没有发现阻塞验收的问题。
- 生成走宿主内置入口。配置目标为 gpt-image-2.5-sunburst/max，但入口没有实际型号/质量字段，逐图保留 actualModel/actualQuality=null 与未确认原因。未调用收费API。
- 原始生成图、拒稿、回退和中间图片按用户授权在最终文件核验后清理，精确prompt、请求、回执、尺寸和SHA等文字证据保留；历史源路径保留为来源记录，不伪改为仍存在。
- 素材制作和离线验收完成。Unity/正式客户端接入未进行，不在本次完成声明内。
''', encoding='utf-8')
print(json.dumps({'final':str(dest),'walk':128,'idle':8,'visual_approval':True},ensure_ascii=False))
