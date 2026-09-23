# 天墉城节庆 64K 主城制作续接

本目录负责一座城市的一种外观：`tianyong_festival`。目标为 65536×65536、16×16、256 张 4096×4096 PNG，坐标 `r01_c01` 至 `r16_c16`。本目录目前是制作过程，**整套未完成、正式成品 0、不可发布给客户端作为完整地图**。

## 最新状态入口

- [当前进度及逐个新增来源 SHA](session-state.json)：以此处实际文件计数为准。
- [256 坐标、480 相邻边、225 四块交点](current-coverage-ledger.json)：区分缺失、候选、局部检查与正式整城验收。
- [接手时实际盘点](audit/current_input_inventory.json)：全部外观共 24 个 4K 候选、502 个已索引原生来源；不是当前增量总数。
- [模型入口核实](model-capability.json)：配置目标与实际可验证值分开。
- [布局、坐标与现有客户端静态来源绑定](tools/layout-source-audit.json)：静态 SHA/坐标一致不代表新画稿的几何或导航已经通过。
- [原整城布局与局部候选的实际图像对照](audit/layout-alignment-review/README.md)：大地标近似保留，铺装线、刻纹和边宽有重描；精确几何与导航尚未通过。

接手时当前外观有 6 个候选，坐标为 `r09_c07`、`r09_c08`、`r10_c07` 至 `r10_c10`。本次补绘 `r09_c09`、`r09_c10`，目前有候选的坐标共 8 个，仍缺 248 个。旧 19 块进度及旧 `E:/work` 路径不用于驱动本次续制；旧记录保留，读取时对应本机 D 盘真实文件。

随后继续向上制作 `r08_c07`、`r08_c08`、`r08_c09`，分别保存在对应 `next_tile_坐标/` 目录。未形成 4096 候选并写入版本指针前，这些目录中的引导图、原生片及临时合成不计入上述候选坐标数。当前进行到哪一步读取各目录计划与实际原生文件；全局完成数读取最新 `session-state.json`。

## 原生细节及检查

每块以 4×4 个原生 1254×1254 输出提供细节，单片核心 1024、四周重叠上下文 115；以相邻重叠区域对齐、拼接为 4326 后裁去外圈，得到 4096 图块。完整原生输出、提示词、调用回执、来源 SHA、配准位移和色差校正均保留。几何引导图及预览允许缩放，仅用于构图与检查，未作为成品像素来源。

- `r09_c09` 最新候选：[v6 PNG](tools/repairs/versions/r09_c09_repair_v6/r09_c09.png)、[派生与返修来源](tools/repairs/versions/r09_c09_repair_v6/repair.json)、[最新局部检查](audit/r09_c09_review_v5/visual-review-v6.json)。内部检查继承实际未变的像素，改变区域重新查看；与左侧 `r09_c08`、下侧 `r10_c09` 的完整边界及相应四块交点通过本轮局部连续性检查。顶部、右侧后续邻居及整城、导航、最近镜头尚未验收。
- `r09_c10` 最新候选：[v8 PNG](next_tile_r09_c10/repairs/versions/external-v8/r09_c10.png)、[版本指针](next_tile_r09_c10/latest-candidate.json)、[局部检查](next_tile_r09_c10/qa/external-v8/visual-review.json)。内部接缝、左／下完整外边、返回带和西南四块交点通过本轮局部连续性检查；顶部、右侧及其余交点未验。v5/v6 的错台与重复砖缝失败记录保留。最新路径和 SHA 同步到 `session-state.json`。
- 历次不合格检查和候选版本全部保留；新记录只对实际检查过的范围作结论，不把旧失败记录改成通过。

## 实际型号与逐图记录

本批配置目标为 GPT Image 2.5 Sunburst／max。实际使用宿主 `image_gen.imagegen` 内置入口；当前工具仅开放提示词和参考图，没有 `model`、`quality` 参数，返回记录也未提供可核实的 2.0／2.5 版本或质量。因此逐图 `actualModel`、`actualQuality` 保留为 `null`，不得把配置、提示词、官方开放公告或通用 `gpt-image` 元数据当作实际版本证明。

原始来源记录保留在图旁的 `.record.json` 或返修版本的 `repair.json`；实际请求及结果在 `requests/`、对应原图的 `.tool-response.json` 或 `request-receipt.json`。新增独立补充索引位于 `provenance/`，使用真实现有证据，无法取得的生成时刻明确为未知，记录保存时间单独说明。

[逐图索引及重跑方法](provenance/README.md)列出各原图对应的独立旁证。18 张 r09_c10 细节／参考图未保存完整请求 JSON，现有证据为真实提示词、输入 SHA、`toolCall` 和工具响应；这些有限证据没有被改写成完整请求回执。

[技术检查脚本](tools/verify_checkpoint.py)逐个完整解码现有候选与新增原生 PNG，并核对尺寸、SHA、坐标和台账完整性；每次在 `tools/checkpoint_reports/` 新建时间戳报告。`TECHNICAL_CONSISTENT` 只表示所读文件与清单一致，不表示任何美术或导航门槛通过。

2026-09-21 本次检查点：[技术报告](tools/checkpoint_reports/checkpoint-20260921T152329872957Z.md)核对 8 个候选、34 张本轮原生来源（23 张细节、10 张返修、1 张参考），232 个输入文件，错误 0、读前后变更 0。[逐图来源索引](provenance/index-20260921T151627286866Z.md)保存对应生成旁证。[候选联系表](previews/20260921T152330112878Z/candidate-contact-sheet-preview-only.png)仅供查看局部范围和画法，缩略图不算成品或原像素接缝证据。

## 正式交付边界

完成一套后，按客户端 [CityTilePublishing.md](../../../../mmorpg-client/Docs/CityTilePublishing.md) 提供图块、行优先坐标清单、来源／拼接 SHA 和绑定同一版本的美术验收证据，再由客户端窗口接入与实机验收。当前未生成 `accepted_complete` 正式交付清单，未发布运行时资源。

剩余工作包括缺失区域原生细节、全部相邻边和四块交点、整城原道路／建筑／出入口／视角对照、导航与前景遮挡证据，以及客户端窗口负责的最近镜头及实机验证。地图机械尺寸或 SHA 检查通过不能代替这些检查。

接续优先考虑 `r08_c09`，用原整城布局和当前底边真实候选共同约束。`r09_c11` 的右侧约 1365 个最终像素超出旧广场参考，且涉及水岸、护栏及树木，必须使用原 6144 整城完整上下文重新校准；不能外推广场或将越界裁切的空区当作原布局。

[通用几何引导工具](tools/prepare_geometry_guides.py)可为后续坐标准备有来源 SHA 的参考裁切，并把已存在邻图的真实核心按全局像素所有权放入外圈上下文。输出在 `future_geometry_guides/`，包括脚本快照及 24 项共享重叠检查。该目录全部是参考，放大的引导像素绝不能作为成品或原生细节来源。

本窗口没有执行 git add、commit、push、reset 或删除。并发窗口提交及其他素材改动保留；仓库收录不表示美术验收通过。根 `status.json`、`production_catalog.json`、`current-batch.json` 的 `activeProductionRun` 指向本目录，原有 24／502 数据作为历史基线保留。不要用仍按多个外观轮转的旧刷新脚本覆盖本次单城目标。
