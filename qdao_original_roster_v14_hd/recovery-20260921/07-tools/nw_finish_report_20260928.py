from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
from finalize_current import metrics

here=Path(__file__).resolve().parent
out=here/'nw-final-repair-20260928'
src=here/'candidate/07_moon_shadow_assassin_girl'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
report=read(out/'report.json')
for row in report['files']:
    assert sha(src/row['slot'])==row['sha256'], 'Current image changed after review'
    assert sha(Path(row['reviewImage']))==row['reviewImageSha256'], 'Review evidence changed'
    row['staticVisualReview']={'observedAt':now,'nativeDisplayPerBackground':[1024,1024],
                               'backgrounds':['dark','light'],'actuallyViewed':True,
                               'clippingObserved':False,'opaqueBackgroundObserved':False,
                               'scope':'static complete-figure, alpha edges, identity, direction and pose inspection; no live animation'}
report.update({'reviewState':'static_review_complete_candidate_frozen_pending_live',
               'generationCallsThisRepair':3,'fullVisualAcceptance':False,
               'targetedRepairs':[
                   {'issue':'NW10-11-12-13 excessive alternating height','before':[849,902,838,905],
                    'after':[849,860,853,867],'method':'existing genuine native PNG uniformly downsampled as complete canvas; no pose synthesis',
                    'staticFinding':'large alternating height jump reduced; smaller head proportion differences remain'},
                   {'issue':'NW15-16 near arm abruptly extends forward','selectedAttempt':'walk-NW-16-continuity-r20260928c',
                    'method':'three separate builtin transparent single-frame edits; c selected',
                    'staticFinding':'frame16 near arm now low; blade tilt and elbow provide an intermediate silhouette; original leg phase retained',
                    'limitation':'15-16-01 timing and residual wrist displacement have not been judged in live playback'}],
               'remainingRisks':[
                   'Live browser playback remains blocked by the previously reported Computer Use URL identification failure; no UI workaround attempted.',
                   'NW11/12/13 head band widths are 396/422/398 pixels. Approximately 6.6 percent maximum adjacent difference needs runtime scale-pulse assessment.',
                   'NW15-16-01 arm transition has improved static silhouettes but is not accepted as smooth in live animation.',
                   'NW05 and08 retain existing heights876/887 and all walking heights range842..887; runtime bobbing is still unverified.',
                   'Historical native raw files for idle/NW and walk/NW/01 are absent after authorized cleanup; this run rechecked their current exports only.'
               ]})
attempts=[]
for suffix, status, reason in [('a','superseded_candidate','Near wrist fell almost to frame15 position; c provides a modest forward shift and blade tilt.'),
                               ('b','rejected','Near arm extended too far forward and upward, increasing pose discontinuity.'),
                               ('c','selected_candidate_pending_live','Conservative near-arm correction; static deep/light review complete, live loop pending.')]:
    folder=here.parent/'07-generation'/f'walk-NW-16-continuity-r20260928{suffix}'
    raw=folder/'raw.png'
    request=read(folder/'request.json')
    result=read(folder/'result.json')
    if not Path(str(raw)+'.generation.json').exists():
        record={'file':str(raw),'sha256':sha(raw),'nativeMetrics':metrics(Image.open(raw)),
                'tool':'image_gen.imagegen','route':'builtin','generatedAt':result['completedAt'],
                'configSnapshot':request['configSnapshot'],'submittedParameters':request['submittedParameters'],
                'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool did not disclose actual model or quality.',
                'requestEvidence':{'path':str(folder/'request.json'),'sha256':sha(folder/'request.json')},
                'resultEvidence':{'path':str(folder/'result.json'),'sha256':sha(folder/'result.json')},
                'prompt':str(folder/'prompt.txt'),'exactPrompt':request['arguments']['prompt'],
                'referenceBindings':request['referenceBindings'],'submittedTransparentBackground':True}
        write(Path(str(raw)+'.generation.json'),record)
    selection={'attempt':folder.name,'rawSha256':sha(raw),'status':status,'reason':reason,'observedAt':now,
               'formalApproval':False,'livePlaybackAccepted':False}
    write(folder/'selection-review.json',selection)
    attempts.append(selection)
report['newAttemptSelections']=attempts
write(out/'report.json',report)
lines=['# 07 NW 离线修正冻结记录：2026-09-28','',
       '当前 NW 为 16 行走 + 1 独立站立候选。静态复核完成并冻结给根任务汇总；未实时播放、未正式批准、未接入客户端。','',
       '- NW11/12/13 从各自真实 1254 RGBA 原生图整画布等比重导出，高度由 902/838/905 改为 860/853/867；NW10 保持 849。未局部拉伸、未拼接或合成伪帧。',
       '- NW16 内置透明单帧编辑共 3 次，选用 continuity-r20260928c；a 被 c 替代，b 因近臂前伸过量拒选。选用 c 原生 1254×1254，导出1024×1024，主体854高，保留原腿相位。',
       '- 已逐张实际查看17组深浅底，每个背景的角色显示保持1024×1024；重查当前PNG、sidecar、原生SHA。15份原生当前在位并匹配，idle/NW及NW01仅有历史删除后的文字链。',
       '- 当前17槽无像素完全重复或精确镜像重复；两份GIF均16帧且每帧30ms。GIF时长检查不等于实时视觉播放。',
       '- 所有本轮实际型号/质量均未披露，字段null；配置目标仍只是目标。收费API调用0。','',
       '仍待live：NW11/12/13头宽396/422/398（最大相邻差约6.6%），NW15→16→01手腕与刀刃的闭环变化，以及其余高度起伏。当前静态没有裁边或实色背景；不以静态结论替代运行时步态验收。浏览器URL识别故障后本轮未操作UI、未绕过。','',
       '绑定报告：[report.json](nw-final-repair-20260928/report.json)。本轮前记录为 pre-repair-text-records.json；只保留文字快照，没有图片回退副本。','',
       '| 槽位 | 当前 SHA256 | 主体高 |','|---|---|---|']
for row in report['files']:
    lines.append(f"| {row['slot']} | `{row['sha256']}` | {row['metrics']['subject_height']} |")
lines.extend(['','恢复第一步：读取此报告并重新核对17槽当前SHA，再在允许且可可靠识别URL的浏览器环境播放当前版30ms深浅底循环，特别检查10→11→12→13及15→16→01。不要把旧全量预览SHA用于当前四张修改图。',''])
(here/'NW_HANDOFF_20260928.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'report':str(out/'report.json'),'reportSha256':sha(out/'report.json'),'frozenSlots':len(report['files']),
                  'selected16':next(r['sha256'] for r in report['files'] if r['slot']=='walk/NW/16.png')}))
