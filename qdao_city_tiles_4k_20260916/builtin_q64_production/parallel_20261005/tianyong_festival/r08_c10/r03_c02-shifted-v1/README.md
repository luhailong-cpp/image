# r03_c02 移位627上下文：第一次实际输出

实际内置生成1次，返回1254×1254，native.png SHA `b94982ca3f36457d5eb59716f06b1d27d5ca8c76618622958c54ed7f1a9d48f1`。来源为当前v002的下627行，与v001对应区域逐像素一致；上627行原来缺失。全局 `[37773,31002,39027,32256]`，本块 `[909,2330,2163,3584]`。

宽象牙横带已生成；底部轮廓偏移最高约38px，超过允许4px，未做配准、未合入current。已实际看过全627行对比及直接回接。第二次实际AI修补和汇总见相邻 `r03_c02-shifted-repaired-v1/`。

实际提示词 `prompt.txt`，请求 `request.json`，真实工具输出提示与时间 `tool-response.json`，宿主路径/原字节SHA/配置/实际参数空值见 `native.png.generation.json`。配置目标gpt-image-2.5-sunburst/max；actualModel/actualQuality为null。未调用API。
