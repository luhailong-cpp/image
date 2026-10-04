from pathlib import Path
import json,hashlib,csv
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
inv=json.loads((R/'inventory.json').read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
rows=[]
for f in inv['frames']:
    p=R/f['path'];h=sha(p)
    rows.append({'action':f['action'],'direction':f['direction'],'frame':f['frame'],'path':f['path'],'sha256':h,'generation_record':f.get('native_evidence',f.get('source_record','')),'native_size':str(f.get('native_size','')),'visual_status':f.get('visual_status','not_reviewed'),'client_status':'not_integrated'})
with (R/'MERGE_FILES.csv').open('w',encoding='utf-8-sig',newline='') as out:
    w=csv.DictWriter(out,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
events={'status':'offline_candidates_not_client_validated','indexBase':1,'root':{'canvas':[1024,1024],'designReference':[512,920],'calibrated':False,'operation':'整画布原生导出，不按最低脚或bbox配准'},'actions':{'run':{'directions':['N','NE','E','SE','S','SW','W','NW'],'framesPerDirection':16,'frameMs':75,'adoptedCycleMs':1200,'uniform':True,'clientConfirmed':False,'phaseReviews':['reviews/run-grounding-review.json','work/run-S/run-S-grounding-review-20261003.json'],'events':'按方向逐图相位审阅记录；不把统一模板帧号当已验证事件'},'hit':{'directions':['E','W'],'framesPerDirection':6,'frameMs':40,'totalMs':240,'event':{'frame':1,'name':'受击开始','status':'设计触发标记；未接客户端'}},'attack':{'directions':['E','W'],'framesPerDirection':12,'frameMs':30,'totalMs':360,'event':{'frame':6,'offsetMs':150,'name':'命中候选','status':'出手伸展峰值候选；未接客户端判定'}},'cast':{'directions':['E','W'],'framesPerDirection':16,'frameMs':45,'totalMs':720,'event':{'frame':9,'offsetMs':360,'name':'释放候选','status':'离线设计标记；未接客户端技能'}}}}
(R/'animation-events.json').write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf-8')
text=f'''# 02 火符少年 · 合并交接（制作中）

更新时间UTC：{now}。当前{len(rows)}/196张候选已落盘；仍在手脚局部返修和动态验收，不是全部通过标记。本文件会随最后验收刷新。

## 合并范围

只合并本目录。正式候选在frames/；逐图路径、SHA256、原生来源记录和当前视觉状态见MERGE_FILES.csv与inventory.json。每张PNG旁的.generation.json关联原生来源；完整提示词与实际回执在prompts/、records/。不覆盖另一台电脑的旧目录，也未更改客户端或共享Git。

|动作|方向|每方向帧|总数|当前状态|
|---|---|---:|---:|---|
|跑步|N、NE、E、SE、S、SW、W、NW|16|128|全部导出；鞋轴与承重/循环复核中|
|受击|E、W|6|12|全部导出；单图脚轴已复核，E06已修；动态复核中|
|普攻|E、W|12|24|全部导出；E脚轴已修，W六张后脚修订中|
|施法|E、W|16|32|全部导出；实际外撇后脚定向修订中|

## 预览与时序

previews/index.html提供完整动作、慢速、逐帧和来源。previews/run-grounding.html提供1200ms正常、4800ms慢放和逐帧。用户明确采用正常16×75ms=1200ms，已移除旧快档；客户端尚未接入。战斗维持受击40×6=240ms、普攻30×12=360ms、施法45×16=720ms。

animation-events.json列出时序和候选事件：普攻第6帧/150ms命中、施法第9帧/360ms释放；需要结合最终动作和客户端战斗系统验证。跑步事件须按各方向实图相位记录读取，不能直接套统一模板。

## 画布与根点

正式PNG1024×1024 RGBA，原生单帧至少1024（本批常见1254）。全画布等比导出；不镜像、不复制、不形变插值，不按bbox独立缩放、不按最低脚像素贴地。设计参考根点(512,920)尚未全序列校准，透视中的远近鞋不强制同一屏幕水平线。接地/尺度未通过项继续在各reviews与work/*审阅表明确记录。

## 模型与来源

内置image_gen。配置目标GPT Image 2.5 Sunburst/max；工具无型号/质量参数，实际提交model/quality=null，返回未披露，因此实际版本/质量未确认。逐图SHA、原生尺寸、真实提示词、参考路径和回执是证据；配置/提示词不是实测型号证据。未用收费API/CLI；未使用另一电脑未提交动作图。

## 未接入与剩余验收

本角色尚未接入客户端，未验证游戏内位移速度、滑步、碰撞点及命中/释放同步。离线预览不能代替客户端验收。当前还在清理少数鞋尖外撇、支撑相位和尺度漂移；所有已正确帧保留。正式成品与引用确认后，按用户要求清除本目录淘汰图片，保留逐图文字来源。
'''
(R/'MERGE_HANDOFF.md').write_text(text,encoding='utf-8')
print({'rows':len(rows),'csv_sha256':sha(R/'MERGE_FILES.csv'),'handoff':'MERGE_HANDOFF.md','complete':False})
