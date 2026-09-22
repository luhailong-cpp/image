# 04 NW04 残边修复复核 — 2026-09-21

建议将 **NW04-edge-v4** 送入完整 NW 循环预览。此结论只覆盖单帧残边、尺寸、姿势与来源复核，尚非整方向或角色批准。未写 canonical、未调用收费 API。

本子任务共调用内置 `image_gen` 2 次：v3 保持了原构图并清除紫边，但玉环中心遗留绿色半透明填充；v4 仅针对该孔再次修图。v3/v4 的原生 raw、精确 prompt、request、完整 generation receipt、真实 output_hint、默认输出路径与 provenance 均已保留。没有复制、镜像或插值凑动作，也没有更改逐帧缩放。旧稿与 v2/v3 均保留。

实际型号/质量为 **host-managed-unverified**；工具无 model/quality 选择器，C2PA 软件值仅 `gpt-image`，不作为 2.5 或 2.0 已显式选中的证据。未验证 C2PA 签名。

| 项目 | 原 NW04 | v4 |
|---|---:|---:|
| 原生单帧 | 1254×1254 | 1254×1254 |
| 正式候选画布 | 1024×1024 | 1024×1024 RGBA |
| common_scale | 0.84 | 0.84 |
| 可见主体高度 | 760px | 761px |
| 上身轴 / 脚底 | 512 / 942 | 512 / 942 |
| body_scale | 0.498257 | 0.498483 |

高度差 +0.13%，body_scale 差 +0.045%。原图原生 alpha>8 主体 bbox 为 `[263,67,1072,1176]`，保留顶部 67px、底部 78px 的空白；没有 v2 的放大问题。现有标准管线使用 `1024/1254×0.84` 整帧统一缩放，再按既定规则平移。记录见 [geometry-comparison.json](geometry-comparison.json)。

对照原始 NW04 与 v4 深/浅底 PNG：棕色发髻、绿色飘带、盾牌、法杖、衣服花纹和两靴姿势继续保持；屏幕左靴着地、右靴抬起露棕色鞋底。未见原图发梢、飘带、杖柄和玉环处的明显紫边。画面边缘没有裁切。

v4 玉环孔中心 raw 像素 `(1003,620)` 为 alpha=1；现有 alpha≤8 清理后，输出中心 `(765,561)` 精确 RGBA `[0,0,0,0]`。深/浅背景均可透过孔中心。新 raw 的大部分主体 alpha 接近 253，不能声称所有内部像素均为 255；正常深/浅底复核未见明显泛透或褪色，完整循环仍应检查与其他帧的颜色衔接。

未修改 verifier 的独立单帧重建通过，状态 `partial_sources_pending_visual`，native 最小边 1254、upscaled_frames=0。来源原默认输出仍在用户 `.codex/generated_images` 路径，工作目录 raw 与其 SHA 一致。

- [1024 透明候选](staging/candidate/04_mountain_guardian_boy/walk/NW/04.png)
- [深底新旧对比](NW04-old-new-dark.png)
- [浅底新旧对比](NW04-old-new-light.png)
- [导入和重建记录](staging/candidate/04_mountain_guardian_boy/recovery-bindings/NW04-edge-v4/import-result.json)

候选 SHA-256：`e9f942771b41f068d1854338b172917e2dfd9a39d590dead91b37ca3a2948dd9`。
原生 raw SHA-256：`b1bfdb1eceea674c8514e8fe13560822de07baad20705a7408c6cee5f4af497e`。

下一步：在完整 NW 16 帧、30ms 循环中与 NW03/NW05 及首尾接缝一起复核，不使用这个单帧报告替代整方向的验收。
