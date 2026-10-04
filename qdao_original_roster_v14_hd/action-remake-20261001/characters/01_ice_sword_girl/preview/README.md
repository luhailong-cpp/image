# 冰剑少女 E 向离线节奏复核

入口 `index.html`。可直接打开，无外部网络依赖；支持 128 / 256 / 512 px、暂停、逐帧、拖动、1× / 0.25×及诊断根线。共有9窗：旧帧四种均匀时长、当前候选四种相同的均匀时长，以及按选择清单逐帧加权的主详情窗口。128/256为新旧正常显示对比尺寸，512放大可横向滚动。

旧 v13 完整16帧各512×512，只用于480/640/720/800ms同序列节奏对比。旧源采用 `lowest_alpha_gt_8` 与 `[256,471]` 对齐，旧 `passed` 不代表本轮高清、接地或跑步验收。所有旧PNG只读，未重新加工或升格。来源、原始SHA及旧模型请求记录在 `baseline-E.json`；未返回的实际模型与质量保留null。

原生候选读取 `../review/run-E-selection.json`。四窗是相同选图分别按480/640/720/800ms均匀播放，主窗单独读取逐帧时长；720ms仍为trial，不能证明姿态修好。构建命令为使用可用Python执行 `../tools/build_grounding_preview.py`；该脚本只写本角色preview目录，更新JSON审计和浏览器数据快照。清单不存在时16槽均为空。每次选择变更后重新构建，以使直接打开HTML的快照和SHA复核同步；本地HTTP预览也可点击重新读取。动态读取与手动载入不授予SHA通过。

选择清单约定：

```json
{
  "schemaVersion": 1,
  "characterId": "01_ice_sword_girl",
  "direction": "E",
  "canvasSize": [1024, 1024],
  "root": {
    "point": [512, 975.872],
    "status": "provisional",
    "definition": "填写真实采用依据；示例坐标不是接地证明"
  },
  "timing": {"status": "trial", "uniformCycleMs": 720},
  "frames": [null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null]
}
```

每个非null槽为 `{frame:1,path:"drafts/run/E/01-v1.png",sha256:"...",nativeSize:[1254,1254],status:"pending_review",plannedPhase:"...",actualContact:{left:"unknown",right:"unknown",confidence:"...",evidence:"..."},notes:"..."}`，`frame`为1起始且必须与位置一致，`path`相对角色目录，可只读引用工作区内旧原生源。`sourcePath`等附加来源字段会保留。`actualContact`可为null，代表未知；不从提示词或计划推断实际接触。`root`可为null。可用 `timing.frameDurationsMs` 的16个正数覆盖均匀试播，仍不修改客户端。

原生槽缺图、SHA不符、加载失败时显示空白及原因，保持其时间槽。完整源画布等比显示，无逐帧alpha对齐、脚底贴线、包围盒归一化、上下挪动、复制、镜像、插值或填空。诊断线跟随清单声明的固定根点，不能证明鞋底真正落地。根点坐标须与 `canvasSize` 一致。

`source-audit.json`保留已有原生7稿和最新旧review引用，不自动选择此前拒稿。预览工具未自行执行人工接触标定，计划与实际证据分列；完整原生循环、正常尺寸美术效果及客户端位移仍需后续验收。浏览器实播核验与工具测试结果另见 `verification.json`（若已生成）。
