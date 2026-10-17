独立视觉修正补丁（2026-10-17）

只安装本目录 `install-manifest.json` 的 18 个文件；旧主包和装备兼容 manifest 均未重写。Sourceguard 来自已安装装备兼容版本的最新 client，25 个记录中两个新文件（bag-item-badge.png 及其 .meta）预期不存在，其余按 SHA-256 校验。

修正：活动空态平铺金边、纸底硬接缝、禁用按钮整块变灰、背包容量/刷新压底框、图标越过分隔线、长文下一行碎片、任务状态徽章省略、完成勾字形缺失，以及空态残留无字按钮与活动说明背后的无用奖励槽。采用已存在 clean-skin 的原尺寸派生素材；没有新 AI 生成，没有 AssetPostprocessor。窗框、标题和挂饰在清理区外的像素逐点保持相同。

禁用仍由原 interactable 权限控制；裁切纸底保持白色，文字变为灰色/低透明度提供禁用反馈。任务完成标识复用正式 EquipmentV1 checkbox Sprite。原背包装备、卸下、分享、养成、任务接取/领奖/追踪、活动参加/查看任务回调及权限条件保留。

两条 Unity 失败已针对原因修复，原业务断言保留：

- 锻造读取中：显式查找并断言唯一的隐藏强化控件为隐藏且不可用；所有可操作控件仍用 activeInHierarchy + Single。
- 任务筛选：按 MissionFilterMenu / MissionStatusFilter_1 / MissionStatusFilter_2 / AvailableMissions 明确语义名查找唯一可见按钮，不以文字匹配父行和子选项。

新增一个测试验证完成目标使用正式勾图，全部目标保留在可滚动内容中并可滚到末端。36 份 Battle 测试源码语法检查和运行时编译均退出 0；没有在此任务启动 Unity 或修改 client。此前 518 测试中的所分配两项失败原文保存在 unity-failure-evidence.json。

安装后先跑 EquipForgeWindowTests、GameplayWindowTests、EquipWindowTests 的 EditMode 测试，再运行：

```csharp
GameplayUiVerification.OutputDirectory = "E:/work/image/designs/gameplay-ui/fidelity-20261016/qa/post-visual-fixes";
GameplayUiVerification.CaptureAll();
```

新的 26 张截图需重新核对 V01–V09。旧 qa/native 截图仅作为修正前证据，不能证明本补丁或此前装备兼容补丁的最终表现。原视觉审查在 ../qa/visual-review.json，含 17 张实看截图与 3 张原稿的 SHA、尺寸、时间证据及验证限制。
