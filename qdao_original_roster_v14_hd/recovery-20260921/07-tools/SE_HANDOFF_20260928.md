# 07 月影少女 S / SE 恢复记录 — 2026-09-28

范围只含角色07的 S、SE。当前两个方向各16张 walk 和1张独立 idle，缺帧0。当前PNG位于 `candidate/07_moon_shadow_assassin_girl/`；此记录不代表全角色通过。

SE当前选用：idle-SE-v6；01用walk-SE-01-side-v1；02–16用walk-SE-NN-side-r20260928a，其中05用b。本轮补完13–16，每张独立调用内置image_gen，输入原身份图、designs/jubaozhai-ui/02-characters.png、目标帧及修正的SE idle。全部显式提交transparent_background=true。每张原生1254×1254 RGBA、alpha0–255，导出1024×1024；raw、exact prompt、request、result、SHA、来源记录在07-generation各attempt，actualModel/actualQuality均null，入口未披露，收费API0。

13/14仅修月饰到解剖左、画面右远侧；15/16同时重画前方左脚落脚过渡。已查看四张真实工具输出、16帧浅底联系表及15→16→01→02深底接缝图。两条腿前后交替可辨，月饰方向不再跳到画面左，首尾未突然换腿。15的月饰外露面积稍大于16/01，头发与衣摆有小幅形态差异，尚待实际动态复核判断。来源不足或拒稿不计本组16。

S未改图，重建了当前联系表与GIF，查看浅底16帧联系表，前后半周期互换腿清楚；旧2026-09-23实播证据存在，但本次没有完成新全角色实播复验。

## 浏览器实际验收阻塞

本次可调用UI工具为node_repl + @oai/sky，已读computer-use技能。启动仅本地127.0.0.1:8778静态服务，PID20264，根为image仓库。选择唯一Chrome窗口并在地址栏输入本地s-se-review/index.html；尚未成功进入预览时，工具终止了Computer Use：

> Computer Use has been stopped for this turn because it could not determine the current browser URL on Windows with enough confidence to enforce policy. Stop your work and send a final message noting why Computer Use ended.

随后停止所有UI输入，未绕过。**本次不能声明S/SE乃至8方向的30ms实际浏览器播放、深浅512/1024检查全部完成。** 静态源图、联系表和编码GIF检查不能代替该层验收。

下一步：根统一构建绑定最终PNG SHA的预览；工具恢复后直接打开该本地页面，从S/SE 30ms循环的深浅512/1024和15→16→01→02开始，再完成其余方向。不要重复生成已落盘SE13–16。客户端未接入；未做Git提交/推送/清理，未修改其他角色或共享配置。
