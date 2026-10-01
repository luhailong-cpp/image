# 雷法少年私有导出与技术审阅工具

固定角色 `06_thunder_caster_boy`，任何输入/输出路径都必须位于本角色目录；所有写入使用拒绝覆盖。工具不会选择图片，也不会声明视觉或客户端验收通过。

## 显式选表

`selection/hit-E.json` 等六份 JSON，各自固定一个动作和方向。示例（实际填写真实 SHA256）：

```json
{
  "character": "06_thunder_caster_boy",
  "action": "hit",
  "direction": "E",
  "status": "selected",
  "frames": [
    {
      "frame": 1,
      "file": "staging/hit-E-01-v1.png",
      "sha256": "SOURCE_PNG_SHA256",
      "generationRecord": "provenance/receipts/hit-E-01-v1.json",
      "generationRecordSha256": "GENERATION_RECORD_SHA256"
    }
  ]
}
```

只接受帧号升序，hit 各 6、attack 各 12、cast 各 16，共 68 个唯一槽；每源图只允许一个槽。未齐全选表标记 `partial`，只能 `--allow-partial` 预检/预览，不能导出 runtime。来源回执字段沿用共享 `register_output.py`；另外严格核对 `generatedAtEvidence`、`width`、`height`、file 和两种 SHA。

## 运行

使用已发现含 Pillow/NumPy 的 Python：

```powershell
$py = 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$tool = 'qdao_original_roster_v14_hd/combat-20260929/characters/06_thunder_caster_boy/tools'
& $py "$tool/export_character.py"
& $py "$tool/export_character.py" --preview-dir preview/selected-v1
& $py "$tool/export_character.py" --publish
& $py "$tool/audit_character.py" --out audit-final-v1
& $py "$tool/preview_character.py" --out preview/runtime-v1
```

默认仅预检。默认变换为原生 1024 画布恒等变换，其他画布必须显式提供 `--transform tools/export-transform.json`。例如原生 1536×1536 全画布缩到 1024：

```json
{
  "targetCanvas": [1024, 1024],
  "common": {"nativeCanvas": [1536, 1536], "scale": 0.6666666666666666, "offset": [0, 0]}
}
```

也可用 `directions.E` / `directions.W` 各指定同格式稳定变换；同方向所有动作必须共用。禁止放大、不进行逐帧居中、包围盒拟合、淡透明清理或姿态合成。原生任何边不足 1024、原生/成品人物触边、变换裁切、可见像素重复或完全水平镜像都会拒绝。

导出 runtime PNG 与 `provenance/receipts/derived` 逐帧记录，保留原生尺寸、原始 PNG/原始回执/选表/导出工具 SHA、稳定变换参数和未确认型号/质量。审计检查 68 槽、PNG 完整性、RGBA/真实透明、边界、像素重复与完全镜像、逐层哈希和选表匹配。原图按素材规则清理后，会明确报告不能现场重算原图像素哈希，但仍核对保留的来源回执。

播放器同时显示深浅底、可切棋盘底；六段连续或逐段播放，正常 hit 40ms、attack 30ms、cast 45ms；慢放显式 0.5×/0.25×。预载完成前不可播放。播放器本身以及循环次数均不构成视觉验收，必须实际审阅并另记所见、问题、通过段和未通过段。
