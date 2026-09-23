# 06 雷法少年 NE 16帧交付

2026-09-23：本方向16张真实独立行走图已补齐；只处理NE，未修改N或其他方向、旧S16与8idle。最终PNG在 `candidate/06_thunder_caster_boy/walk/NE/01.png` 至 `16.png`。本方向离线审核通过；全角色包由主任务另行绑定审核，未进行Unity或客户端接入。

- 全部选稿原生1254×1254，导出1024×1024透明PNG，固定common_scale0.88、全画布LANCZOS缩小、整数脚底锚点[512,942]。不做色键、去紫或逐帧bbox缩放。
- 16帧独立来源重建通过，unique16，body-scale CV0.024811，16张输出画布边界无非零alpha；未放大、复制、镜像、插值或扭曲凑帧。
- `review/NE-dark-30ms.gif`、`review/NE-light-30ms.gif`：各16帧，每帧30ms，480ms/圈。`review/index.html` 有深浅底、暂停/逐帧、放大与15→16→01→02接缝；已在浏览器加载并复核。
- `review/numeric-verification.json` 是像素/来源证据；`review/visual-review.json` 是绑定该manifest SHA的NE离线审核记录。头发、衣摆有克制的次级运动；01/09接触脚与05/13高摆腿相反，武器/符牌持手一致。

## 逐帧来源与取舍

`NE_DELIVERY.json` 为自包含逐图来源文字：记录最终SHA、实际源SHA和尺寸、完整prompt、request/receipt返回证据、配置快照、派生操作及选稿原因。实际型号和质量均未披露，为null/host-managed-unverified；内置生成17次，其中14张新稿选用，另复用已有01和13。收费API0次。

| 最终槽 | 选用批次 |
|---|---|
| 01 | NE01-walk-v1 |
| 02/03/04/05 | NE02-final-v2 / NE03-final-v2 / NE04-final-v2 / NE05-final-v2 |
| 06/07/08/09 | NE06-final-v3 / NE07-final-v4 / NE08-final-v3 / NE09-final-v4 |
| 10/11/12/13 | NE10-final-v3 / NE11-final-v3 / NE12-final-v3 / NE13-walk-v1 |
| 14 | NE06-final-v2：请求06但实际画出右腿伸出，按实际姿势选为14，原提示与回执不改写 |
| 15 | NE07-final-v2：请求07但实际画出右腿落地前，按实际姿势选为15，原提示与回执不改写 |
| 16 | NE16-final-v3 |

拒收：旧NE05为错误右摆腿；旧NE09和NE09-final-v2为错误右领先；NE09-final-v3人物偏大，v4完成构图纠正；NE07-final-v3腿侧错误。全部拒稿的来源文字和原因已收录，不能从这些版本恢复正式帧。

## 清理交接

按2026-09-23最新授权，主任务合并最终游戏图、检查当前引用完整后，可删除本工作树中的原图副本、加工阶段图、拒稿、回退图及冗余审核图。无需另存图片备份。保留最终16PNG、必要设计/接入文件、`NE_DELIVERY.json`及审核文字。`source/`、`processing/`里的PNG和06-generation中的raw当前只为重建审核暂存，不是永久交付要求。未自行删除共用原图或历史目录。

本方向浏览器审核时临时本地服务为127.0.0.1:8906，仅绑定回环；离开子任务前已停止服务。HTML和GIF可由主任务最终预览服务器继续提供。
