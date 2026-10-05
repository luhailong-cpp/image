# 07 月影少女 · 当前动作素材交付

2026-10-04：收到新视频与歪脚反馈后继续修订。当前成品为196张1024×1024透明RGBA PNG及42张配套连图/APNG。最新验收记录是review/axis-continuity-20261004/final-review.json；此前run-grounding等记录只代表当时版本。

[打开全部动作预览](http://127.0.0.1:8777/preview/index.html)。14个动作组可切换，支持正常速度、¼慢放、暂停、逐帧和160px/256px检查。图片带当前SHA版本参数。服务停止时可直接打开本目录preview/index.html，清单已内嵌。

## 本次追加修正

实际读取用户提供的24FPS、418帧视频，在0/4/10/13秒段提取连续24帧查看。外部视频仅用于运动平面和连续性参考；角色较小、有遮挡，不能据此证明每帧鞋掌细节。用户截图为04山岳守卫NW，不是月影少女。原始路径、SHA、抽帧时刻、检查范围和限制见本轮reference-evidence.json。

复看月影八方向后，本轮替换8张：run_NE_14, run_NE_15, run_NW_06, run_NW_07, run_NW_08, run_NW_14, run_NW_15, run_NW_16。修正西北六张及东北两张后蹬靴的横向侧拐，使鞋底纵向轮廓更顺接小腿；保留原支撑腿、膝踝位置、各帧姿态、正常踝俯仰、手部和双刀。其他方向未找到本轮确定的新增横扭问题，因此保留正确帧。具体审查范围见本轮各方向audit及final-review.json。

前轮脚向、战斗动作与接地修订继续有效，分别见direction-alignment-20261004、direction-combat-20261004、run-grounding-20261004记录。不同轮有重叠帧，不能把替换数量相加当成独立成品数；正式像素与路径以manifest.json和SHA256SUMS.txt为准。

## 动作与节奏

跑步八方向各16张，共128张。受击E/W各6张、普攻E/W各12张、施法E/W各16张；战斗动作范围是E/W。

跑步16×75ms=1200ms，¼慢放16×300ms=4800ms；受击40ms、普攻30ms、施法45ms每帧。每半圈同一支撑腿依次四位置，各两张独立姿态：01–02前落地/缓冲、03–04身下承重、05–06后驱、07–08末端前掌；09–16换另一腿。支撑腿、相位、时长和事件未因这次鞋掌修正改变。

## 文件与验证

正式文件：frames/{action}/{direction}/NN.png；每张图的.png.generation.json追溯到实际提示词、输入SHA、原生1254图SHA和工具回执。所有新图由宿主内置image_gen.imagegen编辑，再全画布等比Lanczos导出1024；未裁框、镜像、整体平移或插值造帧。实际模型/质量工具未披露，记录为null，与配置目标分开保存。

本轮提示词集合：review/axis-continuity-20261004/prompt-index.json。前轮提示词索引保留在各自review目录。按项目保留要求，成品验证后删除过程图和检查图片，仅保留196张游戏图与42张预览；来源文字和清理SHA台账继续保留。未删除本角色目录外的任何文件。

最终连图、修正原生图和浏览器状态/画面采样已检查；实际APNG延时与56项虚拟时钟检查通过。没有连续浏览器录屏。本次仅完成素材和离线预览，未修改、接入、启动或测试D:/work/mmorpg-client；世界位移、阴影、滑步和技能判定需要客户端实测。

复核命令（Python需Pillow）：

```powershell
python -X utf8 -B tools/verify_manifest.py --require-complete --report
python -X utf8 -B tools/check_direction_delivery.py --revision review/axis-continuity-20261004
python -X utf8 -B tools/check_final_previews.py
```

只重建当前预览使用tools/rebuild_previews.py；只重建HTML使用tools/build_preview.py。不要重新运行历史发布、修订或导出脚本覆盖当前成品。
