# 08 炼丹童子交接（2026-09-28）

仅负责 `08_alchemy_prodigy_boy`。素材制作、八方向离线目视验收、最终来源核验、授权图片清理及清理后复核全部完成。Unity／正式客户端接入未进行。

## 成品与预览

- 成品目录：`revisions/final-v1/runtime/`。
- [交互预览](revisions/final-v1/index.html)：八方向、深浅底、正常512／原尺寸1024、逐帧、完整循环及15→16→01→02接缝。
- [八方向GIF入口](revisions/final-v1/previews.html)：每方向浅底、深底各1个，16帧×30毫秒＝480毫秒无限循环。
- [清单与逐图SHA](revisions/final-v1/manifest.json)、[选稿](full-selection.json)、[离线验收说明](revisions/final-v1/FINAL-REVIEW.md)、[浏览器检查记录](revisions/final-v1/browser-review.json)、[接入数据说明](revisions/final-v1/INTEGRATION.md)。

| 方向 | 行走 | 独立站立 | 离线目视验收 | 浅底循环 | 深底循环 |
| --- | --- | --- | --- | --- | --- |
| N | 16/16 | 1/1 | 通过 | [N](revisions/final-v1/preview/N-30ms-light.gif) | [N](revisions/final-v1/preview/N-30ms-dark.gif) |
| NE | 16/16 | 1/1 | 通过 | [NE](revisions/final-v1/preview/NE-30ms-light.gif) | [NE](revisions/final-v1/preview/NE-30ms-dark.gif) |
| E | 16/16 | 1/1 | 通过 | [E](revisions/final-v1/preview/E-30ms-light.gif) | [E](revisions/final-v1/preview/E-30ms-dark.gif) |
| SE | 16/16 | 1/1 | 通过 | [SE](revisions/final-v1/preview/SE-30ms-light.gif) | [SE](revisions/final-v1/preview/SE-30ms-dark.gif) |
| S | 16/16 | 1/1 | 通过 | [S](revisions/final-v1/preview/S-30ms-light.gif) | [S](revisions/final-v1/preview/S-30ms-dark.gif) |
| SW | 16/16 | 1/1 | 通过 | [SW](revisions/final-v1/preview/SW-30ms-light.gif) | [SW](revisions/final-v1/preview/SW-30ms-dark.gif) |
| W | 16/16 | 1/1 | 通过 | [W](revisions/final-v1/preview/W-30ms-light.gif) | [W](revisions/final-v1/preview/W-30ms-dark.gif) |
| NW | 16/16 | 1/1 | 通过 | [NW](revisions/final-v1/preview/NW-30ms-light.gif) | [NW](revisions/final-v1/preview/NW-30ms-dark.gif) |

总计128/128真实行走、8/8独立站立；没有缺方向或缺帧。全部交付1024×1024透明RGBA PNG，真实原生生成图为1254×1254。统一脚点记录为左上原点 `(512,942)`。

## 制作与验收边界

实际检查了全16帧接触表、脚部1:1、正常与放大浏览器播放、深浅底、交替迈腿、支撑脚、比例、透明残边和15→16→01→02接缝。错误领腿、高踢腿、比例与步幅异常稿已排除并补画。细微发丝、服饰纹样与踝部绘制变化仍存在，本次所选稿未发现阻塞问题。

128张行走各自对应独立生成请求与原图；8张idle单独生成。不复制、镜像、插值、扭曲或平移某姿势凑动作。后处理只清除低透明度彩色残边、整格统一等比缩小并对齐脚点，不生成新姿势。GIF准确编码30毫秒/帧；浏览器按30毫秒时间线选帧，显示器刷新率可能跳帧，未声称测量屏幕硬件时序。

走宿主内置生图入口，无收费API调用。配置目标为 `gpt-image-2.5-sunburst/max`；实际入口没有提交或返回型号／质量参数，所以 `actualModel` / `actualQuality` 为 `null`，明确标记 host-managed/unverified。原角色肖像与已确认风格图均实际用于参考。S11/S14/S15/S16修订稿实际附本角色此前帧作为派生身份参考，需按真实请求和SHA回溯原肖像，不声称它们直接附过原肖像。

2026-09-28 清理前来源核验已通过：136个独立输出与136个独立原图SHA，原生1254×1254及最终1024×1024 RGBA逐图核实，5份已审阅快照与最终成品逐字节一致。审计0错误，5项说明性警告为4条已经核实的派生身份参考链，以及历史S站立请求未保存配置快照；没有伪造或补改历史请求。[清理前审计](revisions/final-v1/file-audit-before-cleanup.json)与[初次失败记录](../08-tools/audits/final-v1-file-audit.initial-failed.json)均保留。

## 保留与清理

最终136张PNG、配套预览／设计检查图、接入清单及全部逐图文字证据保留。原图、拒稿、回退和加工图片按用户2026-09-23确认规则已清理：本角色工作区删除1774个图片副本，另删除真实回执精确对应的186个宿主原图。最终保留136张游戏PNG与66张配套预览／设计检查图片。清理后逐图SHA、当前预览引用及16×30毫秒GIF时长复核通过；文字证据保留。历史request/receipt/prompt不改写；历史raw路径仅作来源记录，清理后不再代表图片仍存在。共享原角色肖像与确认风格原图仍是当前设计，不属于本角色加工副本清理范围。

仅修改本角色目录与本角色恢复提示，没有改其他角色、00–04、共享候选状态或客户端，没有Git提交、推送或Git清理。

## 后续范围

本窗口完成后停止，不自动继续下一角色。未来若另行授权客户端接入，第一步是读取 `revisions/final-v1/INTEGRATION.md` 与 `manifest.json`，并在实际游戏环境复核锚点、缩放、图集、排序与播放速度；不要恢复旧512图充当本次高清动作。

清理证据：[完成记录](revisions/final-v1/cleanup-completion.json)、[清理后复核](revisions/final-v1/runtime-audit-after-cleanup.json)、[清理前逐稿库存](revisions/final-v1/production-inventory.md)。全部136张素材及八方向离线验收通过，无待处理原图、无缺方向或帧号；本窗口在08停止。
