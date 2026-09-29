"""Close character20 with actual retention results and a precise handoff."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parent.parent;P=R/'20-final';T=R/'20-tools'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ret=read(P/'retention.json');audit=read(T/'final-after-retention-checks.json');A=read(P/'acceptance.json')
assert ret['completed'] and ret['deletedCount']==493 and audit['allPass'] and audit['count']==136
assert {r['slot']:r['sha256'] for r in A['files']}=={r['slot']:r['sha256'] for r in audit['rows']}
for x in ret['deletedFiles']:assert not Path(x['path']).exists()
ext={'.png','.gif','.jpg','.jpeg','.webp','.tiff','.tif','.bmp'}
for name in ['20-generation','20-reference','20-qa','20-work']:
 assert not [p for p in (R/name).rglob('*') if p.is_file() and p.suffix.lower() in ext],name
embedded=[]
for root in [R/'20-generation',P/'source']:
 for p in root.rglob('*.json'):
  if 'data:image/' in p.read_text(encoding='utf-8-sig'):embedded.append(str(p))
assert not embedded,embedded

for r in A['files']:
 p=P/r['slot'];assert sha(p)==r['sha256']
 side=Path(str(p)+'.generation.json');m=read(side)
 m['rawRetention']='Deleted after final SHA and visual acceptance, per user final-only retention instruction. Text source evidence retained; see retention.json.'
 m['retentionRecord']='retention.json';write(side,m)
for report in A['reviewReports']:
 path=(P/report['path']).resolve();assert path.exists() and sha(path)==report['sha256']
selected={}
for r in A['files']:selected.setdefault(r['sourceAttempt'],[]).append(r['slot'])
attempts=[]
for p in sorted((R/'20-generation').glob('*/raw.png.generation.json')):
 v=read(p);attempt=p.parent.name
 attempts.append({'attempt':attempt,'status':'selected-final' if attempt in selected else 'not-selected-superseded-or-rejected',
  'slots':selected.get(attempt,[]),'nativeSha256':v['sha256'],'generationRecord':'../'+str(p.relative_to(R)).replace('\\','/'),
  'rawImageRetained':False})
assert sum(len(x['slots']) for x in attempts)==136
write(P/'source-selection.json',{'at':datetime.now(timezone.utc).isoformat(),'selectedNativeSources':136,
 'attempts':attempts,'pendingRawProcessing':[],'note':'非选用版本不计入成品；所有唯一在制稿均已处理或被后续选用稿替代。历史提示词、请求和回执保持真实原样。'})
A['technicalEvidenceAfterRetention']={'path':'../20-tools/final-after-retention-checks.json','sha256':sha(T/'final-after-retention-checks.json'),
 'all136FinalsAnd16GifsVerified':True,'rawFilesChecked':False,'note':'原图已按授权删除；删除前逐一核实原图字节与SHA，前后检查记录均保留。'}
A['retention']={'path':'retention.json','sha256':sha(P/'retention.json'),'completed':True,'deletedImages':ret['deletedCount'],'deletedBytes':ret['deletedBytes']}
A['packageRelocation']={'finalRoot':'20-final','previewRoot':'20-final/preview','imageBytesUnchanged':True,
 'reviewHistoricalUrls':'原审查URL属于审查当时状态；现用preview/index.html，128行走/8站立相对路径已核查。'}
write(P/'acceptance.json',A)
table='\n'.join(f'| {d} | 16/16 | 1/1 | 通过 | [深底](20-final/preview/{d}-30ms-dark.gif) / [浅底](20-final/preview/{d}-30ms-light.gif) |' for d in A['directions'])
text=f'''# 20 星阵少女 · 已完成交接（2026-09-28）

本窗口负责 `20_star_formation_master_girl`，**素材制作完成，离线预览验收全部通过；客户端接入未执行**。已到本角色终点，不自动继续其他角色。

最终目录：`D:\\luyuan\\wuxingqitan\\image\\qdao_original_roster_v14_hd\\recovery-20260921\\20-final`。

- [正式说明与八向预览索引](20-final/README.md)
- [八方向交互预览](20-final/preview/index.html)，当前已在浏览器打开：http://127.0.0.1:8820/20-final/preview/index.html
- [交付清单](20-final/delivery.json)、[逐图验收](20-final/acceptance.json)、[版本选择](20-final/source-selection.json)
- [删除清单](20-final/retention.json)

| 方向 | 真实独立行走 | 独立站立 | 素材/离线验收 | 30毫秒循环 |
| --- | --- | --- | --- | --- |
{table}

共128张行走、8张独立站立，136张均为1024×1024 RGBA透明PNG；136个原生1254×1254完整单帧来源、最终文件与原生来源SHA均不重复。来源、精确提示词、请求/回执、尺寸和版本文字证据保留。早期来源记录中未确认字段不改写，实际原图尺寸/整帧及1×1导出已复核。未复制、镜像、插值、扭曲或平移同姿势充数；统一导出对齐不增加帧数。

所有方向均已检查16格深浅底、256正常及512放大下的实际全圈播放，交替迈腿、支撑脚、比例、透明残边，以及15→16→01→02接缝播放与逐帧。8张独立站立也检查了两种尺寸与背景。16个深浅底GIF均为16帧、每帧30毫秒、总480毫秒。没有录制连续视频或测量显示器精确刷新节奏；已记录工具观察的边界。

最新修订包括：N08鞋底多余星纹、NW09残边；SE05–08换腿与低幅通过（06 v3高踢腿拒用，选v4）；SW06及08–13修正半周期同腿；S07/15按真实姿态重新排序独立来源，S13选前向v1。准确选用版本以`source-selection.json`为准，不将弃用版本计入成品。

脚底锚点左上原点`[512,942]`；全图有效alpha最低点一致为y942，无画布边缘裁切。入口实际模型/质量未披露，仍为host-managed/unverified；配置目标不当作模型返回证明。收费API调用为0。

按用户只保留最终游戏素材、设计与接入文件的授权，本次删除493张原图、宿主原始副本、拒稿、回退、输入副本和检查中间图，共838,836,466字节。删除前核实全部136张成品与原生来源SHA，删除后再核136张成品及16个GIF通过。既有正式肖像和designs风格样板保留，历史旧动作和其他角色没有改动。此前2026-09-23删除记录继续保留。

**缺帧：无。待处理原图：无。素材/离线阻塞：无。客户端待办：本窗口未执行导入、场景运行或正式发布，不能当作客户端验收通过。** 后续如另行授权接入，应从`delivery.json`读取方向、时长、锚点和路径，在客户端完成导入与运行验收。

未进行Git提交、推送或Git清理；未写其他角色与共享完成状态。旧`20-work/export-v1/...`、`20-delivery-preview`为历史工作路径，最终图片已迁移至`20-final`；历史请求/回执路径没有伪改。
'''
(R/'20-HANDOFF-20260928.md').write_text(text,encoding='utf8')
old=R/'20-HANDOFF-20260923.md';body=old.read_text(encoding='utf-8-sig')
pointer='> 已于2026-09-28完成。本文件以下为历史记录；当前状态与路径以[最新交接](20-HANDOFF-20260928.md)及[正式交付](20-final/README.md)为准。128行走+8独立站立齐全，素材与离线验收通过，客户端未接入。\n\n'
if not body.startswith('> 已于2026-09-28完成。'):old.write_text(pointer+body,encoding='utf8')
print(json.dumps({'complete':True,'walk':128,'idle':8,'nativeAttemptsRecorded':len(attempts),'deletedImages':493,'pendingRaw':0,'clientIntegration':False}))
