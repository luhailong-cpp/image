# 17 灵篆书生隔离工具

这些工具不调用收费 API、不写公共 candidate/preview，不自动批准图片。真实生成只由当前任务的内置 image_gen 调用完成。Python 使用 `C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`，传入 `-B` 避免共享缓存。

## 单帧接口

1. `prepare_request.py --archive <17-generation/fresh-attempt> --prompt <exact.txt> --reference <image1> --reference <image2> --kind idle --direction S`。walk 另加 `--frame 1..16`。读入无 BOM 的 UTF-8 精确提示词、保存参考图调用前 SHA 和配置快照；输出 request 仍是 prepared，没有宣称已经调用。
2. 将 `request.json.actual_request.prompt` 原样传给内置 image_gen，参考图也原样传入。不要重新拼接字符串或去掉末尾换行。保留实际工具结果的 metadata，除图片数据本身可由返回原文件保存，不能替工具补写型号、质量或 output_hint。
3. `archive_builtin_result.py --archive <attempt> --local-result-path <actual-returned.png> --tool-result <actual-metadata.json>`。若已记录真实完成时间可加 `--completed-at <timestamp-with-zone>`；否则记录为归档时观测到生成已完成，不冒称模型生成时间。实际原文件和归档 raw 都保留。已有 raw 只接受与实际原件 SHA 相等，不覆盖。
4. `import_frame.py --archive <attempt>`。可显式选择 `--chroma-profile purple-preserve`，默认 standard。写入 `17-tools/staging/<attempt>/candidate/17_ghost_script_calligrapher_boy`，1024 RGBA、固定 .88 整格缩放、脚锚 [512,942]。拒绝覆盖已导入 attempt。每个处理阶段独立重建，深浅底审查在 `review/dark.png` 和 `review/light.png`。

旧请求若只保存 `prompt.txt` 路径而无 kind/direction，可在归档命令加 `--kind idle --direction S`（walk 另加 frame）。工具新增独立 slot.json，不修改旧 request。旧引用路径若只有字符串，则新增 reference-bindings.json，并明确这些 SHA 是生成后实测，不能证明调用前字节。

## 清单与预览

`inventory.py` 只读列出当前 archives、已导入槽位和同槽多个候选，不自动选择版本。可加 `--output <fresh-json-inside-17-tools-or-preview>` 写不可覆盖快照。

选择文件结构：

```json
{"character_id":"17_ghost_script_calligrapher_boy","overrides":{"idle/S.png":{"import_result":"absolute/path/to/import-result.json","visual_status":"root_selected_unapproved"}}}
```

每槽也可直接放完整 import-result 对象，或其绝对文件路径字符串。`visual_status` 只接受 pending、root_selected_unapproved、static_reviewed_pending_dynamic；不会把选稿写成正式批准。

`build_preview.py --revision <fresh-name> --selections <selection.json> [--require-complete]` 在 `17-delivery-preview/revisions/<fresh-name>` 复制选定PNG原字节，建立逐图来源与SHA清单、站立总览、深浅底16帧总览、15→16→01→02接缝和交互HTML。方向完整时才创建GIF，并重新打开核对16×30ms=480ms。缺槽显示缺失，不用邻帧填充。

预览包含8方向、独立站立、30ms播放/120ms慢看、逐帧、深浅底、正常512与放大1024显示。源文件始终1024，显示缩放不改变交付PNG。构建同时检查单原生来源只分配一槽、无精确重复/水平镜像、比例数值和锚点。数值与文件齐套不是步态或风格通过。

可使用公共 `tools/serve_preview.py --port <free-port>` 只读提供整个V14根目录，在浏览器打开当前17快照相对地址。实际浏览器动态复核另写绑定固定 manifest SHA 的记录，不重写创建时的 pending 状态。没有 Unity 或正式客户端验收声明。

## 已做工具验证

全部Python文件已解析通过。真实 `idle-S-v2` 已完成成功归档、标准色键处理、独立阶段像素重建及RGBA尺寸核对。其1张站立的 `idle-S-tool-smoke` 预览准确报告135缺槽、0GIF；没有给缺帧制造完整循环。W/NW工作器 `worker_wnw.py` 只准备本代理负责方向的精确提示词，不生成图像。
