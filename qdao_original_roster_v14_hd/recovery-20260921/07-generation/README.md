# 07 月影少女：本轮生成来源

本目录仅属于 `07_moon_shadow_assassin_girl`。本轮目标为128张独立生成行走图及8张独立站立图，8方向各16帧、30ms/帧、480ms/圈。生成数量、已选槽位和美术验收分别记录；本目录存在不表示齐套或客户端验收。

## 开工库存

2026-09-21只读核查全仓文件（含忽略目录，排除.git/.agents/.codex）以及V13/V14候选、正式与生成目录：07已有walk=0、idle=0、可归属未导入动作raw=0。仅原始肖像和历史副本可作身份参考，不能算动作。

原肖像：`../../../q_daoist_character_pack_4096/07_moon_shadow_assassin_girl_transparent_4096.png`，SHA256 `8ccc7e9118ed1ca608a407687e5a76cf392b1f694ef7737ccc28536caae84bfc`。肖像历史记录为1254原生、4096导出。`portrait-inspection-1024.png`是整图等比缩小的检查及输入通道副本，不是新增动作。

## 生成入口与证据

只使用内置`image_gen.imagegen`，收费API=0。配置目标读取`config/image-generation.json`；2026-09-21已再次读取[官方Sunburst模型页](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)，确认该页面列有max质量。工具本身仅暴露prompt与参考图，不提供型号/质量选择；实际结果只返回image_url和output_hint，实际型号/质量均未确认，不以官方公告、配置或提示词替代返回证据。

各attempt目录保存精确prompt、request.json、result.json和原字节raw.png。原始默认生成文件保留。拒稿另存selection.json；修订使用新版本目录，不覆盖历史。

身份参考为原肖像的1024副本；主要画法参考实际附上`designs/jubaozhai-ui/02-characters.png`；第三张为本轮方向/比例参考。4096输入首次失败的原始报错保留于idle-S-v1，随后用等比副本成功，不调用API。

`frame-specs.json`是起始相位设计，后续修订的精确实际请求以各attempt/request.json为准。原相位设计不代表实际出图已达标。行走不使用复制、镜像、插值或同姿势平移凑帧。透明导出与脚底对齐仅是同一独立原图的派生，不创建其他动作槽。

## 当前视觉发现

- `idle-N-v1`头背身前：前衣襟、月牙扣、鞋尖仍可见，拒选。
- `idle-NE-v1`同类背向结构问题，拒选。
- 方向站立修订作为后续该方向的动作参考；真实循环和最终边缘仍需验收。
- 部分原图轮廓有细碎白/彩边，需在深浅底处理复核，不能凭RGBA或文件计数判通过。

只在本角色隔离目录工作，不覆盖其他窗口、不改00–03或既有动作；不执行Git提交/推送/清理，不进行Unity或正式客户端验收。
