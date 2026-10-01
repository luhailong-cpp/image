# 火符少年私有库存、导出与离线预览工具

所有路径被限制在 `characters/02_fire_talisman_boy/`，不会扫描或写其他角色。`inventory.py` 只读候选、成品、选表和来源；快照新增到本角色 `inventory/`，不覆盖旧快照。开始时初始快照为 0/68，不代表后续实时库存。

`export_character.py` 默认只读预检，使用带 NumPy/Pillow 的 Python。显式 `--publish` 才写 runtime 和 derived receipts；`--preview-dir` 写指定的新目录。它不覆写现有文件、不删除候选、不写任何移动资源。只有完整 68 槽才能导出。

## 选表

传六个动作/方向 JSON，或一个包含六个 `sets` 的 JSON。文件名、版本由制作者明确选择，不按 vN 自动选稿。每个组格式：

```json
{
  "status": "complete",
  "action": "hit",
  "direction": "E",
  "frames": [
    {"frame": 1, "file": "staging/hit-E-01-v1.png", "generationRecord": "provenance/receipts/hit-E-01-v1.json", "sha256": "真实PNG SHA256"}
  ]
}
```

上例仅展示字段，不是有效完整选表。hit/attack/cast 每组分别必须有连续 6/12/16 个 frame。partial 选表一律拒绝。每张源图只能用于一个槽。

来源必须包括 file、sha256、generatedAt、generatedAtEvidence（或 evidence.timestamp）、width/height、tool/route、configSnapshot、submittedParameters、actualModel/actualQuality、unverifiedReason（未知时）、prompt、references 和 evidence。references 的每项必须有 path 与 role 或 purpose；未知实际型号/质量保持 null，不以目标配置冒充返回值。

## 固定全局变换

`--transform` 指向制作者审阅后写下的配置，例如原生同为 1024 且已经对齐时：

```json
{
  "nativeCanvas": [1024, 1024],
  "scale": 1.0,
  "offset": [0, 0],
  "reason": "示例：所有帧生成时共用1024画布与同一脚根；完整实际核对后使用恒等变换。"
}
```

同一 scale/offset 用于全部 68 张及 E/W。不会按每张 bbox 缩放或居中。原生画布不得小于 1024，不允许放大；画布尺寸必须一致，裁切或触边会报错。由制作者按真实原生尺寸与画布锚点决定参数，上面不构成已确定的生产参数。

## 调用

工作目录可为仓库根；选表、变换、预览参数始终相对本角色目录：

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'qdao_original_roster_v14_hd/combat-20260929/characters/02_fire_talisman_boy/tools/export_character.py' --selection selection/selected.json --transform selection/transform.json
```

完整预检通过后，加 `--preview-dir preview/selected-v1` 先生成隔离预览；加 `--publish --preview-dir preview/runtime-v1` 会先导出，再创建引用 runtime 的页面，不重复存图。输出目录已存在或任何目标已存在即拒绝覆写。

预览同时呈现纯黑与纯白背景，支持六段依次连播、单段、1×正常、0.5×/0.25×明确慢放、逐帧、可选参考轴。正常间隔为 hit 40ms、attack 30ms、cast 45ms。全部图片先预载；页面的 `window.playbackAudit` 记录呈现与计时事件，但不自动授予美术通过。

## 验证边界

检查完整 68 槽、源图/选表/记录 SHA、原生与导出尺寸、RGBA/真透明、可见像素、触边、完全重复及完全镜像。比较前去除隐藏RGB与 alpha<=8 噪声，并采用可见bbox裁切哈希来发现平移后的精确复制/镜像。不会用唯一哈希证明姿态独立、持手正确、脚根稳或六段衔接良好。近似复制、重绘镜像及语义一致性仍需实际连播和逐帧美术检查。

技术预检、生成预览、播放日志均不构成客户端接入、游戏运行验收或美术正式通过。工具始终把这些状态留为 pending / not_integrated / not_tested。
