# 02 火符少年 · 素材与离线手脚复核完成

196张独立1024×1024 RGBA已导出：跑步八方向128、受击12、普攻24、施法32。实际参照用户指定09竹弓少女同方向动作，完成脚向、手臂链、两腿交替、落脚及承重续帧修正；已正确帧保留。当前逐图SHA与离线范围见reviews/final-review.json。

跑步正常1200ms/圈，16×75ms均匀；慢放4800ms，支持暂停/逐帧，旧快档已移除。受击240ms、普攻360ms、施法720ms不变。最新四动作入口previews/index.html；跑步入口previews/run-grounding.html；八方向概览previews/run-eight-directions.gif。

196/196技术检查与来源链核对通过，0重复/0像素镜像/0跨槽原生复用。回执证据分级127原始返回文字、68宿主路径、1 N09恢复推断；实际型号/质量均未确认。目标GPT Image 2.5 Sunburst/max，使用宿主管理内置image_gen，无收费API/CLI。完整提示词和来源记录保留，不沿用旧run-correction/combat在制图，不获取另一电脑未提交图。

尚未接入客户端，未运行游戏内验收；位移速度、滑步、根点、碰撞与战斗事件同步需在客户端合并后验证。统一设计根点(512,920)不代表已完成游戏校准。

清理计划已核对389张work过程图（455.7MB）；自动审批以“blocked by policy”拦截批量删除，删除未执行，过程图暂留，详见reviews/cleanup-blocked.json。正式196张与最新预览完整，不受影响。

只写本角色目录。未切分支，未暂存、提交或推送。合并交接见MERGE_HANDOFF.md，逐图清单见MERGE_FILES.csv。
