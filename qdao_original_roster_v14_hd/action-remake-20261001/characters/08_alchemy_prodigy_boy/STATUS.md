# 08 炼丹童子 · 当前交付状态

2026-10-04：八方向跑步的两帧接地位置修正已导出，离线实图与浏览器预览复核完成，淘汰图已清理。当前结果以 manifest.json、contact-pairs-selection.json、run-timing.json 为准。

- 本轮替换 85 张跑步图：N 9、NE 8、E 11、SE 12、S 11、SW 12、W 10、NW 12。保留其余 43 张正确跑步图和 68 张战斗图。
- 跑步八方向各 16 帧；正常 1× 为 1200 ms 一圈，每帧 75 ms。每个接地位置为两张独立姿态，共 150 ms。
- 支撑脚依次从身体前方接触，到身体下承重、稍后承重、更后前掌蹬离。右足配对 16/01、02/03、04/05、06/07；左足配对 08/09、10/11、12/13、14/15。
- 参照 09 竹弓少女核对脚向与膝踝关系，修正外撇、反向鞋尖、支撑脚提前悬起及换足问题；解剖右手丹炉、左手药瓶的归属保持。
- 受击 E/W 各 6 帧、普攻 E/W 各 12 帧、施法 E/W 各 16 帧，配时保持。战斗动作的现有交付范围是东、西两个方向。

正式资源为 runtime 下 196 张 1024×1024 透明 RGBA；预览入口为 preview/index.html，支持正常 1×、慢放 0.25×、逐帧及 128/256 显示。浏览器地址：http://127.0.0.1:8818/preview/index.html?review=contact-pairs-20261004 。

196 张图片、独立来源、来源记录 SHA 及 14 组预览引用检查通过；28 项正常/慢放播放时钟测试通过，循环无额外首尾停顿。浏览器确认全部 196 张解码成功。完整逐帧联系表和重点相位预览已复核，少量上身绘画轮廓差异仍存在，不宣称像素级一致。

已删除本轮 188 张原图、拒稿及中间图，共 202,832,603 字节。目录内现仅保留 196 张正式图片、14 张当前联系表，以及配套接入文件和全部来源文字记录。清理结果：provenance/contact-pairs-20261004/cleanup-result.json。

本批通过内置 image_gen 编辑。配置目标 gpt-image-2.5-sunburst / max；工具未披露实际模型与质量，记录为未确认。完整提示词、任务回执及逐图记录保留在 generation/contact4-20261004 和 generation/contact-pairs-20261004；来源链见 provenance/contact-pairs-20261004/edit-lineage.json。

当前复核结论：provenance/contact-pairs-20261004/review-result.json。技术校验：provenance/delivery-technical-verification.json；时钟测试：provenance/preview-timing-verification.json。

本次完成离线素材和预览交付。未运行客户端；游戏内位移、滑步、方向切换、命中和特效同步尚未验收。接入说明见 MERGE_HANDOFF.md，当前相位见 RUN_PHASES.md。
