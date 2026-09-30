# 战斗动作离线检查与预览

仅使用 Python 标准库。脚本只读取现有 PNG 与来源 JSON，输出清单和 HTML，不生成、编辑、镜像或插值图片。

在项目根目录运行 00 样板检查：

```powershell
python qdao_original_roster_v14_hd/combat-20260929/tools/audit_combat.py --characters 00
```

检查全部当前保留角色：

```powershell
python qdao_original_roster_v14_hd/combat-20260929/tools/audit_combat.py --all-retained
```

角色范围读取 V14 根目录 `CONTINUATION_STATE_20260920_SCOPE_UPDATED.json` 的 `active_character_ids`，当前是 **15 个保留角色**：00–10、14、15、17、20；不是仅已完成行走的 00–03。`--characters 00` 只是命令行便利别名，解析为完整目录 ID `00_reference_topright_boy`。也可直接传完整 ID，路径与 manifest 均保留完整 ID，绝不重排或缩短角色目录。`--all-retained` 按权威范围检查全部 15 个角色，预期 **1020 帧**；单角色预期 **68 帧**。不在 active 范围的角色会直接报错。

默认输出 `tools/report/manifest.json` 与 `tools/report/index.html`；双击 HTML 即可离线预览。支持角色、动作、方向切换，播放一次后停末帧，逐帧及滑条检查，深／浅棋盘背景。受击 6 帧／240ms，普攻 12 帧／360ms，施法 16 帧／720ms，均为每方向 E、W。

`--root <目录>` 指定另一批根目录；`--scope-state <文件>` 可显式指定权威角色范围 JSON，默认读取批目录上一级 V14 根目录的上述文件；`--out <目录>` 指定输出目录。存在缺失或技术问题时仍会输出完整报告，退出码为 **2**；全部技术检查通过退出码为 **0**。制作期间需要单纯刷新预览可加 `--allow-incomplete`（只改变退出码，不改变清单检查结果或状态）。

## 输入

逐帧路径固定为 `characters/<完整角色ID>/runtime/<hit|attack|cast>/<E|W>/<01起两位序号>.png`，例如 `characters/00_reference_topright_boy/runtime/hit/E/01.png`。每帧应为 1024×1024 的带 alpha 通道 PNG。

逐角色递归读取 `characters/<完整角色ID>/provenance/receipts/**/*.json`。每个独立记录采用项目 IMAGE_MODEL_POLICY 的字段：`file`、`sha256`、`generatedAt`、`tool`、`route`、`configSnapshot`、`submittedParameters`、`actualModel`、`actualQuality`、`evidence`、`prompt`、`references`。`file` 可使用相对本批根目录的 `characters/<完整角色ID>/runtime/...`，或相对该角色目录的 `runtime/...`；两者都会映射至完整角色路径。型号或质量未知应为 `null`，且写明 `unverifiedReason`。配置目标与实际型号不会互相填充。

也支持在 `assets`、`outputs`、`frames`、`images`、`records` 数组中放独立记录，以及 `asset_path`／`output_path` 路径别名。历史重试可以有多个收据；脚本选择与当前 PNG SHA256 相符的记录。派生帧记录必须有 `derivedFrom` 与 `operation`；该工具不会把派生图称作新生成图。

## 证据范围

- 验证帧数／路径、PNG CRC、尺寸、alpha 通道、真实透明像素、可见内容与可见包围盒、PNG SHA256、逐图收据对应及核心字段。
- 解码不交错 8-bit PNG，比较完整 RGBA 像素哈希，并消除完全透明像素中隐藏 RGB 的差异，以发现换元数据或透明区噪声掩盖的完全重复帧。其他编码会明确报 `png_audit_error`，不会默认通过。
- 不判断语义姿态是否独立、左右是否偷用镜像、持武器正确性、身份和服装一致性、实际原生生成分辨率或动作观感。来源链与美术细节仍需人工验收。
- `status` 永远是 `offline_pending`，`visual_approval` 为 `pending`，`client_integration` 为 `not_integrated`，`runtime_acceptance` 为 `not_tested`。技术检查通过不代表客户端接入、运行验收或正式交付。
