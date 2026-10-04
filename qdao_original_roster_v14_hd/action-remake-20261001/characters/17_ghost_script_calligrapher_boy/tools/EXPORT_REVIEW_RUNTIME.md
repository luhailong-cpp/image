# 17 私有整画布导出工具

现在仅准备工具；尚未导出本角色 runtime，也未删除任何素材。主代理完成合审后再运行。

在本角色目录使用 Python（需要 Pillow）：

    python tools/export_review_runtime.py --check
    python tools/export_review_runtime.py --export

不带参数与 --check 相同，只读校验。--export 才生成 runtime/{action}/{DIR}/{NN}.png、对应 .png.generation.json 与根目录 manifest.json。已有 runtime/ 或 manifest.json 时拒绝覆盖。

- 只使用 preview/manifest-preview.json 的 selected；不寻找最新版本，不重新选图。要求八向跑步各 16、E/W 受击各 6、普攻各 12、施法各 16，共 196 槽，身份字段和时长一致。
- 先核验所有源 PNG 的 SHA、原始 generation 记录 SHA 和尺寸；要求原生方形、至少 1024、PNG RGBA、有透明像素，四条最外边线上 alpha > 128 的像素必须为 0。沿用本角色现有边缘诊断阈值。任一失败立即退出，不发布部分 runtime。
- 全画布按同一映射规则用 LANCZOS 缩到 1024×1024；原本 1024 则不缩放。不裁切、不按包围盒适配、不平移贴地、不清 alpha、不修改姿态。技术缩放不代表彩边或美术通过。
- 全部输出先写私有临时目录，并再次核验源图/预览/验收记录未改变；完整包准备好后才发布。普通校验/写入失败不发布残缺包。文件系统不提供跨 runtime 目录和 manifest 文件的单次原子提交；进程被强杀/断电时需人工检查两者完整性后重试。
- run 每帧 75ms、全圈 1200ms；hit 40ms；attack 30ms、第 06 帧 hit_contact；cast 45ms、第 10 帧 cast_release。事件帧是接入标记，不冒充客户端已验证事件。
- manifest 和逐图导出记录完整嵌入原 generation JSON、可读取的原请求/提示文本及 SHA，分开保留 configSnapshot、submittedParameters、actualModel、actualQuality。宿主未披露实际值继续为 null，不用配置目标填补。历史生成路径原样保存，源图片不必仍在旧电脑缓存中。
- 永远保留 clientNotIntegrated: true、clientIntegration: not_integrated、clientRuntimeAcceptance: not_tested。本工具不改主预览生成器、STATUS、动画原图或旧角色目录，不删除源图/拒稿。

## 私有 acceptance.json

不存在时 status 为 candidate。存在时支持 candidate、needs_review、rejected、passed；后面三种非 passed 状态不会算成视觉/动态通过。只有整套通过才使用：

    {
      "character": "17_ghost_script_calligrapher_boy",
      "status": "passed",
      "previewManifestSha256": "填写 --check 返回的当前预览文件 SHA256",
      "visualApproval": "passed",
      "dynamicApproval": "passed",
      "reviewedAt": "填写实际审查时间",
      "notes": "填写实际正常、慢放、逐帧审查结论"
    }

passed 必须绑定当前预览 SHA，且同时有明确视觉、动态通过及审查时间，否则失败。预览重建或选图变化后须重新审查并绑定，不会自动承袭旧通过结论。不要把此示例直接当成已验收记录。

## 工具验证

    python tools/test_export_review_runtime.py

仅使用 tools 内临时合成 PNG 测试 196 槽、缺槽、原 generation SHA 错误、边缘阈值和验收绑定；不调用 export()，不导出真实角色素材。

