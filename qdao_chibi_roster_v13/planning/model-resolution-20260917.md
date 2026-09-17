# V13 本次模型能力核对

核对日期：2026-09-17。状态：用户已明确允许本次使用内置 GPT Image 2；后续角色基线已转向用户指定9adcf929提交原角色。

- 官方模型目录：https://developers.openai.com/api/docs/models
- 最新最高能力图像模型：https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst
- 已核实型号：gpt-image-2.5-sunburst（可固定 gpt-image-2.5-sunburst-2026-09-08），支持最高质量 max。
- 宿主文档：https://learn.chatgpt.com/docs/image-generation，当前明确写 Built-in image generation uses gpt-image-2。
- 当前内置工具实际仅支持 prompt、referenced_image_paths、num_last_images_to_include；无model/quality选择器。不能用提示词切换型号，不能宣称内置生成已用2.5/max。
- 项目AGENTS与docs/IMAGE_MODEL_POLICY.md要求每任务核对并禁止已知旧后端静默降级；尚无本任务API单独计费授权。
- 已向用户提供选择：本次明确允许内置2；或授权2.5 Sunburst API最高质量单独计费。等待回复期间继续基线冻结、参考准备、处理器和客户端兼容改造。
- 本机普通exec/node/view_image均遇到Windows sandbox apply deny-read ACLs初始化失败；require_escalated只读PowerShell可正常访问。该问题不是API密钥问题。参考图可用只读base64在工具结果显示。

本记录是能力核对，不是生图来源证据；每张实际生成图还需记录实际工具响应、原始文件、提示词和SHA。

## 用户已明确授权及更换基线

2026-09-17用户明确：“本次允许内置 GPT Image 2”，随后指定9adcf9291e4a867601868889a5965f3cd48630ba的q_daoist_character_pack_4096，要求用更Q版道家原角色制作16帧行走。该授权持续有效，无需再问绘图模型；不使用单独计费API。新任务目录qdao_original_roster_v13，不能沿用V12吕洞宾身份/验收哈希。
