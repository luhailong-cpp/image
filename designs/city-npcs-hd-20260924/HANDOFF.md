# 主城 NPC 接续说明

交接时间：2026-09-24T11:09:19.839636+00:00。用户要求复制到新窗口继续；当前窗口不再启动新生图。

## 任务与最终授权

为主城绘制 23 位静态 NPC。用户已明确选择截图中的 NPC（杨镖头、月老、善财童子等），不是宠物或金甲黑熊坐骑。当前任务不涉及战斗怪物替换、动画、客户端接入。

风格必须融合：**原有 Q 版道家设定 + image/designs 已确认的圆润、明亮干净、细腻手绘画法 + 中国春节、中秋喜庆气质。** 保持每位人物的职业、年龄、脸型、主色、短身短肢比例和标志道具。节庆元素加入衣缘、发饰、腰饰、道具：红结、暖金团花/云纹、月纹玉佩、桂花、玉兔香囊等，疏密有序。

**用户最终指令：『api收费就不要，不收费就继续』。严禁付费 API/CLI；只用当前会话宿主内置 image_gen。此前 API 选择已被用户撤回，从未执行付费 API。不再要求 API Key，不再重复询问出图入口。**

## 实际进度

已落盘 **15/23 张**原生透明成图，见 `native/`。已完成：01 杨镖头、02 屠娇娇、04 辛仁皑、05 北斗星使、08 阵营战表彰大使、14 朱雀、15 苏苏、16 月老、17 无名药铺老板、18 仙界神捕、19 无名武器店老板、20 善财童子、21 段铁心（补全）、22 云游大仙（补全）、23 店铺掌柜（补全）。

剩余 **8 张**：

| 编号 | 角色 | 状态 |
|---|---|---|
| 03 | 董老头 | 待重试：首稿背景不合格 |
| 06 | 赤灵尊神 | 待生成 |
| 07 | 擂台管理员 | 待生成 |
| 09 | 镇魔道人 | 待生成 |
| 10 | 车夫 | 待生成 |
| 11 | 无想僧 | 待生成 |
| 12 | 无意僧 | 待生成 |
| 13 | 陆压真人 | 待生成 |

03 董老头失败首稿已保留：`native/attempts/03-dong-laotou-attempt-01.png`，存在不合格朦胧光晕背景；不能当透明正式图交付。可在保持人物和衣饰的前提下用内置 image_gen 重做纯透明背景，或重新生成。

05 北斗星使与08大使是在交接时从对应工具输出目录找回并视觉检查后归档。记录明确说明 tool output_hint /部分调用参数未取回，不能补造证据。05 的实际 prompt 已从预先保存文件找回。

## 文件位置

- 工作区：`E:/work/image`
- 本批次：`E:/work/image/designs/city-npcs-hd-20260924/`
- 成图：本批次 `native/`，每图配 `.prompt.txt`、`.png.generation.json`、`.png.provenance.json`
- 全部角色计划与身份/参考路径：`batch-plan.json`
- 原准备提示词：`prompts/`（注意其中具体 API 像素目标是历史计划，内置续做时必须调整，下文说明）
- 旧23位角色与原始截图：`E:/work/image/designs/city-npcs-20260924/`，其中 `manifest.json` 对应原画路径；`references/` 保存8张用户截图
- 主要已确认画风：`E:/work/image/designs/team-ui-v2/team-ui-v2.png`
- 本批融合示例：`native/01-yang-biaotou.png`、`native/16-yue-lao.png`、`native/20-shancai.png`。示例只辅助手法，不复制这些角色的脸和职业道具。

## 开始前读取

项目 `AGENTS.md`、`designs/README.md`、`config/image-generation.json`、`docs/IMAGE_MODEL_POLICY.md`、README接手文档、`docs/QDAO_ART_DIRECTION.md`、UI_SPEC第2节，以及 imagegen / generate2dsprite 技能。配置目标为 gpt-image-2.5-sunburst / max；**内置工具没有 model/quality/size 选择器，实际具体版本与质量未确认，不能宣称已显式锁定2.5/max。**

