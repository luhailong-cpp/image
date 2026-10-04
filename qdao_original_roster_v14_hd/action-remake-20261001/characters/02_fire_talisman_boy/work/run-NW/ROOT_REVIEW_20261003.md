# W / N / NW / NE 私有复核交接（2026-10-03）

自己负责55槽：W16、N16、NW16、NE01–06及09七张。NE07、08、10–16由cast独立清单负责，只读联检。当前无在途生图。

## 当前实图结论

- W、N各16帧：鞋掌轴未见明确外撇，保留；N14摆臂、W10缓冲候选已针对性修订。
- NW八槽鞋轴（01/02/03/10/11/14/15/16）从偏W侧面改为NW纵深，单图鞋向复核通过。NW02、09另改善支撑/初触。整个周期仍待root浏览器实播。
- NE01/02五符与正确右肩连接保留；NE09改为左低位初触、右腿高回收，衔接NE10/11。
- NE04/05最新attempt03已沿03右髋连续后蹬与离地，root局部确认。NE06最新attempt06实际附09竹弓NE15关节/鞋轴参考：右鞋高折、左腿下前过，双鞋高低错开；旧attempt04并腿跳已拒。当前左伸距比07未明显缩短，仍待05→06→07实播。
- NE16帧鞋轴/五符已静态检查。cast九槽未修改，最新相位记录以实际来源和SHA为准。

## 09竹弓参考对照

已读09 manifest、animation-timing、MERGE_HANDOFF及preview/index；正式资源由manifest定位。四方向64张runtime当前SHA与manifest全部匹配。实际查看64帧联系表及14张原尺寸重点帧，范围和观察详见 archer-motion-comparison-20261003.json。

W/N/NW对照未发现新的确定外八槽；露鞋底、正常抬跟或纵深透视不算外撇。NE左右腿起始相位不同，不能按同帧号机械复制；只将09 NE15关节错位用于02 NE06。保留02形象、右扇左铃和真实摆臂。

## 正常时长与动态待验

最新人类明确正常跑步每圈1200ms＝16×75ms，均匀无加权。私有HTML已同步，保留慢放×4、暂停、前后逐帧；删除旧快档。GIF只支持10ms粒度，因此正常用70/80ms交替，总1200ms；HTML与正式时长数据均精确75ms。

时长不代替姿态验收。继续由root实播NE05→06→07、NE01/02→03及16→01、NW01→02摆臂幅度，以及W/N/NW前掌蹬离和共同地面。NW部分髋被袍摆遮挡，左右腿归属保留低置信说明。

## 复核与来源

每方向 grounding-review-20261003.json 给16条实际观察、支撑腿、摆动腿、置信度、SHA和统一75ms时长。foot-direction-review-20261003.json 将鞋轴单图通过与整段动态待验分开；NE另记五符单图通过。

north-final-review-20261003.json 含自己55张正式路径/SHA/来源/原生尺寸，以及四方向64条相位复核。inventory-run-north.json 是自己55张可合并清单，不重复计入cast九槽。

55张均1024 RGBA、真实alpha，导出SHA/sidecar/生成记录/私有inventory一致，独立原生1254；宿主原图→本地当前原生SHA55/55一致。只整画布下采样，没有镜像、复制补帧、插值或逐帧贴地。目标GPT Image2.5 Sunburst/max；内置入口实际model/quality未披露，记录为null。

重生成顺序：run_north_review_notes.py → run_north_handoff_review.py → run_north_ne_phase_update.py；各方向预览由 run_north_preview.py --direction DIR 生成。参考对照由 run_north_archer_comparison.py 只读核验。拒稿本地图片在成品落盘后清理，来源文字保留；当前成品及仍用于统一标定的原生保留。无本机客户端接入，不宣称整段或客户端通过。