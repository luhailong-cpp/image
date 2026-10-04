# 00 角色预览与技术检查

本工具只读取本角色 `frames/`，仅写本角色 `review/technical_report.json` 和 `review/index.html`。不生成或改动 PNG，不裁切、缩放、镜像、插值或对齐帧，不修改共享文件。

运行（PowerShell；无需安装包）：

```powershell
& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy/tools/review_frames.py' all --allow-incomplete
```

正式帧路径为 `frames/{action}/{direction}/{01..}.png`。工具枚举跑步八方向 × 16，以及 E/W 受击 × 6、普攻 × 12、施法 × 16，共 196 槽。没有图片的槽位仅显示文字；不会生成占位 PNG。

可将逐帧来源索引作为 `--sources '完整路径.json'` 传入。无参数时来源状态为未确认。示例结构（值须填真实证据）：

```json
{
  "frames": {
    "run/E/01.png": {
      "source_path": "本角色目录的相对路径或源图绝对路径",
      "source_kind": "single_frame",
      "source_sha256": "真实源图的64位SHA256",
      "native_frame_size": [1024, 1024],
      "evidence_path": "真实生成或复用文字证据的路径"
    }
  }
}
```

图集来源使用 `source_kind: "sheet"`，并提供真实 `native_frame_rect: [x, y, width, height]`。工具读取源文件，并以该裁切区域判断单帧原生尺寸；不能把整张图集尺寸当作单帧尺寸。来源记录中的相对路径以本角色目录为基准，`--sources` 参数本身的相对路径以命令当前目录为基准。

源图按素材保留规则删除后，若保留了 `native_frame_size`、有效 SHA 和实际存在的 `evidence_path`，会标记 `documented_only`，不会冒充本次实测。源文件存在且尺寸与来源信息通过检查才标记 `measured_pass`。未读到或不完整的证据标记 `unconfirmed`。

文件检查包含实际 1024×1024、PNG 格式、RGBA、非全透明、非完全不透明、SHA-256、解码后的 RGBA 像素重复。它不声称能自动判断手脚、身份、左右持物、姿态独立性、锚点或首尾衔接。SHA 不同也不等于美术通过。完全不透明会作为问题列出，供核实背景透明度。

打开 `review/index.html` 可选择动作、方向、正常速度、¼ 慢速、上一帧、下一帧和滑块逐帧。原始完整画布统一显示，跑步 75 ms/帧（16 帧共 1200 ms），受击 40 ms/帧，普攻 30 ms/帧，施法 45 ms/帧。预览默认为循环检查，可关闭循环查看一次完整动作。报告生成后新增或变更图片须重跑工具；页面不代表实时文件系统监视。

`verify` 只生成 JSON；`preview` 与 `all` 同时检查并生成 HTML。未全部齐全并实测通过时默认退出码为 1；工作过程中可使用 `--allow-incomplete`，该参数只改变退出码，不隐藏任何问题或修改通过状态。页面和报告明确标注未进行美术验收、未运行客户端。
