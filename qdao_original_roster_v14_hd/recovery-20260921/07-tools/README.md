# 07 月影少女专用归档、导出与预览

本目录仅服务 `07_moon_shadow_assassin_girl`。`candidate` 和所有预览均为待审候选；库存、哈希不同、16 帧 GIF 均不能证明步态合格。没有接入客户端、没有正式美术批准。

Python：`C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`。从 image 仓库根目录运行，脚本路径为 `qdao_original_roster_v14_hd/recovery-20260921/07-tools/movement_assets.py`。

最短命令（`$py` 指上述 Python，`$tool` 指脚本）：

```powershell
& $py -B $tool ingest --attempt idle-S-v2 --select
& $py -B $tool ingest --attempt walk-NW-09-v4 --select --replace
& $py -B $tool build-preview --revision review-001
```

`ingest` 读取 `07-generation/<attempt>/request.json` 和 `result.json`，要求 result 指向真实内置工具原始返回文件。原文件按字节复制、原尺寸测量、SHA-256 计算；不会把配置目标写成实际模型。实际型号和质量未披露时保持 null。遇到旧候选，只有显式 `--replace` 才替换，并保留旧文件与 sidecar 于 `selection-history`。新的 export 算法复验可使用 `--revision <name>`，旧归档和旧导出不覆盖。

可选诊断尺度校准：`export --attempt walk-SE-01-v2 --revision head-calibrated-v1 --head-reference idle-SE-v5 --replace`。以同方向独立 idle 的头部轮廓带宽为目标，对每张真实完整单帧整体等比缩小，所有变换系数、参考原图 SHA 和量测定义写入 sidecar；限制从 native 的缩放系数≤1，禁止原始画面放大。此项不改变默认导出规则，不改变肢体/头身比例，不会把同姿势生成多个槽。头宽校准只能减轻全画布留白波动，不能修复镜头、躯干或步态错误。

完整接口通过 `--help`、`prepare --help`、`archive --help`、`export --help` 查看。`prepare` 保存精确提示词、请求、参考图哈希及当时配置快照；调用者在生图前记录真实 startedAt，再以 `archive` 保存原始 tool result 或 error。`ingest` 兼容本批已有 attempt 记录。

处理规则：原始透明 RGBA 优先；不做色键，不改真实 RGB。仅删除 alpha≤8 且远离有效轮廓的零散点，以及透明边缘 3px 内 alpha≤8 的极低透明度极饱和杂色；alpha>8 与所有原始 RGB 均保留到统一缩放前。全画布等比缩至最大边 1024，统一系数 1.0；不用逐帧包围盒缩放，不改变肢体。按上部角色轴整数平移至 x=512、有效最低点 y=942。会越界的原图拒绝导出，需要重新生成留白，禁止裁切补救。

每个预览 revision 保留 runtime 字节副本、逐帧来源 sidecar、manifest、结构报告、深浅底联系表、15/16/01/02 接缝放大图。某方向满 16 帧时才生成 16×30ms=480ms GIF，保存后重新读取逐帧时长验证；缺槽只显示 MISSING，不拿别图补。HTML 支持 8 向、独立站立、深浅底、原速/慢速、逐帧、1x/2x。浏览器实际播放与逐帧美术审阅仍须另记证据。

初轮问题：NW 诊断循环存在相位重复、半圈身形/尺寸差及 16→01 接缝跳变；SE 01/09 的相反接触腿势经过09-v4修正，随后11/12等反相失败槽也已重绘，但整体步态、角度及身形仍需审阅。最新逐槽选用与拒稿见 `NW_SE_HANDOFF.md`。候选不能据张数宣布合格，所有原始失败/拒选尝试继续保留。

`verify_candidates.py --out <fresh.json>` 只读验证当前候选的原图/导出SHA、透明清理前后所有RGB和alpha>8不变，并给出头部尺度量测。结构通过不等于美术通过。
