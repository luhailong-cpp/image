from pathlib import Path
import json,shutil,xml.etree.ElementTree as ET,hashlib
root=Path(r'E:\work\image\qdao_chibi_roster_v12');client=Path(r'E:\work\mmorpg-client');evidence=client/'Docs/ArtEvidence/v12-natural-lu';candidate=root/'candidate-stable-body/24_lu_dongbin'
for name in ['copy-provenance.json','prewarm-status.json','final-24-hash-verification.json']:
    shutil.copyfile(Path(r'E:\work\output\qdao-natural-lu-validation')/name,evidence/name)
results={}
for mode in ['editmode','playmode']:
    xml=ET.parse(evidence/f'{mode}.xml').getroot();assert xml.attrib['result']=='Passed' and xml.attrib['failed']=='0'
    results[mode]={'passed':int(xml.attrib['passed']),'failed':int(xml.attrib['failed']),'total':int(xml.attrib['total']),'file':f'{mode}.xml','sha256':hashlib.sha256((evidence/f'{mode}.xml').read_bytes()).hexdigest()}
summary={'status':'passed','character':'24_lu_dongbin','version':12,'alignment_version':3,'validation_mode':'independent project copy to preserve the unsaved scene in the active user editor','formal_project':str(client),'tested_project':r'E:\work\output\qdao-natural-lu-validation\mmorpg-client','pngs_matching_formal_project':81,'matching_csharp_files_at_start':357,'results':results,'source':str(candidate),'game_capture':'tianyong-24_lu_dongbin.png','scope':'offline imported assets, all direction playback, stopped-frame idle, city controller; not a network end-to-end or all-roster art approval'}
(evidence/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
new='2026-09-14 当前状态：用户要求继续修正。年轻吕洞宾的新道家Q版已完成64张步行、8张独立站立及同身份肖像，按对齐v3接入游戏；候选源包为 `candidate-stable-body/24_lu_dongbin`。实际81张PNG及启用记录逐文件核对一致。独立Unity副本的127/127 EditMode、8/8 PlayMode通过，证据见客户端 `Docs/ArtEvidence/v12-natural-lu/summary.json`；原编辑器中的未保存场景保持原状。何仙姑、韩湘子正按具体原画问题修正，其余角色尚未全部完成。内部检查通过不等于用户已认可整批美术。'
old='2026-09-13 当前状态：用户已明确指出道家造型、走路方向与姿势、脸型与大小三项均不符合预期。后续批量制作与发布暂停，目前仅制作吕洞宾自然走路样板，待用户复核后再决定是否扩展。内部数值/视觉记录或运行测试通过，不等于用户美术验收通过；25狮鼓护卫虽内部标记passed，仍未接入，也未获得本轮风格认可。'
for p in [root/'README.md',root/'CLIENT_CONTRACT.md',client/'Docs/qdao-roster-v12-integration.md',client/'Docs/qdao-roster-direction-gait-2026-09-13.md']:
    t=p.read_text(encoding='utf-8-sig');t=t.replace(old,new)
    t=t.replace('本目录保留V11素材。后续升级必须在样板复核及完整资源检查通过后重新评估，当前不按内部passed记录继续批量发布。','本目录保留V11与上一版V12素材。后续角色按已核实的问题逐项修正并完成整套检查，不按旧内部passed记录直接批量发布。')
    t=t.replace('当前仍只推进吕洞宾自然走路样板和用户复核。','新吕洞宾已完成本轮修正与接入；其余角色按最新用户继续指令逐项推进。')
    t=t.replace('当前暂停后续批量发布，仅做吕洞宾自然走路样板。恢复扩展前须先得到用户对造型、步态和脸型比例的复核，再完成64走路、8独立站立、肖像、全部89媒体及运行检查；25内部passed不能作为直接发布依据。并行游戏功能修改独立保留。','最新用户已要求继续。新吕洞宾整套已检查并接入，其他角色仍需完成64走路、8独立站立、肖像、全部89媒体及运行检查；25旧内部passed不能作为直接发布依据。并行游戏功能修改独立保留。')
    t+='\n\n## 2026-09-14：吕洞宾稳定定位与完整接入\n\n对齐v3以同方向独立idle确定固定头部ROI和头顶Y；所有72帧共用一个scale，每帧只整数平移。世界根点仍为(256,471)，但步行时不同远近脚可围绕根点变化，不再把最低鞋像素强行锁死。独立验收按源RGBA重构平移结果，拒绝错位、裁断、改像素及错误参考元数据。旧角色v2仍按原规则验证。\n\n本次修正了SE06腿部遮挡和摆臂、NE头型，以及S/N/E/SE独立站立比例。追加边缘清理显式使用4px边缘及12px颜色参考；全部72帧alpha、G通道、位置和受保护红色不变。默认去色仍2px/6px，旧默认输出54次真实帧比较逐像素一致；细发梢中无可靠参考的像素未强行改色。\n\n最终源：`E:/work/image/qdao_chibi_roster_v12/candidate-stable-body/24_lu_dongbin`。81PNG已接入，alignmentVersion=3；导入前资源留存在 `Docs/ArtEvidence/v12-natural-lu/before-import/`。新运行结果是独立副本127/127 EditMode和8/8 PlayMode，副本81PNG、启用记录及357个C#文件在启动前与正式项目一致。真实城市图为 `Docs/ArtEvidence/v12-natural-lu/tianyong-24_lu_dongbin.png`。这些是离线游戏测试，不是整批8位角色的美术完成声明。\n'
    p.write_text(t,encoding='utf-8')
status=root/'review/lu_natural_walk_sample/STATUS.md';t=status.read_text(encoding='utf-8-sig');t=t.replace('- 暗底验收发现NW idle少量2–4px品红残边，正在增加显式4px边缘清理选项；完成后必须重导出、重核对、刷新预览，再发布。','- 显式4px边缘清理已重导出并通过72帧alpha/G/位置/红色保护检查；已刷新最终预览。细发梢无可靠颜色参考的少量像素不强行改色。').replace('- 尚未覆盖游戏内旧24。本轮只在完整新24通过后替换该角色，其他角色不会凭历史passed批量发布。','- 新24已正式替换，81PNG+启用记录verify-only通过；旧24资源完整留档。其他角色按本轮清单继续修正，不凭历史passed直接发布。').replace('- 用户当前Unity编辑器有未保存场景，独立测试副本正在准备，保留当前场景状态。','- 为保留原编辑器未保存场景，测试使用独立副本；81PNG+启用记录及357C#匹配。127/127 EditMode、8/8 PlayMode通过，root已查看真实城市截图。');status.write_text(t,encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
