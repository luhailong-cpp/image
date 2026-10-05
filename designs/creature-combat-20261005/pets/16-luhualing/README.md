# 露华灵 · 战斗动作

**正在制作，尚未完成验收。** 原有墨青短发露华女仙，米白青瓷纱袖、紫釉露壶与桂枝露珠；只补受击、普攻、施法。

|动作|每向帧数|每帧时间|E/W合计|
|---|---:|---:|---:|
|hit|6|40ms|12|
|attack|12|30ms|24|
|cast|16|45ms|32|

E为朝右下的斜前视；W为朝左上的真实斜后视。每帧独立AI生成，不镜像、不复制、不插值。成品路径为 `runtime/<action>/<E或W>/NN.png`，1024×1024 RGBA；pivot为左下坐标[0.5,0.08]，顶部原点锚[512,942]。

- [当前状态](STATUS.md)
- [动作姿态合同](POSES.md)
- [正常、慢放与逐帧预览](preview/index.html)
- [帧清单](manifest.json) 与 [技术检查](validation.json)
- [SHA256清单](SHA256SUMS.txt)
- [模型核对](MODEL_VERIFICATION.json)

本批采用宿主内置 `image_gen.imagegen`。目标沿配置 GPT Image 2.5 Sunburst / max；实际工具无型号与质量选择器，未返回可核实型号与质量，逐图记为null。官方目标核对见 [OpenAI模型页面](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)，不能用该公告证明每次真实返回型号。

每张原生记录位于 `records/<action>/<direction>/NN.generation.json`，其中链接实际prompt与工具receipt。每张正式PNG旁的 `.png.generation.json` 保存统一缩放导出、原图SHA与原生记录。原生1254×1254整画布统一缩至896×896，贴入1024画布[64,69]，不逐帧调脚点。后处理不冒充新的AI姿态。

身份参考和主要画法样板为Image内跨窗口公共来源，保持只读。最终确认后按根素材保留规则删除本目录原生候选和加工图，保留逐图文字来源与当前正式资源。当前仍在制的唯一原生稿暂保留。

未接入客户端；透明、SHA或数量检查不等于美术、连播或客户端通过。
