# 17 灵篆书生 · 合并交接（在制，未验收）

更新时间：2026-10-03T21:59:35.787160-04:00（America/New_York）。此为真实文件盘点快照；再次运行 tools/audit_inventory.py 刷新。

当前 **154/196 槽位有候选图，缺 42 槽位**。本批实际 PNG 尝试 288 张，覆盖 151 个槽位；另保留 6 张旧关键帧原来源引用。不同版本不重复计槽位。
**视觉通过 0 槽位，动态验收通过 0 组；本角色 runtime 目录内 PNG 0 张。未接入客户端，未运行客户端验收。跑步手脚修复尚未通过，不能宣称已完成。**

| 动作 | 方向 | 有候选/目标 | 视觉通过 | 缺帧 |
| --- | --- | ---: | ---: | --- |
| run | N | 16/16 | 0 | 无；仍待验收 |
| run | NE | 11/16 | 0 | 10, 12, 14, 15, 16 |
| run | E | 16/16 | 0 | 无；仍待验收 |
| run | SE | 1/16 | 0 | 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16 |
| run | S | 16/16 | 0 | 无；仍待验收 |
| run | SW | 6/16 | 0 | 04, 06, 07, 08, 10, 11, 12, 14, 15, 16 |
| run | W | 16/16 | 0 | 无；仍待验收 |
| run | NW | 4/16 | 0 | 02, 03, 04, 06, 07, 08, 10, 11, 12, 14, 15, 16 |
| hit | E | 6/6 | 0 | 无；仍待验收 |
| hit | W | 6/6 | 0 | 无；仍待验收 |
| attack | E | 12/12 | 0 | 无；仍待验收 |
| attack | W | 12/12 | 0 | 无；仍待验收 |
| cast | E | 16/16 | 0 | 无；仍待验收 |
| cast | W | 16/16 | 0 | 无；仍待验收 |

全部尝试中的尺寸异常（原生稿不会强行拉伸为方形；当前选图记录/格式异常 0 张）：
- cast-W-02-v2: 1181 × 1332 RGBA；历史尝试，已不在当前明确选图中。
- run-N-09-v1: 1133 × 1388 RGBA；历史尝试，已不在当前明确选图中。

本机本角色唯一写入目录：D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/17_ghost_script_calligrapher_boy。本角色仍在制作，不能用候选覆盖游戏正式素材。当前未操作客户端或 Git 暂存/提交/推送；其他电脑未提交内容不在本盘点范围。

每张实际图片的文件路径、SHA-256、原生尺寸、记录/请求路径与目标/实际型号在 [inventory-audit.json](provenance/inventory-audit.json) 的 current_images/prior_keyframes 中；196 个槽位与候选映射在 slots 中。逐图生成模型/质量实际值未披露时保持 null（未确认），不能把配置目标 GPT Image 2.5 Sunburst / max 当作显式参数或实测结果。

帧时长与标记：

| 动作 | 每帧 | 全段 | 标记 |
| --- | ---: | ---: | --- |
| run | 75 ms（均匀） | 1200 ms | 用户最新指定；完整16帧，首尾无额外停顿；客户端未接入 |
| hit | 40 ms | 240 ms | 无正式事件标记 |
| attack | 30 ms | 360 ms | 第06帧接触候选 |
| cast | 45 ms | 720 ms | 第10帧释放候选 |

锚点：新稿提示中的参考画布 1254×1254、根点 x=640、虚拟地面 y=1155 **只是目标，并未逐帧视觉确认**。最终画布 1024×1024 RGBA。完整画布统一映射规则须经审核确定；不得逐帧最低脚贴地或按包围盒独立缩放，也不得将非方形原生稿拉伸成方形。运行跳跃应保留真实起伏。

旧6关键帧只读引用（不计本批新图）：

| 关键帧 | 原文件 | SHA-256 |
| --- | --- | --- |
| hit-E-03-v3 | D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/17_ghost_script_calligrapher_boy/staging/hit-E-03-v3.png | acbd61afb9d60712ce3f0aeca6d9a489f173acf4d634a587ee61e4f831c35234 |
| hit-W-03-v2 | D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/17_ghost_script_calligrapher_boy/staging/hit-W-03-v2.png | ebf883a5d08e372bb21cb4dc67a1d00e3d6f02cede77d4558322f59d1d78f56c |
| attack-E-06-v2 | D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/17_ghost_script_calligrapher_boy/staging/attack-E-06-v2.png | 2d4cdc6ffdaab73415bbfa2018013342b99d9c367ba32681bd136ad07b9b7c3d |
| attack-W-06-v1 | D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/17_ghost_script_calligrapher_boy/staging/attack-W-06-v1.png | 4ce4de80b17563ed200fa5a7ba733c091131f2223d2bc4663f7d4b89ef20de5b |
| cast-E-10-v2 | D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/17_ghost_script_calligrapher_boy/staging/cast-E-10-v2.png | 2aac3dc4e60ff070dd98e269603005e98c344e385017469b868fdd0073bf5956 |
| cast-W-10-v2 | D:/work/image/qdao_original_roster_v14_hd/combat-20260929/characters/17_ghost_script_calligrapher_boy/staging/cast-W-10-v2.png | db35bb9f1830be7595be600ed8d68d4b02a1a491e8a20d546709f14300802de5 |

未解决事项：缺帧、跑步左右腿/摆臂/关节/持物连续性、透明边缘杂色、部分流苏/饰物错误、全局比例与根点、全部动作正常/慢速/逐帧验收。查看 [STATUS.md](STATUS.md) 和已有 review 文件获取详细情况。未找到审核记录的候选保持待验收。

[本地预览](preview/index.html) 支持正常、0.25慢速、逐帧、深浅棋盘底；页面使用静态清单，需在新图登记后运行 tools/build_preview.py。预览代码可播放不等于动画美术已通过。

刷新：使用含 Pillow 的 Python 运行 tools/audit_inventory.py。它只读取图片/原记录并重写本交接、STATUS.md 与 provenance/inventory-audit.json，不修改图像，不导出、不删除、不访问 Git。
