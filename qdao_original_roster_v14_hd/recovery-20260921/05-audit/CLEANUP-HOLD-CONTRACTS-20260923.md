# 05 清理 HOLD 与当前入口补充核验

2026-09-23，只核验与记录，没有删除图片，没有改写入口。此报告补充 `CLEANUP-PLAN-20260923.json`，以用户最新 AGENTS 保留规则为准。

## 五张 HOLD 的结论

| 文件（仓库相对路径） | 结论 | 已核实依据 |
|---|---|---|
| `qdao_original_roster_v13/baseline/q_daoist_character_pack_4096/05_celestial_musician_girl_transparent_4096.png` | 可删除重复基线 | 与当前 `q_daoist_character_pack_4096/05_celestial_musician_girl_transparent_4096.png` 字节完全相同，SHA256 `f8cd360988a1d5d9b6aebb81d9868b5d4692aa520d7fcae1af9d525bf70e12f8`。当前设计保留。 |
| `qdao_original_roster_v13/candidate/05_celestial_musician_girl/portrait.png` | 保留一份最终接入肖像 | 1024×1024 RGBA，SHA256 `0c0564080d8515e0df789d336704c4ba5bb283d65d4167f48eb7e098d932cdaa`；逐像素等于当前4096设计的整图 LANCZOS 降采样。可原路径保留，或字节原样复制到 final 的配套接入目录后删旧副本。 |
| `qdao_original_roster_v13/candidate/05_celestial_musician_girl/walk/N/strip.png` | 可删除旧派生条带 | 8192×512，16格逐像素等于对应16张保留的512单帧。 |
| `qdao_original_roster_v13/candidate/05_celestial_musician_girl/walk/E/strip.png` | 同上 | 同上。 |
| `qdao_original_roster_v13/candidate/05_celestial_musician_girl/walk/S/strip.png` | 同上 | 同上。 |

肖像属于配套接入文件，不计入本次128行走+8站立。客户端 `Assets/Scripts/World/QdaoOriginalHdResourceIndex.cs:35–40,75–90` 明确137张＝portrait+136动作，`QdaoCharacterCatalog.cs:378` 校验肖像，`QdaoBoySpriteAnimator.cs:423–426` 也拒绝缺少1024肖像的外观。V14发布器 `tools/publish_original_roster_v14.py:186–187` 明确无runtime条带。当前客户端原版V13只装有00–03，V14目录不存在；05候选图并未被现有游戏运行时直接加载。以上为静态代码/资源盘点，不是Unity或游戏运行验收。

## 删除后的实际消费者与 05 专属修复入口

1. **最终预览。** `05-delivery-preview/revisions/complete-review-v1/index.html` 的 `Image.src` 只读取自身 `runtime/<slot>` 和自身 `preview/`，不读取 manifest 中的历史 `source`。final应同样自包含。每张最终图SHA、136槽、当前图片链接检查通过后，历史 `source/raw` 字段可保留，追加删除状态即可，不能把旧来源记录伪改成最终图。
2. **旧在线可打开HTML。** `05-audit/preview.html` 直接载入V13/V14候选NE图及同目录旧接缝；删除V14候选和旧接缝后会破图。`05-delivery-preview/revisions/ne-repair-v1/index.html`、`ne-repair-v2/index.html`、`complete-review-v1/index.html` 都读各自runtime/preview；删快照图片会破图。根代理可把这4个05专属HTML改成明确“历史版本已清理”的final链接/跳转，并保留旧manifest等文字记录。
3. **当前选用文件。** `05-delivery-preview/selected-overrides.json` 现有67个override指向staging；另9张新NE来自V14候选回落。它被 `build_preview.py` 消费。直接把path换成 `final/runtime/...` 仍会被该脚本第94行的 `CHAR in source.parts` 拒绝（final路径无角色ID）；脚本也仅接受pending状态。应将旧选用记录标为历史，增加明确 final manifest/current入口；若保留重建功能，则必须同步改成验证final自包含库存与SHA，不能只换字符串。
4. **四个方向选用表。** `05-generation/{NW,SW,W}-selection.json` 及 `SE-back-selection.json` 的 `rows[].output` 为staging；`05-tools/assemble_selection.py` 会读它们重新覆盖selected-overrides，还硬编码前10个SE的staging路径。建议将其标为历史作者工具并在已最终导出时明确停止/导向final验证；若要保持可执行，则更新四个表的active output以及该脚本硬编码，同时保留历史output/raw和SHA。
5. **交接入口。** `recovery-20260921/README.md:11` 仍写“NE03/16待返工、缺64walk”；`new-window-prompts/05_celestial_musician_girl.md:17` 与 `candidate/05.../HANDOFF_20260919_PAUSED.md` 是起始/历史状态。前者的05条目和05专属交接应指向final及验收文字；起始任务文件可加“已完成，请从final交接开始”提示，保留原任务文本。
6. **候选manifest与来源。** V13/V14的05 `manifest.json` 仍是incomplete候选，列出旧图。删除后不应作为当前入口；在05目录旁加明确历史状态/final指针即可。`processing/frame-sources.json`、逐图receipt/request、generation记录必须保留为历史证据。删raw后不再宣称可重新逐像素重建。

## 旧共享发布流程的边界

旧 `qdao_original_roster_v14_hd/tools/assemble_mixed_roster.py:353–360` 锁定V13整树清单和所有SHA；第402–435行重建动作并读取保存的原始肖像。任何V13原图/加工图/strip清理都会使旧流程不再可重跑，保留五张HOLD也解决不了。旧V13发布器还要求8条带（145图），但本次目标是V14混合136动作。不要据此继续保留全部中间图，也不要改其他角色或全局冻结证据；把05新final作为当前交付入口，记录旧重建流程已因新保留政策停止。正式发布若另行执行，需单独落实保留政策感知的137图接入器与客户端验收。

`qdao_original_roster_v13/inventory.json:106–107` 的05 baseline/restored路径仍为旧电脑 `E:\work\image\...`，不是当前真实运行时引用。保留文字SHA与原路径可追溯；05最终设计指针应明确指向当前D盘设计，不应为了这条过时路径保留副本。

本报告不改共享代码、全局清单、其他角色、不删目录。执行清理时逐文件复核绝对路径仍在workspace、SHA未变且最终引用已完整。
