# 14 唤雪少女 · 资源交接

本轮素材修正与离线验收完成。目前离线通过196/196，其中run通过128/128；实时状态以manifest.json与review.json为准。当前只修改本角色目录，没有修改09竹弓少女或其他角色，也未执行Git暂存、提交、推送。

## 正式资源

|动作|方向|每向帧数|总数|播放时长|
|---|---|---:|---:|---|
|run|N/NE/E/SE/S/SW/W/NW|16|128|每帧75ms，整圈1200ms|
|hit|E/W|6|12|每帧40ms，整段240ms|
|attack|E/W|12|24|每帧30ms，整段360ms|
|cast|E/W|16|32|每帧45ms，整段720ms|

正式路径为动作/方向/01.png起，196张均为1024×1024透明RGBA。support-idle/另有8张配套旧idle注册导出，不计入196张。manifest.json列出逐帧路径、SHA、时长、相位、来源、注册与验收状态；SHA256SUMS.txt由最终验收工具刷新。

统一目标根点[512,942]，身份尺度0.80。逐张原生图整画布导出并依据人工解剖根注册，不镜像、复制、插值凑帧，不按逐帧包围盒缩放或最低脚贴底。注册参数以成品.generation.json内registrationTransform为准；已注册画布若直接重画，则保留原尺度且不再缩0.80。双脚的近远透视和腾空高度不能用同一条最低像素线强制替代。

## 按竹弓少女重审

用户反馈后撤回全部run旧通过状态，以09当前实际PNG重新对照脚掌长轴、膝踝连接、前后腿推进、承重交换、落脚与循环。修复同时保留左臂抱一只白狐、右掌托一枚雪花晶体、左侧发饰。不会把09的相同帧号自动当成本角色相同支撑腿。

本轮已替换帧共106张：

- N：01、02、03、05、06、07、08、09、10、11、13、14、15、16
- NE：01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16
- E：03、04、05、06、07、08、09、10、11、12、13、14、15、16
- SE：04、05、06、07、08、12、13、14、15、16
- S：04、05、06、07、08、12、13、14、15、16
- SW：01、02、04、05、06、07、08、12、13、14、15、16
- W：01、03、04、05、06、07、08、09、10、11、12、13、14、15、16
- NW：01、02、03、05、06、07、08、09、10、11、12、13、14、15、16

## 四个连续支撑位置，每位置两帧

同一脚接地8帧，四位置各2张独立姿态；第9帧换另一脚。每帧75ms、每对150ms、整圈1200ms。依据成品实图标注，不照搬09帧号。禁止复制、插值、加长单帧或整图平移凑接地。逐方向证据、各对空间观察及当前SHA在audit/contact-方向-review.json。

- N：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- NE：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- E：anatomical_left_far 01→02→03→04→05→06→07→08；anatomical_right_near 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- SE：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- S：anatomical_left_screen_right 01→02→03→04→05→06→07→08；anatomical_right_screen_left 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- SW：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- W：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- NW：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）

最新要求：同一支撑脚依次经过前落脚、髋下承重、稍后支撑、后侧前掌蹬地四个位置，每位置两张不同姿态。01–08为第一只脚持续接地，09–16为另一只脚持续接地；脚位随运动与透视推进，不能向外撇脚。每对150ms，整圈1200ms。

要求和最终对应帧号见audit/spatial-contact-requirement.json。

原反馈前SHA和历史审核保存在audit/bamboo-baseline.json；本轮逐方向诊断、候选与最终SHA见audit/bamboo-*-review.json。review.json只对当前成品SHA生效；run/方向/grounding-review.json保存当前相位、时长和观察。历史通过记录不替代本轮审核。

## 播放与预览

run-timing.json为权威时长：每方向16×75ms=1200ms，¼慢放为4800ms。预览、manifest与WebP采用相同参数；旧480/640/720/800ms跑步档位已移除。hit第2帧受力/第3帧峰值、attack第5帧出手、cast第9帧释放为建议画面事件，游戏判定由客户端决定。

- index.html：全部14组动作、240px/512px、正常/¼慢速、逐帧。
- all-directions.html：八方向并排，240px/480px、逐帧；正式SHA缓存版本，128帧预解码完成后播放。
- timing-grounding.html：1200ms正常与¼慢放对照，暂停和逐帧。
- bamboo-reference.html：与09实际图并排对照，依赖同级09_bamboo_archer_girl/runtime目录。仅为可选审图页，游戏成品不依赖09。
- preview/：14组连图JPG和正常/慢速WebP，共42个预览。

以characters目录为根启动本地静态服务即可使用全部预览；只复制本角色时，除竹弓对照页外的成品与预览均独立可用。

## 验证、来源与保留

tools/verify_delivery.py核对196成品、审核SHA、注册、相位、预览来源和实际WebP时长；tools/technical_qa.py核对尺寸、Alpha、原生来源与独立性。tools/verify_uniform_timing.cjs验证播放器帧边界、1200ms循环及预览脚本语法。检查通过不等于已运行游戏客户端。

配置目标GPT Image 2.5 Sunburst/max。宿主管理的内置工具未提供型号/质量参数，实际值未披露；逐图保留为未确认，绝不把提示词或配置当作返回证据。成品.generation.json关联原生记录、SHA、请求和回执。历史cast E06/E07中断恢复映射无法逐一确认，来源记录已明确标记。本轮NE部分回图在中断后依据文件时间与画面恢复关联；最终仍采用推断关联的帧及SHA单列在audit/north-ground2-recovery-evidence.json，未改写为确切逐图回执。

按用户2026-09-23素材保留要求，确认正式成品、预览和引用完整后，删除工作目录里的原图、拒稿和加工中间图，不另存图片备份；逐图文字来源保留。清理明细在audit/cleanup-result.json和本轮bamboo清理记录。本角色外参考、正式设计和宿主缓存未动。旧源图路径是历史标识，不是游戏运行依赖；清理后不要重跑需要源图的旧制作工具。

## 客户端边界

本轮没有接入或运行D:/work/mmorpg-client。1200ms为离线动作播放参数，未修改游戏移动配置。客户端接入后仍需结合世界位移速度复核滑步、根点、阴影平面及受击/攻击/施法事件。
