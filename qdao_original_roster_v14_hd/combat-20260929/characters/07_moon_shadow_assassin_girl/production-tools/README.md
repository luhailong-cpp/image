# 07 私有制作工具

只读其他目录，只写 `07_moon_shadow_assassin_girl`。不自动选版本，不制造姿态，不覆盖现有文件，不授予视觉/客户端验收。所有 `--out` 使用角色目录内尚不存在的路径。

Python：`C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。

## 调用

```powershell
$py='C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$tool='qdao_original_roster_v14_hd/combat-20260929/characters/07_moon_shadow_assassin_girl/production-tools/combat07.py'
& $py $tool snapshot --out inventory/start.json
& $py $tool register --source '<工具实际返回PNG绝对路径>' --label hit-E-01-v1 --submission prompts/hit-E-01-v1.submission.json --returned provenance/returns/hit-E-01-v1.return.json
& $py $tool export --selection selection/complete.json
& $py $tool export --selection selection/complete.json --publish
& $py $tool preview --out preview/normal-and-slow.html
& $py $tool audit --out inventory/final-technical-audit.json
```

## 提交记录 schema

每次调用之前写一个独立 JSON，保留真实完整 prompt/config/参数/参考用途。示意中的尖括号必须换成真实证据，不能当作回执。

```json
{
  "submittedAt": "<实际UTC时间>",
  "submittedAtEvidence": "<clock工具/本机UTC调用前观测>",
  "configSnapshot": {"model":"<当次配置目标>","quality":"<当次配置目标>"},
  "prompt": "<真正提交的完整提示词>",
  "submittedParameters": {
    "prompt": "<与上面完全相同>",
    "transparent_background": true,
    "referenced_image_paths": ["<实际附入的参考绝对路径>"]
  },
  "references": [{"path":"<同上>","role":"<身份/朝向/风格/动作衔接用途>"}]
}
```

## 成功返回记录 schema

```json
{
  "status": "success",
  "returnedAt": "<实际观察到工具成功完成的UTC时间>",
  "toolReturnedPath": "<真实工具返回PNG路径>",
  "actualModel": null,
  "actualQuality": null,
  "unverifiedReason": "宿主工具没有披露实际型号与画质，未确认。",
  "evidence": {"<真实返回字段或去掉图像base64后的证据>": "<真实值>"}
}
```

不能把 config/prompt 中目标型号当作实际返回值。没有成功图的尝试应另存失败文字返回记录，不能传给 register。register 保持 PNG 字节不变，拒绝小于1024的原生输出，记录原生尺寸和可见边界；边界/视觉问题仍由后续选稿检查决定。

## 完整选表 schema

```json
{
  "status": "complete",
  "frames": [
    {"action":"hit","direction":"E","frame":1,"file":"staging/hit-E-01-v1.png","generationRecord":"provenance/receipts/hit-E-01-v1.json","sha256":"<源图SHA256>"}
  ]
}
```

必须实际包含68个唯一槽；示意的一条不能导出。显式选表可以按已验收顺序排列，导出器仅按action/direction/frame落盘，不从命名最大vN推断选稿。

## 固定导出

1024×1024 原生输入默认直接固定画布 identity 导出，不改透明像素、不调整边界、不做姿态变化。非1024原生输入需显式 `--transform production-tools/export-transform.json`，所有帧同一原生尺寸、统一整体等比缩小，禁止放大：

```json
{"nativeCanvas":[1536,1536],"scaledWholeCanvas":[1024,1024],"offset":[0,0],"reason":"全套1536原生画布使用同一整体等比缩小，保持生成时固定地根。"}
```

如确有一致方向基准差，可提供固定 `directionOffsets:{"E":[0,0],"W":[0,0]}`；它对每方向所有动作都保持一致，不从任何帧bbox自动计算。任何非透明内容被裁切即拒绝。

全68帧校验和内存导出通过后，`--publish` 才写 runtime 与派生来源；预检也拒绝选表/来源哈希错位、无透明、触边、可见像素重复或精确镜像。可见像素哈希仅在审核时将 alpha<=8 归零，真实图片不受此归一化影响。像素唯一性不能证明独立姿态，六段人工实际连播仍必要。

preview 页面有40/30/45ms正常速度及明确0.25×慢放、深浅底同步、六段每段循环3次顺序播放和逐帧控件。页面预载68张；图片加载失败则拒绝播放。页面播放次数只是可读现场信息，不是视觉通过记录。

审计输出保留 `visualApproval=pending`、`clientIntegration=not_integrated`、`runtimeAcceptance=not_tested`；真正视觉验收请由实际观察者另写独立报告，不能修改这些技术语义。工具不执行素材清理；最终清理需要先核实成品、引用与来源链，并另存删除操作记录。清理后的原始回执不可修改，否则派生来源链哈希失效；另写 `provenance/retention.json`，格式为 `{"removed":[{"file":"staging/...png","sha256":"原图SHA","removedAt":"实际移除UTC时间","reason":"成品与引用核实后按保留规范移除","verifiedFinalSha256":"该槽已核实成品SHA"}]}`，审核会据此区分经核实的清理与意外丢失源图。
