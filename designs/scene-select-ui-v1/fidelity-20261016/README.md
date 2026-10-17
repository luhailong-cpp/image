# 线路选择原稿还原包

当前客户端 `SceneChannelWindow` 使用 GameplayV1 通用窗、两列十六项，和已确认 `scene-select.png` 的三列八行画面不同。本包恢复原稿 1931×814 坐标及唯一等比缩放 2560/1931，保留标题、背景、框体和同源按钮画法。线路名称、负载、当前标记与状态由真实目录绘制；未收到的线路保持空白，每页最多二十四条，超过二十四条继续分页。

点击线路仍按原来的规则即时申请切线。原稿绿色“确认”所在按钮承接真实“刷新”功能，取消和右上关闭承接原关闭功能；没有新增演示确认流程。原协议、scene_id、负载状态、容量判定、队员/队长限制、冷却、切线在途及点击前二次校验保持原样。

## 安装与核验

`installation-manifest.json` 列出十三个安装文件及 SHA：一个表现脚本、一个隔离截图脚本和 meta、五个最终 PNG 和 meta。安装前重新核对 `source-checkout.json`，源变化时合并表现层。保留已有运行时脚本 meta，不覆盖数据层和原有验证器，不添加 AssetPostprocessor。

在稳定 Edit mode 执行 `SceneChannelFidelityVerification.Capture`。独立 PreviewScene 不切换或保存用户场景、不创建账号/连接、没有网络请求；真实原生窗口会按多线、切换中、冷却、失败、空目录、单线、队员限制和二十八条分页夹具截图，输出两种分辨率和逐图几何/字体/按钮记录。夹具仅离线截图使用。旧验证器“二十条分两页”的假设已不适合二十四条容量，本工具用二十八条验证分页。

`verify-packages.cjs` 检查安装源 SHA、保留的逻辑区域，并逐像素证明动态替换掩模外仍是原稿原像素。离线编译不等于已截图或在线切线成功；本包未写客户端、未启动 Unity。

## 图像来源

内置 imagegen 只清理原稿动态示例文字；实际返回 1932×814。最终资源局部复合回原稿，画布 1931×814 不冒称 AI 原生尺寸。五个 PNG 各有 `.generation.json`，追溯到 `source/host-edit.json`、实际提示词、输入 SHA、输出 SHA 和原稿。配置目标为 Images 2.5/Sunburst/max；工具没有型号/质量选择器，实际型号和质量均未确认，未调用付费 API。

重建：运行 `build-stage.cjs`、`build-verification.cjs`、`compile-staged.ps1`、`verify-packages.cjs`。主包源及过程工具只在两个 fidelity 目录写入。
