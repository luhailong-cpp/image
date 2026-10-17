# 聊天 UI 原画还原 · 清理底板

2026-10-16：以现存世界聊天原画为唯一编辑对象，使用宿主内置 image_gen 移除动态文字、头像、消息气泡及分享卡，保留空白控件、静态装饰与淡山水，供原生 UI 叠加内容。未修改客户端。

- [干净底板](assets/world-clean-skin.png)：实际原生 1932×814，RGB PNG；未插值或裁切。工具输出比 1931×814 的原图宽 1 像素。
- [逐图模型／质量／来源记录](assets/world-clean-skin.png.generation.json)：配置目标 Images 2.5 / Sunburst / max；实际型号与质量未披露，均为未确认，不能当作已显式锁定。
- [实际提示词](world-clean-skin.prompt.txt)与[工具结果文字记录](world-clean-skin.tool-result.json)。
- [原画目标](../02-world.png)永久保留，本次未覆盖。

底板已去除交互文字、人物与消息内容；外侧挂联文字、灯笼、葫芦、关闭 X、表情／分享图标和按钮框保留。聊天区被原消息遮挡的山水由模型重建，不能声称恢复了未知原始像素。接入时继续按原画坐标校准，并尽量从原画保留确定性的静态边框与装饰。

同日各追加一次内置编辑，完成群组与谣言清理底板，仍未修改原画或客户端。

| 页面 | 清理底板 | 逐图记录 | 实际提示词／工具结果 |
|---|---|---|---|
| 群组 | [groups-clean-skin.png](assets/groups-clean-skin.png) | [模型与来源](assets/groups-clean-skin.png.generation.json) | [提示词](groups-clean-skin.prompt.txt) · [工具结果](groups-clean-skin.tool-result.json) |
| 谣言 | [rumor-clean-skin.png](assets/rumor-clean-skin.png) | [模型与来源](assets/rumor-clean-skin.png.generation.json) | [提示词](rumor-clean-skin.prompt.txt) · [工具结果](rumor-clean-skin.tool-result.json) |

这两张同为原生 1932×814 RGB PNG，实际型号／质量未披露。群组保留三栏、左侧列表卡及右侧空头像框；顶部选中勾被清掉、首卡空置顶牌移位，接入时从原画或原生层修正。谣言保留四张大卡面及空事件框；底部灰色结束按钮多出的右箭头需按原画修正。所有局部差异已写入逐图记录，不将 AI 清理结果宣称为原画逐像素复现。
