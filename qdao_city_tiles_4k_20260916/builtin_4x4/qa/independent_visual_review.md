# 天墉广场首块候选：独立视觉检查

检查对象：`output/tianyong_plaza_4k_candidate.png`（首版）及 `output/tianyong_plaza_4k_candidate_v2.png`（南阶局部修补版）。坐标均为最终 4096 × 4096 图像的左上原点 `(x,y)`，向右／向下增加；下述缺陷位置为实际目测范围，不表示逐像素自动定位。

**结论：v2 仍不通过发布前美术验收。** 南侧台阶中央已改善，但明显断阶转移到修补区右边缘。像素尺寸和文件来源通过不能替代此项几何连续性检查。

v2 SHA256：`ee918902ffa8f9199af397d601953729af074909c62a7a303c127c3f59350d49`。

## 必须修复

| 优先级 | 版本与位置 | 实际看到的问题 | 图像证据 |
|---|---|---|---|
| P1：阻止样块发布 | 首版，约 `x=1945..1975, y=3380..3840` | 南阶多条水平踏面在中央突然上下错开。整图缩略图已能看见，原尺寸裁剪更明确。 | [首版下方中缝](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/seam_x2048_y3072_100pct.png)、[首版总览](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/overview_1024.png) |
| P1：当前仍未解决 | v2，约 `x=2580..2655, y=3410..3810` | 修补右边缘形成纵向锯齿状断口，多条踏面／踢面在接缝两侧错开约 10–20 像素。不是可忽略的石缝或色纹变化。 | [v2 右接缝原尺寸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v2_south_stairs_right_seam_100pct.png)；该裁剪原点为 `(2225,3196)`，问题大致位于局部 `x=355..430, y=214..614` |

在 v2 的中间和右侧可见部分，按上平台下第一条深色踢面至最底条计，目测均约 13 条，未看到少一整级；目前更像两侧高度／间距未对齐。此计数只描述画面，不是工程测量。修补中央和左边界的水平线在已检查裁剪中已连续，但这不能抵消右边界的新断裂。

若继续使用 1254 × 1254 的局部修补，建议供后续制作参考的取景为 `[2023,2842,3277,4096]`：同时覆盖已修中央、右接缝、右侧栏杆与阶底，并明确固定两侧对应级的高度。此处仅提出取景建议，尚未生成或验证下一版。

## 已实际检查且未发现同等级断裂的部分

- 已查看首版 1024 总览，以及围绕 `x/y=1024、2048、3072` 九个网格交点的 900 × 900 原尺寸裁剪。太极 S 形分界、可见圆形嵌片和左右环带没有发现南阶那样的明显错位。石缝、浅雕纹样及金色边线在查看尺度上清楚。
- 已查看 `stair_right_100pct.png`，覆盖北侧台阶的中央偏右部分；所见踏面线和右扶栏连续。未据此断言北侧台阶每一像素都通过。
- 已查看 v2 南阶中心、左边界和上边界裁剪。中央原有大断口已消失；上方道路两侧装饰条存在石纹／图案变化，但所见外轮廓连续，未将其列为发布阻断项。
- 已查看 v2 四角各 900 × 900 的原尺寸水岸／栏杆裁剪。在这些范围内，石栏、岸墙和水面边界没有看到新增的明显拼接断裂。树叶、花瓣、屋瓦与石材轮廓清楚，未见整个分块突然偏色。未进行全图逐像素颜色测量。

## 检查证据与范围

原生尺寸裁剪没有缩放。由于本地 `view_image` 的 Windows ACL 读取失败，实际目检通过同尺寸 JPEG quality 90 预览传递；保存的 QA PNG 保留原始裁剪像素。总览图仅用于整体构图和色调判断，不能替代原尺寸检查。

新增独立 QA 裁剪：

- [西北水岸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent-v2-northwest-waterfront.png)：`[0,0,900,900]`
- [东北水岸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent-v2-northeast-waterfront.png)：`[3196,0,4096,900]`
- [西南水岸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent-v2-southwest-waterfront.png)：`[0,3196,900,4096]`
- [东南水岸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent-v2-southeast-waterfront.png)：`[3196,3196,4096,4096]`
- [旧图同范围总览](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent-source-overview.png)：由旧 6144 图的 `[2048,2048,4096,4096]` 区域缩为 1024，仅作布局参考，不是新增美术。

本次只做静态视觉检查，没有生图，没有修改候选或客户端，没有验证角色遮挡、导航、运行时缩放、内存或全部七套地图。首块候选不等于完整主城交付。
## 追加：v3 台阶全宽修补复查

保留上文 v1／v2 历史结论。本节对象为 `output/tianyong_plaza_4k_candidate_v3.png`，两张原生图组合范围为 `[909,2842,3187,4096]`。

已实际查看 v3 整图 1024 总览、台阶中央原缝、左右新的外接缝和上边道路接头的原尺寸裁剪。所见中央及左右踏面连续，未再看到 v1／v2 的大幅锯齿错阶；两侧栏杆及岸墙的已查看连接处没有发现同等级断裂。

仍有外观变化：约 `x=1680..2400, y=2890..3390` 的南向通路石缝、颗粒和明暗比原候选更重，原尺寸及总览中都能辨认出更换范围。这不等同于断阶，但本版扩大了材质变化区域；随后提供的 v3a 缩小了修补范围。

