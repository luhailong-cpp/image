# 天音少女 · 素材接入交接

2026-10-03：离线素材完成，196张正式1024×1024 RGBA、14段动作，全部文件核验通过。**客户端未接入，未进行游戏运行验收。** 本轮修改仅限本角色目录。

## 当前交付

入口为[final/manifest.json](final/manifest.json)及[final-selection.json](final-selection.json)。图片路径为`final/<action>/<direction>/<两位帧号>.png`，同名`.png.generation.json`保留完整来源、导出变换与SHA。193张选定来源为本轮新图，E跑步01/02/05保留旧批三张；196个来源与196个正式输出各自SHA均唯一。

| 动作 | 方向 | 每方向帧数 | 帧时长 | 总时长 |
| --- | --- | --- | --- | --- |
| run | N/NE/E/SE/S/SW/W/NW | 16 | 75ms | 1200ms |
| hit | E/W | 6 | 40ms | 240ms |
| attack | E/W | 12 | 30ms | 360ms |
| cast | E/W | 16 | 45ms | 720ms |

跑步正常1×统一1200ms/圈，每帧75ms，16帧正好整除。[节奏检查](preview/timing-grounding-final.html)已移除偏快旧档和分相位试验，保留慢放、暂停、逐帧及播放一圈。当前参数见[animation-timing.json](animation-timing.json)。单圈01至16各75ms，首尾不额外停顿。接入时仍须结合世界移动速度复核脚滑。

## 根点与导出

[registration.json](registration.json)保存每个动作/方向的固定源根。所有196帧采用同一个0.65比例，目标根为像素(512,942)，底部原点pivot为[0.5,0.080078125]。每段内变换保持不变，保留真实姿态起伏与腾空；没有逐帧按最低脚、包围盒或头顶进行归一化。远近脚具有透视差，不要求同时落在同一屏幕水平线。

正式输出与已复核配准图字节相同；所有图片均完整解码为1024 RGBA，四周边缘alpha为0。生成来源的原生输入至少1024；本轮新图原生1254×1254。目标模型为GPT Image 2.5 Sunburst/max，工具实际型号/质量未披露，记录中的实际值为null，不能据目标字段宣称已锁定型号。

## 动作复核与事件

已检查八方向跑步的支撑、蹬离、短腾空、下降、压重和首尾换腿。修复包括N08/N10、NE01/02、SE14–16鞋向，S01/02落脚与压重，以及W持琴手臂关系。战斗另修复attack W09鞋向、hit E03比例和cast W08持琴手臂拓扑。

解剖左手扶琴上段、右手拨下弦；W近侧左臂跨琴至上端，E近侧右手位于下弦。背面被头发和身体遮住的关节未声称直接可见。

建议事件锚点以1为首帧，时间从帧起点计算：

| 动作 | 可见事件 | 帧号 | 起点偏移 |
| --- | --- | --- | --- |
| attack E | 首次触弦 | 04 | 90ms |
| attack E | 出力重拍 | 05 | 120ms |
| attack W | 明确触弦/出力 | 05 | 120ms |
| cast E/W | 释放/接触锚点 | 09 | 360ms |

事件来自离线姿态复核；客户端伤害、特效和声音事件尚未接线。14段已在本地浏览器正常播放，浏览器结果不能替代客户端运行验证。

## 证据与清理

- [离线验收与196个选定来源SHA](provenance/offline-acceptance.json)
- [全部来源静态检查覆盖](provenance/static-review-coverage.json)
- [最终文件核验](provenance/final-validation.json)及[清理后浏览器检查](provenance/formal-browser-check.json)
- [清理记录](provenance/cleanup-final-delivery.json)

本角色原图、回退稿、拒稿、配准中间图及旧预览已清理；保留196张正式PNG、一张交付预览凭证和文字记录。旧批、其他角色、宿主生成目录没有删除。

历史选表保存在[原生选表](provenance/native-selection-at-export.json)、[原生来源库存](provenance/native-selected-files-at-export.json)、[配准选表](provenance/registered-selection-at-export.json)，其中图片路径是历史证据，不能作为当前加载路径。后续接入使用正式清单，按实际相机与位移速度验证；本机目前没有客户端验收证据。

2026-10-04 竹弓当前版对照收尾：196帧均已按同向实图复核，191帧保留，东南跑步01/02/03/12/13局部重修近右靴鞋尖方向，持琴手臂和原动作相位保留。跑步统一16×75ms＝1200ms；正常播放、单圈停止与首尾衔接已检查。详见[本轮验收](provenance/bamboo-reference-20261003/closeout.json)与[五帧修复验收](provenance/bamboo-reference-20261003/SE-repair-acceptance.json)。旧离线验收和选表保留其历史SHA，本轮五帧以新记录为准。客户端仍未接入实测。

本轮53张诊断／原生／导出中间图已核验后删除，保留196张正式PNG与一张交付预览凭证。[本轮清理记录](provenance/bamboo-reference-20261003/cleanup.json)。
