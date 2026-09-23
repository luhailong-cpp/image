# 09 最终离线包工具

`finalize_package.py` 只接受 `09-delivery-preview/revisions` 中的完整快照，并要求另行提供绑定该快照 manifest SHA256 的明确验收事实。它不生成验收事实，也不删除图片。

运行方式：

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B 'qdao_original_roster_v14_hd/recovery-20260921/09-tools/finalize_package.py' --snapshot '<完整快照路径>' --acceptance '<本角色验收JSON路径>' --check-only
```

检查通过且需要正式打包时去掉 `--check-only`。输出固定为 `09-delivery-preview/final`；已存在时拒绝覆盖。中途失败只留下明确命名的 `final-staging-*` 目录，不会把未完成包改名为 final。

验收 JSON 必需字段：

- `character`：`09_bamboo_archer_girl`。
- `status`：实际完成全部离线验收后才可记录 `passed`。
- `reviewedManifestSha256`：这一次被实际审阅的快照 `manifest.json` 的 SHA256；素材换版后必须重新审阅并绑定新快照。
- `reviewer`、`reviewedAt`：真实审阅者与带时区的时间。
- `directions`：必须恰好包含 N、NE、E、SE、S、SW、W、NW。
- 每方向必需 `status`、`walkCount:16`、`idleCount:1`；`checks` 中以下每项均须有独立审阅支持的 `passed`：`gait`、`supportFoot`、`anchor`、`proportions`、`equipment`、`alpha`、`seam15_16_01_02`、`dark`、`light`、`normalSize`、`enlarged`、`browserPlayback`。
- `clientIntegration`：`not_performed`。本工具只打包离线资源，不能认证客户端接入。

未通过、缺项、旧 SHA、缺少站立、未完整覆盖八方向都会拒绝；文件数量完整不能替代视觉验收。N 已进入靴后跟返工，旧 N 的审查疑点不能自动转写为新版已通过。

正式包包含：

- `runtime/`：精确 128 张行走和 8 张独立站立透明 PNG，逐张 sidecar 保留原字节。
- `sources/`：历史加工记录原字节，加 `index.json` 提供每张图到包内 generation 证据的相对路径与实际型号／质量（未知仍为 null）。
- `preview/`、`index.html`：深浅底八方向 30ms GIF、联系表、首尾图、站立概览；播放脚本沿用已审阅快照，仅替换包内 metadata 和验收状态文案。
- `acceptance.json`：输入验收记录原字节。旧来源记录的 pending/canPublish 是历史出口状态，不伪改；当前验收单独链接。
- `evidence/`：全部 09-generation 中的文字请求、结果、提示词、生成记录；同时保留 work、revisions 及诊断目录的历史文字。图片不复制入 evidence。`evidence/index.json` 将历史绝对路径映射到本包文字路径。
- `retention.json`：明确源原图在打包时仍存在、计划于收尾删除，工具本身并未删除。历史图路径不是原图永久可读承诺。
- `cleanup-plan.json`：逐文件精确路径、SHA、尺寸与理由，仅提出删除计划。
- `package-checksums.json`：包内文件校验，排除它自身。

清理计划仅覆盖本机项目内的 09-generation 图片、09-delivery-preview/work 与 revisions 副本，以及 09 诊断派生图。外部原肖像、designs 正式样板、其他角色、宿主 generated_images 缓存、工具和 generation 文字证据不在删除范围。清理前必须确认没有进行中的生成仍引用待删图，重新核验包内引用、每个目标路径和 SHA，再另记实际删除结果；本工具没有删除参数。

已验证：命令帮助；缺 136 张快照的拒绝；pending、缺支撑脚检查、缺方向、缺站立、旧 manifest SHA、冒充客户端已接入的六种拒绝；当前文字与清理范围只读枚举。未执行正式打包，因为最终新版素材和验收记录尚未就绪。
