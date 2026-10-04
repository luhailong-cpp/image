# 02 火符少年当前进度

2026-10-04：本机素材制作与离线复核完成，共196张1024×1024 RGBA正式PNG：跑步128、受击12、普攻24、施法32。

八方向跑步按最新要求修订：同一只脚连续支撑8帧，4个相对位置各2张独立姿态，再换另一脚；16×75ms=1200ms，慢放4800ms。已补修承重、后蹬、换腿、脚掌朝向，以及符扇/铜铃持手与收臂衔接。

逐向支撑帧、当前SHA及离线范围见 reviews/run-position-pairs-final-20261004.json 与 reviews/final-review.json。八方向播放抽样、正常/慢速时长及控件核对见 reviews/final-browser-review-20261004.json。预览时钟的首帧负下标问题也已修复。源图至全画布导出审计196/196通过，未发现复制或镜像同图。

交付入口：previews/index.html（四动作）、previews/run-grounding.html（八向跑步）、MERGE_HANDOFF.md、MERGE_FILES.csv。正式游戏图仅在frames/。

内置image_gen制作；目标GPT Image 2.5 Sunburst/max，工具未披露实际型号/质量，逐图如实记未确认。未用收费API/CLI，未操作共享Git暂存、提交、推送，未改其他角色。

客户端尚未接入，游戏内位移、滑步、根点和事件同步未验。过程图批量清理被自动审批以“blocked by policy”拒绝，未提供更具体理由，文件暂留，详见reviews/cleanup-blocked.json；未绕过重试。
