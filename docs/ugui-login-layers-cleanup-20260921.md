# 2026-09-21：清理旧选服整页分层目录

用户要求以当前 Unity UGUI 客户端为准，清理没有对应画面的旧素材，不再为 FairyGUI 或旧制作工具保留资源。

已删除 `q_daoist_login_ui_uncropped_highres_final_layers/`，共 13 个文件、104,864,092 字节（100.01 MiB）：6 张 5120/10240 像素整页 PNG、3 份 SVG 布局、1 个已禁用的历史构建脚本、2 份 JSON 清单和 1 份说明。

## 核查依据

- 客户端源码、编辑器工具、配置和现行导入脚本没有直接读取此目录。
- `QdaoServerSelectView.cs:392` 的 `BuildVisualTree` 调用 `BuildRefreshVisualTree`；`QdaoServerSelectView.Visuals.cs` 使用 RefreshV8 登录背景及独立 UGUI 控件。
- 旧 `screen_art_headband` 兼容入口指向客户端自己的 `Assets/Resources/UI/Ugui/Native/screen_art_headband.png`，同步源为 `qdao_ui_redesign_v5/02_server_select_2560x1080.png`。实际查看确认这张客户端兼容图与已删旧组合图设计不同。
- 对照客户端 UI Resources 和 Editor/ReferenceArt 中 38 张宽屏候选 PNG，六张旧图无 SHA-256 相同文件；统一灰底缩略图最近匹配平均通道差为 25.84–43.09/255，没有发现同画面缩放副本。候选筛选为宽高比 1.7–3.1，适用于本批完整宽屏画布，不是对任意裁剪/局部切片的等价证明。
- 删除前重新核对 13 个源文件和 38 个客户端图片的 SHA-256；所有删除路径解析后均位于指定目录。逐文件删除，再移除空目录，无递归删除。

未修改客户端，未启动 Unity，未提交 Git。旧美术组合和恢复脚本可能仍引用这些已弃用分层；这些历史流程不作为本次保留理由。

[逐文件路径、哈希、清理前提交与比对记录](ugui-login-layers-cleanup-20260921.json)可用于按单文件恢复；不要恢复整个工作区覆盖其他并行改动。
