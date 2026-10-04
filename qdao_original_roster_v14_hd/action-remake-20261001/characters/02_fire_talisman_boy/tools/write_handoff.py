from pathlib import Path
import json,hashlib,csv
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((R/p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inv=read('inventory.json'); now=datetime.now(timezone.utc).isoformat()
review=read('reviews/final-review.json') if (R/'reviews/final-review.json').exists() else {}
checked={x['path']:x['sha256'] for x in review.get('frames',[])}
rows=[]
for f in inv['frames']:
    h=sha(R/f['path']); current=checked.get(f['path'])==h
    rows.append({'action':f['action'],'direction':f['direction'],'frame':f['frame'],'path':f['path'],'sha256':h,'generation_record':f.get('native_evidence',f.get('source_record','')),'native_size':str(f.get('native_size','')),'visual_status':'offline_directional_review_complete_client_pending' if current else f.get('visual_status','not_reviewed'),'client_status':'not_integrated'})
with (R/'MERGE_FILES.csv').open('w',encoding='utf-8-sig',newline='') as out:
    w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
complete=len(rows)==196 and all(checked.get(x['path'])==x['sha256'] for x in rows) and not review.get('knownUnresolvedArtFailures',['review pending'])
events={'status':'offline_material_reviewed_client_not_integrated' if complete else 'offline_review_pending','indexBase':1,'root':{'canvas':[1024,1024],'designReference':[512,920],'clientCalibrated':False,'operation':'整画布原生导出，不按最低脚或bbox配准'},'actions':{'run':{'directions':['N','NE','E','SE','S','SW','W','NW'],'framesPerDirection':16,'frameMs':75,'adoptedCycleMs':1200,'uniform':True,'clientConfirmed':False,'phaseReviews':['reviews/run-grounding-review.json','work/run-S/run-S-grounding-review-20261003.json'],'events':'按方向实图相位，不把统一模板帧号当接触事件'},'hit':{'directions':['E','W'],'framesPerDirection':6,'frameMs':40,'totalMs':240,'event':{'frame':1,'offsetMs':0,'name':'受击开始','status':'设计触发标记，未接客户端'}},'attack':{'directions':['E','W'],'framesPerDirection':12,'frameMs':30,'totalMs':360,'event':{'frame':6,'offsetMs':150,'name':'命中候选','status':'出手峰值候选，未接客户端判定'}},'cast':{'directions':['E','W'],'framesPerDirection':16,'frameMs':45,'totalMs':720,'event':{'frame':9,'offsetMs':360,'name':'释放候选','status':'离线设计标记，未接客户端技能'}}}}
(R/'animation-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
audit=read('reviews/full-source-chain-audit.json') if (R/'reviews/full-source-chain-audit.json').exists() else {}
status='素材制作与离线手脚复核完成；客户端尚未接入' if complete else '素材已齐，最后离线复核中'
lines=[]
for s in review.get('sequences',[]):
    lines.append('|'+ '|'.join([s['action'],s['direction'],str(s['frames']),s['observations'],'客户端位移、滑步及事件同步待接入'])+'|')
table='\n'.join(lines) or '|全部|14组|196|最终复核待写入|客户端未接入|'
text=f'''# 02 火符少年 · 合并交接

更新时间UTC：{now}。{status}。196张正式PNG：跑步128、受击12、普攻24、施法32。

## 合并范围与复现

只合并本角色目录。正式游戏素材在frames/，逐帧路径、SHA256、来源和状态见MERGE_FILES.csv及inventory.json；提示词在prompts/，真实生成证据在records/。每张图片通过清单中的generation_record追溯；部分帧另有相邻.generation.json。未切分支、操作暂存/提交/推送，未覆盖客户端或另一台电脑资源。

打开previews/index.html检查四动作，previews/run-grounding.html检查八方向正常/慢放/逐帧。previews/run-eight-directions.gif为八方向并排概览。重建顺序：tools/merge_inventory.py、tools/build_previews.py --manifest inventory.json、tools/final_contacts.py、tools/write_handoff.py；在本目录用项目Python运行。所有重建默认值均为当前时长。

## 逐动作与方向

|动作|方向|帧数|本次已复核/修正|待接入验收|
|---|---|---:|---|---|
{table}

详细离线范围与对应PNG SHA见reviews/final-review.json。单图与整组对照由代理实际看图，浏览器仅提供播放、慢放、逐帧及画面抽样；不将文件数量或SHA差异当美术通过。用户指定09竹弓少女为动作参照，采用同方向脚轴、承重与摆臂关系；火符少年保持自身画像及右扇左铃。

## 时序与根点

正常run为16×75ms=1200ms，所有方向均匀；慢放4800ms，旧快档已移除。hit为6×40=240ms、attack为12×30=360ms、cast为16×45=720ms。HTML按准确规格时钟播放；GIF以10ms量化，跑步80/70交替总1200、施法50/40交替总720。

animation-events.json：受击01开始、普攻06/150ms命中候选、施法09/360ms释放候选，仍需游戏系统同步。1024×1024 RGBA；原生单帧≥1024，全画布等比导出，不镜像、复制、变形或插值补姿态，不按bbox独立缩放/最低脚贴地。设计参考根点(512,920)，客户端尚未校准，透视远近脚不能强制同一屏幕水平线。

## 来源与模型证据

本批使用内置image_gen；配置目标GPT Image 2.5 Sunburst/max。工具无型号/质量选择器，实际提交参数model/quality=null，返回型号/质量未披露，均记未确认；未使用收费API/CLI，不取另一电脑未提交图，不沿用旧run-correction/combat在制图。

reviews/full-source-chain-audit.json保存清理前的196帧来源、原生尺寸、宿主哈希与实际全画布导出像素审计。原始回执证据分级如实保留：部分旧生成记录只有宿主路径；N09为带标记的回溯推断。它们不能冒充原始返回文字或型号证据。淘汰稿与导出中间图清理以reviews/cleanup-completed.json为准，文字来源与SHA保留；历史路径不代表原图仍存在。

## 客户端边界

尚未接入客户端，未运行游戏内验收；位移速度、地面锚点、滑步、碰撞及命中/施法时序需在合并后检查。当前完成状态只指本机素材制作、离线复核、预览和合并资料。
'''
(R/'MERGE_HANDOFF.md').write_text(text,encoding='utf-8')
print({'rows':len(rows),'csv_sha256':sha(R/'MERGE_FILES.csv'),'offlineMaterialsComplete':complete,'clientIntegrated':False})
