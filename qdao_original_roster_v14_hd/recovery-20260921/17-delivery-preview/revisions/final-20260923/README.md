# 17 灵篆书生：游戏素材交付

本目录包含128张行走帧（N/NE/E/SE/S/SW/W/NW各16张）和8张独立站立图。成品位于 `runtime/`，均为1024×1024透明PNG；各动作由独立原生1254×1254完整单帧导出。

打开 [index.html](index.html) 查看八方向、深浅底和正常/放大预览。逐方向GIF位于 `preview/`，均为16帧、30毫秒/帧、480毫秒/圈。客户端与Unity接入尚未执行。

- [delivery.json](delivery.json)：最终交付索引。
- [acceptance.json](acceptance.json)：绑定具体manifest SHA的离线验收。
- [manifest.json](manifest.json)：逐槽选稿、成品SHA与创建时状态。
- [source-evidence.json](source-evidence.json)：136个独立来源及863份文字证据；如实保留历史提示词差异和未披露的实际模型/质量。
- [runtime-recheck-20260928.json](runtime-recheck-20260928.json)：封包时的文件与GIF时长复核。

`manifest.json`和部分派生记录保留创建时的pending标志；后续验收以同一SHA绑定的`acceptance.json`为准。来源文本中的本机绝对路径是历史证据标识，预览只加载本目录中的相对资源，不依赖原图、旧快照或staging目录。

脚底锚点按画布和轮廓测量，不能将透明轮廓最低点等同于每只靴底：S04有1像素差，NE13支撑靴与摆脚尖有5像素斜后视投影差，已在验收中记录并接受。

最终manifest SHA256：`fecd8028b6facb779ee6f8f86d28243937912bca790cf61997368ecc1ceeea8d`。
