【2026-10-08 用户已取消本套制作与交付】
用户确认：02、03 都取消。禁止继续生图、修图、扩块或发布。以 ../production-scope.json 为准；以下旧指令仅作历史记录。

# 02 小镇日景地图：本轮交付索引

截至 2026-10-08，本任务目录已新增完成 **4 块 4096×4096 候选图块**：`r08_c09`、`r08_c10`、`r09_c09`、`r09_c10`。它们已完成各自清单所列的原生检查及必要修复，`qualifiedComplete4KCandidate=true`；**整张 65536×65536、16×16 共 256 块地图仍未完成**。四块的 `formalAccepted=false`、`clientValidated=false`、`wholeCityComplete=false`，正式美术验收、客户端加载／导航验证和全图相邻接缝验收仍未完成。

`r09_c09` 已完成 16 张原生细节的整块拼接，93 项导出的接缝、边缘、交点及导图过渡检查均有实际观察或精确像素继承证据，见[完整检查记录](r09_c09/qa/root-final-review.json)。当前正继续制作西侧 `r09_c08`，其后续接入使用 `r09_c09/selected` 的完整成图；`r09_c08` 尚未计为完整候选。

## 已选文件

| 图块 | 游戏图块 4096×4096 | 含邻接余量 4326×4326 | 查看用缩略图 1024×1024 | 交付清单与逐图来源索引 |
|---|---|---|---|---|
| `r08_c09` | [core4096.png](r08_c09/selected/core4096.png) | [extended4326.png](r08_c09/selected/extended4326.png) | [preview1024.png](r08_c09/selected/preview1024.png) | [delivery.manifest.json](r08_c09/selected/delivery.manifest.json) |
| `r08_c10` | [core4096.png](r08_c10/selected/core4096.png) | [extended4326.png](r08_c10/selected/extended4326.png) | [preview1024.png](r08_c10/selected/preview1024.png) | [delivery.manifest.json](r08_c10/selected/delivery.manifest.json) |
| `r09_c09` | [core4096.png](r09_c09/selected/core4096.png) | [extended4326.png](r09_c09/selected/extended4326.png) | [preview1024.png](r09_c09/selected/preview1024.png) | [delivery.manifest.json](r09_c09/selected/delivery.manifest.json) |
| `r09_c10` | [core4096.png](r09_c10/selected/core4096.png) | [extended4326.png](r09_c10/selected/extended4326.png) | [preview1024.png](r09_c10/selected/preview1024.png) | [delivery.manifest.json](r09_c10/selected/delivery.manifest.json) |

四个交付清单各含 `sourceChain.nativeSources` 的 16 张原生来源索引，记录 SHA256、逐图生成记录路径、实际提示词／参考图、来源证据，以及后续拼接和修复操作。`r08_c09` 包含一张复用的历史原生细节，其旧来源记录原样保留。清单的 `outputs` 提供所选成品的哈希与尺寸，`qaSummary`、`remaining` 说明实际检查范围和未验证项目。上表十二个所选 PNG 已在编写本索引时重新核对存在性、尺寸与清单哈希。

## 原生尺寸与模型记录

每块由 4×4 张实际生成的 1254×1254 原生细节接续：每张核心 1024×1024、周边余量 115 像素、邻图重叠 230 像素。4096 图块来自中心裁切与所记录的局部修复，区域放大导图仅用于引导构图，不作为最终绘画像素。1024 缩略图仅供查看，不用于游戏正式切块。

本轮使用宿主内置 `image_gen`。配置目标为 `gpt-image-2.5-sunburst`／`max`，2026-10-08 的官方核对证据见 [model-verification-20261008.json](preflight/model-verification-20261008.json)。该目标不等于调用时已锁定型号和画质：内置工具未开放选择器，也未披露可核实的实际返回值，所以逐图记录的实际／提交型号与画质均为 `null`（未确认）。配置快照、实际参数和工具证据分开保存，历史图不会因后续配置核对而改写为新版本。

## 素材清理与追溯

按已确认的素材保留规则，确认成品落盘与当前引用完整后，已删除不再使用的原图、拒稿和加工中间 PNG；保留最终图、仍在使用的邻接参考、必要技术数据，以及逐图模型／质量／提示词／来源文字与 SHA256。历史清单中的文件路径和哈希用于追溯，**不表示被清理的旧 PNG 仍然存在**；旧图的历史检查记录也不等于现在能够重新读取其像素。

- `r08_c09`：[清理记录](r08_c09/cleanup-manifest.json)、[已退役依赖清理记录](r08_c09/retired-dependency-cleanup.json)。
- `r08_c10`：[清理记录](r08_c10/selected/cleanup.manifest.json)、[清理后核验](r08_c10/selected/post-cleanup-verification.json)、[南侧图块完成后的旧依赖清理](r08_c10/retired-south-dependency-cleanup.json)。
- `r09_c09`：[清理记录](r09_c09/selected/cleanup.manifest.json)、[清理后核验](r09_c09/selected/cleanup-verification.json)、[已退役路径记录](r09_c09/selected/retired-source-paths.json)。本次删除 180 张中间 PNG，保留 3 张所选 PNG；120 个原有非 PNG 文件（包括交付、来源和检查记录）的哈希保持不变。
- `r09_c10`：[清理记录](r09_c10/selected/cleanup.manifest.json)、[清理后核验](r09_c10/selected/post-cleanup-verification.json)。

本索引只描述上述四块当前交付候选，不将活动中的 `r09_c08` 或尚未制作的其余图块计为完成。
