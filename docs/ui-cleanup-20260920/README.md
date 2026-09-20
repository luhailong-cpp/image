# UI 暂存去重记录（2026-09-20）

本轮删除 **57 个同字节暂存副本，144,624,305 字节，约 137.92 MiB**：31 张 PNG、26 个 SVG。两个正式 UI 目录的所有图片、SVG、清单和脚本保留；仅更新说明文档。没有重新生图、覆盖正式美术、修改客户端、重写 Git 历史或 push。

逐文件路径、大小、SHA-256 与恢复来源见 [cleanup.json](cleanup.json)，实际恢复和校验见 [verification.json](verification.json)。容量为工作区文件逻辑体积；删除并提交不会缩减 Git 历史体积。

| 删除位置 | 数量 | 保留来源 |
|---|---:|---|
| v10 staged 下的原子控件目录 | 46（23 PNG + 23 SVG） | 原子控件正式原路径 |
| v10 staged 下的高清分层目录 | 5（2 PNG + 3 SVG） | 高清分层正式原路径 |
| 节庆 server/staged 下的高清分层目录 | 6 PNG | 高清分层正式原路径 |

## 高清分层目录为什么保留

对 `E:/work/mmorpg-client` 的 Assets、Docs、Packages、ProjectSettings 下代码、Unity 文本资源、清单及 meta 文件进行了路径/名称检索；没有发现高清目录、uncropped 文件名或物件图集的直接引用，也没有找到对应客户端文件名。当前选服代码 `QdaoRefreshArt.cs:9` 使用 `UI/Ugui/RefreshV8/`，`QdaoServerSelectView.cs:732,768` 读取独立页签和卡片控件。这是静态检查，不声称运行了 Unity 或排除了所有间接、动态、二进制依赖。

**不直接整目录删除。** 素材仓库当前节庆发布器对 `native_q5/base.svg`、`controls.svg`、`labels.svg` 的正式路径执行来源哈希保护；分层清单和 `verify_delivery_contracts.py` 仍核验正式 PNG。六张高清 PNG 不是独立原生 10K 生图，但仍属于兼容交付合同。保留正式路径，删除已经发布的暂存副本，可避免让构建、校验和说明悬空。

当前选服来源是 `qdao_festival_refinement_20260910/scenes-sync/server/compose_server.mjs` 与该目录 `plan.json` 的冻结输入。不要运行旧 v10 全量 publish 来恢复当前选服图；其中四张 background/recomposed 暂存图与现行图不同。

## 图集与其他保留项

- 原子目录全部 148 张 PNG（含 124 张物件图标及正式图集）保留；兼容别名、徽标母图和布局 SVG 保留。
- 54.65 MiB 的 `qstyle_fairygui_atlas_600.png` 在隔离目录按 JSON/XML 的 124 个帧重建。尺寸 7912×6088，RGBA 像素与 SHA-256 均完全一致：`99d14084574811d3fc14fba6221321c882dbc3df226e0bdbf6e49c05e4480484`。它仍是物件包清单声明的正式 FairyGUI 输出，因此本轮不把“可以重建”当成“已经废弃”。
- 四张内容不同的 v10 高清暂存图、所有 JSON 清单、server/before 回滚备份、current-inputs 冻结输入和必要脚本保留。回滚备份仍被当前校验/重建读取，不能仅凭其中两张与现行按钮层一致就删除。
- `exact_qdao_slices`、主城、角色资源及客户端文件没有改动。

## 去重后的读取与恢复

`validate_staged.py` 和 `publish_staged.py` 的暂存读取支持清单内的缺失副本：只在正式来源仍匹配清理时 SHA-256 时读取它；写入目标仍然是原 staged 路径。正式来源变化时拒绝回退，必须重新构建并审查；已有的新暂存文件不会被旧清单替换。历史报告不改成当前发布证明。

以下命令均从素材仓库根目录运行，不触碰客户端：

```powershell
# 默认只验证恢复来源，不创建副本。
python qdao_ui_style_recut_v10/tools/staged_copies.py

# 需要磁盘实体供外部工具使用时，恢复缺失的 57 份副本；拒绝覆盖不同文件。
python qdao_ui_style_recut_v10/tools/staged_copies.py --restore

# 隔离恢复，保留完整仓库相对路径。
python qdao_ui_style_recut_v10/tools/staged_copies.py --restore --output-dir .work/ui-copy-check

# 保持历史验收报告不变，另写本次机械检查结果。
New-Item -ItemType Directory -Force qdao_ui_style_recut_v10/.work | Out-Null
python qdao_ui_style_recut_v10/tools/validate_staged.py --output qdao_ui_style_recut_v10/.work/validation.json
```

恢复与显式构建可按需产生本地副本；57 条精确 `.gitignore` 规则防止再次提交它们，不屏蔽新的正式资源。普通验证不会重建被清理的副本。源文件版本日后变化，若仍需旧副本，应从清理前的 Git 提交恢复相应精确版本并重新审查，不绕过哈希保护。

## 已执行核验

1. 删除前重新计算 57 对哈希，在隔离目录实际恢复全部文件并再次核对 SHA-256。
2. 独立重建 124 帧图集，验证 XML/JSON 几何、完整 RGBA 与编码字节。
3. 删除前后 v10 全量检查结果完全相同：158 项输出，155 项换皮、3 项允许不变，143 条清单记录、112 对 PNG/SVG，错误 0。
4. 删除后逐一验证 57 个只读恢复来源、51 个 v10 发布载荷、当前选服六个正式输出及六个回滚备份、六项冻结输入；194 个正式文件在文档更新前哈希不变。
5. 用隔离模拟文件验证：来源被改、越界路径、非法清单路径、恢复目标已有不同内容均拒绝处理；不覆盖现有文件。没有运行会写历史报告的旧 `build_atlas.py --check` 或发布器。

本次提交只包含精确列出的清理项、读取/恢复支持和说明；不包含并行窗口的主城或角色工作。

执行期间后台小时快照 `a3558242` 已自动提交并行主城工作、原交接文档及恢复脚本的初始单行占位文件。本轮保留该既有提交，不重写它；后续专门清理提交只暂存本任务精确路径。
