# 本角色预览与技术检查

`build_previews.py` 只读显式列出的图片，只写同角色 `previews/`。不生图、不补帧、不镜像、不插值、不导出变形图、不修改正式 PNG，也不接触 Git。HTML 直接显示完整 1024 画布的原 PNG，统一随窗口缩放；不会按逐帧包围盒缩放或最低脚贴地。库存完整后可另输出 GIF，其中整个 1024 画布统一缩小到 512，源文件不变。

输入清单位于角色目录内，图片 `path` 相对于角色目录。清单可用 `frames`（也接受 `images`/`entries`）数组：

```json
{
  "root_anchor": [512, 880],
  "frames": [
    {
      "action": "run",
      "direction": "E",
      "frame": 5,
      "path": "frames/run/E/05.png",
      "native_size": [1024, 1024],
      "native_evidence": "provenance/run-E-05.json",
      "sha256": "可省略；有值时必须与实图一致",
      "visual_status": "not_reviewed"
    }
  ]
}
```

以上只说明格式，不是已存在图片或已确定锚点。锚点应取制作时确认的全局值；未知时省略。脚本不会推断或证实图片已对齐。`native_size` 是清单中的原生单帧尺寸声明，也接受 `native_width`/`native_height`；当前 PNG 为 1024 不能单独证明原生输入不少于 1024。`native_evidence`（或 `source_record`）保留来源文字引用，脚本不把该字符串当作实测模型/质量证据。

`frame` 从 1 开始：run 为 1–16、hit 为 1–6、attack 为 1–12、cast 为 1–16。方向按批次规定。正式路径强制为 `frames/{action}/{direction}/{两位帧号}.png`；其他角色、旧在制图目录或同角色的其他路径都不会被当正式帧导入。缺槽直接不列入，或设置 `path: null`；不会生成占位图片。重复槽位或跨角色路径会直接拒绝。输出路径解析后仍须在本角色目录内，不能借符号链接越界。

PowerShell 运行（系统 `python` 是 Windows Store 别名，使用宿主已配置的真实解释器）：

```powershell
$privatePython = 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$character = 'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/02_fire_talisman_boy'
& $privatePython -B "$character/tools/build_previews.py" --self-test
& $privatePython -B "$character/tools/build_previews.py" --manifest "$character/inventory.json"
```

输出 `previews/index.html` 与 `previews/technical-report.json`。HTML 支持正常速度、慢速 ×4、暂停、上一槽/下一槽、逐槽按钮和滑杆，展示每槽的来源与技术检查。自动播放保留全部规格槽位：缺帧显示文字空槽，并占用相同单帧时长，不跳过缺帧、不延用上一张实图。例如只有 run/E/01 时，02–16 都明确为空，整圈仍为 1200ms；不会伪造成单张高速循环。

只有某动作方向全部槽位可加载时才生成 `run-E-normal.gif` / `run-E-slow.gif` 等；不完整序列不生成 GIF，并清除该方向已过期的工具生成 GIF。不会扫描目录自动导入旧图。动画标注库存数量；库存完整仍不等于视觉通过。HTML 可切换棋盘格、浅底、深底以检查透明边缘；视觉结论需由美术验收者逐项记录。

正常时长：run 75ms（1200ms/圈）、hit 40ms、attack 30ms、cast 45ms；慢速为 4 倍。GIF 只能存储 10ms 精度，所以 run 正常 GIF 用 80/70ms 交替，总计1200ms；cast 正常 GIF 用 50/40ms 交替，完整 16 帧仍为 720ms。HTML 使用 45ms 规格计时（浏览器调度可能有偏差）。技术报告保存 GIF 重读后的真实帧数/时长。

技术审计包含尺寸、模式、SHA256、透明/半透明像素数、透明 bbox（仅诊断）、边缘像素警告、原生尺寸声明、重复 SHA、现有/缺失槽位。非 1024×1024 的图不进入固定画布预览；非 RGBA、原生尺寸未知/不足、SHA 不符、无透明背景、多个槽位 SHA 完全相同等会报告失败。缺帧和视觉未验收分别保留，技术通过不等于美术通过。SHA 检查不能替代手脚、握持和动作连续性检查。

退出码：`0` 表示本次可加载清单的技术检查通过（可以只有部分帧）；`2` 表示清单错误或已列图片技术检查失败。无论现有帧是否技术通过，都必须以报告中的 `target_frames: 196` 和 `loadable_frames` 判断完整度，不能用退出码宣称完成。

自检覆盖 196 槽规格、GIF 量化时长、尺寸字段解析与目录边界，不创建测试图或假帧。`preview-audit-input.json` 是工具空库存核验输入，明确不代表成品；正式制作后使用根代理维护的实际清单重新运行。真实 PNG 到位后须再运行并目视检查 HTML/GIF。

2026-10-02 工具核验已实际执行：Python 自检通过；空库存构建显示 0/196、14 段全部未完成、196 个缺槽且不生成 PNG/GIF；Node 执行生成页面的 JavaScript 验证全部 16 个空跑步槽位均按序播放、施法 45ms/帧与 720ms/段、逐帧按钮正常。跨角色、旧 generation 路径、动作/方向不匹配路径均被拒绝。这些是预览逻辑检查，尚无本批真实帧的浏览器视觉验收结论。
