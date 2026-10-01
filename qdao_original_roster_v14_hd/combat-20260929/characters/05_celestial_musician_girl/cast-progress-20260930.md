# 天音少女施法生产记录 · 2026-09-30

本分工只负责 cast/E/01–16 与 cast/W/01–16，共32槽。当前候选0/32、选定0/32、runtime导出0/32；本记录不是已完成动作的视觉验收。

## 调用结果

唯一实际调用为 cast/E/09 v1。内置 image_gen.imagegen 返回：

`image generation failed: network error: error sending request`

没有图片、文件路径、output_hint、实际型号或质量元数据。没有重试，没有切换 API/CLI。

真实调用文本和输入参考保存在 [cast-E-09-v1-request.json](provenance/receipts/cast-E-09-v1-request.json)，完整失败记录在 [cast-E-09-v1-failed.json](provenance/receipts/cast-E-09-v1-failed.json)。时间为 clock.curr_time 读取的准备前与失败后 UTC 观察时间，工具自身未提供服务端时间。两份记录都包含当次配置快照，提交 model/quality 与实际 model/quality 均为 null。配置目标 gpt-image-2.5-sunburst / max 不能代表实际返回型号。

## 已完成的准备

- 实际读取本角色交接与共同契约；遵守角色与cast前缀写入范围。
- 实际 view_image 肖像、E/W idle及designs/jubaozhai-ui/02-characters.png，唯一调用实际附上肖像、E方向idle与主要风格参考。
- 完成32个独立逐帧动作描述和32个唯一提示词路径；[动作计划](prompts/cast-action-plan-20260930.json)逐槽区分失败与未提交。
- E/W使用对应参考各自独立绘制的提示词；维持1024画布、E根(x535,y934)、W根(x470,y934)、常态冠顶y126及对应512 idle的2倍比例。保持解剖左手扶上琴、右手拨弦。
- [E选表](selection/cast-E.json)和[W选表](selection/cast-W.json)均为partial，frames为空，分别列出缺帧01–16。
- 静态文字检查：32个prompt、32个计划槽、32个唯一prompt路径、无缺失prompt。JSON均可解析。

## 尚未完成

全部32张施法独立PNG仍缺失。未做透明/尺寸/哈希图片检查、选稿、统一导出、正常45ms/帧及慢放连播、深浅底视觉验收。没有新增或改动移动/站立/肖像，没有客户端接入或运行验证。

后续恢复内置图像通道后先继续释放关键姿态，再补前后过渡。不要把预写提示词计为候选；同槽新增成功输出使用不覆盖既有记录的版本与来源记录。最终释放标记需依真实选定图核定，当前09–10只是设计计划。