当前实际原生尺寸主要是1122×1402，另有941×1672和1254×1254。已试请求2160×3840但没有返回该尺寸。交付必须如实记录，不能把放大图称为原生4K。用户已接受继续内置入口，不要因此再次阻塞。

## 剩余角色出图步骤

1. 先检查 `native/*.png`，以实际文件和记录为准，避免重复已完成角色。
2. 读取 `batch-plan.json` 相应条目及 `prompts/` 文件。把 `target canvas 2160x3840/2560x3200` 句改成『highest native detail available through built-in host』。一般使用4:5构图，瘦长可2:3，宽翼用正方形；保留短Q版比例，人物及所有道具完整，要求8%透明边距。
3. 实际附两张图：①team-ui样板为主要画风；②该NPC的旧图为身份/脸型/主色/姿势。若只附两张，删掉提示词Reference3句。若第三张附融合样稿，强调只参考装饰手法，不复制其人物身份。
4. 用内置 `image_gen` 单角色出图，真正透明alpha PNG，全身，无场景/地台/阴影/UI/标签。不得调用付费API。
5. 保存原始返回文件，检查完整轮廓、身份、画风、透明背景，明显裁切或多余背景才重试。保留失败尝试的独立记录。
6. 每张保存模型/质量目标与实际证据的差别、实际尺寸、哈希、生成时间、实际prompt和参考用途。不确认的参数写null/未确认。

## 已验证的工具通道与坑

- 本环境普通 exec、view_image、image_gen 的 referenced_image_paths 曾报 Windows sandbox-helper setup 错误。`exec_command` 使用 `sandbox_permissions: require_escalated` 可读写工作区；这是环境故障，不是用户未授权绘图。
- 参考图可用 Pillow 仅制作**内存 JPEG 预览**，base64由exec输出，然后 `functions.image('data:image/jpeg;base64,' + result.output.trim())` 显示。不要用text打印大段base64。两幅参考实际显示后，下一次调用 `image_gen({prompt, num_last_images_to_include: 2})` 已反复成功。不要把脚本绘图替代AI角色创作。
- 调用先 `@exec yield_time_ms:120000`；可启动promise后 `yield_control()`，再等待返回，维持进度更新。新用户消息可能重置functions store并使旧exec cell句柄失效，所以尽早落盘prompt、输出路径和记录，不依赖内存store跨新消息。
- 根当前窗口的生成目录：`C:/Users/luyua/.codex/generated_images/01a0d23f-b48f-7911-b9e6-12909ca754d2/`。
- 02–05协作目录：`C:/Users/luyua/.codex/generated_images/01a0d240-e2ea-76f0-a8df-d7b88c0de91e/`。已找回最后未收录05；不要再从这两个目录猜图替代缺失角色。
- PNG中的C2PA仅确认ChatGPT / gpt-image系列；未做签名密码学验证，不说明具体2.5/2.0或max。

## 已备辅助工具

`tools/record_builtin.py <job.json>`：仅复制已有生图文件并记录来源，不发起生图或API。job字段可参考 `tools/root-record-14-zhuque.json`，至少source、destination（相对批次）、prompt、toolOutputHint、status、references、numRefs、referenceCompleteness、visualReview。C2PA解析器引用旧批次 `tools/inspect_image_provenance.py`。

`python tools/make_delivery.py`：核查23个编号、生成记录哈希、尺寸、RGBA、alpha透明和画布边缘；缺图会输出remaining并退出。齐全后生成manifest.json、overview.jpg、qa-dark.jpg与预览派生记录。原生PNG不做放大。该工具尚未完成整批成功运行。

## 最后交付

补齐剩余图后，运行检查，查看浅底/深底总览；纠正真正可见问题。重写本批README为最终状态，列出23张原生尺寸和对应生成记录，强调未使用付费API。将native/成图+逐图prompt/记录、manifest、README、总览与validation打包成新的ZIP。不要覆盖旧批次的旧ZIP；不要修改客户端或其他宠物任务目录。

第21–23位属于截图仅局部可见的职业原创补全（段铁心、云游大仙、店铺掌柜），保持这一标注；店铺掌柜原截图名字不全，不能编造为确定原名。
