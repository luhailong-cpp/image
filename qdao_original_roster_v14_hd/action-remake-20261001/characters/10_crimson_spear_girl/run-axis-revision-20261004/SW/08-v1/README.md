# SW08 抬靴方向修复

内置 imagegen 局部编辑已完成并通过单帧与 SW07/SW09 对照审查。原来正对镜头的宽鞋底改为顺摆腿平面的鞋面和鞋尖；保留第08帧较高的膝盖姿势与第四支撑位置。runtime 未修改。

- 输入及配置快照：[request.json](request.json)
- 实际完整提示词：[prompt.txt](prompt.txt)
- 工具回执：[receipt.json](receipt.json)
- 1254 原生：[native.png](native.png)；来源记录：[native.png.generation.json](native.png.generation.json)
- 1024 审查派生：[review1024.png](review1024.png)；来源记录：[review1024.png.generation.json](review1024.png.generation.json)
- 前后与邻帧：[before-after.jpg](before-after.jpg)
- 审查：[visual-review.json](visual-review.json)、[technical-check.json](technical-check.json)

实际 model、quality 工具未披露，均为 null；配置目标保存在逐图记录，不冒充实际返回值。未插帧、未用相似变换制造新姿势。最终整组正常速度验收由根代理完成。
