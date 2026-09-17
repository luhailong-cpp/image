# 主城 64K / 单块 4K 重制

## 最新目标与状态（2026-09-17）

用户最新要求为：**每套整城 65536×65536（64K），单块 4096×4096（4K），16×16 共 256 块**；在这一密度下逐区域重新制作真实细节，采用更 Q 版、圆润饱满、明亮干净的风格。高清依靠清楚的轮廓与结构，减少写实裂纹、颗粒和脏污，不能放大旧样图充数。

用户最新决定：独立 API 需要额外收费，因此本轮改用**内置 GPT Image 2.0 路线（`builtin_image_gen`）**。严格指定 GPT Image 2.5 的要求及 API 凭证阻塞已撤销；**本轮不调用单独计费 API，不需要配置 Key**。活跃制作目录为 [builtin_q64_r10_c07](E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_r10_c07/)，正在准备天墉城 `r10_c07` 首块；**首块尚未完成，当前没有已验收的 64K Q 版交付块**。七套外观共计划 1792 块，计划数量不代表已生成。

内置工具没有模型、尺寸或质量选择器，后端由宿主管理。历史抽检图片的 C2PA 生成动作标注 `softwareAgent={name:gpt-image,version:2.0}`；这支持用户所选内置 2.0 路线的历史来源说明，但不能据此预先保证每次新输出的实际后端。逐张保留实际尺寸、来源和可获得的元数据，未核实的型号不作确认声明。核验限于元数据解析，未做密码学验签，见[历史来源核验](E:/work/image/qdao_city_tiles_4k_20260916/q64_gpt25/qa/builtin_model_audit.json)。原 [GPT Image 2.5 API 执行包](E:/work/image/qdao_city_tiles_4k_20260916/q64_gpt25/执行包.md)保留为停用历史方案，不再等待或配置该方案的 API 凭证。
旧 v3b 样图与 [32K 等效密度试作](E:/work/image/qdao_city_tiles_4k_20260916/builtin_density32k_r05_c04/plan.json)仅作历史对照；用户认为既有画面仍不够清楚，随后明确了更 Q 版和整城 64K 的目标。这些旧样图不是本轮目标的验收通过结果，32K 试作也不表示完整 32K 城市已完成。32K 已产原图、提示词及记录保留在 [试作目录](E:/work/image/qdao_city_tiles_4k_20260916/builtin_density32k_r05_c04/)。

四个地点的七套外观尚未按新目标完成，客户端地图尚未发布或替换。以下保留旧样图的来源、局部修补结论和历史链接。


## 历史对照：首块 4K 样图

- [首块 4K 无损 PNG（v3b）](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png)
- [缩小总览](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3b_overview_1024.png)
- [本次局部修补拼接记录](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/output/south_stairs_v3b_assembly.json)
- [独立视觉检查](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent_visual_review.md)
- [全部七套外观制作清单](E:/work/image/qdao_city_tiles_4k_20260916/production_catalog.json)

旧首块已核对 PNG 尺寸、原生来源与 SHA256，并检查重点接缝。南阶错位修复是局部视觉结论，不代表全城邻块、前景、最近景或设备性能已通过。客户端的视野加相邻一圈加载、隐藏候选准备及齐备后同帧换景已实现；最新隔离 EditMode 21/21 通过，307 个运行时代码文件编译无错误，详见[客户端验证](E:/work/mmorpg-client/Docs/VerificationEvidence/city-tiles4k-atomic-20260917/summary.json)。


