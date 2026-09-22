# 04 西南行走恢复与预览审计

SW14/15/16 已保存真实回执中的精确提示词、原生 PNG 来源检查，并按 `.84` 全角色固定比例导入本目录独立 staging。三张均为原生1254×1254、输出1024×1024 RGBA，逐阶段独立像素重建通过；最新三个 validation 绑定三帧齐全后的同一 manifest。原图、回执和宿主管理型号记录保真，没有收费 API。

混合预览使用旧 V13 SW01/05/09/13、现有 V14 SW02/03/04/06/07/08/10/11/12，以及本次三张 staging 帧；旧512只在预览里按同一世界尺寸显示，没有改写旧输出。16张真实PNG均有逐帧路径/SHA，身体比例CV=0.0219165。两个GIF解码均确认16帧、每帧30ms、每圈480ms。

- [逐帧与循环HTML](preview/index.html)
- [深底30ms GIF](preview/SW-30ms-dark.gif) / [浅底30ms GIF](preview/SW-30ms-light.gif)
- [深底16帧总览](preview/SW-contact-dark.png) / [浅底总览](preview/SW-contact-light.png)
- [SW16到旧01的脚部近景](preview/SW16-to01-feet-closeup.png)
- [逐项视觉结论及证据SHA](visual-observations.json) / [导入与来源验证](import-summary.json)

目前**不批准完整SW方向**：SW14的早降相位可读；SW15已较接近落步，须配合修订16检视相位；SW16的前摆靴从15的屏幕右下跨到屏幕左前，靴底明显朝镜头，接旧01又回到屏幕右下，脚横向位置和裤腿遮挡在16→01间跳变，建议重画16。法杖正面镂空已经存在于原SW12，未误判为新引入身份缺陷。三张新输出浅深底检查未见明显新增连续紫边；旧01/13的暖色和历史残边保留。

实际浏览器动态审核尚未完成：本会话 `cua.createBrowserTab('iab',...)` 返回 `Browser is not available`，`cua.listBrowsers()` 返回空列表。30ms GIF已制作并校验编码时长，静态逐帧和接缝已检查；这些不冒充已实际连播验收或Unity运行验收。

没有写canonical候选、旧资源或客户端，没有创建批准标记。`finish_sw.py` 用主任务指定 `04-tools/import_local_frame.py --staging-root` 导入，公共 helper 自行将导入前 staging 元数据备份到其 `history/`；没有改公共脚本。
