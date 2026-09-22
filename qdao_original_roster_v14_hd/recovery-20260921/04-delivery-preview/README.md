# 04 山岳守卫八方向独立素材与预览

> 创建快照之后，主任务已完成离线素材与预览复核，见[绑定v3固定SHA的最新复核](review-20260921/REVIEW.md)及[本窗口交接](../04-HANDOFF-20260921.md)。下文pending及浏览器未记录的描述保留快照创建时历史语义；它们不代表当前尚未执行离线检查，也不代表正式批准已通过。

[用户预览入口](index.html)提供八方向、独立站立、正常／放大、深浅底、逐帧、30ms／帧循环和15→16→01→02接缝。这里只制作隔离快照，未修改canonical、旧V13、客户端或批准标记。

当前快照为 [review-set-v3](revisions/review-set-v3/index.html)：实际 **128 walk + 8 idle**，8方向各16张行走，16个深浅底GIF，每个16帧×30ms=480ms。只把v2的NW15替换为指定的NW15-pose-v3，其余PNG完全一致。全部素材仍为待审状态，未正式批准。

`review-set-v3/audit.json`核对136/136快照SHA与当前来源一致、所有GIF真实帧数和时长、透明边界未碰画布；`action-scope-audit.json`核对旧104walk+8idle共112张原字节保留，24张新增原生1254×1254单帧、输出1024×1024。新增原图24个独立SHA和像素哈希，136输出去透明边后的像素哈希互异，无精确水平镜像对。这些是文件、来源和像素检查，不等于步态美术批准；本轮13个新增／改稿的完整来源、请求与重建独立审计另由主任务协调。

NW15-pose-v3和SW16-pose-v3需完整循环检查。SW16在15→16主体高度上升22px；原图主体占高92.5%，未完全符合89%提示目标，未发生裁切。相关待审限制已显示在v3预览页。固定manifest SHA：`77f6a60a37f2016a8643150a34921bd389f253c1a92e534a3adc303125182737`。

选择规则：所有既存V13动作优先原字节保留；缺槽才取V14 canonical；仅对这些新增槽允许主任务指定 staging 修订。选择须绑定精确路径、SHA、版本名和待审状态，绝不覆盖旧槽。磁盘内旧512保持512，新1024保持1024；预览等世界尺寸显示不算提升原生清晰度。PNG没有插值造帧；完整方向GIF的16帧均来自16个对应PNG，每帧30ms，总480ms。

`initial-v1` 实际118walk+8idle，SW缺14/15/16，NW缺08/10/11/12/14/15/16；未将尚未确认的staging稿自动列为正式选择。旧N/NE/E/SE/S/W六向齐套，已生成12个深浅底GIF、八向深浅静态总览和首尾接缝图。六旧向做了完整16帧静态总览及首尾静态复查；可读性与历史残边见 `six-directions-static-notes.json`，不重认证历史生图来源或宣布动态通过。

本包制作代理此前的浏览器入口不可用（iab unavailable，浏览器列表为空），未由此代理完成浏览器动态验收。主任务将对v3固定快照使用其浏览器验动态；这些后续结果应单独绑定本快照manifest SHA，不能由文件数字检查推定。引擎运行验收未进行。

历史`review-set-v2`已经完整构建并核对136张固定SHA和16个GIF；它保留待修的NW15-equipment-v2。此后原staging的NW15被pose-v3替换，所以v2历史审计记录当前源135/136一致、NW15源漂移1处，但快照文件136/136仍匹配原manifest。保留旧快照以供对比，绝不原地覆盖。

主任务确认SW/NW选择后，在新的选择JSON中填写 `overrides`，键如 `walk/SW/16.png`，值为 `{ "path": "绝对路径", "sha256": "实际SHA", "selected_revision": "SW16-pose-v3", "visual_status": "root_selected_unapproved" }`；然后用新revision生成不可变快照：

```powershell
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'qdao_original_roster_v14_hd/recovery-20260921/04-delivery-preview/build_package.py' --revision selected-v2 --selections '新的选择JSON绝对路径'
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'qdao_original_roster_v14_hd/recovery-20260921/04-delivery-preview/audit_snapshot.py' --revision selected-v2
```

每个snapshot的 `manifest.json` 保存136个目标槽的实际库存、每张输出尺寸、SHA、原路径、所选修订、关联frame-source记录和30ms时间合同；`audit.json`另核对固定SHA、当前来源、alpha和GIF时长。历史快照的来源若后续已换稿，用审计参数`--historical-snapshot`可明确报告源漂移，不能把漂移称为当前来源一致。源图静态检查与文件数字通过都不会传播为 `formal_approval=true`。
