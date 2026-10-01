# 本角色生图设置核对

2026-09-30 读取共享配置并实时核对官方页。[模型说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)列为最强图像生成与编辑模型，支持 low/medium/high/xhigh/max/auto；[发布说明](https://openai.com/index/introducing-chatgpt-images-2-5/)列出 ChatGPT、ChatGPT Work 与 Codex 内置开放。

本批目标沿用 gpt-image-2.5-sunburst / max。未改共享配置。实际调用 image_gen.imagegen 只开放 prompt、referenced_image_paths、transparent_background 等参数，无 model/quality 选择器；所有结果实际型号和质量仍为 null（未确认），不能从公告或目标推断。每张图片旁的 .generation.json、.request.json、.prompt.txt、.tool-result.txt 保存当次证据。

