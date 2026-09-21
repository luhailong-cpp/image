# 2026-09-21 本机发布工具与资源接续报告

当前新V14可发布人物为0。00–03仅有正式完整V13；04/05/06缺walk分别10/64/107；其余保留8名各缺128walk+8idle。原始肖像均保留，候选运行时portrait与3JSON状态逐项列在[15名实际盘点](RETAINED_ROSTER_STATUS.md)及[详细JSON](retained-roster-inventory-detailed.json)。未生成、恢复、批准、stage或publish任何人物。

## 已完成代码

- `mixed_workspace.py`：checkout自定位正式路径；隔离默认`workspace/tmp/qdao-original-live-candidate-20260921`，支持限定在workspace/tmp的`QDAO_ISOLATED_PROJECT`。历史JSON保持原字节。仅固定SHA历史formal baseline的旧工程标签接受精确E:/work别名。
- `prepare_mixed_roster.py`和全高清publisher按保留15ID过滤；历史23ID身份inventory不改，不恢复被删除人物。
- `approve_mixed_roster.py`、`stage_mixed_roster.py`：修复Windows短/长路径重复调用兼容。先检查两侧所有祖先均非链接，再resolve并验证包含关系/唯一工程；没有放松隔离或覆盖保护。
- `publish_mixed_roster.py`：支持04–06按新同ID发布；每个前序V14必须提供顺序完整的正式导入inventory与原publication receipt SHA链。每份旧正式meta/index、隔离stage inventory分别精确保护；跨工程只比较作者资源，允许各自独立的GUID/index字节。
- `record_mixed_formal_import.py`：实际正式Editor导入并关闭后，检查原有资源一字节不变、新包140作者文件/合法派生白名单及137行index。每行绑定本工程PNG GUID、SHA、尺寸、PPU、文件大小与本机时间戳。只记录文件/序列化绑定，不生成Unity/视觉通过证据。
- `verify_mixed_walk_captures.py`已成为publisher硬门禁。每个native方向选manifest中首张native-hd走帧，至少2方向；校验实际Run、1024、104PPU、脚点、运动速度、真实位移、资源SHA、simulationFrame和正常/最近PNG。每个旧/新mixed人物都必须重新通过几何、移动、生命周期库存及全部截图审查。`walk_views`缺失、不全或仍是旧idle会拒绝。
- 新`identity_runtime_contract.py`在历史50绑定之外增加15份身份脚本/协议及15.meta，当前mixed绑定共80项；旧历史baseline source_paths保持原值。要求实际14项身份Edit及3项Play用例，包含首次进图后AOI修复空账号外观的回归，并区分已发布资源几何与合成HD生命周期。fullHD当前绑定也增加身份链。
- 两份新增身份测试.meta需由实际Unity生成后才能进入新快照；本工具不伪造它们。截图源C#由根代理负责同步和运行，本报告不将保存C#或离线编译计为运行通过。

当前操作说明：[混合发布2026-09-21版](../../tools/PUBLISH_MIXED_ROSTER_CURRENT.md)。旧工具说明加了历史标记和链接；暂停交接、旧批准、旧运行证据和历史baseline均未重写。

## Python验证记录

首次8套共142项，134通过、8项失败，暴露Windows TEMP短名/长名问题。修复approval路径后，7套113项109通过、4项stage execute路径失败。进一步修复stage双方路径归一。失败日志保留在本目录，不能当通过。

2026-09-21最终审计重新运行当前8套完整Python测试：**147/147通过，176.527秒，退出码0**。原始日志：[python-audit-full-suite-20260921.log](python-audit-full-suite-20260921.log)；执行范围和工具SHA：[pipeline-audit-final-result.json](pipeline-audit-final-result.json)。执行命令：在`qdao_original_roster_v14_hd/tools`下运行本机Python 3.12的`-X utf8 -B -m unittest discover -s . -p 'test_*.py' -v`。

覆盖assemble/approve/stage、Windows路径、顺序发布3份import链、既有meta/index篡改拒绝、本工程137行index绑定、角色计数/错误回退拒绝、实际native走帧绑定和独立视觉审查门禁。合成夹具仅证明工具门禁和保护行为，不能替代真实人物/Unity/正式链验收。失败日志全部保留，最终通过记录不替换历史失败记录。

同次只读复核了详细inventory中的每个动作槽，当前计数全部一致；正式V13仍仅00–03，正式V14仍0。新身份测试的两个`.meta`尚待实际Unity导入生成，发布门禁不因此放宽。

## 仍明确阻塞

1. 缺1205walk+64idle；04部分边缘、05完整NE连播/接缝、06边缘与新原图导入仍未批准。没有完整新人物可走真实mixed流程。
2. 本轮正式Unity导入触发旧TextureImporter `.meta`序列化变化。这必须与PNG/JSON和GUID是否改变分开审计。固定历史baseline SHA仍为`8238ab4d32a2c4782f2b853339257cd3054b5e9b8c9c796351d78b42b823377f`，本次实测未改变。Publisher仍拒绝旧meta漂移；没有以当前文件或新Git HEAD重新封存基线，也未实现泛化meta例外receipt。后续若要接受导入迁移，必须先有精确旧meta字节、GUID/原字段/纹理合同和真实导入后字节的专门审核，不能仅放开SHA。
3. 当前没有本次真实新1024走帧、正常/最近视图目视批准或mixed正式流程截图。工具单测、已有512资源或沙盒枚举不构成这些证明。
4. 正式登录/选角/保存/主城/队伍/战斗/重登结果由主任务汇总；本资源库存与工具报告不替它们宣布完成。

## 并发与保留

开始核查时image HEAD为068e9bc3，人物最后修改为f09d353c范围更新。工作过程中外部提交3132dbcc等包含了部分本代理尚在实现的文件，本代理未执行git add/commit/push，也未回滚并发主城删除。最终任务改动不能只按当前git diff估算。
