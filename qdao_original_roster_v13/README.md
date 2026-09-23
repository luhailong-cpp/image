# 指定原版角色恢复与 16 帧动画工作区

> 2026-09-23 保留范围更新：已按用户要求清理原图、回退／中间图；当前游戏输出及配套设计保留。下文来源路径与像素重建命令属于历史制作记录，不能据此认定原图仍在。逐图来源文字与哈希未改写；当前清理范围见[清理记录](../docs/ASSET_CLEANUP_20260923.md)。

2026-09-20 追加精简：移除历史快照中54张已有相同字节保留件的PNG，约81.27 MiB；当前人物素材、逐帧验收文件和冻结身份基线保留。[保留副本与恢复方法](../docs/PNG_PROCESS_CLEANUP_20260920.md)。

2026-09-20 存储清理：移除修正前历史快照中的1,291张派生处理／导出图，约362.89 MiB。当前候选、混合版本旧帧、原图和冻结身份基线保留；旧快照图片可按Git记录恢复。[清理明细](../docs/CITY_CHARACTER_CLEANUP_20260920.md)。

本次按用户明确指定的提交 `9adcf9291e4a867601868889a5965f3cd48630ba` 恢复 `q_daoist_character_pack_4096`。原目录全部当前文件已先备份，再仅覆盖该提交中的角色包文件；没有回滚整个 Git 仓库、删除新增文件或改写客户端资源。

- 冻结原包：`baseline/q_daoist_character_pack_4096/`，保留指定提交的全部原字节。
- 已恢复原路径：`E:/work/image/q_daoist_character_pack_4096/`。原 README 与原工具也按提交恢复。
- 恢复前完整备份：`E:\work\image\qdao_original_roster_v13\history\before-restore\20260917T083741206166Z\q_daoist_character_pack_4096`。
- [逐文件恢复记录](restoration.json)记录原 SHA、恢复后 SHA 和保留未动的新文件。
- [基线清单](baseline/git-extraction-manifest.json)记录每个 Git blob 与 SHA-256。
- [23 人角色清单](inventory.json)列出 00–22 的准确源路径、SHA 和正式 ID。24 个 PNG 中两张道童参考逐像素相同，额外文件只记作 00 的 alias。
- [原版总览](old-style-overview.jpg)只对完整原图等比排版，未重新设计人物。

新动画独立写入 `candidate/<character_id>/`；参考图、生成过程与记录位于本工作区 `references/`、`generation/` 和各候选目录。目标为八方向、每向 16 帧、30ms/帧、480ms 周期。静态原图恢复已完成，不能据此声称新行走、独立站立或游戏接入完成；这些由主任务继续逐角色制作并验证。

Native single idle: `pipeline.py import-idle --character ID --direction SE --rows 1 --cols 1 --source RAW --prompt PROMPT --receipt RECEIPT --batch-id IDLE_BATCH`. The full raw image is one source cell, with `output_direction_map: ["SE"]`; the independent verifier reconstructs it using the same immutable character-wide scale. Existing eight-direction 2x4 imports are unchanged. No repeated synthetic sheet is required.
