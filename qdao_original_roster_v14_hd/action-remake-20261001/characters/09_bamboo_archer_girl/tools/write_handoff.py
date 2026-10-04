from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[(p.relative_to(ROOT).as_posix(),sha(p)) for p in sorted((ROOT/"runtime").rglob("*.png"))]
(ROOT/"SHA256SUMS.txt").write_text("".join(f"{h}  {p}\n" for p,h in rows),encoding="utf-8")
status=load(ROOT/"status.json");review=load(ROOT/"review.json");c=status["counts"]
feedback=status.get('userFeedback',{})
accepted_note=("用户经统筹反馈“弓足少女对了”，已明确指向竹弓少女当前版本。本次继续没有改动任何成图，196张与认可时的SHA逐项一致，按要求保留当前动作。详见[accepted-version.json](accepted-version.json)。这次认可的具体已看方向/帧未单独指定，因此不自动扩展成整套动态或游戏内通过。\n\n" if feedback.get('currentImagesMatch') else '')
timing={"updatedAtUtc":datetime.now(timezone.utc).isoformat(),"run":{"frameMs":75,"frameDurationsMs":[75]*16,"cycleMs":1200,"slowFrameMs":300,"slowCycleMs":4800,"timingStatus":"offline_default_applied_client_unconfirmed","availableNormalCycleMs":[1200],"formalClientTimingConfirmed":False,"phaseWeightsApplied":False,"extraLoopPauseMs":0},"hit":{"frameMs":40,"cycleMs":240,"peakFrame":3},"attack":{"frameMs":30,"cycleMs":360,"fullDrawFrame":6,"releaseFrame":7},"cast":{"frameMs":45,"cycleMs":720,"fullDrawFrame":9,"releaseFrame":10},"clientIntegration":"not_integrated"}
(ROOT/"animation-timing.json").write_text(json.dumps(timing,ensure_ascii=False,indent=2),encoding="utf-8")
notes=[]
for s in review.get("sequences",[]):
 issues=s.get("remainingIssues") or s.get("knownIssues") or []
 if isinstance(issues,str):issues=[issues]
 detail="；".join(str(x) for x in issues) if issues else str(s.get("evidence","需查对应逐帧审阅记录"))
 detail=detail.replace("正常尺寸720ms试播/640及800ms比较、慢速及客户端校准由主审完成。","当前正常预览1200ms/75ms；动态观感及客户端校准仍未验收。")
 notes.append("- "+str(s.get("sequence"))+": "+str(s.get("status"))+"。"+detail)
