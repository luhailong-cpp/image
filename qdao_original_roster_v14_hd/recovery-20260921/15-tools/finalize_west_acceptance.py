"""Record the completed W/NW visual review, bound to the reviewed final bytes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image, ImageChops

R = Path(__file__).resolve().parents[1]
review = R / '15-review'
audit_path = review / 'W-NW-source-bound-audit.json'
audit = json.loads(audit_path.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert audit['allMachineChecksPass'] and audit['sourceUnique'] and audit['outputUnique']

for row in audit['frames']:
    p = R / '15-delivery-preview/runtime' / row['slot']
    assert sha(p) == row['outputSha256'], p

sheet_checks = []
for d in ['W', 'NW']:
    for bg in ['light', 'dark']:
        for start in [1, 5, 9, 13]:
            p = review / f'W-NW-final/{d}-{start:02d}-{start+3:02d}-{bg}-native-sheet.png'
            sheet = Image.open(p).convert('RGB')
            for i in range(4):
                x = (i % 2) * 1024
                y = (i // 2) * 1048 + 24
                source = review / f'W-NW-final/{d}{start+i:02d}-{bg}-1024.png'
                actual = Image.open(source).convert('RGB')
                assert ImageChops.difference(sheet.crop((x, y, x+1024, y+1024)), actual).getbbox() is None, source
            sheet_checks.append({'path':str(p), 'sha256':sha(p), 'allFourCellsExactlyMatchCurrent1024Composites':True})

for artifact in audit['reviewArtifacts']:
    assert sha(Path(artifact['path'])) == artifact['sha256'], artifact['path']

report = {
    'character':'15_water_dragon_scholar_boy',
    'reviewedAt':datetime.now(timezone.utc).isoformat(),
    'scope':['W','NW'],
    'walkCount':32,
    'idleCount':2,
    'missingFrames':[],
    'sourceAudit':{'path':str(audit_path),'sha256':sha(audit_path)},
    'reviewMethod':'Actual visual inspection of every final in light and dark composites at 1024x1024 per frame; original-detail 2x2 sheets preserve frame pixels. Also reviewed all 16-frame contact sheets and 15-16-01-02 seams on both backgrounds at 256 display size.',
    'nativeSheetBinding':sheet_checks,
    'frameSourceBinding':[{'name':r['name'],'finalSha256':r['outputSha256'],'nativeSourceSha256':r['sourceSha256']} for r in audit['frames']],
    'materialProductionComplete':True,
    'fileAndSourceChecksPass':True,
    'staticVisualReviewPass':True,
    'encodedPreviewTimingPass':all(a['timingPass'] for a in audit['reviewArtifacts'] if 'timingPass' in a),
    'previewTiming':{'frames':16,'frameMs':30,'cycleMs':480,'loop':0},
    'visualFindings':{
        'W':'Both half cycles show different trouser-leg depth/occlusion, support and return configurations. Frames 05-06 and 13-14 pass under the body; 07-09 extend into the opposite contact. Feet, sole shapes and fan grip remain readable. 15-16-01-02 retains the same direction and support transition.',
        'NW':'Frames 01-04 show the screen-right trailing boot sole; 09-12 show the opposite screen-left returning boot sole, with support switching to screen-right. Passing frames and 15-16-01-02 retain continuous phase order.',
        'identity':'Navy ponytail, teal-gold ornament, blue tassel, blue-ivory-gold cloud/wave robes, jade pendant and right-hand fan preserved. No additional limbs, duplicated boots, missing fan or clipped body discovered.',
        'proportion':'Previously applied 24 uniform native-source export adjustments are retained without reapplication. Final head/shoulder sizes have no remaining conspicuous outlier in the reviewed sheets. Natural rise/fall and robe/tassel motion remain.',
        'alpha':'No visible checkerboard, magenta rim, rectangular background or detached fringe discovered on either background. All final borders are transparent.',
        'idle':'Two independent sources and outputs; both depict a balanced two-foot standing pose rather than a reused walking frame.',
        'minorVariation':'Fine hair highlights, fan motifs and robe curls vary between independently generated images. Static review accepted these details; actual temporal flicker is not asserted absent.'
    },
    'runtimeFilesChangedThisFinalReview':False,
    'dynamicPlaybackObserved':False,
    'dynamicReviewStatus':'blocked_by_prior_browser_file_access_safety_rejection; no workaround attempted',
    'clientIntegration':'not_performed',
    'allRequestedAcceptanceComplete':False,
    'remainingEvidence':['Actual 30ms playback observation and client integration/runtime testing are not established by this offline report.'],
}
(review/'W-NW-acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(review/'W-NW-acceptance.md').write_text('''# 15 水龙书生 W / NW 验收记录

2026-09-28：W、NW 各 16 张真实行走帧和 1 张独立站立图齐全，共 32 + 2 张。只核查本角色这两个方向，本轮未重新缩放、未修改 runtime 图片。

## 已完成并通过

- 34 张来源互不重复，34 张最终图片互不重复；逐图核实最终 SHA、原生来源 SHA、请求／回执／精确提示词 SHA 和提示词一致性。来源原生尺寸均不低于 1024，最终均为 1024×1024 RGBA 透明 PNG。
- 全部最终帧脚底 y=942，头肩中心锚点 x=512±1；四边透明，源图到最终图为等比缩小，没有放大旧图、镜像、扭曲或修改姿势。既有 24 项原生导出比例修正已保留，未重复施加。
- 实际查看全部 34 张深、浅底的 1024 原尺寸图；行走图使用四张一组原尺寸拼版，拼版每一格与当前单帧合成图逐像素相同。另查看两方向全 16 帧、深浅底 256 尺寸排列和 15→16→01→02 衔接。
- W 的两半周裤腿遮挡、支撑与回收形态不同，05–06、13–14 为交替经过身体下方的阶段。NW 的 01–04 为屏幕右侧后靴露底，09–12 改为屏幕左侧后靴露底，支撑脚相应切换。首尾静态相位次序可衔接。
- 发型发饰、蓝白金衣袍、玉佩和右手扇子保持；未发现多肢、双靴叠影、缺扇、人物截断、棋盘背景、洋红残边或独立浮点。头肩比例未发现剩余明显异常帧。两张 idle 均为独立的双脚站稳姿势。
- 深浅底 GIF 均实解码为 16 帧，每帧 30 毫秒、每圈 480 毫秒、无限循环。

独立绘制的发丝高光、扇面纹样及衣摆细节存在小幅变化，静态检查可接受；不能据此保证动态播放没有细节闪动。

## 尚未成立的验收证据

动态实播未观察：此前浏览器访问本地预览文件被安全审核拒绝，未采用替代浏览器、localhost 或其他方式绕过。这里只确认逐帧静态检查与 GIF 编码时序，不能标记“全部预览验收通过”。

客户端接入与游戏内运行未执行。

## 证据

- `W-NW-source-bound-audit.json`：34 张来源、输出及逐图文件检查；4 个 GIF 的时序与 SHA。
- `W-NW-acceptance.json`：本次静态目检结论、最终 SHA 绑定和原尺寸拼版逐像素绑定。
- `W-NW-final/`：深浅底原尺寸检查图、拼版及 30ms GIF。
- `W-NW-scale-plan.json`、`scale-reexport-history.jsonl`：之前完成的比例导出修正。

最终素材：`../15-delivery-preview/runtime/walk/W/`、`../15-delivery-preview/runtime/walk/NW/`、`../15-delivery-preview/runtime/idle/W.png`、`../15-delivery-preview/runtime/idle/NW.png`。
''',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['walkCount','idleCount','staticVisualReviewPass','encodedPreviewTimingPass','dynamicPlaybackObserved','allRequestedAcceptanceComplete']},ensure_ascii=False))
