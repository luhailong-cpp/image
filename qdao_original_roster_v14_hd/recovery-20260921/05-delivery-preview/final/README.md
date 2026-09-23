# 05 天音少女最终交付

动作成品在 runtime/walk 和 runtime/idle；128张行走、8张独立站立，另runtime/portrait.png为正式1024肖像。index.html可离线打开，提供八方向30ms循环、逐帧、深浅底与512/1024显示。preview含各方向深浅底GIF、16帧总览和15→16→01→02接缝图。

素材与离线验收通过，非阻塞观察见offline-review.json；客户端接入、Unity运行验收、正式发布均未执行。manifest.json为当前路径和SHA权威清单。不要把frame数量或source审计单独当作视觉验收。

方向顺序：N/NE/E/SE/S/SW/W/NW。每方向walk/01.png–16.png，30毫秒每帧、480毫秒一圈。idle每方向独立一张，禁止拿walk代替。

60张既有512PNG保持原字节；76张高清PNG为1024透明RGBA，67本轮新选用加9既有NE。新动作均来自1254原生完整单帧，不包含镜像、插值或复制补帧。显示同世界尺寸时512的PPU=52、1024的PPU=104。alpha>8最后可见脚底行：旧512为471、新1024为942，身体轴分别256/512；逐图实测anchor以manifest为准。不要把旧512保存成1024冒充高清。

逐图png.generation.json和lineage保留模型/质量/请求/提示词/回执/来源SHA文字证据。实际内置工具没有披露型号或质量，不能声称锁定配置目标。收费API调用0。历史来源路径只用于追溯；原图、拒稿、回退和处理图在最终核验后按用户要求删除，删源前76张HD独立像素重建全部通过。

当前4096角色设计保留在仓库q_daoist_character_pack_4096/05_celestial_musician_girl_transparent_4096.png。本目录不含其他角色。
