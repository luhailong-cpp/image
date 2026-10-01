# 09 竹弓少女私有导出工具

仅允许读写本角色目录；不更改共享工具、其他角色、移动或客户端。输入不足会报错退出，默认运行不写任何文件。不会自动批准视觉或客户端验收。

## 显式选表

在 `selection/` 放六个 JSON：`hit-E.json`、`hit-W.json`、`attack-E.json`、`attack-W.json`、`cast-E.json`、`cast-W.json`。每组分别 6、12、16 帧，按帧号连续排序；总计严格 68 槽。一份原生图只可选进一个槽。也兼容角色根目录 `*selection.json`，但不能重复同组。

```json
{
  "status": "complete",
  "action": "hit",
  "direction": "E",
  "frames": [
    {
      "frame": 1,
      "file": "staging/hit-E-01-v1.png",
      "sha256": "实际原生PNG SHA256",
      "generationRecord": "provenance/receipts/hit-E-01-v1.json",
      "generationRecordSha256": "实际来源JSON SHA256"
    }
  ]
}
```

上面仅示意字段，缺少 02–06 的示例不能导出。每组只有实际挑选完整后才写 `status: complete`。来源要求记录生成时间及时间证据、原生尺寸、入口、配置快照、实际提交参数、实际返回型号/质量、提示词和参考；未披露值保持 null 并解释。来源记录自身 SHA 必须在最终写完 JSON 后计算。

## 命令

工作目录为仓库根 `D:/luyuan/wuxingqitan/image`。当前可用 Pillow / NumPy Python 已由依赖工具确认：

```powershell
$py = 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$char = 'qdao_original_roster_v14_hd/combat-20260929/characters/09_bamboo_archer_girl'
& $py "$char/tools/export_bamboo_combat.py"
& $py "$char/tools/export_bamboo_combat.py" --preview-dir "$char/preview/pre-export-01"
& $py "$char/tools/export_bamboo_combat.py" --publish --preview-dir "$char/preview/runtime-01"
```

第一条只读预检；第二条生成私有待审预览；第三条在全部预检通过后写 68 张 `runtime/<action>/<direction>/<NN>.png`、配套 `provenance/receipts/derived/` 和引用这些 runtime 的最终预览。拒绝覆盖任何同名成品、来源或预览目录。预览与导出操作相互独立，技术检查不代替人工选择或美术批准。

导出默认：所有源图必须具有同一方形画布且边长不小于 1024；1024 原生图原字节复制，较大的原生图对整张画布一致等比缩为 1024。绝不按照逐帧包围盒调整大小/居中，不合成动作。

如实际参考和成图需要整体平移/缩放，可在角色目录写固定变换 JSON，并加 `--transforms <该JSON路径>`：

```json
{
  "E": {"nativeCanvas": [1024, 1024], "factor": 1, "offset": [0, 0]},
  "W": {"nativeCanvas": [1024, 1024], "factor": 1, "offset": [0, 0]}
}
```

每方向一个固定变换，三个动作共用；导出器拒绝放大和可见主体裁切。变换只是工具能力，是否使用必须根据成图与参考实际核对。输出来源完整记录变换。

## 验证范围

- 68 槽完整；每槽输入/来源/选表哈希；渲染完成后再次核对输入没有并发变更。
- 原生尺寸与记录一致，完整 PNG、RGBA、真透明、主体未触边；输出 1024。
- 清空完全透明像素的隐藏 RGB 后比较可见像素；拒绝完全重复和完全镜像重复。
- 六段按正常 40/30/45ms 连续循环，也可 0.25× 慢放（160/120/180ms），同步白色/深色背景，支持逐帧。

独立姿态、手部解剖、武器数量、衣饰连续性、地根与脚滑仍需六段连播审阅；精确像素查重不能证明这些内容。预览报告始终初始标记 `visualApproval: pending`，客户端 `not_integrated / not_tested`。

共享 `audit_combat.py` 可以用 `--characters 09_bamboo_archer_girl --out <本角色私有audit路径>` 进行另一次技术核对；其回执加载会读取整个批次，如果其他角色坏 JSON 引出全局问题，要记录准确归属，不改别人的文件。

## 工具准备验证

2026-09-30：CLI 可加载，空选表正确拒绝导出，预览 JavaScript 通过 Node 语法检查。尚无 68 帧真实输入时，未执行完整导出或宣称六段视觉验收。
