# 天音少女普攻制作进度

记录日期：2026-09-30，America/New_York。

- 工作范围仅为 `attack/E/01–12` 与 `attack/W/01–12`，共 24 槽。
- 已完整读取本角色交接、共同契约、imagegen 技能及项目要求的风格和来源文档。
- 已实际查看身份肖像、E/W idle 和 `designs/jubaozhai-ui/02-characters.png` 四张参考。
- 已准备 24 份逐帧提示词，见 `prompts/attack-{E|W}-{01..12}-v1.txt`。
- `prompts/attack-plan-20260930.json` 保存逐帧阶段、精确预备提示词和预备参考输入。`submissionStatus: not_submitted` 表示仅准备，未真实调用。
- 本普攻工作单元未调用 `image_gen`，没有新候选、生成回执或选定图片。主协调报告两次受击调用和施法工作单元调用均出现 `image generation failed: network error: error sending request`，未返回图片；本轮不再提交普攻请求。
- 已创建 `selection/attack-E.json` 与 `selection/attack-W.json`，二者显式标明 `status: partial`，`frames: []`，缺槽各为 01–12。空选表不得用于要求完整序列的导出。
- `prompts/attack-preparation-check-20260930.json` 已核对 24 份提示词与预备参数逐字一致、对应方向 idle 引用存在、左扶琴右拨奏锁定和朝向正确，并保存提示词 SHA256。这仅证明制作准备文件完整。

预定制作顺序为 E/05 和 W/05 拨弦峰值，然后依据实际峰值图完成前后过渡。两方向分别独立绘制，解剖左手扶琴上段、右手拨奏；1024 画布、固定头身尺度和地根，禁止按包围盒逐帧居中缩放。目标命中姿态为 05–06，但最终帧号必须根据实际选图再确认。

当前完成状态：普攻候选 0/24，选定 0/24，runtime 导出 0/24，视觉连播未做，客户端接入及运行验收未做。准备稿不能计为图像交付。
