# 五行奇谈 · Q 版游戏美术

本仓库保存当前游戏地图、角色、UI、美术设计、生成来源记录与接入文件。素材保留、模型记录和风格要求见 [项目长期指令](AGENTS.md)。远端已经删除、客户端不再使用的旧资源保持删除，双方当前新增与修改继续保留。

图片和交付包按 [.gitattributes](.gitattributes)使用 Git LFS。换电脑先准备 Git LFS 并取回当前需要的素材对象；LFS 指针文件不代表图片字节已经下载。

## 地图制作与迁移

换电脑先看 [迁移交接](docs/COMPUTER_HANDOFF_20261011.md)。2026-10-12 用户要求“边继续做边传吧”，上传窗口确认本批内容固定为独立快照，按[恢复制作指令](docs/MAP_PRODUCTION_RESUME_20261012.json)接续主城、渔村和八仙岛。15/15 [迁移冻结记录](MAP_MIGRATION_FREEZE_20261011.json)及各区断点是已捕获批次的历史证据；新增图另批补传，本地存在或旧冻结就绪不代表新增图已经上传。

该批恢复范围为三张日景：主城16×16个4096图块，渔村和八仙岛各14×14；固定坐标与分区读取各自 production-contract.json，当前采用版本、缺片及验收状态读取各区最新账本。5000人静态脚点排布已通过条件试验；地图任务只做美术，实际游戏运行不在制作范围。当前稿与制作来源按项目长期指令保留，旧图模型字段保持历史记录；提交和上传由用户指定的上传窗口统一处理。

## 当前入口

- [已确认风格与成图索引](designs/README.md)
- [统一图像设置](config/image-generation.json)与[执行策略及逐图记录](docs/IMAGE_MODEL_POLICY.md)
- [UI 制作规范](qdao_ui_redesign_v5/UI_SPEC.md)
- [主城地图切图规范](主城地图切图规范.md)、[地图制作记录](qdao_city_tiles_4k_20260916/README.md)与[恢复制作入口](qdao_city_tiles_4k_20260916/builtin_q64_production/resume-production-20261010/README.md)
- [当前角色动作制作](qdao_original_roster_v14_hd/action-remake-20261001/)
- [装备 UI 设计与验证](designs/equipment-ui-20261009/)
- [场景交付说明](SCENE_DELIVERY.md)

## 给接手的 Codex

开始制作前读取 [项目长期指令](AGENTS.md)，再阅读 [后续交接](docs/WUXING_QITAN_HANDOFF.md)、[美术定调](docs/QDAO_ART_DIRECTION.md)、[已确认成图](designs/README.md)及当前任务的生产合同。绘图型号与质量统一读取配置，每张新图保留实际模型、质量和来源证据。地图生成前核对[并行坐标分工](docs/MAP_PARALLEL_SPLIT_20261013.json)，从当前采用版本和缺片断点继续。

工具移机见 [AI 设计工具安装与交接](docs/AI_DESIGN_TOOLS_SETUP.md)。客户端地图接入见相邻仓库 [CityTiles4K.md](../mmorpg-client/Docs/CityTiles4K.md)，角色归档动作接入见 [QdaoArchivedActions20261005.md](../mmorpg-client/Docs/QdaoArchivedActions20261005.md)。

2026-10-15 已清理46张浏览器与 Unity 截图，2026-10-16 续清理3张 Azure DevOps 网页截图；正式美术及文字来源记录保留，历史报告里的截图路径仅作记录。逐文件清单见 [10月15日清理记录](docs/screenshot-cleanup-20261015.json)与[10月16日续清理记录](docs/screenshot-cleanup-20261016.json)。
