# 天音少女私有导出与连播工具

`export_validate.py` 仅允许读选角色 05 内的来源并写其私有目录；默认只进行内存技术预检，不写图片。未运行成品导出。共享脚本与其他角色未修改。

六份显式选表均为 JSON 对象：`action` 为 hit/attack/cast，`direction` 为 E/W，`frames` 按 1 起顺序列齐 6/12/16 帧。每项必须包含 `frame`、`file`、`generationRecord`、`sha256`。路径可为角色相对、批次 `characters/05.../` 相对或本角色绝对路径。禁止同图入多槽，禁止 partial 选表。所有源图必须原生至少 1024×1024 RGBA PNG；没有从多格切图制造高清的步骤，独立生成证据仍须人工核对。

选择实际全局变换后在角色目录保存 JSON；参考 `transform.example.json`，经视觉检查才设置 `approvedForExport: true`。E/W 全部共用一个等比 scale，每方向只用一组固定 offset。原生画布必须匹配。工具不去除低 alpha，不按单帧包围盒缩放/居中，不上采样，不镜像，不改变姿态。琴与浅紫半透明飘带均保留。所有非零 alpha 超出输出边界则拒绝。

命令用现有依赖环境，例如 PowerShell：

```powershell
$python = 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$role = 'D:/luyuan/wuxingqitan/image/qdao_original_roster_v14_hd/combat-20260929/characters/05_celestial_musician_girl'
& $python "$role/tools/export_validate.py" --selection "$role/selection/hit-E.json" "$role/selection/hit-W.json" "$role/selection/attack-E.json" "$role/selection/attack-W.json" "$role/selection/cast-E.json" "$role/selection/cast-W.json" --transform "$role/export-transform.json"
```

预检通过后加 `--preview-dir "$role/preview/export-v1"`，写全新私有预览；加 `--publish` 才向 `runtime/` 和 `provenance/receipts/derived/` 写 68 份成品及记录。二者均拒绝覆盖。请在所有来源及选表停止并行写入后操作。所有内容先渲染检查，再预检全部目标不存在，最后逐文件以排他创建写入；磁盘错误仍可能导致部分写入，工具不假称事务原子性。发生这种情况，复核哈希后处理，不能盲目删掉任何文件。

检查包含 68 槽完整、来源/选表/记录 SHA、必备生成证据、1024 输出真透明、重复可见像素、裁除透明区域后的完全重复（平移复制）、完全镜像及平移镜像。隐藏 RGB 噪声不会绕过精确比较；近似复制、插值和动作语义不能单靠哈希自动判定，必须连播视觉检查。输出记录保留 source/receipt/selection 哈希、当次生成信息及固定导出变换；实际未披露型号和质量继续为 null。

预览以 hit/E、hit/W、attack/E、attack/W、cast/E、cast/W 六段连续播放。1× 按 40/30/45ms，完整六段共 2640ms；0.25× 共 10560ms，界面明确标识。两幅画布同时显示深浅底，预载全部 68 帧后播放。浏览器 `window.playbackEvidence` 只记录预载与播放事件，不替代视觉判断；在高刷新画面不足时浏览器可能跳过显示某帧，逐帧按钮用于细查。

本工具始终将视觉审核标记为 pending，客户端标记未接入/未测试。由实际审阅者另写角色私有视觉记录；最终再运行共享 `audit_combat.py --characters 05_celestial_musician_girl --out <角色私有新的audit目录>`，不带 allow-incomplete，并阅读实际结果。
