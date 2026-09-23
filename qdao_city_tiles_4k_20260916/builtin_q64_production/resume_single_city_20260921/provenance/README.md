# 本次会话逐图来源补充审计

本目录只补充 `resume_single_city_20260921` 内新增的原生生成图、AI 修补图及生成的风格参考图。原始 record、receipt、图片、客户端文件及会话根 README 不改写。组装、裁切和预览沿用原组装记录，不冒充新生图。

运行命令（工作目录为 image 仓库）：

```powershell
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'qdao_city_tiles_4k_20260916\builtin_q64_production\resume_single_city_20260921\provenance\audit_native_sources.py'
```

每次运行生成新的 `index-<UTC时间>.json` 和 `.md`。按文件名排序取最新索引。`records/` 的逐图 `.generation.json`、`evidence/` 的来源字节副本均按内容 SHA 命名，已有文件不覆盖；重复执行没有新证据时只增加索引。新增图或新增证据会产生新的旁证记录，旧旁证保留。

每条记录包含原生 PNG SHA、实际尺寸、原输出与保留副本、原始记录／回执／提示词的 SHA 和不可变副本、实际输入路径与 SHA。参考图 SHA 逐一与已有记录核对；若只有当前观察值而没有当时登记值，单独标明。发现缺文件、SHA 不一致或并发写入会列入缺项，不标通过。

`configSnapshot` 优先取该图已有独立 generation record 保存的当次目标；旧图没有独立快照时取会话保留的 `history/image-generation.before-20260921.json`，表示会话负责人确认的生成前批次目标。逐条记录快照来源及含义，不从当前可变配置回填，也不表示实际参数锁定。宿主管理入口没有型号、质量选择器，因此 `submittedParameters.model/quality`、`actualModel/actualQuality` 均为 `null`。保留 PNG 中可读的软件字符串作为未验签观察，不将其等同后端型号。

工具回执没有可核实的生成时间，因此 `generatedAt=null`。已有 `createdAtUtc` 单独保存为 `recordSavedAt`，含义是本地登记或组装记录保存时间；它不是生成完成时间。

外边修补的新结构可由 `repair.json.generationRecord` 指向图旁独立记录，兼容缺少 `createdAtUtc` 和 `files` 的组装记录。独立记录中的原图、提示词、参考图 SHA 会核对并留不可变旁证。回执 `completedAtUtc` 单独记录为 `observedCompletionAt`，仅表示宿主收到工具结果的观察时间。即使旧图旁记录把此值写入 `generatedAt`，补录也不会把它当作确切服务器生成时间，原记录保持不动。

首次审计覆盖 31 张原生输出：23 张细节（r09_c09 新补 6 张，r09_c10 共 17 张含重试）、1 张生成风格参考、7 张 AI 修补。13 张有完整 request/response JSON；18 张 r09_c10 细节／参考仅有工具响应、已有 toolCall、实际提示词文件及输入 SHA，缺少完整请求 JSON，逐条如实标明。所有图实际型号／质量与确切生成时间均未确认。可重跑纳入之后新增修补。

本目录不提供美术通过、布局语义通过、导航通过或正式交付声明。