计费说明：不是 GPT Image 2.5 这个版本必然另收费用；此前提到的是改走独立 API。内置生图计入现有套餐额度，额度用尽后可能使用另购 credits；本轮只走内置入口，没有调用独立 API。依据：[Codex/ChatGPT 额度说明](https://learn.chatgpt.com/docs/pricing)、[ChatGPT 与 API 独立计费说明](https://help.openai.com/en/articles/9039756-managing-billing-settings-on-chatgpt-web-and-platform)。
## 统一需求话术

所有主城地图按用户最新选择使用内置 GPT Image 2.0 路线和最高可用画质，按更 Q 版、圆润饱满、明亮干净的方向逐区域重绘；每套整城为 65536×65536，按 16×16 切成 256 张 4096×4096 图块。旧图仅作布局参考，不能直接放大；高清依靠真实清楚的轮廓、结构和雕刻层次，减少写实裂纹、颗粒与脏污，道路、台阶、建筑与水岸必须连续。客户端按当前视野加载并预载周边图块，切换外观时等目标图块齐备再整体切换。切图 MD 只记录切图和美术规则，客户端实现、型号与每轮制作进度分别记录。

## 历史内置样图制作路线

旧首块样图使用 4 × 4 个生成分区。已落盘的原生输出为 1254 × 1254，每张包含 1024 × 1024 核心和四边各 115 像素上下文，相邻分区重叠 230 像素；已拼成首块 4096 × 4096 候选，并追加两张原生 1254 × 1254 图修复完整南阶，所有版本保留。**这是多张原生图片的拼接，不是单次原生 4K 生成。** 实际完成情况以文件和逐张记录为准，不以预设数量表示成功。

本会话内置工具没有模型、尺寸或质量选择器；尺寸和最高画质要求写在提示词中，实际尺寸由输出文件核验。后端由宿主管理，记录为 `backendModelVerified=false`，不能把结果称为已确认使用 GPT Image 2.5。这批历史样图没有调用单独计费 API；本轮已改用内置路线，但旧样图仍仅为历史对照，不计作新目标的完成量。

- [旧首块分区计划](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/plan.json)
- [布局参考目录](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/guides/)
- [手写提示词目录](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/prompts/)
- [原生结果与逐张来源记录](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/native/)
- [交付状态说明](E:/work/image/qdao_city_tiles_4k_20260916/status.json)

逐张记录保留实际尺寸、生成输出来源、提示词／参考图／输出图 SHA256 和执行路线；不会编造模型版本或请求 ID。布局参考只用于约束构图，不属于新增高清美术。Windows 本地图像读取存在 ACL 故障时，使用可见参考预览传入内置生成；具体参考传递方式记在各张记录中。

旧首块范围取自现有 6144 × 6144 地图的 `(2048,2048)-(4096,4096)`，对应世界 X=150..250、Z=100..200。它用于历史重绘细节、太极纹样、铺装和接缝对照，不符合本轮 64K 的最终密度与 Q 版验收要求；此前局部修补结论不等于全图近景清晰度或设备性能通过。

## 保留的旧方案

根目录的 [preparation.json](E:/work/image/qdao_city_tiles_4k_20260916/preparation.json)、`references/`、`prompts/`、`pipeline.py` 及 `verify_pipeline.py` 保留原先的 API 方案：指定 Sunburst 快照与最高质量，采用 2 × 2 张 2304 × 2304 原生图。**该 API 方案未执行；它与历史 `builtin_4x4/` 实际产图记录及新一轮 64K 正式方案分开保留，不应混用。**

[旧机械验证报告](E:/work/image/qdao_city_tiles_4k_20260916/qa/verification.json)仅证明合成夹具的裁接与证据缺失检查通过；其中的零生成数量属于旧测试范围，不是实际内置生成进度，也不证明美术或实机验收通过。

## 发布前验收

新一轮 64K Q 版素材须检查原生来源、100% 像素细节、内部接缝、外围上下文、色调一致性以及道路与既有导航的对应关系。完整地图还需核查前景剪影、最近景、宽屏、跨块移动、换景和内存释放；全部通过后才发布生产 manifest。其余地图保持各地域原有自然配色。

[主城地图切图规范](E:/work/image/主城地图切图规范.md)仅记录切图规则；本文件负责本轮制作路线和交付状态。