# 05 天音少女：本轮停止记录

用户最新要求：必须确认 GPT Image 2.5 后才继续新图；旧素材不重做、不重标。当前没有生成调用进行中，没有新增 HD 图，也没有正式视觉审批。

本轮只有一次实际返回的内置 image_gen 调用，发生在旧 GPT Image 2.0 授权阶段。真实返回已经保存：
- raw.png：1254×1254 RGBA，4×4原生网格；单格约313/314px。SHA256 bb7c053a78f77fb57f7110b34a0f98f428ef44eae60aa080bda187b62a4b2669。
- prompt.txt：调用的完整原提示词。
- tool-result.json：真实 output_hint、原始保存路径、SHA、当时 requested 与未暴露的 actual 状态。

该图存在低原生格分辨率和散落边缘伪影，拒绝用于交付，未导入 pipeline。原始生成路径仍保留。本轮此前的巨大内联 image_url 序列化命令被卡住并中断；已改为保存原图二进制和真实返回的 output_hint，而不是把数 MB 数据URL塞入命令。

只读核实当前 V13：60个来源记录=52walk+8idle。S/E/N各16，NE4，SE/SW/W/NW0；缺76walk。walk目录另含3条strip，因此glob得到55 PNG并不代表55动作。common_scale0.84，root[256,471]，alignment v2未改。

原生cell只读统计：8idle为443/444px；43walk为627×627；9walk为1254×1254。未重做、重标或扩展旧C2PA审核。没有HD pilot目录。

待解决：确认可使用2.5的真实生成入口；之后按独立V14HD合同处理剩余新图。旧候选未进行完整136源重建或最终浏览器视觉验收，不能stage或正式发布。公共工具、全局进度和正式client均未修改。
