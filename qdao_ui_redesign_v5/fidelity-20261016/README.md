# 核心界面原稿还原接入包

基准是当前目录上一级已确认的 `01_login_2560x1080.png`、`02_server_select_2560x1080.png`、`03_character_select_2560x1080.png` 和 `hud/placement.json`。原 `UI_SPEC.md` 未找到；没有据此编造规范。本包沿用已确认画法，只清理预览中的动态文字、状态、角色示例，交给原生控件显示真实数据。

## 分阶段接入

1. `hud-install-manifest.json`：6 文件。主城三入口使用正式 v10 同源按钮，位置为 x2160，y176/280/384，336×81.6，字体36。第四宠物入口继承同款。TeamFollow 的派生定位继续保留16间距。父任务已接入并完成当前459源码编译。
2. `core-login-server-install-manifest.json`：34 文件。3源码及14Sprite。把登录与选服原稿的静态画层和可交互内容分离；真实搜索、分类、分页、选择、维护禁入、加载忙态、账号输入和登录事务保留。安装后需在 EditMode 调用 `MmorpgClient.UI.EditorTools.QdaoUguiBuilder.BuildAll()` 重建生产 `Assets/Resources/UI/Ugui/Prefabs/QdaoServerSelect.prefab`；仅改源码不能更新已烘焙界面。
3. `core-role-install-manifest.json`：14 文件。RoleFlowUi及6Sprite，依赖前阶段helper的精确SHA。使用选角原稿的云山、平台、题签、列表和详情框。当前服务端职业数组、全部可选外观、0至5角色槽、创建和选角事务、名字规则、拒绝后的恢复不变。已有山岳守卫空白头像使用同ID正式独立portrait作为UI加载后备；没有激活或审批其动画包，没有借用其他人物。
4. `core-tests-install-manifest.json`：2文件。只更新旧皮肤/旧节点断言，全部原交易、维护、搜索、加载、凭据和过期点击回归保留；另验证导航切换两个正确画层。

每个manifest记录完整payload SHA与源文件安装前守卫。前置guard不匹配时应先核对差异，不盲目覆盖。runtime/art payload在首次阶段交付后冻结；若原生截图发现问题，后续以明确补丁发布。

## 验证

- `compile-staged-core.ps1 -Phase login-server`：当前461运行时源码，退出0。
- `compile-staged-core.ps1 -Phase role`：当前461运行时源码，退出0。
- `compile-staged-core-tests.ps1`：登录选服测试源码编译退出0。
- `qa/core-package-audit.json`：34/14文件两包均通过存在性、源SHA和离线编译核对。
- 以上离线检查没有启动Unity，不能替代原生视觉与点击验证。安装后的原生截图及测试由父任务执行。

推荐运行 `MmorpgClient.Tests.EditMode.Ugui.QdaoServerSelectPrefabTests` 和 `MmorpgClient.Tests.PlayMode.QdaoRoleIdentityPlayModeTests`。重建prefab后用当前 `ClientUiRefreshVerification` 捕获登录、选服、选角、建角两分辨率，核对中文字体、卡片层叠、实际状态以及输入遮挡。当前设计画层使用1931/1932×814原生返回尺寸按2560×1080布局显示，报告保留实际尺寸。

## 素材与模型记录

`art/*generation.json`记录4张AI清理母版，`prompts/`记录逐图指令；所有派生Sprite旁的记录关联来源、裁切与SHA。目标配置为ChatGPT Images 2.5 / gpt-image-2.5-sunburst / max。宿主内置工具没有版本或质量选择器且未披露实际型号，因此实际值明确记为未确认。原稿是编辑目标和风格参考。

保留4张当前切片母版、正式Sprite、逐图文字记录及必要接入/核查脚本；不保留中间候选或编译DLL。主城场景与玩家操作输入由现有客户端承担，不把旧预览地图作为背景覆盖当前可玩世界。
