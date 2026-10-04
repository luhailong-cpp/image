# 冰剑少女 · 本机动作交接

用户时区2026-10-03。只修改本角色目录；未写其他角色或客户端，未作Git提交/推送。

## 当前优先参数

**跑步八方向统一1200ms/圈，16帧每帧75ms，正常1倍。** 当前预览已移除旧快速档及相位权重；保留0.25倍慢放、暂停和逐帧。单圈16帧全部播放，16→01不额外停留。正常速度来自用户最新指定，不宣称已改变游戏内速度。

受击40ms×6=240ms；普攻30ms×12=360ms；施法45ms×16=720ms，均保持原值。参数入口为[animation-timing.json](animation-timing.json)。E选图、候选清单、预览构建/导出和旧检查工具默认已同步，重建不会回到旧速度。

E当前可视触地候选仍为E01右脚、E08左脚，因此均匀75ms时两次间隔为525/675ms；本次没有伪造600/600或继续套用旧360/360。离地候选E05→06在375ms、E13→14在975ms。相位来自实图，时长遵循用户等帧要求。

## 当前文件和验证

- [正常1倍E动画](preview/run-E-1x-1200ms.webp) · [交互预览](preview/index.html)
- [当前源选择](review/run-E-selection.json) · [E候选PNG与SHA](candidate/manifest.json)
- [1200ms浏览器实测](preview/verification-current-timing.json) · [E当前视觉复核](preview/CURRENT16_REVIEW.md)
- [八方向脚向审计](review/FOOT_DIRECTION_E.md) · [制作状态](STATUS.md)

E向16张1254原生、16张1024 RGBA候选已齐，PNG技术、来源SHA和真实透明度通过。浏览器实测当前1200ms完整16帧顺序和回环、128/256显示、暂停/慢放/逐帧均通过；不是游戏内验收。

## 每段当前落盘数量

| 动作/方向 | 1024候选 / 目标 | 正常单帧ms |
|---|---:|---:|
| run/N | 0/16 | 75 |
| run/NE | 0/16 | 75 |
| run/E | 16/16 | 75 |
| run/SE | 0/16 | 75 |
| run/S | 0/16 | 75 |
| run/SW | 0/16 | 75 |
| run/W | 0/16 | 75 |
| run/NW | 0/16 | 75 |
| hit/E | 0/6 | 40 |
| hit/W | 0/6 | 40 |
| attack/E | 0/12 | 30 |
| attack/W | 0/12 | 30 |
| cast/E | 0/16 | 45 |
| cast/W | 0/16 | 45 |

上述是文件库存，不自动授予美术或动态通过。正式目标196张仍在继续制作，不能以E向齐全声称全套完成。旧512八方向128张作为已核查姿态参照保留，不直接放大计HD；旧受击E01/03/06三张原生先复核/编辑，缺槽逐张补。

## 最新参照与实际问题

用户已指定09竹弓少女当前版本作为姿态、脚向、手动作、节奏与接地参照，取代此前撤回的月影整体通过判断。实际读取09 manifest列出的同方向runtime图，对照具体相位；不复制竹弓的像素、衣服、武器、持手或跨方向编号。

E已补落地—全掌压缩—蹬离—短腾空链；08反向抬脚、15先着地后回升、旧03/04与11/12翻剑及多手已修。03→04左符臂摆幅仍偏集中，继续针对中间臂姿处理；右手晶剑、左手蓝符不交换。其他方向和战斗分段继续补齐。

## 根点与来源

E暂用全1024画布虚拟近根[512,975.872]，远脚轨道970.752，只作观察诊断。不同方向需按实图膝踝与承重核实，不机械套用E鞋底线。所有导出整画布缩放、translation=[0,0]，不作最低脚贴线、镜像、复制或姿态插值。

新图使用宿主内置image_gen；同批配置目标2.5 Sunburst/max，实际工具无型号/质量参数且未返回实际值，均记录null。各图旁.generation.json绑定sources/中的实际提示词/参考角色/工具回执/时间/SHA，保留配置目标与实际证据区别。

## 客户端与保留

D:/work/mmorpg-client目前已存在；旧“不存在”记录过时。本任务仍仅写私有素材目录，客户端尚未接入或运行。后续需同时接入资源、时长校验与位移步频关系，不能只复制75ms就声称游戏内生效。

保留当前在制及编辑所依赖素材；成品落盘和当前引用完整后清理淘汰图，保留逐图文字来源。当前candidate为审阅导出，不自动覆盖客户端。

## 当前E候选SHA

| 文件 | SHA256 |
|---|---|
| candidate/run/E/01.png | a2ad44d5339fed043e5f81f36088e223ec67e3144270f6907b24668593c68b96 |
| candidate/run/E/02.png | 314c0acd7939c6e20d176c4dcca70aa41a22d9309bee7347831a975b8668b330 |
| candidate/run/E/03.png | 2308cb098e401b9c98d7247ed1e1197bcc190b86084fe77b8eaab33ead0281c0 |
| candidate/run/E/04.png | d0ac32728b42cb5c8bce710f3fc32b784b6d2ff6387136dfb675cca856d3912c |
| candidate/run/E/05.png | cb1f6252a4daac5278be1436c0f595045bb3a9651bc17d8db9ff9753d15207e1 |
| candidate/run/E/06.png | d9a36997bef24d29e96b8d64e7dac6a69043f23e129d020eca64f118e9d50d0e |
| candidate/run/E/07.png | f00b550e7702ee36e1a7e4fa9d9e649aa0383ecef895768264dba4d985d49cfc |
| candidate/run/E/08.png | cd274086bf4da3eda8f4efcfed55ddfff09483b42c0fc04791eee47d9e3f6180 |
| candidate/run/E/09.png | 8dda03ca488ef9ccc37539c3083ba2da28d6935936de5e9708b0e2049a335fef |
| candidate/run/E/10.png | b434a4abca24b6843aabeb06e9c03d1581d883dd3325237ec6b6ebf27d2f9476 |
| candidate/run/E/11.png | 4d35abe3c98cdc1477a5f6715ffa8c07315a116779bf863456e2beae6f361a7a |
| candidate/run/E/12.png | 66b25cbff5a9593c2bde6ce7fa50e3e374f8e399735dd8680dd2de44485fb833 |
| candidate/run/E/13.png | a68a6b3a6360ad03458f5e883fff0071b5c0c98381425a54c09c6716ad9fb725 |
| candidate/run/E/14.png | 072987f7ee812004c733cb096a572271ebfc6308951435c3b66facb7af71b0ee |
| candidate/run/E/15.png | 68857ca308ff8c5838847594c5b800590b6df3d64ab3402e16f9187c7056b834 |
| candidate/run/E/16.png | c9e89f527b6af587ac1d4aa6593a26c64df2b968e91d804109110fdc78ceb760 |
