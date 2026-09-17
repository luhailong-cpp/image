# 本次代码验证与V12运行基线

本次最终Unity验证发生于2026-09-17 UTC，使用Unity 6000.6.0f1与隔离副本 `E:/work/tmp/qdao-v13-verify-20260917`。不是正式V13素材验收，也不是在线登录测试。

- 输入：`input-snapshot-run3.json`，4690文件，SHA-256 `9990e59c95594352c4d332d756e3f19ce0700b06d41c439debe18472b08ce058`。
- EditMode：`contract-run3/editmode.xml`，300通过/0失败/0跳过，56.01秒测试时间。
- PlayMode：`contract-run3/playmode.xml`，20通过/0失败/0跳过，12.83秒测试时间。
- 本轮观测：`contract-run3/city-captures/runtime-observed-appearances.json`。报告的输入快照SHA匹配；八人的启用文件SHA已与实际加载的Resources TextAsset及隔离文件核对。
- 真实场景八人全部V12/8帧，8方向各8张纹理，独立idle匹配。年轻吕洞宾实际移动约4.8单位、观察8帧、停步成功；控制器速度9，步态周期约480ms、周期距离4.32单位。实际运动采样方向是N；八向资源库存检查不是八向真实移动观测。
- 16帧代码测试使用内存夹具，验证16/30ms/480ms契约、距离与相位、停止idle、失效缓存与同角色缺帧回退；不能替代64张真实新增动作。
- 设备maxTextureSize=16384，只表明设备能力；未实际导入不存在的V13 8192条带。

截图已检查：受控八人场景和真实天墉城中的年轻吕洞宾均为现有V12。截图有原PNG及便于审阅的JPEG副本。

之前两轮证据完整保留：run1为297中296通过、1个测试夹具错误；run2因Unity弃用GetInstanceID编译失败而无XML。修正测试夹具非十六进制SHA和使用当前GetEntityId接口后，run3两平台通过。测试断言未删除。

`summary.json`记录测试XML SHA、截图SHA、隔离保存输入复核以及正式工程同时变化。隔离工程唯一运行后文件变化为动态字体 `Assets/Resources/Fonts/QdaoBody SDF.asset`；原/新SHA均保留，未改写输入快照。正式工程有其他任务的并行变更，均未覆盖。未来V13发布必须针对完整真实素材重新暂存、捕获输入并完成运行核验；不得将此V12观察文件冒作V13发布批准。
