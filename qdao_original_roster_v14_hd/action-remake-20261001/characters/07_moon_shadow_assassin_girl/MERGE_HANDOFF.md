# 07 月影少女 · 动作素材交付

2026-10-04：本轮脚向与接地修订已完成离线验收。当前交付为196张正式1024×1024透明RGBA PNG，以及42个配套连图/APNG预览。正式文件以manifest.json的frames[].path为准，当前验收记录为review/run-grounding-20261004/final-review.json；旧日期记录只代表历史版本。

直接打开[全部动作预览](http://127.0.0.1:8777/preview/index.html)，用页面下方14个动作组按钮切换。支持正常速度、¼慢放、暂停、逐帧、160px/256px/放大检查。页面的图片地址带当前SHA版本参数，避免加载旧帧。本机服务停止时，preview/index.html也可作为本地HTML打开，清单已嵌入页面。

## 本次修订

先按竹弓少女同方向参考修正29张跑步脚向，再修正60张受击/普攻/施法的脚向，最后补修56张跑步支撑与交叠。三轮有重叠帧，以最终SHA为准，不能相加当成不同成品数量。保留原先正确帧、人物身份、每手一把弯月匕首和各自摆臂。东南05/13追加修正髋部到膝踝的交叠，避免只改脚尖却提前换腿。

跑步八方向各16张，共128张；受击E/W各6张，共12张；普攻E/W各12张，共24张；施法E/W各16张，共32张。战斗动作范围是E/W，不应理解为八向战斗都已制作。

## 跑步接地和时长

正常跑步固定1200ms/圈，16帧均匀75ms；¼慢放为4800ms/圈、300ms/帧。受击40ms、普攻30ms、施法45ms每帧保持不变。

接地按最新确认的四个位置、每位置两张不同姿态组织：01–02前落地/缓冲，03–04身下承重，05–06后驱，07–08末端前掌蹬离；09–16换另一只脚重复。落地标记在01/09，末端蹬离标记在08/16。逐方向A/B腿别及128张实图SHA见review/run-phase-review.json；这些是画面相位描述，不是碰撞检测或物理锁脚。

脚跟到脚尖遵循各朝向，远近脚保持透视。统一画布根点[512,968]是近地参考，后方脚不能硬拉到前脚同一水平线。没有逐帧裁框缩放、整体平移、镜像、复制凑帧、插值或最低像素贴地。每张新原生图为1254×1254，再全画布等比缩至1024×1024。

## 验收范围

逐张查看新原生候选，并复核最终八组跑步与六组战斗连图的脚向、腿部衔接、手和双刀。浏览器实际验证各组正常播放的末帧、慢放和循环状态，记录见本轮browser-check.json及direction-combat-20261004/browser-check.json。实际APNG延时与页面播放函数的56项虚拟时钟检查均通过。浏览器检查是状态/画面采样，没有连续录屏；结构和计时测试不代替美术判断。

本次只交付角色素材和离线预览。没有修改、接入、启动或测试D:/work/mmorpg-client。世界位移、脚底阴影、游戏速度匹配、滑步和技能判定仍须在客户端接入时实测。

## 来源与保留

本轮使用宿主内置image_gen.imagegen。每张PNG的.generation.json指向原生SHA、真实提示词、参考用途和工具回执；模型/质量配置目标与实际返回值分开记录，工具未披露的实际型号/质量均为null。三轮提示词与请求索引分别在review/direction-alignment-20261004、review/direction-combat-20261004、review/run-grounding-20261004下的prompt-index.json。

按项目保留规则，最终文件及引用核验后已删除本角色过程原生图、拒稿和临时检查连图；当前删除台账共496条。仅保留196张游戏PNG和42个必要预览图片，来源文字不删除。其他角色后来更新的参考文件按原SHA标记为历史来源，没有用新SHA回填旧记录，也没有删除角色目录之外的文件或宿主缓存。

复核命令（Python需Pillow）：

```powershell
python -X utf8 -B tools/verify_manifest.py --require-complete --report
python -X utf8 -B tools/check_direction_delivery.py --revision review/run-grounding-20261004
python -X utf8 -B tools/check_final_previews.py
```

重建当前42个预览和HTML使用tools/rebuild_previews.py；仅重建HTML使用tools/build_preview.py。旧export_candidates、finalize_delivery、revise_feet和complete_*脚本是历史流程，不要重新运行覆盖当前成品。
