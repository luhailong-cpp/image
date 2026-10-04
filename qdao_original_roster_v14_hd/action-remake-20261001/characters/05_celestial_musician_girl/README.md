# 05 天音少女 · 正式动作素材

2026-10-04：本轮接地修订已完成。八方向跑步共128张，按同一只脚连续支撑、接地点随身体经过逐段变化来制作，每个位置两张独立姿态。65张重新绘制，63张正确来源保留；手臂持琴、膝踝鞋向和换脚衔接已实图复核。全套仍为196张1024×1024 RGBA透明PNG、14段动作。

[打开正式预览](preview/index.html) · [160px跑步检查](preview/timing-grounding-final.html) · [正式素材清单](final/manifest.json) · [接入交接](MERGE_HANDOFF.md)

| 动作 | 方向及帧数 | 正常播放 |
| --- | --- | --- |
| 跑步 | 八方向各16帧，共128张 | 75ms/帧，1200ms/圈 |
| 受击 | E/W各6帧，共12张 | 40ms/帧，240ms/段 |
| 普攻 | E/W各12帧，共24张 | 30ms/帧，360ms/段 |
| 施法 | E/W各16帧，共32张 | 45ms/帧，720ms/段 |

八方向均为01–08右脚支撑，09–16左脚支撑；前掌蹬地也计入接地。每两帧的具体位置如下：

| 接地位置 | 右脚 | 左脚 |
| --- | --- | --- |
| 前部落脚、接受负荷 | 01–02 | 09–10 |
| 身体经过支撑脚 | 03–04 | 11–12 |
| 髋下向后过渡 | 05–06 | 13–14 |
| 身体后侧前掌蹬地 | 07–08 | 15–16 |

全套共用0.65比例，各动作/方向整段共用固定源根，目标根(512,942)、底部原点pivot[0.5,0.080078125]，见[registration.json](registration.json)。保留真实姿态和透视高差，没有逐帧移动贴地、重复帧、插帧或时长权重。

浏览器中128张跑步图已逐一成功加载，八方向在主预览及160px检查页正常1×单圈均停在16帧；14项播放时序检查通过。受击、普攻、施法的68张及其时长保持原样。当前无剩余必修美术项；客户端未接入实测，实际世界位移下速度匹配仍待验证。

[本轮实图验收](provenance/ground-contact-20261004/position-acceptance.json) · [浏览器检查](provenance/ground-contact-20261004/position-browser-check.json) · [完整收尾记录](provenance/ground-contact-20261004/closeout.json) · [文件核验](provenance/final-validation.json)

修图使用宿主内置image_gen；本批目标GPT Image 2.5 Sunburst/max，工具实际型号与质量未披露，实际字段保留null。每张正式图片旁的`.png.generation.json`保存来源、原生尺寸、SHA、请求与返回证据和固定导出变换。[最终提示词集](provenance/ground-contact-20261004/selected-prompt-set.json)。

正式文件及当前引用验证后，已清理本角色目录内245张原生、拒稿、诊断及导出中间图，只留196张正式PNG和一张[交付预览凭证](preview/delivery-proof.png)，保留全部文字来源记录。[本轮清理清单](provenance/ground-contact-20261004/cleanup.json)。历史来源路径仅供追溯，当前加载以`final/`为准。