证据：[v3 总览](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3_overview_1024.png)、[中央](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent-v3-internal-seam.png)、[左外缝](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent-v3-left-boundary.png)、[右外缝](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent-v3-right-boundary.png)、[上边道路接头](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3_south_stairs_top_seam_100pct.png)。

## 追加：v3a 本轮局部验收

对象为 `output/tianyong_plaza_4k_candidate_v3a.png`，本版修补范围收窄为 `[909,3260,3187,4096]`。已实际查看整图总览、全宽台阶总览，以及中央、左右外缝、上边接头原尺寸裁剪；另保存一张上边铺砖的 900 × 240 原尺寸聚焦裁剪。

**限定结论：本轮南阶几何连续性局部通过；仍保留一项 P2 外观接缝。** 所看全宽阶梯和三处接缝中，踏面贯通，没有再次出现 v1／v2 的明显错阶。左右栏杆、阶底和岸墙连接处在所看裁剪内连续。整图中 v3 的大面积铺砖变深已减轻。这里的“通过”只指所检查南阶几何，不能表述为首块完全无缝、完整游戏地图或客户端已验收。

| 优先级 | 像素位置 | 实际看到的残留 | 证据 |
|---|---|---|---|
| P2：外观完善项 | 主要在 `x=1775..2320, y=3320..3375`，较重横缝约 `y=3345` | 上平台前最后一排铺砖附近可辨认新旧材质接入：较重的横向石缝、短竖缝在接缝上方伸出，以及局部石纹深浅变化。未看到台阶轮廓再次跳变；这是原尺寸可见的铺砖衔接问题。 | [上边铺砖聚焦原尺寸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/independent-v3a-top-paving-100pct.png)，裁剪 `[1598,3260,2498,3500]`；[v3a 顶缝](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3a_south_stairs_top_seam_100pct.png) |

其余实际查看证据：[v3a 总览](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3a_overview_1024.png)、[全宽台阶总览](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3a_south_stairs_fullwidth_overview_1400.png)、[中央原尺寸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3a_south_stairs_internal_seam_100pct.png)、[左外缝原尺寸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3a_south_stairs_left_seam_100pct.png)、[右外缝原尺寸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3a_south_stairs_right_seam_100pct.png)。

本次补充检查仍采用原尺寸裁剪经 JPEG 75–95 预览传递的方式，未缩放用于接缝判断的裁剪。没有新生图或修改候选；没有新增实机、导航、角色遮挡或七套地图完成声明。

Reviewed v3 SHA256: 048b26ab759fdfffa1e72d9f6f639ead47bc9dacf6f4ac48372d04f78c515ee1
Reviewed v3a SHA256: 47fb768c3a2c7f756a5ebf707470552f1f02520863aef39c446bc8c0891240df

## 追加：v3b 最终边界对比与本轮选择

对象为 `output/tianyong_plaza_4k_candidate_v3b.png`。本节保留 v1、v2、v3、v3a 的全部历史结论，只记录对 v3b 的实际复查。

**本轮选择 v3b 作为首块候选。** 对照同坐标的 v3a／v3b 上边接头原尺寸裁剪，v3a 在约 `x=1775..2320, y=3345` 横穿最后一排铺砖的深色接线已消失；v3b 的材质交接更接近台阶上沿阴影，未再切出一整排细长的砖块。中央可见踏面仍连续，没有重新出现 v1／v2 的大幅上下错阶。

同时实际查看 v3b 全宽台阶 1400 × 627 总览。所见完整阶梯、两侧扶栏与阶底连接自然，未看到新的明显断阶。此总览只支持整体连续性判断，不能替代左右边缘每个像素的复查。

上沿附近仍可见少量短竖石缝，例如约 `x=1875..1900, y=3358..3380`；它们靠近平台与第一阶的阴影交界，没有形成 v3a 那样横贯铺砖的接线。本轮将其视为 P3 局部外观细节，未据此判为阶梯几何缺陷。

实际检查证据：

- [v3b 上边接头原尺寸](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3b_south_stairs_top_seam_100pct.png)：`[1598,2810,2498,3710]`，900 × 900；与 [v3a 同坐标裁剪](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3a_south_stairs_top_seam_100pct.png)直接比较。
- [v3b 全宽台阶总览](E:/work/image/qdao_city_tiles_4k_20260916/builtin_4x4/qa/v3b_south_stairs_fullwidth_overview_1400.png)：由 `[650,2842,3450,4096]` 缩至 1400 × 627，仅用于整体判断。

上边裁剪以相同 900 × 900 像素尺寸、JPEG quality 60 传递查看；总览以现有 1400 × 627 尺寸、JPEG quality 55 查看。坐标是目测范围，未做亚像素或色差测量。

**限定结论：v3b 在本次南侧台阶与顶缝的对比范围内优于 v3a，可作为当前首块 4K 候选。** 这不代表整块逐像素无缝、完整主城、七套地图或客户端生产验收通过。本次没有生图、没有修改候选、没有实机验证。

Reviewed v3b SHA256: `21a40f32316a0d77e411510b71d8dc80a4ace8c4b0e4605291ee060b1aeccf98`