# 05 天音少女 · 正式动作素材

2026-10-03：本角色离线素材已完成，共 **196 张 1024×1024 RGBA 透明 PNG、14 段动作**。八方向跑步的可见手臂持琴关系、鞋尖朝向、换腿、压重和首尾衔接已复核。客户端尚未接入或实测，实际位移下的速度匹配仍待验证。

| 动作 | 方向与帧数 | 播放时长 |
| --- | --- | --- |
| 跑步 | 八方向各16帧，共128张 | 75ms/帧，1200ms/圈 |
| 受击 | E/W各6帧，共12张 | 40ms/帧，240ms/段 |
| 普攻 | E/W各12帧，共24张 | 30ms/帧，360ms/段 |
| 施法 | E/W各16帧，共32张 | 45ms/帧，720ms/段 |

- [正式动作预览](preview/index.html)与[跑步节奏检查](preview/timing-grounding-final.html)
- [交付清单](final/manifest.json)、[逐帧索引](final-selection.json)、[状态](STATUS.json)
- [接入交接](MERGE_HANDOFF.md)与[预览使用说明](tools/PREVIEW_USAGE.md)
- [离线验收](provenance/offline-acceptance.json)、[文件核验](provenance/final-validation.json)、[正式浏览器检查](provenance/formal-browser-check.json)

全196帧共用0.65比例，每段动作/方向共用一个固定源根，输出根为(512,942)，底部原点pivot为[0.5,0.080078125]。参数见[registration.json](registration.json)。没有逐帧包围盒归一化、脚贴线、镜像、复制或插帧来补动作。

生成目标为GPT Image 2.5 Sunburst/max；宿主内置工具未披露实际型号和质量，因此实际值保留为未确认。每张正式图旁的`.png.generation.json`保存原生尺寸、来源SHA、请求与返回证据以及导出变换。

正式成品及引用核验后，已按用户政策删除本角色原图、拒稿和中间图片，保留文字来源记录。清理记录见[cleanup-final-delivery.json](provenance/cleanup-final-delivery.json)。旧批次、其他角色与宿主生成目录未改动。历史源图路径仅作来源追溯，当前使用`final/`。

2026-10-04 竹弓当前版对照收尾：196帧均已按同向实图复核，191帧保留，东南跑步01/02/03/12/13局部重修近右靴鞋尖方向，持琴手臂和原动作相位保留。跑步统一16×75ms＝1200ms；正常播放、单圈停止与首尾衔接已检查。详见[本轮验收](provenance/bamboo-reference-20261003/closeout.json)与[五帧修复验收](provenance/bamboo-reference-20261003/SE-repair-acceptance.json)。旧离线验收和选表保留其历史SHA，本轮五帧以新记录为准。客户端仍未接入实测。

本轮53张诊断／原生／导出中间图已核验后删除，保留196张正式PNG与一张交付预览凭证。[本轮清理记录](provenance/bamboo-reference-20261003/cleanup.json)。
