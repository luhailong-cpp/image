# 赤枪少女角色私有导出工具

`export_and_preview.py` 只接受此角色的显式选表，默认只读预检；不自动选版本，不合成动作，不修改其他角色、共享文件、移动或站立资源。输出文件使用独占新建模式，已有 runtime/来源/预览一律拒绝覆盖。

选表可放角色根目录、`staging/` 或 `selections/`，文件名须以 `selection.json` 结尾。六段各一份，示例结构如下（仅示例，不是已选图）：

```json
{
  "action": "hit",
  "direction": "E",
  "status": "partial",
  "frames": [
    {
      "frame": 1,
      "file": "staging/hit-E-01-v1.png",
      "generationRecord": "provenance/receipts/hit-E-01-v1.json",
      "sha256": "真实源PNG的SHA256"
    }
  ]
}
```

完整段须具有该动作从1起连续的6/12/16帧。工具不把 `status` 文字当作完成证据，实际检查68槽。部分段必须显式标 `partial`，并传 `--allow-partial`。同一个源图禁止选到多个槽；选表、源图、来源记录的SHA必须相符。

来源字段与共享 `register_output.py` 兼容，额外要求 `generatedAtEvidence`。必须包括真实提示词、参考图、配置快照、实际提交参数、实际返回型号/质量及证据；返回型号/质量未知时为null，且提供 `unverifiedReason`。

所有选图原生画布为1024正方形时使用固定身份变换，保留生成图地根。其他原生尺寸必须提供角色私有 `--transform-json`；每方向只允许一个固定整体等比缩放与偏移，跨受击/普攻/施法共用，禁止逐帧包围盒缩放或居中。示例变换（必须根据实际原生画布确认）：

```json
{
  "E": {"nativeCanvas": [1536, 1536], "scaledWholeCanvas": [1024, 1024], "offset": [0, 0]},
  "W": {"nativeCanvas": [1536, 1536], "scaledWholeCanvas": [1024, 1024], "offset": [0, 0]}
}
```

以下命令从仓库根目录执行。将 `--allow-partial` 去掉后才要求完整68槽；部分导出始终标记partial。`--preview-dir` 为角色相对路径且必须尚不存在。`--publish` 才写runtime和派生来源。

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'qdao_original_roster_v14_hd/combat-20260929/characters/10_crimson_spear_girl/tools/export_and_preview.py'

& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'qdao_original_roster_v14_hd/combat-20260929/characters/10_crimson_spear_girl/tools/export_and_preview.py' --preview-dir preview/selected-v1 --publish
```

预览按 hit/E、hit/W、attack/E、attack/W、cast/E、cast/W 顺序支持六段连播，同时显示白底/深底。正常分别40/30/45ms；慢放明确标0.25×，每帧时长4倍。缺槽保留空位，不跳槽不复制填充。PNG全部预载后开始计时。

技术预检检查PNG RGBA、真透明、原生尺寸、源/选表/来源SHA、导出1024尺寸、边界裁切、重复可见像素和精确镜像可见像素。它不能证实独立姿态、握位、脚根、枪杆长度或动作连贯；所有机器产物固定标美术验收pending、未接入客户端、未运行验证。

准备阶段仅运行了空库存的只读预检：`--allow-partial` 返回0/68及partial，完整模式拒绝缺槽。尚未测试真实图导出，也未生成任何成品或选表。
