# 04 独立 staging 结果（2026-09-21）

本轮只写本恢复目录及主代理授权的新生图目录中的精确 prompt/provenance。未写 canonical candidate、公共管线、旧 receipt、共享 preview 或正式资源；未生图、未运行 Unity。

## 可复用导入入口

```powershell
$qdaoPython = 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$qdaoRoot = 'D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd'
& $qdaoPython -X utf8 -B "$qdaoRoot/recovery-20260921/04-tools/import_local_frame.py" --archive "$qdaoRoot/recovery-20260921/04-generation/NW06-edge-v2" --batch-id 'FRESH_UNIQUE_BATCH_ID' --direction NW --frame 6
```

默认写 `04-tools/staging/candidate/04_mountain_guardian_boy`。只有明确传入 `--canonical` 才写实际候选，本次没有使用。归档目录必须包含 raw.png、精确 prompt.txt、generation-receipt.json、provenance.json；原图 SHA 必须匹配 provenance，prompt 必须逐字对应 actual_request，费用调用数必须为1次内置/0收费API。

同一 source/processing 批次拒绝重用。任何目的角色元数据已存在时，导入先在 `04-tools/history/UTC-batch` 保存原目标PNG（若有）、完整 frame-sources、当前独立 source record、manifest/qc/对应旧validation及SHA。公共模块只在当前进程内重定向输出和禁用 preview，不修改源码。每次导入后由公共 verify 独立重建，保存本机迁移映射和深浅底预览。

## 本轮处理与视觉结论

| 输入 | 处理状态 | 视觉处理建议 |
|---|---|---|
| 历史 NW08-single-v1 | 新 staging 1024，独立重建通过 | 深浅底未见连续亮紫外圈；姿态不同，待完整16帧连播 |
| 历史 NW10-single-v1 | 同上 | 同上 |
| 历史 NW11-single-v1 | 同上 | 同上 |
| 新 NW04-edge-v2 | 新 staging 1024，独立重建通过 | **不建议换入**；原画被明显放大，需修订 |
| 新 NW06-edge-v2 | 新 staging 1024，独立重建通过 | 去紫边有效，尺寸保持，可进入完整连播复核 |
| 新 NW07-edge-v2 | 新 staging 1024，独立重建通过 | 去紫边有效，尺寸保持，可进入完整连播复核 |

目视实际读取了三份新旧深底与浅底对比，以及NW08/10/11深浅底三联图。接触图只用于展示，未改最终PNG。

### 修边新版的固定尺度比较

所有输出按相同 .84 全格尺度和脚锚 [512,942]。

| 帧 | 原输出主体高 | 新输出主体高 | 新/旧体积指标 | 判断 |
|---|---:|---:|---:|---|
| NW04 | 760 | 842 | 1.08126 | 高度+10.79%，明显变大；脚点一致无法抵消比例漂移 |
| NW06 | 772 | 771 | 0.99292 | 尺寸基本一致 |
| NW07 | 773 | 774 | 0.99405 | 尺寸基本一致 |

体积指标是既有管线 body_scale（中央半幅alpha面积平方根），不是自动美术通过门禁。NW06/07的发梢、飘带空隙、法器与挂件孔的亮紫边在新图上已明显消失；服饰、持物和抬脚姿态保持。仍需完整NW连播/接缝检查。

三份新 raw 都是1254×1254真实RGBA，存在大量alpha0背景；可见主体alpha主要253（约99.2%不透明），少量252/254及正常软边，并非所有主体像素严格255。未擅自归一alpha。现有管线只移除alpha<=8的极弱背景，再按记录执行色键/缩小/有限去色溢/锚点，独立重建完全一致。此结果不等于透明处理与几何在完整循环中已批准。

## 证据位置

- `review/staging-analysis.json`：六张图在最后一次导入后的同一最终manifest下新鲜独立重建，以及新旧几何/原生alpha数据。
- `review/NW04-old-new-dark.png`、`NW04-old-new-light.png`：应拒收比例变化的直接对比。
- 同目录NW06/NW07新旧深浅底图。
- `review/NW08-10-11-dark.png`、`NW08-10-11-light.png`。
- `staging/candidate/04_mountain_guardian_boy/recovery-bindings/<batch>/`：历史回执不变的迁移映射、历史provenance副本、每次导入结果。

单次导入时生成的早期逐帧validation绑定当时manifest；后续增帧会使其manifest字段过时。以 `review/staging-analysis.json` 的最后六次重建为本次统一源检查证据。完整人物未齐，全部visual_review仍pending。

严格mixed assembly仍要求旧E:/与旧luyua原默认路径存在；本辅助记录迁移事实但不伪造严格绑定通过。完整来源迁移合同/正式assembly问题详见邻目录pipeline-audit/PIPELINE_AUDIT.md，本轮没有放松或改动它。
