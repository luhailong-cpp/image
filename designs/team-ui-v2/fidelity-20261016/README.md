# 组队 UI 原稿还原接续包

此包将当前原生 TeamWindow 改为 `team-ui-v2.png` 的 1931×814 原稿坐标和唯一等比缩放（2560/1931），保留画面、主框、标题、纸张、控件的既有画法；动态名字、等级、职业、在线状态、队伍编号、申请、邀请及操作按钮仍由原生 uGUI/TMP 和真实组队状态驱动。

正式角色头像只读取 CharacterId，或权威职业/性别对应的角色目录；未知身份显示待同步。原稿裁出的五个头像只接受 `preview-team-*` 明确标记，该标记仅由本包的离线截图夹具设置，不通过玩家编号推测身份。

## 安装

`installation-manifest.json` 是逐文件安装清单。安装前重新比较 `source-checkout.json` 的两个客户端源 SHA；发现变化时合并表现层，保留对方更新的组队业务。只能替换 TeamWindow/TeamUiArt，禁止用此包覆盖 Game/Team、TeamFollow 或其他业务文件。

将清单内 16 个文件映射到客户端路径：两个表现脚本、一个编辑器截图脚本及其 meta、六张 PNG 及其 meta。保留现有 TeamWindow/TeamUiArt 的脚本 meta。现有 14 张 TeamV2 切片继续复用。PNG 的 meta 为 Single/FullRect、无压缩、无 mipmap、Clamp，未添加 AssetPostprocessor，也不应触发全项目贴图重导入。

本包未写客户端、未启动 Unity。安装后在稳定 Edit mode 执行 `TeamFidelityVerification.Capture`（菜单 `MMORPG/UI/Team/Capture fidelity pixels and geometry`）。工具使用隔离 PreviewScene，拍摄 2560×1080 与 1920×1080 的五种状态，共十张 PNG，并输出 `qa/fidelity-capture.json` 的矩形、字体、Sprite、按钮和隔离结果。不导入资源、不保存或切换用户场景、不连服务器、不创建 EventSystem。截图须由统一接入者实际执行并检查，不能把离线编译当作截图完成。

## 验证与复建

已通过 .NET SDK 10.0.400 Roslyn 的 450 源文件运行时 overlay 编译和编辑器截图工具编译，零错误、无缺失引用；有现有依赖 netstandard 兼容警告及其他开发工具脚本的引用比较警告，均不来自组队包。`qa/compile-report.json` 与编译日志记录确切结果。

`verify-package.cjs` 比较公开 API/事件、权限、显示/关闭/焦点、状态、补位/开战及其他事务区域，确认与 checkout 源保持一致。此检查不代替在线服务器验证。

需要从保留的正式设计和既有切片复建时，依次运行 `node build-assets.cjs`、`node stage-presentation.cjs`、`node finalize-package.cjs`、`pwsh -NoProfile -File compile-staged.ps1`、`node verify-package.cjs`。PNG 派生记录不声称进行了新 AI 生图；最终 runtime 素材、设计和来源文字保留。
