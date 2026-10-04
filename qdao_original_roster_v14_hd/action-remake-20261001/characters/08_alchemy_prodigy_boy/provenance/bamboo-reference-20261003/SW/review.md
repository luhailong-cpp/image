# SW06 / SW07 参照09修复证据

## 选择

- run/SW/06：generation/bamboo-reference-20261003/SW/06-v1.png
- run/SW/07：generation/bamboo-reference-20261003/SW/07-v2.png
- 07-v1虽修正腿轴，但上半身放大、上移，已明确拒选。

三张均实际目检。最终06保持屈膝前摆，07为逐渐伸膝、踝背屈将落地；膝踝进入身体左下前摆平面。靴的左右朝向由原SE外撇转回SW，前鞋尖位于鞋跟左侧。07背屈时脚尖抬起、有限鞋底可见属于pitch变化，不把露底误判成左右yaw错误。两腿前后分工清楚，右手炉/左手瓶及人物道具保持。07-v2重新使用原runtime作为上半身和画布锁定目标，修正v1头身尺度变化。

## 实际输入与来源

06-v1附：08 runtime/run/SW/06.png、09 runtime/run/SW/06.png、designs/jubaozhai-ui/02-characters.png。
07-v1附：08 runtime/run/SW/07.png、09 runtime/run/SW/07.png、同style。
07-v2附：08 runtime/run/SW/07.png锁上身、07-v1仅供正确下肢参考、09 runtime/run/SW/07.png动作参考、同style。
以上均在提交前记录输入SHA，不只将路径列入提示词。

同名.prompt.txt保存完整提示词；本目录.job.json保存提交参数和未改写的宿主outputHint及原始hostOutput位置；原生返回PNG复制落盘未改像素；同名.png.generation.json保存输出SHA、原生1254×1254 RGBA、真实alpha、配置快照和静态结论。工具未暴露实际型号/质量，actualModel/actualQuality=null未确认，submitted model/quality=null；配置目标与实际证据分开。

## 交接边界

selection.json含两张最终源图绝对路径、SHA和记录SHA。父任务整画布至1024、offset0导出；本子任务没有写runtime、总选表或预览，正确邻帧不动，也没有机械旋转/平移腿图。05→06→07→08衔接交主流程合并检查，dynamicAccepted仍false。

节奏沿用用户最新1200ms每循环、16帧均75ms；本轮不提出旧时长或加权配时。
