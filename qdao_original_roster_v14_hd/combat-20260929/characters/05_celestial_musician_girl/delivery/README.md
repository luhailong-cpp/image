# 天音少女战斗动作续作状态 · 2026-09-30

**未完成：内置生图通道返回网络错误，当前候选与 runtime 均为 0/68。**

本窗口完整读取本角色交接与 COMMON_CONTRACT 后实扫，角色目录原先不存在，初始 0/68。实际查看身份肖像、E/W idle 与已确认风格图；原移动、站立、肖像和既有参考只读。全部本地写入限定本角色目录。

## 当前实物与检查

| 项目 | 结果 |
|---|---|
| 受击 hit | E 0/6，W 0/6 |
| 普攻 attack | E 0/12，W 0/12 |
| 施法 cast | E 0/16，W 0/16 |
| 候选/显式选定/runtime | 0/68、0/68、0/68 |
| 内置生图实际尝试 | hit/E/03 两次；cast/E/09 一次；共三次均失败 |
| 六方向动作提示词 | 68 份准备完成，不计作图片 |
| 六份选表 | selection 下全部标明 partial，frames 为空 |
| 最终规格技术检查 | 未通过：缺 68 张；audit-network-blocked，命令实际退出码 1 |
| 视觉六段正常/慢放、深浅底 | 未执行：没有可播放图片 |
| 客户端接入/运行 | 未接入、未启动、未测试 |

三次真实错误均为 `image generation failed: network error: error sending request`。没有图像、输出路径或实际型号/质量元数据返回。局部参考图可读取，不据此猜测服务端故障原因。未调用单独计费的 API/CLI。

## 来源与续作入口

- 初始实扫：[inventory-snapshot.json](../audit-initial/inventory-snapshot.json)
- 当前缺槽检查：[audit-network-blocked](../audit-network-blocked/)
- 参考哈希：[reference-snapshot-20260930.json](../provenance/reference-snapshot-20260930.json)
- 受击动作表：[hit-frame-plan.json](../prompts/hit-frame-plan.json)
- 普攻动作表：[attack-plan-20260930.json](../prompts/attack-plan-20260930.json)
- 施法动作表：[cast-action-plan-20260930.json](../prompts/cast-action-plan-20260930.json)
- 失败回执：[hit 首次](../provenance/receipts/hit-E-03-v1.attempt-01.json)、[hit 重试](../provenance/receipts/hit-E-03-v1.attempt-02.json)、[cast 首次](../provenance/receipts/cast-E-09-v1-failed.json)
- 角色私有导出/连播：[tools/README.md](../tools/README.md)

逐次回执保存实际提示词、参考路径、时间证据、配置快照和真实错误。目标配置为 gpt-image-2.5-sunburst / max；2026-09-30已核对[官方模型页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)。内置入口没有型号/质量参数，实际提交这两个参数及实际返回值均为 null；不是已锁定 max 的证明。没有成功图片，所以不存在可编造的图片 SHA、原生尺寸或生成成功时间。

## 恢复后的执行顺序

1. 再次实扫本角色库存及在制稿，保留新出现文件；不要覆盖当前失败回执。以新 attempt 文件保存重试，实际成功结果才进入 staging 与来源记录。
2. 从已准备的 hit/E/03 与 cast/E/09 关键帧和 attack/E/05 开始锁定身份、持手、琴形、相机与固定地根，审图后补 E/W 两套独立动作。68份提示词是计划，须结合真实返回邻帧调整；不能把准备好的文本当作姿态已验收。
3. 每槽真实独立绘制；禁止镜像、复制、程序扭曲或插值。保存完整成功或失败回执，未披露型号/质量继续标明未确认。
4. 看图后逐槽写明确选表与源哈希，齐全后选定稳定的整体导出变换。私有工具现已准备并通过防护/时序测试，但未运行真实素材导出；不能把工具自测当成图片验收。
5. 导出 68 张 1024×1024 透明 PNG，检查真实 alpha、持手/琴数量与长度、脚根、裁切、重复/镜像及来源链。
6. 正常速度 hit 40ms、attack 30ms、cast 45ms；六段合计 2640ms。0.25×慢放合计10560ms并标注倍率。实际播放并检查深浅底、根位置/脚滑、头身与衣饰闪变、起止衔接后记录结论。
7. 命中/释放帧必须按最终实图确定。本轮提示词的峰值槽仅是设计计划，没有游戏事件对齐证明。
8. 此授权不包含客户端、共享文件或其他角色。未产生拒稿图片，也未清理或复制任何现有游戏图。

API/CLI备用路线需要用户另行明确选择及本地 OPENAI_API_KEY；本轮继续遵守内置优先，没有切换。

