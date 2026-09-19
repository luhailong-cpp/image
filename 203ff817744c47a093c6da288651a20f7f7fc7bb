# V14 原生高清工具

## 新窗口混合分辨率接续

最新状态见[接续记录](../CONTINUATION_MIXED_20260918.md)。客户端逐帧512/52与1024/104兼容已通过真实Edit363/Play43并同步角色源码；实际完整混合素材仍为0。旧全HD工具和审批门禁保留。

- `prepare_mixed_roster.py`：仅为04–06保留旧图写新的证据快照、137槽计划和19名精确缺帧表；不会导入、审批、stage或publish。用法见[MIXED_PRESERVED_CONTRACT.md](MIXED_PRESERVED_CONTRACT.md)，12项保护测试通过。
- `capture_mixed_formal_baseline.py`：本轮正式角色资源/相关源码的只读安全基线；不是Unity测试输入快照，也不删除锁。
- `review_mixed_client_run.py`：只接收本轮真实完整Edit/Play/post证据，核对14/8混合测试及原HD用例、50源码绑定、12真实正常截图；仅允许明确10个角色C#/meta同步。实际资源发布仍须完整美术审批和另行混合发布门禁。

## 原有全高清工具与历史验证

先读[当前用户范围与暂停点](../CONTINUE_AFTER_MODEL_CONFIRMATION.md)。旧素材保留；当前没有确认的2.5新图，不开展新增绘图。V14准备工作不构成重做全23名旧角色的授权。

- pipeline.py：真实源图抠色、整格统一缩小、整数对齐；最低原生cell两边均1024，禁止放大；输出1024×1024。单人物源用rows1/cols1及明确output-frames。角色固定common_scale：04/05为.84，其余已有定义为.88；不得逐帧按身体包围盒缩放。
- verify.py：从原始PNG逐阶段独立重建，核验来源、137运行PNG与review/strips；可用--direction E --frame1只查单帧，但它不是完整审批，不能与--require-visual组合。完整审批须独立视觉复验。
- approve.py：保留旧流程的最新输入、SHA、审核历史绑定，额外要求native_resolution_review和closeup_1080p_review及具体notes。操作前读--help和代码，不凭候选文件数量假通过。
- preview.html/serve_preview.py：预览实际输出帧。尚未有完整V14角色的浏览器视觉审批。
- publish_original_roster_v14.py：仅接收完整已审批资产与本次真实Unity输入证据；运行包137PNG+3JSON，8条16384×1024strip只存review。正式发布必须提供[运行视觉审查](RUNTIME_REVIEW_FORMAT.md)，stage不等于发布。
- inspect_image_provenance.py：只读提取PNG中C2PA创建动作及软件版本，校验PNG CRC和SHA；不验证签名，也不能把隐藏后端型号锁定为某版本。

## 本轮实际检查

04现有单人物原生1254样本导入1024后，独立重建通过；原人物高1145px，factor0.685933，无放大。报告：[validation-E-01.json](../candidate/04_mountain_guardian_boy/review/validation-E-01.json)。状态partial_sources_pending_visual；没有完整角色审核或发布。原图属于此前已有样本，未重标为2.5。

627格反例：[只读门禁记录](../model-evidence/readonly-native-minimum-guard.json)。真实import_sheet的所有写函数替换为禁止写入保护，然后读取实际1254/2×2源；在触达任何写函数之前被原生分辨率门禁拒绝。先前直接导入测试被自动审批阻止、并未执行；此次安全只读验证独立完成，无候选文件新增。

Unity最新真实验证：Edit349/349、Play35/35，发布器15项门禁检查通过。46绑定一致、25973输入无增删改。完整证据见[客户端交接](../CLIENT_INTEGRATION_HANDOFF.md)。真实HD角色仍为0，不能用这些结果替代未来新角色的真实验收。

vendor来自V13的2个原加工器原样复制，SHA见vendor-provenance.json。所有新图仍须保存真实raw/prompt/receipt，不能镜像、复制或插值凑帧。
