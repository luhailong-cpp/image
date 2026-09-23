# 08 清理候选清单（只计划）

快照时间：2026-09-23T13:18:21.932748+00:00。未删除、移动或改写任何图片。详细逐文件路径、字节数、SHA、作用范围和回执映射见 [cleanup-candidates.json](cleanup-candidates.json)。计划脚本 [cleanup_inventory.py](cleanup_inventory.py) 只读取文件并更新此计划，不含删除逻辑。

- 仓库候选图片 1712 个，1,492,159,978 字节；只来自 08-generation、08-delivery-preview、08-tools 三个专属根目录。
- 检查真实回执 186 份，精确映射宿主图片 186 个，其中存在 186 个、与仓库 raw SHA 一致 186 个。未扫描宿主输出目录，也未认领无回执的图片。
- N/NE 在制保护：仓库图片 386 个、宿主映射 48 个；都标记等待最终锁定。
- 未核实回执映射 0 项；无回执 attempt 4 项。这些项目不构成宿主原图删除授权。

候选不是立即删除清单：所有条目 deleteAllowedNow=false。runtime 副本和 revision 预览必须等 root 锁定最终 136 张游戏 PNG、最终预览设计名单后再逐文件排除保留项。N/NE 正在制作的唯一稿仍应保留；其他方向也等待最终成品与引用审计。后续新增文件不在本次快照内，执行前重新核对。

可在上述前提满足后移除：仓库 raw、拒稿图、清边/缩放加工图、被正式包替代的 frame 副本、未选用的旧 revision/临时 review 图片，以及回执精确映射且 SHA 匹配的宿主原图。08-generation/references 内的 identity1024/style1280 只是本角色临时输入副本，须待全部生成结束后再移除；共享原始4096身份设计、designs 风格原件未进入候选。

逐图 prompt/request/receipt、模型与质量记录、SHA/来源链、选用和拒稿文字证据全部保留。只能据精确路径移除图片，不递归删除 attempt、revision 或宿主目录。此清单没有执行任何清理。
