"""Write the character20 delivery index without changing image pixels."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
R=Path(__file__).resolve().parent.parent
P=R/'20-final'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=read(R/'20-tools/offline-acceptance.json')
for row in A['files']:
 p=P/row['slot'];assert sha(p)==row['sha256']
 side=Path(str(p)+'.generation.json');m=read(side)
 m.update(file=str(p),processingRecord=str(P/'processing/frame-sources.json'),visualApproval=True,
          visualApprovalRecord='acceptance.json',generationRecordRelativeToDelivery='../'+row['generationRecord'])
 m['rawRetention']='Final selected and exported; original images scheduled for user-authorized deletion. Consult retention.json for actual deletion status.'
 write(side,m)
write(P/'acceptance.json',A)
files=[{k:r[k] for k in ['slot','sha256','nativeSourceSha256','nativeSize','sourceAttempt']} for r in A['files']]
manifest={'schema':'qdao-character-movement-delivery-v1','character':'20_star_formation_master_girl','displayName':'星阵少女',
 'at':datetime.now(timezone.utc).isoformat(),'canvas':[1024,1024],'format':'RGBA PNG',
 'directions':['N','NE','E','SE','S','SW','W','NW'],'walkPattern':'walk/{direction}/{01..16}.png','idlePattern':'idle/{direction}.png',
 'walkFramesPerDirection':16,'walkCount':128,'independentIdleCount':8,'frameMs':30,'cycleMs':480,
 'anchor':{'pixelTopLeftOrigin':[512,942],'uvTopLeftOrigin':[0.5,0.919921875],'unityPivotBottomLeftOrigin':[0.5,0.080078125]},
 'source':{'nativeCompleteFrameMinimum':[1254,1254],'uniqueNativeSources':136,'route':'built-in image_gen','actualModel':None,'actualQuality':None,'paidApiCalls':0},
 'status':{'materialProduction':'passed','offlineAcceptance':'passed','clientIntegration':'not-performed'},
 'preview':'preview/index.html','acceptance':'acceptance.json','files':files}
write(P/'delivery.json',manifest)
links='\n'.join(f'| {d} | [深底](preview/{d}-30ms-dark.gif) | [浅底](preview/{d}-30ms-light.gif) | 16 + 1，通过 |' for d in manifest['directions'])
readme=f'''# 20 星阵少女 · 正式移动素材

本角色已完成 **128 张独立行走帧 + 8 张独立站立图**，八方向素材及离线视觉验收通过。**客户端接入未执行**。本窗口到此结束，不自动继续其他角色。

- 游戏图片：`walk/N、NE、E、SE、S、SW、W、NW/01.png…16.png`；`idle/N.png…NW.png`。
- 每张1024×1024透明RGBA PNG；136个独立原生1254×1254完整单帧来源，未复制、镜像、插值或变形凑帧。旧512动作未用于放大冒充；既有旧动作未改动。
- 行走每方向16帧，30毫秒/帧，480毫秒/圈。站立为独立姿态，不从行走帧抽取。
- 统一脚底锚点（图像左上为原点）`[512,942]`。若使用Unity底部原点的归一化pivot，对应`[0.5,0.080078125]`；实际客户端导入参数尚未配置验证。
- 固定0.94整格归一化、透明残边清理及脚底对齐属于导出处理；每帧保留独立真实绘制姿态。处理记录在`processing/frame-sources.json`。

[八方向交互预览](preview/index.html)支持深浅底、256正常/512放大/1024原尺寸、站立切换、单步及15→16→01→02接缝。浏览器预览按30毫秒目标推进，GIF文件已逐帧核实16×30毫秒；没有声称测量显示器实际刷新时序。

| 方向 | 深底循环 | 浅底循环 | 行走 + 站立验收 |
| --- | --- | --- | --- |
{links}

逐图SHA、原生来源与版本选择见[交付清单](delivery.json)；逐图视觉验收及五组审查记录见[验收记录](acceptance.json)。全16格图已在深浅底检查；全圈与接缝实际启动播放，并结合关键帧暂停检查交替迈腿、支撑脚、脚底锚点、比例、装备及透明边缘。

身份依据为仓库既有正式资源`q_daoist_character_pack_4096/20_star_formation_master_girl_transparent_4096.png`；风格依据为`designs/README.md`及`designs/jubaozhai-ui/02-characters.png`，生成时实际附图。维持高髻长发、红金星冠、黑红象牙金袍，解剖右手星盘、左手三卡。

内置生图入口未披露实际模型与质量，记录为`host-managed/unverified`，不将配置目标当作返回证明。未调用收费API。逐图精确提示词、请求、回执、尺寸、SHA和版本文字记录保存在相邻`../20-generation/`；PNG侧车含具体来源路径。历史请求与回执保持原样，旧路径或pending字段表示生成当时状态，当前验收以本目录`acceptance.json`为准。

按用户2026-09-23素材保留要求，成品核实后删除原图、拒稿、回退、输入副本和加工中间图片；保留正式成品、配套预览/设计及来源文字证据。实际删除清单见`retention.json`。既有正式身份肖像与designs风格图保留。
'''
(P/'README.md').write_text(readme,encoding='utf8')
print(json.dumps({'final':str(P),'files':len(files),'metadataUpdated':True}))
