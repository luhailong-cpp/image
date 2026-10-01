# 炼丹童子私有导出工具

`combat_pipeline.py` 只写当前 `08_alchemy_prodigy_boy` 目录，所有产物拒绝覆盖。它不调用生图、不选稿、不修改动作姿态、不生成镜像、不清理素材。它不会把技术检查或生成预览声明为视觉验收。

使用有 Pillow / NumPy 的 Python：

```powershell
$py = 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$tool = 'qdao_original_roster_v14_hd/combat-20260929/characters/08_alchemy_prodigy_boy/tools/combat_pipeline.py'
& $py $tool --help
```

## 登记真实输出

保存当次实际工具参数为 `request.json`（其 `prompt` 必须与 `prompt.txt` 完全一致）、工具真实返回为 `response.json`，保存当次配置为 `config.json`。参考用途 `references.json` 是与请求 `referenced_image_paths` 顺序完全一致的数组：

```json
[{"path":"D:/absolute/reference.png","role":"对应E方向身份、道具持手与地根参考"}]
```

```powershell
& $py $tool register --source 'D:/exact/tool/output.png' --label hit-E-03-v1 --request 'D:/actual/request.json' --response 'D:/actual/response.json' --prompt 'D:/actual/prompt.txt' --config 'D:/actual/config.json' --references 'D:/actual/references.json'
```

工具把全部输入文字原样保存在 `provenance/evidence/<label>/`，字节不变复制 PNG 到 staging，写 `provenance/receipts/<label>.json`。返回未提供型号/质量时保持 null。只有真实返回包含可靠字段时，可指定 `--model-pointer /model` / `--quality-pointer /quality`；不能指向提示词或目标配置。时间采用原文件 UTC mtime 并注明证据局限。记录失败时用 `--failure '真实失败信息'` 替代 `--source`，失败不会占用候选槽。

登记器要求所有引用文件仍可读取，以计算实际引用哈希。注册后输出及文字都不允许覆盖；重试使用新版本号。它仅支持本任务的本地路径参考输入。

## 显式选表和统一导出

每组 JSON：

```json
{"action":"hit","direction":"E","status":"selected","frames":[
  {"frame":1,"file":"staging/hit-E-01-v1.png","generationRecord":"provenance/receipts/hit-E-01-v1.json","sha256":"真实源图SHA256"}
]}
```

示例只示意结构，不是完整选择；实际必须每组有序 1..6/12/16。可传六个文件，或一份 `{"groups":[六组]}` 合集。所有68槽齐全才允许导出，任何 partial 选表拒绝。选表必须人工/主代理按实图明确写出，不根据版本号选稿。

```powershell
& $py $tool export --selection selection.json
& $py $tool export --selection selection.json --publish
```

默认 identity 仅接受原生1024×1024；原生更大尺寸须提供一份明确固定变换，且各方向所有动作共用。示例结构（数值仅示意，需依据真实画布决定）：

```json
{"E":{"nativeCanvas":[2048,2048],"scale":0.5,"offset":[0,0]},
 "W":{"nativeCanvas":[2048,2048],"scale":0.5,"offset":[0,0]}}
```

通过 `--transform transforms.json` 指定。禁止放大，禁止每帧包围盒拟合/居中；不会清透明噪声、修边或扭曲角色。变换会裁掉可见内容时拒绝导出。源图和来源链、重复/精确镜像先检查，再写 runtime 和独立派生记录。进程中断可能留下部分新文件，但永不覆盖；审计会显示不完整，不应盲目重跑。

## 六段预览及验收

```powershell
& $py $tool audit --out preview/qa-v1
```

输出必须是新的本角色目录。`manifest.json` 核对68帧尺寸、透明、来源哈希链、重复与精确水平镜像；`index.html` 支持六段顺序连播、单段循环、单帧定位，正常40/30/45ms及明确0.25x慢放，深白底并列。

浏览器帧显示受刷新频率限制，页面以累计时间计算动作帧，不将90ms等慢放冒充正常速度。自动检查不能识别重绘镜像、近似复制、手部错误或所有姿态重复；需要实际观看。页面创建本身不改变 `visual-review-pending.json` 的pending状态。实际观看后另存带时间、审阅者、各段结果和问题的验收记录；客户端始终另计。

`audit` 不指定 `--out` 时只读；制作途中 `--allow-incomplete` 只放宽退出码，报告仍列出缺槽。
