# 灵玥 W 向受击与普攻制作记录

2026-10-05。此记录只覆盖本子任务：design/W.png、hit/W 6帧与attack/W 12帧。W cast由另一子任务制作，未改动。

## 实际产出

- W真斜背参考：design/W.png。三次真实内置生成；第3次补足可辨第9尾，四足、后脑、脊背与后跟可见。此设计为1024导出版，原生1254；其独立生成记录保留设计自身的全幅缩放，不能把设计当runtime统一变换。
- runtime/hit/W/01.png–06.png：6×40ms。
- runtime/attack/W/01.png–12.png：12×30ms。
- 18张均为独立image_gen生成，不复制、不镜像、不整图平移、不插值补帧。
- 所有runtime使用根ingest.py的同一变换：完整1254×1254画布等比缩至980×980，再贴入1024×1024透明画布[22,0]；没有逐帧按脚重对齐。
- 技术核验18/18存在、1024×1024 RGBA、Alpha0–255、SHA各不重复。详见receipts/W-hit-attack-validation.json。

## 逐帧查看与修稿

每次工具返回图已实际查看；最终18张又通过两组接触表逐帧复查，均可辨9尾及4条兽肢，真W背向与原金玉项圈身份保留。
四次定点修正已完成，旧候选仅保留文字来源记录，runtime保留当前选定结果：
1. attack03：首次抬近侧前爪；attempt02改为远侧右前爪，近侧左前足与两后足落地。
2. attack09：首次缺一条支撑前腿；attempt02补回近侧支撑前腿，共3足支撑+1收肘爪。
3. hit04：首次直接站直；attempt02改为仍屈腿的初段回弹。
4. attack06：首次爪尖偏长；attempt02改为紧凑犬科兽爪。
逐帧备注见receipts/W-frame-visual-review.json及每图generation.json。

## 尚未通过的项目

本子任务不宣称整组动画完成验收。可见风险：
- hit02–03与01相比仍有小幅支撑脚点漂移，04→05的起身幅度应连播检查。
- attack02→03体态高度变化偏大；10–12远侧前足落点比设计基准靠前，闭环至01的稳定性需要进一步修正或验收。
- 未实际操作原速/慢速連播，未做客户端接入。cua.createBrowserTab(iab)返回Browser is not available，cua.listBrowsers返回[]；本环境没有可用浏览器。不能以WebP已生成或哈希通过替代动态视觉验收。

预览供主任务继续验收：
- receipts/W-hit-contact.png、receipts/W-attack-contact.png。
- receipts/W-hit-normal.webp（40ms）、receipts/W-hit-slow.webp（160ms）。
- receipts/W-attack-normal.webp（30ms）、receipts/W-attack-slow.webp（120ms）。
- 根preview.html由主任务维护，未改动。

## 模型与来源

路线：内置image_gen。每次实际附原有身份、design/W方向参考/当前动作编辑对象、已确认人物属性风格成图。配置目标gpt-image-2.5-sunburst/max；工具未暴露model/quality参数且结果未披露，submittedParameters.model/quality与actualModel/actualQuality均为null。逐图prompt、参考角色、工具output_hint、实际原生尺寸和SHA均保留；拒稿及重试记录也已补齐。

没有读取客户端、兄弟仓库或其它机器，没有修改旧资源、共享配置、Git索引或分支。所有项目写入均在灵玥目录。工具默认生成缓存位于宿主CODEX_HOME；本子任务受只写宠物目录限制，没有修改或删除该目录外文件。项目内没有保存拒稿/旧版本图片备份。

