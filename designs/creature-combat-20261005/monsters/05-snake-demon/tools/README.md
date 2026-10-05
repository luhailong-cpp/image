# 蛇妖交付检查工具

工具只检查本角色目录，并生成清单和 QA 派生预览，不绘制、移动、对齐或修改正式图片。完整合同为 `hit` 每向 6 帧 × 40ms、`attack` 每向 12 帧 × 30ms、`cast` 每向 16 帧 × 45ms，E/W 共 68 张。

本机已确认可用的 Python：

```powershell
$combatPython = 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$combatTool = 'D:\work\image\designs\creature-combat-20261005\monsters\05-snake-demon\tools\prepare_delivery.py'
& $combatPython $combatTool --check-only
```

不带 `--check-only` 时生成 `manifest.json`、`provenance-index.md`、`qa/technical-report.json`、六张 QA 联系表及对应派生记录、`preview/index.html`。无需服务器，可直接打开 HTML；正常与 0.25 倍慢放、六组独立暂停/逐帧、透明棋盘/深浅背景和锚点显示均可用。每张图保持整个画布，不按可见边界重新对齐。

退出码 0 表示技术检查通过；2 表示缺图、来源缺项、尺寸/透明异常、重复帧或多余正式 PNG。即使技术失败也能生成预览，缺图显示为缺图，不补帧。美术、连播、邻接和客户端状态默认待验，技术通过不能改变它们。

## 逐图来源约定

读取 `runtime/<action>/<E|W>/01.png.generation.json`，兼容 `01.generation.json`。直接生成图必须按项目策略记录 `file`、`sha256`、`generatedAt`（有时区）、原生 `width`/`height`/`format`、`tool`、`route`、`configSnapshot`、`submittedParameters`、`actualModel`、`actualQuality`、`evidence`、`prompt`（保留的实际提示词文件路径）、`references`。

宿主未披露的型号/质量为 JSON `null`，并保留 `unverifiedReason`。配置目标和实际结果分别展示；脚本不会按配置填充实际型号。来源图片允许依照素材保留规则清理，但文字记录与哈希必须保留。

派生正式图记录 `sha256`、`operation` 和 `derivedFrom`，每项包含 `file`、`sha256`、`generationRecord`。脚本沿保留的 generationRecord 检查来源记录；支持单对象或数组，不要求保留已清理的原生图片。相对路径优先相对于记录文件，其次相对于本角色根目录。

## 人工检查记录

可在实际检查后由制作负责人保存审核 JSON，并使用 `--review <文件路径>` 写入 manifest 和预览。脚本不会自动创建“已通过”的记录。示例结构仅为格式说明，不能在尚未检查时照抄通过状态：

```json
{
  "reviewedAt": "实际含时区时间",
  "reviewer": "实际检查者",
  "clientAcceptanceStatus": "not_tested",
  "frames": {
    "runtime/hit/E/01.png": {"status": "pending", "notes": "实际观察记录", "event": null}
  },
  "groups": {
    "hit/E": {
      "visualStatus": "pending",
      "normalPlaybackStatus": "pending",
      "slowPlaybackStatus": "pending",
      "adjacencyStatus": "pending",
      "notes": "实际观察记录"
    }
  }
}
```

工具检查 PNG/RGBA/1024 尺寸、透明像素与边界、文件哈希与解码像素哈希重复、缺帧、额外正式 PNG、来源记录字段与哈希、来源链和实际提示词文件。它无法自动确认 AI 姿态独立、蛇盘身连续性、方向与身份、画法完成度、模型真实版本或游戏客户端表现。
