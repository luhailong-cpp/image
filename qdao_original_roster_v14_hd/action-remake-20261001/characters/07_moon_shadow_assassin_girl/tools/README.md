# 月影少女私有预览与结构检查

运行位置不受限；默认从脚本上级角色目录读取 `manifest.json`。只读图片，输出仅写入本角色 `preview/`。不修改图像、不做缩放/贴地、不生成占位图，不访问其他角色，不操作 Git。

```powershell
python tools/build_preview.py
python tools/verify_manifest.py --report
python tools/verify_manifest.py --require-complete --report
```

当前电脑的 `python` 为 Windows 商店占位。实际可用运行时：`C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。在 PowerShell 用 `& '此绝对路径' -B '脚本绝对路径'` 调用；运行时自带 Pillow，可完整解码及检查非全透明/非全不透明。

用浏览器直接打开 `preview/index.html` 即可离线使用。无需服务器；清单改动后重新运行生成器。正常速度、¼ 慢速、前后逐帧、滑块、联系表、四种透明检查背景及虚拟根锚点开关均可使用。键盘左右箭头逐帧，空格播放/暂停。不完整组按现有帧播放并明确标注数量，不证明完整循环通过。

## manifest v1 约定

清单只有真实存在的帧；index 从 **0** 起始。每个帧对象：

```json
{
  "id": "run_E_00",
  "action": "run",
  "direction": "E",
  "index": 0,
  "path": "frames/run/E/00.png",
  "nativePath": "native/run/E/00.png",
  "sha256": "文件真实SHA256",
  "nativeSha256": "原生文件真实SHA256",
  "durationMs": 30,
  "status": "exported",
  "visualApproved": false,
  "sourceRecord": "provenance/run_E_00.json",
  "events": []
}
```

以上仅为文档字段示例，不是资源清单。原生图即为 1024 RGBA 正式帧时，`nativePath` 与 `path` 可引用同一最终文件，无需重复保留原图。原生来源文字仍保留。研究小格不得放大后冒充原生高清单帧。`events` 可用 `contact`、`release` 等标记实际命中/释放帧。

顶层字段为 `schemaVersion: 1`、`characterId`、`canvas: {"width":1024,"height":1024,"mode":"RGBA"}`、`frames: []` 和：

```json
{
  "registration": {
    "method": "shared_camera_root",
    "globalScale": 1,
    "rootAnchor": [512, 850],
    "perFrameBboxScaling": false,
    "lowestPixelGrounding": false
  }
}
```

锚点示例须由真实成图统一确认。不能为了通过检查虚构锚点，或仅凭声明认为美术通过。腾空、蹬地和重心起伏保留在固定画布中。

帧节奏：run 30 ms（16 帧），hit 40 ms（6 帧），attack 30 ms（12 帧），cast 45 ms（16 帧）。run 八方向，其余 E/W。合计 196 帧。

## 检查边界

检查实际 PNG 头中的尺寸/RGBA、文件 SHA256、逐图来源路径存在、组数量、重复槽位和完全重复内容，核对统一注册声明及已记录的逐帧 transform.scale。有 Pillow 时额外完整解码和检查 Alpha 范围。默认允许尚未制作槽位，以警告列出；`--require-complete` 将未满 196 帧、未视觉通过或未正式导出判为错误。退出码 0 表示所启用结构检查通过，1 为结构错误，2 为清单不可读。

检查器不能从元数据证明独立绘制、左右手正确、透明边缘、角色身份或连续性；缺少 Pillow 时会明确警告未完整解码。必须配合逐帧目检与来源记录。预览不会自动将任何帧改为视觉通过或客户端已接入。
