# 聚宝斋七页原稿还原暂存包

本包只写入本目录，未写客户端、未启动 Unity。七页沿用同一套原稿布局和当前真实 `JubaozhaiState`；现有 36 张专用 Sprite 继续复用，新增 20 张原稿派生片，无新 AI 生图。来源、原生尺寸、原图/派生图 SHA、既有切片来源链见 `asset-manifest.json`；原图历史实际型号/质量仍按原 `../manifest.json` 证据，不以当前配置回填。

原失真来自通用 Attributes 主框与 2200×940 重排。本包改为原稿 1932×814 native 坐标整页单比例缩放，恢复原图外景、主框、标题雕花、两侧挂联、玉珠红穗；动态区域使用同源空纸清理，分类、四商品行、搜索/分页和右竖牌由原生控件重建。`verify_package.py` 验证动态清理范围之外的原稿像素逐像素未变。原画 06-summoning 宽度为 1933，其余母图为 1932；共用框来自 01-empty，不把母图宽度差异冒称统一原生尺寸。

未修改 Models、Client 或 UiRoot。原 public API、全部 `State` 调用次数及 22 项业务/焦点方法逐字保持；包括服务端分页原样展示、收藏确认后写回、服务端详情、超时/结果未知状态展示、交易与联系入口的当前语义。不会从历史说明把在线接口退回演示。新表现层不调用 `LoadDemo`。所有八类与子类可滚动访问，点击当前类别可返回该类别全部商品。当前默认 PageSize=4；若传入更大的服务端页，同页内容纵向滚动显示全部条目，不截取前四条，不自行过滤、排序或改写页码。摘要长文单独滚动，真实名称、价格、等级、时间和详情始终来自当前 State。

安装前核对 `sourceguard.json` 中客户端代码和 36 张复用图片的 SHA，再按 `install-manifest.json` 将 `staged/` 相对路径复制到客户端。原 `JubaozhaiWindow.cs.meta` GUID 保留；新资源明确 Single/FullRect/100 PPU/Uncompressed/无 mipmap/max4096，没有新增 AssetPostprocessor。既有全局 `QdaoUiTextureQuality` 可能将导入上限改成 16384，不会缩小这些源图。

运行时离线编译见 `compile-check.rsp` / `compile-validation.json`，仅将运行时源列表中的 JubaozhaiWindow 替换为暂存代码并加入 partial/fit。新增 `JubaozhaiFidelityWindowTests` 四项用例覆盖服务端六行原样/滚动、分页委托、收藏确认/详情未知状态以及全分类/子类可达；测试独立 fixture 不进入正式 State。原 ServerPaging、Client、Model 测试保留不改。离线语法编译不代表 Unity 测试已运行。

安装后在 Edit Mode 执行现有 `JubaozhaiUiVerification.OutputDirectory = <本项目验收目录>; JubaozhaiUiVerification.CaptureAll();`，或菜单 `MMORPG/UI/Jubaozhai/Capture and verify`。该标准入口在独立 additive 场景使用当前正式窗口，输出两种分辨率共 20 张截图并验证原生交互；截图数据明确标注离线样例，不接网络、不替换在线 State。另执行现有聚宝斋业务测试和新增 UI 测试，再在实际编辑器游戏中检查七个类别状态、空态、搜索、分页、收藏、详情与超时提示。截图成品核验后按项目规则清理过程图。

复现资产和暂存代码：`build_assets.py`、`prepare_code.py`、`verify_package.py`。全部脚本只写本目录，不调用生图、不启动 Unity、不改客户端。
