# 符小虎 W 子任务交接

本子任务完成真正 W 左上斜背设计参考，以及受击 6 帧、施法 16 帧，共 22 张独立生成的 1024×1024 RGBA PNG。W 普攻 12 帧由根任务负责，本文件不声称其完成或验收。

- 身份/相机参考：`design/W-reference.png`（实际原生 1254×1254，持续引用的设计文件）。
- 正式帧：`runtime/hit/W/01.png` 至 `06.png`（40ms）；`runtime/cast/W/01.png` 至 `16.png`（45ms）。
- 每帧 PNG 旁有 generation.json；实际 prompt、receipt、失败和修正前文字证据在 records/W-*。
- 技术与静态检查：`records/W-QA/technical.json`、`records/W-visual-review.json`、两张 contact sheet。
- 独立检查页：`records/W-QA/index.html`，含正常速度、0.25 慢速、暂停和逐帧。

全部使用内置 image_gen。目标沿用本批 GPT Image 2.5/max 配置；工具未开放 model/quality 参数，实际型号与质量均记 null/未确认。每张以独立AI调用生成，无复制、镜像、平移补帧或插值。

本子任务导出只有固定整画布 1254→1024 Lanczos 缩放，未逐帧重排锚点。根任务已计划全部 W 统一 y=-4、E 统一 y=-15；应由根任务统一更新 operation、SHA、manifest 和技术报告。W 帧现在可交给根任务处理，本子任务不再改像素。

已实际逐张看全部生成返回图与最终全帧对照。hit03意外漫画标记已AI删除；cast08实体圆盘已AI改成透明能量球；cast10释放光效和尾巴完整；cast11增加了伸爪后的早期回收。技术检查22帧通过尺寸、RGBA、真透明、SHA一致、无重复和无alpha≥128触边。

**动态播放目视验收未完成。** 尝试 cua 内置浏览器返回“Browser is not available: iab”，浏览器清单为空。检查页已具备所需播放方式，但不能把静态检查或JS预览存在标成动态通过。未接入客户端。

素材保留：本宠目录未建立原生中间副本或拒稿图片备份，只有当前W设计参考、最终runtime、QA预览和文字证据。生成工具默认宿主缓存位于本宠目录外，本子任务遵守写入边界未删除它们。

