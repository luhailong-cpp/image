# 山贼生产支撑脚本

`scripts/combat_pack.py` 只处理真实已生成图片的记录、固定导出、清单和预览。它不会生图、镜像、插值、平移复用补姿态，也不会删除图片。脚本所有输出限定在本角色目录；其它目录只读。

Python：`C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`，已含 Pillow。

命令均以角色目录为相对路径起点，不依赖当前 shell 工作目录。

## 单图入库

```powershell
& '<上述Python路径>' scripts/combat_pack.py ingest --source '<工具返回的真实PNG路径>' --dest 'design/identity-E.png' --metadata 'qa/identity-E-input.json'
```

metadata 示例：

```json
{
  "generatedAt": "2026-10-05T06:00:00-04:00",
  "prompt": "本次真实提交的完整提示词",
  "references": [
    {"path": "D:/work/image/designs/creature-combat-20261005/references/monsters/06-bandit/legacy-idle-E-01.png", "role": "identity"},
    {"path": "D:/work/image/designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png", "role": "primary-style"}
  ],
  "evidence": [{"path": "receipts/identity-E.json", "fields": ["output_path"]}],
  "toolResult": null,
  "imageRole": "identity-design",
  "pose": "E 静态身份",
  "event": null
}
```

`generatedAt` 必须包含时区；不能用示例日期冒充真实时间。配置历史快照默认读取根配置，可通过 `configSnapshot` 显式传入当次已保存的快照。工具实际没有 model/quality 选择器，因此提交参数强制为 null；实际返回型号和质量仅在有结果证据时通过 `actualModel` / `actualQuality` 写入，默认 null。完整提示词另存 `图片.png.prompt.txt`，记录为 `图片.png.generation.json`。已有目标拒绝覆盖，防止丢失旧版本文字记录。

原生就是 1024 RGBA 时，可直接 `--dest runtime/hit/E/01.png` 入库。其它原生尺寸先保留唯一在制源，确认方向统一变换后导出。

## 统一导出

```json
{
  "directionTransforms": {
    "E": {"mode": "identity"},
    "W": {"mode": "fixed-affine", "scale": 0.8165869219, "translateX": 0, "translateY": 0}
  },
  "frames": [
    {"source": "native/hit/E/01.png", "action": "hit", "direction": "E", "frame": 1, "pose": "实际姿态说明", "event": null}
  ]
}
```

`export --plan qa/export-plan.json`。示例缩放不构成推荐值，应按真实原生画布决定并一次固定；E/W各自全方向、跨三动作完全相同。禁止逐帧 transform、负缩放和镜像。脚本验证源SHA及源生成记录，并为正式输出保存 `derivedFrom` 和 `operation`。执行计划可分批，但每批须使用相同方向变换，最终 `build` 会检查是否混用。

## 核验与预览

```powershell
& '<上述Python路径>' scripts/combat_pack.py inspect 'runtime/hit/E/01.png'
& '<上述Python路径>' scripts/combat_pack.py build --strict
```

`build` 输出 `manifest.json`、`generation-index.json`、`qa/technical-report.json`、`preview/index.html`。可指定 `--manifest`、`--report`、`--index`、`--preview` 路径。尚未齐图也可建立待验清单，缺帧如实列出；`--strict` 遇缺帧或错误返回2。

技术检查包括68图合同、尺寸格式、alpha、文件与解码像素SHA重复、源记录SHA、提示词和参考图可读性、同向导出变换。碰到边缘非零alpha只记录警示，须实看是否裁切。不会把技术通过写成视觉通过。

离线HTML将清单直接内嵌，无 fetch，无服务器依赖；六组按钮、正常1×、0.25×、上一帧/下一帧、滑条、缩略图、背景切换及原生像素局部检查齐备。按空格播放/暂停，左右箭头逐帧。使用 requestAnimationFrame 加时长累计，不将 hit/attack/cast 时长硬改为浏览器刷新帧率。图像加载失败会显示。

必须由制作代理另行实际查看全部帧、六组连续播放及邻接；这个脚本不会代签美术审核或客户端验收。源图已依根保留政策删除时，保留的逐图来源记录链仍可读，但不意味着原图仍可复验。
