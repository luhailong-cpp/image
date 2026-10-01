# 灵篆书生战斗动作离线预览

本目录为 `17_ghost_script_calligrapher_boy` 的角色私有预览，不能作为客户端接入或运行验收证据。预览工具只展示已有图片，不生成、镜像、变形、插值或复用姿态。

## 显式选表

在本角色 `selections/` 下保存六份文件：`hit-E.json`、`hit-W.json`、`attack-E.json`、`attack-W.json`、`cast-E.json`、`cast-W.json`。受击每方向6帧、普攻12帧、施法16帧；帧号从1开始，递增，源图不能重复。

```json
{
  "action": "hit",
  "direction": "E",
  "status": "partial",
  "entries": [
    {
      "frame": 1,
      "file": "staging/hit-E-01-v1.png",
      "generationRecord": "provenance/receipts/hit-E-01-v1.json",
      "sha256": "真实源文件SHA256"
    }
  ]
}
```

完整且明确选定的单段把 `status` 改为 `selected`。文件与回执必须位于本角色目录内；可用角色相对路径、`characters/17_ghost_script_calligrapher_boy/...` 批次相对路径或绝对路径。

来源回执必须包含源文件 `file/sha256/width/height`、`generatedAt/generatedAtEvidence`、`tool/route/configSnapshot/submittedParameters/evidence/prompt/references`、`actualModel/actualQuality`。宿主未披露的型号和质量为 null，`unverifiedReason` 解释未确认原因；不能补造调用参数。

## 命令

从角色目录运行以下命令；`python` 须提供 Pillow。当前可用运行时为 `C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。

```powershell
python tools/combat_pipeline.py --audit
python tools/combat_pipeline.py --preview
python tools/combat_pipeline.py --export --preview
```

`--audit` 只输出 JSON，不写文件。`--preview` 写 `preview/index.html` 与 `preview/technical-report.json`，不足帧也可展示且明确标记 PARTIAL，缺槽不会用其他图片填补。预览优先读取通过检查的 runtime；否则展示通过检查的原生候选。

`--export` 必须完整68槽通过检查，并且68张源图具有同一个原生画布尺寸。工具把整张画布按同一比例缩至1024，矩形画布采用固定透明留边；不向上放大、不逐帧按包围盒缩放或居中。PNG须为RGBA、有全透明像素、可见主体不触边。精确像素重复和精确水平镜像会被拒绝；这些检查不等于姿态质量通过。

导出只新增本角色 `runtime/<action>/<E|W>/<01>.png` 和相邻的 `01.generation.json`，拒绝覆盖。逐图派生记录包含真实原生尺寸、源图与源回执哈希、选表哈希、整体缩放/留边参数。所有图片先完成校验和渲染，再执行新增；遇到并行写入或I/O中断可能留下部分产物，需如实核对，不能删除他人WIP后重跑。

退出码0表示选表与runtime技术检查均通过；不足帧、尚未导出或有问题返回2。打印的 `visualApproval` 始终为 `pending`，`clientIntegration` 为 `not_integrated`，`runtimeAcceptance` 为 `not_tested`。技术结果与人工视觉验收记录分开。

## 连播观察

打开生成的 `index.html`，等预加载完成后，使用“六段顺序连播”。顺序为受击E/W、普攻E/W、施法E/W；正常速度分别40/30/45ms每帧。慢放选0.25×，明确显示四倍时长。可选择当前段循环、暂停、逐帧拖动，并切换深/浅纯色背景检查边缘。

实际观察六段正常速度和慢放后，另记比例、脚根、头身、持手、毛笔长度、空白卷轴、两只墨灵数量、服装连续性、裁切和边缘情况。页面或PNG存在不代表完成视觉验收；未做客户端工作不能宣称客户端通过。
