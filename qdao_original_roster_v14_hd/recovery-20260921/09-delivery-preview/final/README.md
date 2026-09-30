# 09 竹弓少女 · 最终离线素材包

128 张行走（8 方向 × 16）及 8 张独立站立，均为 1024×1024 透明 PNG。
直接打开 [index.html](index.html) 审阅；全部图片使用包内相对路径，无需原图或网络。
循环为 30 毫秒/帧、480 毫秒/圈。离线通过依据见 [acceptance.json](acceptance.json)，客户端和 Unity 接入未执行。

| 方向 | 浅底循环 | 深底循环 | 联系表 | 首尾 |
|---|---|---|---|---|
| N | [GIF](preview/N-light-30ms.gif) | [GIF](preview/N-dark-30ms.gif) | [16帧](preview/N-light-contact.png) | [15→16→01→02](preview/N-light-seam.png) |
| NE | [GIF](preview/NE-light-30ms.gif) | [GIF](preview/NE-dark-30ms.gif) | [16帧](preview/NE-light-contact.png) | [15→16→01→02](preview/NE-light-seam.png) |
| E | [GIF](preview/E-light-30ms.gif) | [GIF](preview/E-dark-30ms.gif) | [16帧](preview/E-light-contact.png) | [15→16→01→02](preview/E-light-seam.png) |
| SE | [GIF](preview/SE-light-30ms.gif) | [GIF](preview/SE-dark-30ms.gif) | [16帧](preview/SE-light-contact.png) | [15→16→01→02](preview/SE-light-seam.png) |
| S | [GIF](preview/S-light-30ms.gif) | [GIF](preview/S-dark-30ms.gif) | [16帧](preview/S-light-contact.png) | [15→16→01→02](preview/S-light-seam.png) |
| SW | [GIF](preview/SW-light-30ms.gif) | [GIF](preview/SW-dark-30ms.gif) | [16帧](preview/SW-light-contact.png) | [15→16→01→02](preview/SW-light-seam.png) |
| W | [GIF](preview/W-light-30ms.gif) | [GIF](preview/W-dark-30ms.gif) | [16帧](preview/W-light-contact.png) | [15→16→01→02](preview/W-light-seam.png) |
| NW | [GIF](preview/NW-light-30ms.gif) | [GIF](preview/NW-dark-30ms.gif) | [16帧](preview/NW-light-contact.png) | [15→16→01→02](preview/NW-light-seam.png) |

逐图实际模型、质量和来源映射见 [sources/index.json](sources/index.json)。工具未披露的字段仍为 null；配置目标不能替代实际版本证据。
历史请求、回执、精确提示词、生成记录与加工记录保持原字节，见 [evidence/index.json](evidence/index.json)。原记录里的 pending/canPublish 字段是当时状态；本次验收单独保存在 acceptance.json。
本包不含生成原图。09 原图、拒稿和中间图已按 SHA 校验清理，结果见 [cleanup-result.json](cleanup-result.json) 与 [retention.json](retention.json)；正式角色肖像、设计成图及其他角色保留。
历史绝对路径保留为来源事实；清理后由哈希与包内文字证据追溯。原图已不在，不能再重新读取原图验像素。

本次生成对应的宿主缓存原图也已逐文件核对 SHA 后删除，记录见 [host-cache-cleanup.json](host-cache-cleanup.json)。
