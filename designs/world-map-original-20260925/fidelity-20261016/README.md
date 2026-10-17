# 世界地图原稿还原包

当前 `CityTravelWindow` 使用通用纸窗和方形地图缩略图，与已确认 `world-map-original_2560x1080.png` 不同。本包让原稿以 2560×1080 整屏等比呈现；十八个静态原创地名、山海、框体和标题保留。演示“当前位置：归元城”、中心玩家标记与底部动态按钮文字已清除，当前位置和可达目的地由原生控件显示。

客户端目前只有四个可达 SceneConfigId，名称仍是天墉城、蓬莱仙岛、东海渔村、揽仙镇。原稿 README 明确十八个原创地名尚未接入地图 ID，因此本包仅显示四个实际目的地选择，不虚构十八个可传送地点，也不擅自改名或改协议。当前目的地/日景/节庆/区服和传送状态继续读取原有数据，完整保留同区与跨区事件、在途锁定和权限。旧方形预览仍接收其资源数据，整屏视觉改为原稿。

## 安装与核验

`installation-manifest.json` 列出七个安装文件及 SHA：一个表现脚本、一个隔离截图脚本和 meta、两个最终 PNG 和 meta。安装前重新比较 `source-checkout.json`；保留现运行时脚本 meta，不覆盖 `CityTravelUiRoot`、传送状态机或原验证器。没有 AssetPostprocessor。

执行 `WorldMapFidelityVerification.Capture`，在稳定 Edit mode 用隔离 PreviewScene 拍摄四个真实目的地的数据夹具、可用日景/节庆以及传送在途/失败状态，输出两种分辨率及逐图几何/字体/按钮记录。不切换或保存当前场景、不连接服务器、不发传送请求。本包未写客户端、未启动 Unity；安装后的真实截图由统一接入者执行。

## 图像来源与准确边界

内置 imagegen 仅用于原稿动态区域清理，实际输出 1930×815。最终 `world_skin.png` 通过局部裁取清理结果复合回原稿 2560×1080；掩模外静态像素与原稿逐字节一致。`runtime-assets/*.generation.json` 逐图关联 `source/host-edit.json`、实际提示词、输入/输出 SHA。配置目标为 Images 2.5/Sunburst/max；本次工具没有型号/质量参数，实际型号与质量未确认，没有付费 API。

离线编译及静态像素检查记录见本目录 QA 与安装清单；不把它当作在线传送验收。重建工具位于相邻 `scene-select-ui-v1/fidelity-20261016`。
