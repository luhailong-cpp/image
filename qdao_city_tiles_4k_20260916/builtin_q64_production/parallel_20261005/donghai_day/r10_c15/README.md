# 东海渔村日景 r10_c15

本块正在收尾。16 张原生细节片已经齐全，内部接缝与东侧导图残缝已修复；北公共边和东公共边的颜色匹配仍在核查。`output/r10_c15.png` 目前仍为初始拼合候选，不能据此判断本块或整城验收完成。当前状态与候选校验值见 `current-work.json`。

- 正式目标：4096 × 4096 PNG；整城坐标 x=57344、y=36864，块号 r10_c15。
- 原生素材：4 × 4 张，每张 1254 × 1254，包含 1024 × 1024 有效区域和四边各 115 像素上下文。4096 图块由原生素材拼合，不是单次原生 4K，也没有将低清导图放大作为成品。
- 画面保留浅色平台、石墙、柱桩、绳索与投影的布局及几何，沿用已确认的 `designs/gameplay-ui/04-guild.png` 手绘材质。
- 北邻 r09_c15 固定 SHA-256：`33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff`。本块修补没有改动北邻像素。

## 逐图来源与模型记录

所有 AI 图均使用宿主内置 imagegen；当次配置目标与实际提交值分别记录。工具没有披露实际模型版本及质量档位，因此记录中的 `actualModel`、`actualQuality` 均为 `null`，不把配置目标或提示词当作实际返回版本。

| 用途 | 图片及记录 |
|---|---|
| 16 张有效原生细节片 | `native/r01_c01.png` 至 `native/r04_c04.png`；每张旁有 `.generation.json`，对应 `prompts/` 与 `guides/`，参考图用途和 SHA 记录于各图记录内 |
| 原生布局结构参考，仅用于生成 | `guides/local-structure.png` 及其记录，不计为高清成品 |
| 内部石墙导图残缝修补 | `repairs/internal-wall/edited-native.png.generation.json` |
| 北边左补片 | `repairs/north-joint/n2/edited-native.png.generation.json` |
| 北边右补片 | `repairs/north-joint/n3-narrow/edited-native.png.generation.json` |
| 东侧石墙导图残缝修补 | `repairs/east-guide-joint/edited-native.png.generation.json` |
| 北边最右木柱与斜栏杆连接修补 | `repairs/north-right-joint/edited-native.png.generation.json` |
| 原生拼合来源链 | `output/assembly-manifest.json` |
| 内部修补和颜色场 | `repairs/internal-integrated-v2/manifest.json` 及其引用 |
| 东侧修补与冻结范围 | `repairs/east-integrated/manifest.json`、`visual-review.json` |
| 最右北接与木柱有限修色 | `repairs/north-right-color-v3/manifest.json`、`visual-review.json` |

原生图不做放大；本地处理仅包含按实际像素拼合、窄接缝权重以及已记录的有限 RGB 颜色场。缩小总览仅用于预览，不能代替原像素接缝检查。拒稿、旧候选和中间图片在最终资源与引用确认后清理，来源文字和 SHA-256 记录保留。

## 验收范围

内部检查包括 6 条完整内缝、9 个交点、4 个角和补片插入边。北邻、东邻及四块交会另外核查。西侧 r10_c14、南侧 r11_c15 尚未完成的邻块不计为已验收公共边；单块像素验收也不代表整城 256 块或客户端验收完成。
