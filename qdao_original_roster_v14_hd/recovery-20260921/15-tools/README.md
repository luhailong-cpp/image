# 水龙书生逐图归档工具

`archive_frame.py` 只处理 `15_water_dragon_scholar_boy`。它保存真实原图、精确提示词、请求、回执及逐图模型记录；不调用生图服务、不生成动作、不修改共享 pipeline 或预览索引。默认只归档；用户授权的确定性残边处理须显式加 `--process`。

使用本机 Python：`C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。依赖 Pillow 与 NumPy。

归档单帧（PowerShell；示例路径按实际结果替换）：

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'qdao_original_roster_v14_hd/recovery-20260921/15-tools/archive_frame.py' --generation-dir 'qdao_original_roster_v14_hd/recovery-20260921/15-generation/S-idle-v1' --source 'C:/actual/generated/result.png' --request-json 'qdao_original_roster_v14_hd/recovery-20260921/15-generation/S-idle-v1/request.json' --receipt-json 'qdao_original_roster_v14_hd/recovery-20260921/15-generation/S-idle-v1/receipt.json' --direction S --kind idle
```

walk 改为 `--kind walk --frame 1`，方向必须为 N/NE/E/SE/S/SW/W/NW。`--generation-dir` 是 `15-generation` 下单次输出的独立文件夹，不能是归档根目录。同一位置重复调用仅在原图、槽位、prompt、request、receipt 的字节证据完全相同时接受；不同稿必须用新的目录。

`request.json` 应直接保存工具请求，或将实际参数放入 `arguments`、`tool_arguments`、`toolArguments`、`parameters`、`request` 对象。精确提示词优先取实际请求的 `prompt` 字符串，按原字节另存 `submitted-prompt.txt`，保留已有 `prompt.txt` 原件（即使它有额外末尾换行）。请求未含文本时才读取 `prompt_path`/`promptPath` 或旁边的 `prompt.txt`。参考图读取 `referenced_image_paths`，或 `references: [{"path": "...", "purpose": "identity"}]`。推荐请求中带当次 `configSnapshot`；缺少时记录归档时配置，并明确它不能证明生成时配置。原始请求与回执原字节保留，不增删字段。

默认只归档。添加 `--select` 才授权交付至 `15-delivery-preview/runtime/walk/D/nn.png` 或 `runtime/idle/D.png`。已经存在的交付槽或记录一律拒绝覆盖。选择不代表美术通过，生成记录始终保留 `pending_manual_review`，正式客户端/Unity验收不在本工具范围。

原生完整单帧两边必须至少1024；不是PNG或低于原生尺寸要求时在任何写入前拒绝。机器不能证明图内只有一个人物或动作相位正确，调用者须先目视确认完整单帧，不能传入小格拼图。

1024×1024、有真实透明像素和可见人物、画布四周全透明的PNG可以原字节交付。无真实alpha、碰边或非正方形先归档并标记 `needs-processing`，不自行抠图。大于1024的方形透明原图另需 `--allow-downscale` 才会等比缩小至1024，缩放方式、比例与原图SHA写入派生记录；不会放大、逐人物包围盒适配或改变姿势。它不检查固定脚点或同批比例，必须由美术复核处理。

本任务已获用户授权处理残边、保持脚点，因此正式处理新图使用 `--process --select`。`--process` 直接复用原有 `tools/vendor/generate2dsprite.py` 和 `edge_despill.py`：透明原图先去掉 alpha≤8；执行既有100/150抠色、整格 `1024/max(native_width,native_height)*0.88` 等比缩小，再执行边缘半径4/参考半径12的颜色去溢出；按身体上42%区域alpha>8的x中值与最低有效alpha脚点对齐至 `(512,942)`。原图碰边或最终固定scale将裁切时拒绝，不能缩小单个身体或局部变形掩盖问题。

处理阶段、SHA、算法、vendor SHA、边缘统计、深浅底检查图保存在该次归档的 `processing-fixed088-v1/`，可重复核验；不同处理像素禁止覆盖。同批全部采用相同 `.88`，不把对齐、缩放或检查底图记为新的AI创作。边缘统计只定位候选像素，紫色衣物/发丝也可能被统计为品红相近色，数值不是独立美术判定。

只读库存JSON：

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'qdao_original_roster_v14_hd/recovery-20260921/15-tools/archive_frame.py' --scan
```

扫描统计128个walk及8个独立idle槽、缺槽、每张交付图尺寸/alpha/SHA、原生尺寸、来源哈希校验、原始来源复用和交付文件SHA重复。它只输出JSON，不写库存文件。原图相同不能分配多个动作槽；像素相似但编码不同、镜像、错误步态或不连续循环仍需独立人工检查。
