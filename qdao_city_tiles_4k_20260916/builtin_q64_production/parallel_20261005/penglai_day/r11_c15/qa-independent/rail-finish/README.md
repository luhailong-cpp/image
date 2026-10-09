# 船舷高光局部修补

按 `merge-manifest-v1.json` 的 `origin: [1600,2200]`，以 `replacement.png` 和 `alpha.png` 在原图上只合成一次；不要把完整替换图贴上去。`composite.png` 是 1254×1254 原尺寸回接检查图。

真实内置 AI 编辑来源为 `generated-v1.png`，输入为 `input.png`，实际附上 `04-guild.png` 作为风格参考。提示词见 `prompt.txt`，原始工具提示见 `tool-output.txt`。配置目标与真实提交参数分开记录：工具未开放型号和质量选择器，actualModel、actualQuality 均为 null，未确认。

修补两处白色倒角台阶；掩码沿高光形成两条窄带，侧面过渡 6 px，两端过渡 24 / 48 px，仅作用于 alpha。未缩放、形变、模糊图像或改变真实板缝，未修改内部 v5 原图。全幅与局部回接图已按原尺寸检查；最终整图由负责合并的 agent 统一审查。

每张 PNG 均附 `.png.generation.json` 来源及 SHA256。输入、生成源、replacement、alpha、composite 和两组局部 QA 图均可沿记录追溯。`validation.json` 记录精确重放、掩码外逐像素不变与基底 SHA 校验。
