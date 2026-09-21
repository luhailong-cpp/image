# 单城原生续作工具

`city_native_resume.py` 不调用生图、不修改旧来源、原 plan、旧 assembler、共享 catalog/status 或客户端。所有新增输出位于本目录的 `sessions/{appearance}/{tile}/`。历史 `E:/work/image` 只在读取时解析到当前仓库；旧 JSON 字节不改。

```powershell
$CityPython = 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$ResumeTool = 'D:\luyuan\wuxingqitan\image\qdao_city_tiles_4k_20260916\builtin_q64_production\resume_single_city_20260921\tools\city_native_resume.py'
$TileDir = 'D:\luyuan\wuxingqitan\image\qdao_city_tiles_4k_20260916\builtin_q64_production\tianyong_festival\r09_c09'
& $CityPython $ResumeTool inventory --tile-dir $TileDir
& $CityPython $ResumeTool import-request --tile-dir $TileDir --id r03_c03 --request-file '<实际 request/response JSON>'
& $CityPython $ResumeTool metadata --tile-dir $TileDir
& $CityPython $ResumeTool assemble --tile-dir $TileDir
& $CityPython $ResumeTool check --tile-dir $TileDir
```

`import-request` 读取 `request.prompt`、`request.referenced_image_paths` 和 `response.output_hint`。提示词按实际提交文本保存，原图按原始字节复制，实际尺寸通过 PNG 解码获取。也可手动登记：

```powershell
& $CityPython $ResumeTool register --tile-dir $TileDir --id r03_c03 --source '<原生 PNG>' --prompt-file '<实际提示词>' --reference '<第一个实际参考图>' --receipt-file '<实际工具回执 JSON>'
```

多参考图重复 `--reference`。登记不允许覆盖已存在版本，可将原生版本名设为 `r03_c03.v2`；若同一坐标有多个本会话版本，工具拒绝自动选优，必须在继续组装前明确选择规则。1254² 之外的原生输出仍按真实尺寸登记，但此旧 4×4 组装器会拒绝接收。

机械组装使用历史 assembler 的算法，原生 4×4、core 1024、halo 115、overlap 230；生成 `output_resume_20260921/` 与 `qa_resume_20260921/`。只复制 plan 并使用新记录自己的 `promptFile`，不会假称新图用了历史提示词。组装记录继续引用旧脚本 SHA；额外 `adapter-record.json` 绑定本适配器、原 plan、旧 assembler 和新 assembly 的 SHA。

旧机器的 `sourceOutputPath` 若不可访问，仅确认保存的 native 同时匹配历史 `outputSha256` 与 `sourceOutputSha256`，明确记录 `originalGeneratorOutputAvailable=false`。不伪造旧生成缓存仍存在。

PNG `caBX` 等元数据中的软件声明仅记录原始可读字符串与字节偏移，不做 C2PA 验签。`actualModel/actualQuality` 保持 null，`backendModelVerified=false`；配置目标、提示词、未验签的软件声明都不等于实际后端型号证据。

工具的机械检查通过只说明文件、来源和拼合完整性。视觉、内部接缝、外部接缝、四块交点、导航、最近镜头和实机验收均须另外检查，不提升正式状态。
