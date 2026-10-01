# 本批模型核对

2026-09-30 已搜索并打开 [OpenAI 官方 Sunburst 模型页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)，页面将 Sunburst 列为最强图像生成编辑模型，并列出 max 质量。本批保持既有目标 gpt-image-2.5-sunburst / max；未修改共享配置。

实际调用采用内置 image_gen.imagegen，仅有 prompt、referenced_image_paths、transparent_background 参数。model 与 quality 未开放，实际版本与质量均为 null / 未确认。配置目标与官方公告不证明本次实际使用型号。逐帧请求和工具输出另行记录。
