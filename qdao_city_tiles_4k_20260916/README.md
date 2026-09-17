# 主城单块 4K 重制

当前已按用户要求使用内置 `image_gen`，生成并拼成**天墉城中央广场的首块 4096 × 4096 候选图（v3b）**，明显的南侧台阶错位已通过局部重绘修复。四个地点的七套地图外观尚未全部完成，客户端地图尚未发布或替换。


## 当前结果

- [首块 4K 无损 PNG（v3b）](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png)
- [缩小总览](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3b_overview_1024.png)
- [本次局部修补拼接记录](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/output/south_stairs_v3b_assembly.json)
- [独立视觉检查](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent_visual_review.md)
- [全部七套外观制作清单](E:/work/image/qdao_city_tiles_4k_20260916/production_catalog.json)

首块已核对 PNG 尺寸、原生来源与 SHA256，并检查重点接缝。南阶错位修复是局部视觉结论，不代表全城邻块、前景、最近景或设备性能已通过。客户端的视野加相邻一圈加载、隐藏候选准备及齐备后同帧换景已实现；最新隔离 EditMode 21/21 通过，307 个运行时代码文件编译无错误，详见[客户端验证](E:/work/mmorpg-client/Docs/VerificationEvidence/city-tiles4k-atomic-20260917/summary.json)。

## 统一需求话术

所有主城地图按最高可用画质逐区域重绘，最终交付图块每张为 4096×4096，整张地图的总尺寸以最终分块数量和布局为准，不固定为16K。旧图仅作布局参考；每块要有真实清楚的细节，道路、台阶、建筑与水岸必须连续。客户端按当前视野加载并预载周边图块，切换外观时等目标图块齐备再整体切换。切图 MD 只记录主城地图切图规则，客户端实现和每轮制作进度分别记录；后续新模型可用时再按同一标准重制。

## 当前实际制作路线

当前布局为 4 × 4 个生成分区。已落盘的原生输出为 1254 × 1254，每张包含 1024 × 1024 核心和四边各 115 像素上下文，相邻分区重叠 230 像素；已拼成首块 4096 × 4096 候选，并追加两张原生 1254 × 1254 图修复完整南阶，所有版本保留。**这是多张原生图片的拼接，不是单次原生 4K 生成。** 实际完成情况以文件和逐张记录为准，不以预设数量表示成功。

本会话内置工具没有模型、尺寸或质量选择器；尺寸和最高画质要求写在提示词中，实际尺寸由输出文件核验。后端由宿主管理，记录为 `backendModelVerified=false`，不能把结果称为已确认使用 GPT Image 2.5。没有为本轮调用单独计费 API，也不以 API 授权作为当前工作的等待条件。

- [当前分区计划](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/plan.json)
- [布局参考目录](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/guides/)
- [手写提示词目录](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/prompts/)
- [原生结果与逐张来源记录](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/native/)
- [交付状态说明](E:/work/image/qdao_city_tiles_4k_20260916/status.json)

逐张记录保留实际尺寸、生成输出来源、提示词／参考图／输出图 SHA256 和执行路线；不会编造模型版本或请求 ID。布局参考只用于约束构图，不属于新增高清美术。Windows 本地图像读取存在 ACL 故障时，使用可见参考预览传入内置生成；具体参考传递方式记在各张记录中。

首块范围取自现有 6144 × 6144 地图的 `(2048,2048)-(4096,4096)`，对应世界 X=150..250、Z=100..200。它用于检查重绘细节、太极纹样、铺装和接缝，不决定全城分块数量；样块通过也不等于全图近景清晰度或设备性能通过。

## 保留的旧方案

根目录的 [preparation.json](E:/work/image/qdao_city_tiles_4k_20260916/preparation.json)、`references/`、`prompts/`、`pipeline.py` 及 `verify_pipeline.py` 保留原先的 API 方案：指定 Sunburst 快照与最高质量，采用 2 × 2 张 2304 × 2304 原生图。**该 API 方案未执行，已被本轮内置制作路线替代，不应与 `builtin_4x4/` 的实际产图记录混用。**

[旧机械验证报告](E:/work/image/qdao_city_tiles_4k_20260916/qa/verification.json)仅证明合成夹具的裁接与证据缺失检查通过；其中的零生成数量属于旧测试范围，不是当前内置生成进度，也不证明美术或实机验收通过。

## 发布前验收

首块仍需检查原生来源、100% 像素细节、内部接缝、外围上下文、色调一致性以及道路与既有导航的对应关系。完整地图还需核查前景剪影、最近景、宽屏、跨块移动、换景和内存释放；全部通过后才发布生产 manifest。其余地图保持各地域原有自然配色。

[主城地图切图规范](E:/work/image/主城地图切图规范.md)仅记录切图规则；本文件负责本轮制作路线和交付状态。