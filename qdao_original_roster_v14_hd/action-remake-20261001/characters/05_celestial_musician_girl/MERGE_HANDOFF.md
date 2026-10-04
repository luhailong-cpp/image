# 天音少女 · 素材接入交接

2026-10-04接地修订完成：196张正式1024×1024 RGBA、14段动作，文件与本地浏览器检查通过。当前无剩余必须修复的离线美术项。客户端尚未接入，也未进行游戏运行验收。

## 当前交付与接地帧

以[final/manifest.json](final/manifest.json)及[final-selection.json](final-selection.json)为当前入口。图片为`final/<action>/<direction>/<两位帧号>.png`，同名`.png.generation.json`保存来源、导出变换、SHA和验收记录。196个原生来源SHA和196个正式PNG的SHA各自唯一。历史选表及已删除中间图不作为加载入口。

本轮八方向跑步选用65张新绘来源、63张正确旧来源，每方向仍为16×75ms＝1200ms。01–08连续由RIGHT支撑，09–16连续由LEFT支撑；每组依次为前部落脚、身体经过、髋下向后、后侧前掌蹬地，各占两张独立姿态。逐帧`supportLeg`与`stancePosition`已写入正式清单和sidecar。08→09、16→01换腿；根据裤腿遮挡追踪真实腿属，不把屏幕左右或鞋底最低位置当作腿身份。

| 动作 | 方向 | 每方向帧数 | 帧时长 | 总时长 |
| --- | --- | --- | --- | --- |
| run | N/NE/E/SE/S/SW/W/NW | 16 | 75ms | 1200ms |
| hit | E/W | 6 | 40ms | 240ms |
| attack | E/W | 12 | 30ms | 360ms |
| cast | E/W | 16 | 45ms | 720ms |

[animation-timing.json](animation-timing.json)为时长配置，首尾不额外停留、不应用分相位权重。68张战斗图及其sidecar保持本轮修改前字节。既有触弦事件建议保持：attack E04起90ms首次触弦、E05起120ms重拍；attack W05起120ms；cast E/W09起360ms释放。客户端伤害、特效和音效事件尚未接线。

## 配准与来源

全196帧共用0.65比例、每段动作/方向固定源根，目标根(512,942)，底部原点pivot[0.5,0.080078125]，见[registration.json](registration.json)。没有每帧按脚底、头顶或包围盒移动缩放；远近脚保持透视差。后跟抬起时仍由前掌支撑，不要求远近脚同时落在同一屏幕水平线。

正式PNG均完整解码为1024 RGBA、边缘alpha为0。新绘原生输入1254×1254，采用固定预乘Alpha重采样。右手拨琴下弦、左手扶琴上段；被头发和身体遮住的关节不声称直接可见。

修图通过宿主内置image_gen执行，配置目标GPT Image 2.5 Sunburst/max；工具未披露实际型号/质量，实际字段null，不能据目标值声称已显式锁定模型。逐图sidecar内嵌来源记录，提示词与证据汇总见[最终提示词集](provenance/ground-contact-20261004/selected-prompt-set.json)。

## 核验与清理

- [实图与成对接地验收](provenance/ground-contact-20261004/position-acceptance.json)：绑定128条选帧和替换前SHA。
- [安全重排记录](provenance/ground-contact-20261004/position-promotion.json)：先缓存全部来源，再覆盖槽位；来源记录随图走，战斗68张未改。
- [浏览器检查](provenance/ground-contact-20261004/position-browser-check.json)：128张逐一加载，主预览及160px检查页的八方向1×单圈均到16并停止。
- [14项时序检查](provenance/run/timing-1200-checks.json)与[最终文件核验](provenance/final-validation.json)。
- [清理记录](provenance/ground-contact-20261004/cleanup.json)：245张中间图已删除，196张正式PNG与一张预览凭证保留，SHA未变。

旧离线验收及旧选表保留原有历史SHA；本轮以当前正式清单和本轮验收为准。当前预览只读正式文件，不依赖被删原生/中间图。其他角色、客户端、全局设置及宿主生成目录均未修改。接入时仍需按实际相机和世界移动速度复核脚滑与观感。
