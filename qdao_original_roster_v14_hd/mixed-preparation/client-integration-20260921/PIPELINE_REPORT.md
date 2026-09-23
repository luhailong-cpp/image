# 2026-09-21 本机发布工具与资源接续报告

当前新V14可发布人物为0。00–03仅有正式完整V13；04/05/06缺walk分别10/64/107；其余保留8名各缺128walk+8idle。原始肖像均保留，候选运行时portrait与3JSON状态逐项列在[15名实际盘点](RETAINED_ROSTER_STATUS.md)及[详细JSON](retained-roster-inventory-detailed.json)。未生成、恢复、批准、stage或publish任何人物。

## 已完成代码

- `mixed_workspace.py`：checkout自定位正式路径；隔离默认`workspace/tmp/qdao-original-live-candidate-20260921`，支持限定在workspace/tmp的`QDAO_ISOLATED_PROJECT`。历史JSON保持原字节。仅固定SHA历史formal baseline的旧工程标签接受精确E:/work别名。
- `prepare_mixed_roster.py`和全高清publisher按保留15ID过滤；历史23ID身份inventory不改，不恢复被删除人物。
- `approve_mixed_roster.py`、`stage_mixed_roster.py`：修复Windows短/长路径重复调用兼容。先检查两侧所有祖先均非链接，再resolve并验证包含关系/唯一工程；没有放松隔离或覆盖保护。
- `publish_mixed_roster.py`：支持04–06按新同ID发布；每个前序V14必须提供顺序完整的正式导入inventory与原publication receipt SHA链。每份旧正式meta/index、隔离stage inventory分别精确保护；跨工程只比较作者资源，允许各自独立的GUID/index字节。
- `record_mixed_formal_import.py`：实际正式Editor导入并关闭后，检查原有资源一字节不变、新包140作者文件/合法派生白名单及137行index。每行绑定本工程PNG GUID、SHA、尺寸、PPU、文件大小与本机时间戳。只记录文件/序列化绑定，不生成Unity/视觉通过证据。
- `verify_mixed_walk_captures.py`已成为publisher硬门禁。每个native方向选manifest中首张native-hd走帧，至少2方向；校验实际Run、1024、104PPU、脚点、运动速度、真实位移、资源SHA、simulationFrame和正常/最近PNG。每个旧/新mixed人物都必须重新通过几何、移动、生命周期库存及全部截图审查。`walk_views`缺失、不全或仍是旧idle会拒绝。
- 当前`identity_runtime_contract.py`绑定17份身份脚本/协议及17.meta；另单独绑定WorldLabelBillboard与camera测试及各自meta，当前mixed共88项。旧历史baseline source_paths保持原值。要求实际14项身份Edit、6项身份Play与28项camera/nameplate Edit用例，包含首次进图后AOI修复空账号外观、真实按钮driver和近景完整构图回归；断网/合成夹具不等于联网或高清验收。fullHD当前绑定同样增加这些依赖。
- 两份新增身份测试.meta需由实际Unity生成后才能进入新快照；本工具不伪造它们。截图源C#由根代理负责同步和运行，本报告不将保存C#或离线编译计为运行通过。

当前操作说明：[混合发布2026-09-21版](../../tools/PUBLISH_MIXED_ROSTER_CURRENT.md)。旧工具说明加了历史标记和链接；暂停交接、旧批准、旧运行证据和历史baseline均未重写。

## Python验证记录

首次8套共142项，134通过、8项失败，暴露Windows TEMP短名/长名问题。修复approval路径后，7套113项109通过、4项stage execute路径失败。进一步修复stage双方路径归一。失败日志保留在本目录，不能当通过。

2026-09-21最终审计重新运行当前8套完整Python测试：**147/147通过，176.527秒，退出码0**。原始日志：[python-audit-full-suite-20260921.log](python-audit-full-suite-20260921.log)；执行范围和工具SHA：[pipeline-audit-final-result.json](pipeline-audit-final-result.json)。执行命令：在`qdao_original_roster_v14_hd/tools`下运行本机Python 3.12的`-X utf8 -B -m unittest discover -s . -p 'test_*.py' -v`。

覆盖assemble/approve/stage、Windows路径、顺序发布3份import链、既有meta/index篡改拒绝、本工程137行index绑定、角色计数/错误回退拒绝、实际native走帧绑定和独立视觉审查门禁。合成夹具仅证明工具门禁和保护行为，不能替代真实人物/Unity/正式链验收。失败日志全部保留，最终通过记录不替换历史失败记录。

同次只读复核了详细inventory中的每个动作槽，当前计数全部一致；正式V13仍仅00–03，正式V14仍0。新身份测试的两个`.meta`尚待实际Unity导入生成，发布门禁不因此放宽。

