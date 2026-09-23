# 05 天音少女最终来源与时长独立审计

审计快照：`D:\luyuan\wuxingqitan\image\qdao_original_roster_v14_hd\recovery-20260921\05-delivery-preview\revisions\complete-review-v1`。
快照 manifest SHA256：`b47adeff4c3889935c9475b5e527dea5e756ffa11b679cb2f0fb21ee779853f8`。
审计时间：2026-09-23T07:16:53.417697+00:00。

结果：**passed_source_and_timing_only**；仅代表文件、来源与时长检查，不代表视觉通过或客户端通过。

- 成品：128 张行走 + 8 张独立站立；136 个最终文件逐个核对文件 SHA、像素 SHA 与选用来源。
- 尺寸：{'512x512': 60, '1024x1024': 76}；旧 512 未放大成高清。
- 来源分组：{'preserved_v13': 60, 'retained_hd_ne': 9, 'new_recovery': 67}；67 个新选用稿的独立 raw、prompt、request、tool-result、receipt、元数据与重建记录逐个核对。
- 76 张高清帧重新只读像素重建，通过 76 张；保留的 9 张旧 NE 使用既有 evidence-shadow，不改历史 LF/CRLF。
- 8 张 idle 像素互异，且均不复用任何行走图的像素或原始格子。
- 16 个 GIF 均逐帧核对：每个 16 帧，每帧 30ms，每圈 480ms，无限循环。

## 缺证与差异

- 文件/来源问题行数：0；全局问题数：0。
- v1 的 `selected_revision=staging` 标签共 54 条；已按真实路径和 SHA 核验，不将标签误写视为来源造假。
- 历史 LF/CRLF 提示涉及 8 行；字节原样保留，细项见 JSON。
- 实际模型/质量由宿主管理且未披露；新图均保留目标配置、实际未提供的参数与未确认原因，不能据此宣称锁定指定型号或 max。

## 边界

未修改来源、选用配置或历史换行，未删除图片；未执行视觉批准、Unity 或正式客户端验收。此为删源前的当前字节核验，删源后仅能追溯文字与哈希记录。

[完整逐帧证据](FINAL-SOURCE-AUDIT-20260923.json)
