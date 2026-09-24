# 本批模型核对

2026-09-24 已实际打开官方发布公告和 Sunburst 模型页。Images 2.5 已向 Codex 开放；Sunburst API 文档列出的最高显式质量为 max。本批沿用项目配置目标 gpt-image-2.5-sunburst / max，未发现需升级的型号或质量。

本次内置工具只接受 prompt 与参考图，没有 model、quality、size 参数。逐图记录实际提交 model=null、quality=null；返回只披露图像及保存提示，没有可验证的实际版本/质量。不能据此宣称每张图已锁定2.5、Sunburst或max。未调用单独计费的API/CLI，也未显式切换2.0。

- [Images 2.5 官方公告](https://openai.com/index/introducing-chatgpt-images-2-5/)
- [Sunburst 官方模型说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)

参考图本地输入通道遭遇 Windows sandbox helper 错误。读取已获授权的文件并以无落地路径的内存预览传入会话后，使用 num_last_images_to_include 生图；实际输入方式见逐图记录。