后续代码冻结新增同身份缺资源恢复用例，以及真实角色按钮driver的两项断网UI用例。身份门禁已随之扩为**14 EditMode + 6 PlayMode、当前mixed绑定84文件**（新增driver及分离测试源和两份meta）。原147项结果保留，不能当作此次新绑定的结果。受影响5套实际定向重跑 **73/73通过，34.417秒，退出码0**：[新增角色UI门禁日志](python-role-ui-gates-20260921.log)及[补充结果](pipeline-role-ui-gates-result.json)。新driver的真实Unity截图和联网运行仍由主任务验证；这里的Python测试没有生成或代替那些证据。

正式run1实跑结果为377 Edit/49 Play，但实际nearest截图发现人物头顶裁切，视觉未通过。随后相机/名牌修改对应新增4份当前源/meta绑定与28项camera Edit必测；runner加入完整camera类，并修复了publisher与runner旧Edit filter排列不一致造成的精确比较拒绝。新5套定向测试 **76/76通过，43.229秒，退出码0**：[相机门禁日志](python-camera-label-gates-20260921.log)及[补充结果](pipeline-camera-label-gates-result.json)。旧147/73结果和固定baseline均未覆盖。

对真实run1 XML的只读验证确认身份14 Edit/6 Play名称和数量一致，旧Edit因缺camera用例/旧filter被当前门禁正确拒绝；Play结果及launch绑定可解析。见[真实XML负例记录](run1-real-xml-camera-negative.json)。这不追认run1视觉通过。`check_runtime_view`仍依据实际投影计算clipped标志，nearest允许如实记录false但不会自动成为视觉批准；没有把旧false改成true或放宽投影检查。当前新相机运行的真实XML与PNG结果仍须另行验证。

新相机正式run2的真实Edit结果**405/405通过**，当前`check_results`与`check_launch_binding`只读函数验证接受，确认camera28、身份14及完整实际filter均到位：[实际Edit门禁记录](run2-real-camera-editmode-gate.json)。该记录仅绑定Edit XML/launch/completion/log/input；Play、截图和联网状态仍由后续实际结果确定。

run2随后实际**49/49 Play通过**；只读`check_unity_results`与`check_launch_binding`均接受真实Edit/Play证据，16张实际PNG通过路径/SHA/尺寸/投影绑定检查。00–03的nearest记录中full frame、脚点和名牌均为true；这是实际捕获数据，未重写run1裁切记录。见[实际运行绑定记录](run2-real-camera-runtime-gates.json)。图片目视结论由主任务另行审查，不能仅由这份JSON作结论。

该轮完整输入一致性仍有明确差异：Edit前后仅`ProjectSettings/ProjectSettings.asset`变化，原始长度20711→20686。只读内存字节验证证明差异恰好是删除`Standalone: APP_UI_EDITOR_ONLY`之后的`;SENTIS_ANALYTICS_ENABLED`后缀；恢复后缀后的SHA精确回到Edit前快照。没有写回设置或放宽门禁。因此run2的函数级XML/launch/截图绑定通过，不表示它已满足publisher要求的Edit/Play/post全量输入一致性；当前也无齐套mixed包可发布。

## 仍明确阻塞

1. 缺1205walk+64idle；04部分边缘、05完整NE连播/接缝、06边缘与新原图导入仍未批准。没有完整新人物可走真实mixed流程。
2. 本轮正式Unity导入触发旧TextureImporter `.meta`序列化变化。这必须与PNG/JSON和GUID是否改变分开审计。固定历史baseline SHA仍为`8238ab4d32a2c4782f2b853339257cd3054b5e9b8c9c796351d78b42b823377f`，本次实测未改变。Publisher仍拒绝旧meta漂移；没有以当前文件或新Git HEAD重新封存基线，也未实现泛化meta例外receipt。后续若要接受导入迁移，必须先有精确旧meta字节、GUID/原字段/纹理合同和真实导入后字节的专门审核，不能仅放开SHA。
3. 当前没有本次真实新1024走帧、正常/最近视图目视批准或mixed正式流程截图。工具单测、已有512资源或沙盒枚举不构成这些证明。
4. 正式登录/选角/保存/主城/队伍/战斗/重登结果由主任务汇总；本资源库存与工具报告不替它们宣布完成。

## 并发与保留

开始核查时image HEAD为068e9bc3，人物最后修改为f09d353c范围更新。工作过程中外部提交3132dbcc等包含了部分本代理尚在实现的文件，本代理未执行git add/commit/push，也未回滚并发主城删除。最终任务改动不能只按当前git diff估算。
