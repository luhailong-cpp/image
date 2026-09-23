# 09 竹弓少女专用归档与导出

这些脚本不调用生图 API、不生成新姿势、不批准美术、不改公共工具或其他角色。

Python：`C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`。

## 真实结果归档

```powershell
& $python 09-tools/archive_generation.py --archive 09-generation/S01-v1 --original C:/真实工具输出.png --tool-result 09-generation/S01-v1/result-metadata.json
```

默认使用该稿目录 `request.json` 中的 `actual_request`。若成功调用实际为重试文件，加 `--request 09-generation/S01-v1/retry-request.json`，保留最初失败请求。`--tool-result` 的 JSON 必须包含真实 `output_hint`，其中可验证原始文件路径；可另保存实际 `completed_at_utc`，缺失时只记录请求开始时间与归档时间，不冒充准确完成时间。

每稿归档原字节 `raw.png`、精确无附加换行 `prompt.txt`、实际请求与结果、配置快照、参考图 SHA、来源元数据和 `generation.json`。请求未保存配置时，明确标注配置在归档时读取；未保存参考 SHA 时标注 SHA 仅在归档时核对。宿主未披露的 actualModel/actualQuality 为 null。

## 单帧导出

```powershell
& $python 09-tools/export_frame.py --archive 09-generation/S01-v1 --direction S --kind walk --frame 1
& $python 09-tools/export_frame.py --archive 09-generation/S-idle-v1 --direction S --kind idle
& $python 09-tools/export_frame.py --archive 09-generation/S01-v3 --direction S --kind walk --frame 1 --chroma-profile standard
```

输出为 `09-delivery-preview/work/S/runtime/walk/S/01.png` 或 `idle/S.png`。每帧独立来源记录在对应 `work/S/sources/`，PNG 旁保存派生生成记录。方向之间无需并发改同一个 JSON；同方向有短时文件锁。

原生单帧两边至少 1024；整画布统一 `1024/max(native_size)*.88` 缩小、整数平移对齐脚锚 `(512,942)`。默认 `--chroma-profile none` 需要真实 RGBA，保留原生颜色与透明度。纯洋红底使用显式 `--chroma-profile standard`，调用项目原有 `remove_bg_magenta(100,150)`，缩小后调用 `despill(radius=4,reference_radius=12)`；记录工具文件 SHA、全部参数、处理报告和每阶段 RGBA 像素 SHA 供独立重建。两种模式均不按人体包围盒逐帧缩放。原稿可见触边、导出裁切、重复来源、覆盖已有槽均拒绝。每张导出始终是 `pending`，数量和脚锚检查不能代替真实步态、残边及循环目视验收。
