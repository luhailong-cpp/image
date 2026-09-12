# 素材清单与来源分类更新

时间：2026-09-12T08:01:58.076632+00:00。本子工作只更新本任务元数据，图片修改 0 张。视觉精修尚未由本子工作执行。

## 写入边界

- build_inventory.py 唯一文件写入是本任务 inventory.json；扫描使用 rg，图片只读头信息，SVG 只解析尺寸。无 image.save、删除、移动、生产目录写入或 monitor-state 写入。
- 本次另外更新 source-families.json，并产出本说明及 inventory-classification-check.json，均在 qdao_festival_refinement_20260910 内。
- 全库头信息只读一遍；发现更精确的元数据后对同一稳定快照重新分类，没有重复全库哈希/解码。

## 清点结果

共 6047 个可见图像/SVG 路径，读头错误 0、读期间变更 0；821 条路径关联当前交付清单，映射缺项 0。158 条 UI 合同、1027 条曝光记录、1142 条旧审计记录已附上。声明哈希为来源信息，不代表本次重验。

| 家族 | 路径数 |
|---|---:|
| 人物动作 | 599 |
| 客户端派生 | 257 |
| 属性/任务背包活动页面 | 104 |
| 其他待归属（大量历史/处理副本） | 3766 |
| UI/旧切图 | 916 |
| 静态人物 | 27 |
| 场景插画 | 57 |
| 道具/图集 | 134 |
| 宠物 | 8 |
| 地图 | 179 |

| 分类角色 | 路径数 |
|---|---:|
| asset_review_pending | 1322 |
| reference_do_not_repaint | 21 |
| accepted_derived_export | 636 |
| evidence_do_not_repaint | 133 |
| accepted_preview_derivative | 24 |
| source_review_pending | 168 |
| accepted_source_art | 144 |
| supporting_history_or_work | 3580 |
| accepted_processing_input | 17 |
| new_design_preview | 2 |

## 已纠正的主要问题

- 高清主城不再误判为 1254 预览：36 张原生 refined 源图、6144 母图/2048 预览/36 tile 共 38 派生均明确登记。旧 stylematch/gptimage2 两张预览保留原身份。
- 扩展场景归入 scene_illustrations：4 个原生源、5 个用途成图；主城横版与庭院共享绘图来源。另纳入 runtime-manifest 指向的五张 2560×1080 派生，定位覆盖图归为证据；不混淆原生尺寸与运行画布尺寸。
- v11 从正式整包清单取得八人范围；408 个正式成品、77 个当前来源、17 个拼接输入、2 个总览派生分别登记，撤下的老道人物不进入当前交付。墨鸢 NW/NE/SE 的拼接输入与 lineage 原生候选分开；只使用记录中已接受的格子。
- v10-preview 的 22 张资产副本记录回正式 source 路径；4 张浏览器截图为 evidence_do_not_repaint。属性/新页面家族与一般 UI 切图分开。
- 当前交付清单优先于历史文件夹/文件名启发式；源图、输入表、派生、参考和证据不再一律 asset_review_pending。

## 清理影响

- 主任务清理审计确认 293 张删除图不损失正式内容：258 张 .work 原本不在旧 inventory；35 张 exposure_v8/review/rebuilt 中间副本曾误列待精修（31 other_review + 4 UI）。
- inventory.deleted_duplicate_aliases 保留 35 条 removed_path→keep_path，涉及 32 个唯一保留路径。哈希/字节等价由主任务清理审计验证，本子工作没有重复哈希。
- 别名依据：docs/STORAGE_DUPLICATES_20260912.json。
- duplicates SHA256：ebf78d77785fb6e204a9e249b2c557651386adbbf160e48212fe93434a042971。
- cleanup 记录 SHA256（主任务提供）：507d64f9cc37deea6bf7b6f9d372b6cd96c9ee9aa814ebac9ff8fe81331be168。

## 尚需判断的分类与审图顺序

1. 先以最新 HD/五场景、v9/v11、v10 发布素材建立风格参照。既有节庆风格通过视觉复核后可保留，不因本轮开始就重复重绘。
2. 对 1322 条 asset_review_pending 和 168 条 source_review_pending 先归属到权威家族、确认是否重复/被取代，再决定精修；它们不是 1490 张已确认需要重画的图片。other_review 共 3766 路径主要包含处理/历史资料，不应整类当作待重绘素材。
3. 优先审真正缺少统一风格的静态人物、宠物、道具原图和旧 UI/场景母图；道家 Q 版为主体，春节/元宵/中秋为少量装饰，保留角色身份和版面功能。
4. 源图发生变化后再处理 636 个已登记派生及其他兼容导出：人物逐帧/横条/GIF/总表，地图接缝/tiles，场景 native→final→runtime，UI alpha/九宫格/图集/SVG，最后客户端资源副本。
5. 最后刷新 24 个预览派生并重跑浏览器/运行截图，证据图不直接涂改。所有视觉批准均需针对本轮实际输出；旧历史审计不能替代。

## 核验

inventory-classification-check.json：9 项检查，错误 0。只验证元数据覆盖与分类，不宣称完成视觉精修或客户端验收。
