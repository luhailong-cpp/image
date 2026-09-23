# 20 星阵少女：本窗口证据工具

这些工具仅处理本角色的证据，不生图、不去背景、不插值、不生成占位帧，也不改公共索引。

- [初始库存](initial-inventory.json)：本次制作前 walk 0/128、idle 0/8。目录存在、图片存在和美术验收为不同状态。
- [身份查看图来源](../20-reference/identity-inspection-1024.png.generation.json)：原肖像4096整图等比缩到1024，仅作查看和身份输入，不能计入动作。历史肖像原生1254，4096是历史导出。
- `archive_builtin_result.py`：保存一次真实内置工具成功返回的原图和证据；没有真实返回时不能使用伪回执填充。

## 归档一次成功返回

每次独立重试使用新的 `20-generation/<attempt>/`。真实调用前保存 `prompt.txt` 和 `request.json`。`request.json` 支持本窗口正在使用的 `actual_request`，至少含实际 `prompt`、`referenced_image_paths`、含时区的 `started_at`，并在顶层保存调用启动时的 `configSnapshot`。本内置入口不开放 model/quality，两个提交值必须为 null。提示词文件须与实际提交的 UTF-8 字节一致，包括末尾换行。

工具返回后，将真实返回的 `output_hint` 保存到 `tool-result.json`；可以保留其他返回字段，但不要把目标配置复制为工具实际返回值。`--original` 必须是 output_hint 中真实指出的本地原文件。

历史已发生调用若没有记录开始时间，允许 `started_at: null` 并写 `started_at_basis` 明确未记录；脚本不会从晚于调用的文件时间推测开始。参考路径除本仓库外仅额外允许本机 `.codex/generated_images` 下实际存在的原图，实际请求和SHA照录，不为归档把请求路径伪改成副本。

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' `
  'qdao_original_roster_v14_hd/recovery-20260921/20-tools/archive_builtin_result.py' `
  --attempt 'qdao_original_roster_v14_hd/recovery-20260921/20-generation/idle-S-v1' `
  --tool-result 'qdao_original_roster_v14_hd/recovery-20260921/20-generation/idle-S-v1/tool-result.json' `
  --original '<工具真实返回的绝对PNG路径>' `
  --completed-at '<实际返回时刻，含时区，例如2026-09-21T16:10:00Z>'
```

`--completed-at` 可省略。省略时脚本使用工具明确返回的 `completed_at`，否则使用归档时刻，并写明这不是已知的精确生成时刻。不得填写示例时间冒充事实。

生成文件：

- `raw.png`：原文件原字节复制，校验SHA，保留工具原文件。
- `tool-result.json`：真实工具结果；同名文件已存在时只接受相同SHA。
- `provenance.json`：PNG原生尺寸、SHA及可读取的C2PA元数据；不验证C2PA签名，不据softwareAgent推断已锁定API型号。若解析器不能读某段元数据，保留错误和原图。
- `generation-receipt.json`：真实请求/结果绑定、configSnapshot、参考SHA、原生尺寸、alpha直方图摘要、实际型号/画质可用证据和未确认状态。
- `raw.png.generation.json`：逐图来源记录，目标配置与真实提交参数、真实返回型号/画质分开保存。

脚本兼容当前 `idle-S-v1/request.json`。新请求可补 `reference_bindings_at_start` 来验证参考文件未发生变化；未在启动时保存SHA则明确记录为不可验证，不事后捏造。可补 `reference_roles` 映射记录各参考用途；未补时用途保留在精确prompt中。`source_is_single_frame: true` 只能在调用者确认为单幅完整动作时填写。

归档保存全部候选，包括不合尺寸或透明要求的失败稿，不把归档成功当作可用动作。`native_canvas_min_1024` 仅是整幅尺寸检查；独立单帧、alpha残边、身份、步态、脚底锚点和30ms动态循环仍须后续实看。脚本始终保持 `visual_review: pending`、`canPublish: false`，没有Unity或正式客户端通过声明。