text=f"""# 09 竹弓少女 · 本机合并交接

更新：{datetime.now(timezone.utc).isoformat()}（UTC；用户时区 America/New_York）。

{accepted_note}196/196 动作PNG已落盘。当前技术检查 {c['technicalChecksPassed']}/196；单帧静态记录通过 {c['visualPassedSlots']}/196，完整动态记录通过 {c['dynamicPassedSequences']}/14。技术、静态、动态与用户对当前观感的认可是不同记录；不自动互相改写。当前制作版本已保留交付，未查看范围及客户端仍未扩大验收。

## 合并入口

- 仅本角色目录，不覆盖其他角色、旧成品或客户端。
- runtime/run/<N,NE,E,SE,S,SW,W,NW>/01..16.png：128张。
- runtime/hit/<E,W>/01..06.png、runtime/attack/<E,W>/01..12.png、runtime/cast/<E,W>/01..16.png：68张。
- 全部1024×1024 RGBA；每帧原生输入证据≥1024。无复制补帧、镜像补方向或插值。整画布等比导出，透明度≤2/255的噪点归零；未做逐帧最低脚贴地或包围盒缩放。
- [SHA256SUMS.txt](SHA256SUMS.txt)列出196张当前PNG路径与SHA；[manifest.json](manifest.json)绑定来源；selection/逐图指向当前generation记录（位于PNG旁或provenance/），并保留真实请求、回执、时间、尺寸和参考SHA。
- [review.json](review.json)合并当前人工审阅；review-parts/保留分组实见证据。变更图后旧SHA的通过记录不适用。

## 时长和动作事件

最新用户要求：跑步正常1×采用1200ms完整循环，16帧均匀75ms，首尾不额外停顿；正式预览已移除480/640/720/800ms旧速度选项。慢速0.25×为每帧300ms、一圈4800ms。正确PNG保持用户认可的同一版本，不套用相位权重。受击40ms/帧、普攻30ms/帧、施法45ms/帧保持不变。客户端未同步或运行验收。accepted-version.json中的720ms是当时认可的历史预览节奏，当前时长以本文件和animation-timing.json为准。

战斗候选事件：受击03峰值；普攻06满拉、07释放；施法09满拉、10释放。见[animation-timing.json](animation-timing.json)。跑步接触、承重和离地依据各方向实际图像审阅记录，不能直接拿提示词相位当事件。

## 根点与接地

导出使用完整1024画布，translation=[0,0]。N提示目标为[512,940]，E战斗提示目标为[600,940]，均不能当成实测根点。N实见支撑鞋底通常位于约y933–951；SW另有约y980的待核接触带。远近脚投影高度可以不同。预览地面线是诊断线，可输入y值，不移动角色。全方向可信根点和客户端位移/滑步尚未标定完成。

## 预览及验证范围

打开[preview/index.html](preview/index.html)：全部14段、真实196帧、深浅底、128/256px游戏尺寸、放大、逐帧、暂停和慢放。正常跑步只保留1200ms。preview/qa/的跑步APNG与HTML均精确使用75ms/帧，慢放300ms/帧；战斗GIF时长不变。不复制画面补时长。

播放器JS语法及VM控件/循环边界测试已通过。浏览器工具拒绝本地file协议导航，未通过其他协议或浏览器绕过；未完成浏览器实播视觉验收。2026-10-03重新检查发现D:/work/mmorpg-client现在存在，旧文档的“不存在”已过时；本角色遵循仅写私有素材目录的边界，未接入或运行游戏内验收。

客户端只读检查：QdaoCharacterCatalog.cs当前仍将v14的FrameDurationMs固定30，并在原角色manifest验证中要求30ms/480ms；QdaoBoySpriteAnimator按Fps/ReferenceRunSpeed计算FramesPerUnit。后续集成须同时更新相应时长校验、资源索引与位移步频关系，不能只复制本包75ms参数就声称游戏内降速已生效。具体本机证据见[audit/client-readonly-check.json](audit/client-readonly-check.json)。当前未修改共享客户端。

## 当前分组结论

以下是逐组既有技术审查与待观察项，保留为追溯记录；其中审阅者提及的旧试播时长不是当前播放配置，当前统一以1200ms/75ms为准。用户随后已认可当前版本；不据这些未证实静态疑点继续重画已认可图片。

{chr(10).join(notes)}

## 模型与素材

本批目标为配置的GPT Image2.5 Sunburst/max，使用宿主内置image_gen。实际调用无model/quality选择器，工具未披露实际型号/质量，均按null/未确认记录；提示词或配置不能证明实际版本。画风遵循既有角色/方向idle与designs/jubaozhai-ui/02-characters.png。

当前PNG是各槽唯一选定稿；拒稿只保留文字来源/原因。项目旧角色定稿只读。仍在更新的在制稿和当前预览保留，清理不影响runtime或当前预览引用。

## 最新脚尖反馈处理

用户最后明确由本角色逐图判断脚掌是否外撇；此前月影少女整套方向和垂直方向均已撤回作为通过模板。N及E战斗经完整接触表与下肢放大核查：N背向靴跟/鞋底长轴顺小腿，E战斗两靴均朝前偏右，未见横向分叉。其余方向见对应review-parts的当前脚尖、膝踝及承重证据。正常透视与后脚提踵保留，不用缩窄腿间距替代摆正脚掌。

当前196张对应记录见[audit/foot-grounding-closeout.json](audit/foot-grounding-closeout.json)，W/S/SE本轮脚轴补查见[audit/foot-axis-20261003.md](audit/foot-axis-20261003.md)。[八方向1200ms总览](preview/qa/run-eight-directions-1200.apng)使用完整画布等比缩至256px，单圈16帧，无插值、复制补帧或根点移动。
"""
(ROOT/"MERGE_HANDOFF.md").write_text(text,encoding="utf-8")
print(json.dumps({"pngHashes":len(rows),"handoff":"MERGE_HANDOFF.md"}))

