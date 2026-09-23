# 08 炼丹童子 N / NE 静态选稿

范围内完成 32 张独立行走帧及 2 张独立 idle。静态检查已通过；浏览器动态播放由主任务接续，未做 Unity 或正式客户端验收。

- 选稿：[N-NE-selection.json](N-NE-selection.json)
- 逐帧检查与准确库存：[N-NE-review.json](N-NE-review.json)
- 离线预览：[n-ne-review-final-v1](revisions/n-ne-review-final-v1/index.html)

每张选用稿原生 1254×1254，导出 1024×1024 RGBA。统一整格缩放 0.88，脚底有效像素锚点 (512, 942)。34 个来源 SHA 和 34 个导出 SHA 均独立；没有镜像、复制、插值或变形生成姿势。4 个深浅底 GIF 各 16 帧，每帧 30ms、每圈 480ms。

N01 / N09 为相反支撑腿。NE09-v3 以近侧右腿在前遮挡远侧左腿、右腿向左后伸，区别于 NE01 的近右腿领先；NE06–12 与其重接。NE14/15-v1 因跨步过大拒用，v2 缩小为连续过腿与预接触阶段。N15-v1 因丹炉、药瓶换手拒用，v2 已修正。

已检查深浅底全帧联系表、脚髋原尺寸裁图、15→16→01→02 静态接缝及两张 idle。静态检查不代替动态验收。共享构建清单仍把其它六方向列作缺失，本报告只覆盖 N/NE，范围内无缺帧。

配置目标为本批次 gpt-image-2.5-sunburst / max；实际工具无型号、质量选择器，返回值未披露，所有新图 actualModel / actualQuality 保持 null、host-managed/unverified。逐图精确 prompt、request、真实 output_hint 回执及 raw SHA 可从修订 evidence 和 processed 来源记录追溯。

48 张真实来源中选用 34 张，拒稿 14 张；另有 N13-v1、NE13-v1 两份中断未返图请求，不计图片。原图仍用于当前多方向合并和最终审核引用，本阶段未清理。

## 拒稿

- walk-N-02-v1：Wrong support half-cycle: anatomical left sole faces camera while frame01 and frame03 keep left support and right trailing; use N02-v2.
- walk-N-08-v1：Both boots show their soles toward camera, with insufficient support-foot contact for an ordinary walk; use N08-v2 which restores right support transition.
- walk-N-14-v1：Left foot phase insufficiently advanced; v2 gives intermediate foot height.
- walk-N-15-v1：Props swapped hands.
- walk-NE-06-v1：Old phase sequence failed anatomical left/right alternation; replaced in corrected knee-occlusion sequence.
- walk-NE-07-v1：Old phase sequence failed anatomical left/right alternation; replaced in corrected knee-occlusion sequence.
- walk-NE-08-v1：Old phase sequence failed anatomical left/right alternation; replaced in corrected knee-occlusion sequence.
- walk-NE-09-v1：Near thigh remains in first-half forward overlap; v2 redraws the near thigh across the far thigh for opposite-half support, making knee ownership more legible.
- walk-NE-09-v2：Same near/right leg leading as frame01; no anatomical opposite contact.
- walk-NE-10-v1：Old phase sequence failed anatomical left/right alternation; replaced in corrected knee-occlusion sequence.
- walk-NE-11-v1：Old phase sequence failed anatomical left/right alternation; replaced in corrected knee-occlusion sequence.
- walk-NE-12-v1：Old phase sequence failed anatomical left/right alternation; replaced in corrected knee-occlusion sequence.
- walk-NE-14-v1：Stride too wide, causing abrupt inward movement into frame16; compact v2 replaces it.
- walk-NE-15-v1：Stride too wide, causing abrupt inward movement into frame16; compact v2 replaces it.
