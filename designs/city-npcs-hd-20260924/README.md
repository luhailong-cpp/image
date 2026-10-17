# 主城 NPC · 道家 Q 版与春节中秋融合

23 位静态 NPC 已完成。正式资源是 `native/` 中的 23 张原生透明 PNG；每图配套实际提示词、生成记录及嵌入来源信息。仅用于主城静态角色，本批未制作动画或修改客户端。

画风沿用原有道家 Q 版与已确认 designs 的圆润、明亮、细腻手绘质感；将红结、暖金云纹、月纹、桂花等节庆细节融入各自服饰。人物职业、年龄、主色与标志道具保持可辨认。第 21–23 位为原截图局部可见的职业原创补全，店铺掌柜不是已确认的原名。

## 成品与校验

- [23 位总览](overview.jpg) / [深底透明边缘检查](qa-dark.jpg)
- [素材清单与 SHA-256](manifest.json) / [自动校验结果](validation.json)
- [批次设计与历史参数](batch-plan.json) / [图片清理记录](retention.json)
- `native/编号-名称.png`：游戏用成图；同名 `.prompt.txt`、`.png.generation.json`、`.png.provenance.json`：逐图文字记录。

已核查 23 个唯一角色编号、文件哈希、RGBA、透明 alpha、尺寸记录和画布边缘，并查看浅底与深底总览。原生 PNG 未放大、未裁切；总览仅缩小展示。多数原生尺寸为 1122 × 1402，杨镖头为 941 × 1672，朱雀为 1254 × 1254。**这些不是原生 4K。**

## 生成入口与来源

全部使用宿主内置 image_gen，未调用单独计费 API。内置入口未提供 model、quality、size 选择器；可读取的 C2PA 仅标识 ChatGPT / gpt-image 系列，具体数字版本与质量档位未确认，亦未做 C2PA 签名密码学验证。历史配置目标不等于实际模型返回证据，逐图记录保留生成时配置，不随后续项目配置升级改写。

11–13 为中断后找回的原始工具输出，提示词与参考信息已在原批次计划中保存；记录明确注明未取回的工具输出文本。没有重新调用 API 或新增绘图费用。

历史身份参考图、旧稿和原截图不作为本次交付恢复；它们的生成时路径与哈希仅用于来源追溯，当前成品与校验工具不依赖旧图。当前风格索引已经改版，因此历史风格参考使用固定 Git 版本链接：

- [已确认画风样板](https://github.com/luhailong-cpp/image/blob/eff4fedbd71b598d78dca176d2f5127f60c0dec8/designs/team-ui-v2/team-ui-v2.png)
- [历史 NPC 身份参考与原截图](https://github.com/luhailong-cpp/image/tree/eff4fedbd71b598d78dca176d2f5127f60c0dec8/designs/city-npcs-20260924)

## 角色文件

| 编号 | 角色 | PNG / 原生尺寸 | 来源 |
|---|---|---|---|
| 01 | 杨镖头 | [941 × 1672](native/01-yang-biaotou.png) | [生成记录](native/01-yang-biaotou.png.generation.json) |
| 02 | 屠娇娇 | [1122 × 1402](native/02-tu-jiaojiao.png) | [生成记录](native/02-tu-jiaojiao.png.generation.json) |
| 03 | 董老头 | [1122 × 1402](native/03-dong-laotou.png) | [生成记录](native/03-dong-laotou.png.generation.json) |
| 04 | 辛仁皑 | [1122 × 1402](native/04-xin-ren-ai.png) | [生成记录](native/04-xin-ren-ai.png.generation.json) |
| 05 | 北斗星使 | [1122 × 1402](native/05-beidou-xingshi.png) | [生成记录](native/05-beidou-xingshi.png.generation.json) |
| 06 | 赤灵尊神 | [1122 × 1402](native/06-chiling-zunshen.png) | [生成记录](native/06-chiling-zunshen.png.generation.json) |
| 07 | 擂台管理员 | [1122 × 1402](native/07-arena-manager.png) | [生成记录](native/07-arena-manager.png.generation.json) |
| 08 | 阵营战表彰大使 | [1122 × 1402](native/08-faction-commendation-envoy.png) | [生成记录](native/08-faction-commendation-envoy.png.generation.json) |
| 09 | 镇魔道人 | [1122 × 1402](native/09-demon-quelling-taoist.png) | [生成记录](native/09-demon-quelling-taoist.png.generation.json) |
| 10 | 车夫 | [1122 × 1402](native/10-carter.png) | [生成记录](native/10-carter.png.generation.json) |
| 11 | 无想僧 | [1122 × 1402](native/11-wuxiang-monk.png) | [生成记录](native/11-wuxiang-monk.png.generation.json) |
| 12 | 无意僧 | [1122 × 1402](native/12-wuyi-monk.png) | [生成记录](native/12-wuyi-monk.png.generation.json) |
| 13 | 陆压真人 | [1122 × 1402](native/13-luya-immortal.png) | [生成记录](native/13-luya-immortal.png.generation.json) |
| 14 | 朱雀 | [1254 × 1254](native/14-zhuque.png) | [生成记录](native/14-zhuque.png.generation.json) |
| 15 | 苏苏 | [1122 × 1402](native/15-susu.png) | [生成记录](native/15-susu.png.generation.json) |
| 16 | 月老 | [1122 × 1402](native/16-yue-lao.png) | [生成记录](native/16-yue-lao.png.generation.json) |
| 17 | 无名药铺老板 | [1122 × 1402](native/17-medicine-shopkeeper.png) | [生成记录](native/17-medicine-shopkeeper.png.generation.json) |
| 18 | 仙界神捕 | [1122 × 1402](native/18-celestial-constable.png) | [生成记录](native/18-celestial-constable.png.generation.json) |
| 19 | 无名武器店老板 | [1122 × 1402](native/19-weapon-shopkeeper.png) | [生成记录](native/19-weapon-shopkeeper.png.generation.json) |
| 20 | 善财童子 | [1122 × 1402](native/20-shancai.png) | [生成记录](native/20-shancai.png.generation.json) |
| 21 | 段铁心（补全） | [1122 × 1402](native/21-duan-tiexin.png) | [生成记录](native/21-duan-tiexin.png.generation.json) |
| 22 | 云游大仙（补全） | [1122 × 1402](native/22-yunyou-daxian.png) | [生成记录](native/22-yunyou-daxian.png.generation.json) |
| 23 | 店铺掌柜（补全） | [1122 × 1402](native/23-shopkeeper.png) | [生成记录](native/23-shopkeeper.png.generation.json) |

## 维护

`python tools/make_delivery.py` 使用 Pillow 复核正式图并重建清单、总览；重建总览依赖 Windows 的 `C:/Windows/Fonts/msyh.ttc` 与 `msyhbd.ttc`，其他系统需先调整为本机中文字体路径。`tools/inspect_image_provenance.py` 为本目录自包含的来源解析器。`tools/record_builtin.py` 只归档已有图片和已知元数据，不调用生成服务。

`prompts/` 与批次 `proposedApiParameters` 为历史设计提案；实际执行提示词以 `native/*.prompt.txt` 为准。付费 API 提案已被用户撤回，不能将历史提案当成执行指令。

已按素材保留规则删除本批 4 张重复、失败或被替代的图片，保留其逐图文字证据。`source/` 与 `native/attempts/` 仅存历史记录，不是正式素材入口。
