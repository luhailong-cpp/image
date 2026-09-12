# 月兔肖像发梢补充修复

2026-09-12 已完成并同步最终包。补充仅涉及 `qdao_chibi_roster_v11/28_moon_rabbit_artificer/portrait.png` 左下发梢 166 个 RGB 像素，坐标包围框 `[351,420,410,432]`；Alpha、全透明隐藏 RGBA、未选像素、紫色肩缘 `(454,425)` 及 y≥451 的所有身体像素完全相同。没有改动作帧、帧图、条图或 GIF；因此重建的动作总览与补充前仍同字节。

父任务放大 28 肖像和 29 SW 首帧时发现疑似色点。本轮先用 Pillow 原尺寸 `alpha_composite` 在浅米底和深绿底渲染，再对合成结果做最近邻放大；排除缩放时未预乘 Alpha 导致的显示假象。29 SW/01 的手腿未确认独立白／绿泄漏点，白袖和鞋饰属于原画；该文件未变。28 发梢的短段暗紫确实在正确合成中可见，因此补修；先前示例 `(454,425)` 放大确认是紫色肩缘，不是头发，明确保护。

[repair.py](repair.py) 从首轮已发布的不可变 before 取图，用上部中性深色的八邻接连通域定义黑发。仅在 y=330…450、距透明边 8 px 内且距连通黑发 4 px 内选择 `min(R,B)-G>10` 的像素；供体必须属于同一连通中性黑发、Alpha≥240、向内一像素且 `min(R,B)-G<5`。在 8／16／32 px 搜索中使用原图品红混色拟合与距离评分，直接复制附近已有 RGB，不创造细节。166 处修改全部落在确认发梢；最大供体距离 11.402 px，平均 4.683 px，无未解决像素。

- [before.json](before.json) 与 `before/`：首轮 303 项修复后的肖像、当前角色清单/QC/批准、总览/整包/下载、旧最终报告与复现脚本的冻结快照。
- [trial.json](trial.json)、[trial.png](trial.png)、[changed-mask.png](changed-mask.png)：逐像素试样、实际原尺寸浅／深底前后对照、166 像素遮罩。
- [approval.json](approval.json)：本轮真实目视批准及 29 复查归属；SHA `22369c1072da1a99ce4620af2c7b5544efb2a3f03fa28e4a42bcbdb9b384b800`。
- [publication.json](publication.json)：肖像、28 manifest／qc／当前批准和一张正式补充对比图的发布；SHA `5959b0150db45a88af3e75681b581d65b56da866d1a4f9f7d5d145835fa532d5`。
- [../final-verification.json](../final-verification.json)：唯一当前整包终检，包含全部 408 媒体、25 新证据图、两个总览和 ZIP 的当前哈希。原 `stage.json`／`derived.json`／`publication.json` 仍保存初轮事实，由当前审计叠加本补充发布。

整包现为 303 项修复媒体（255 PNG、48 GIF），105 项保留；27／30 全部 102 项和 23／24／29 肖像仍与最初独立审查同字节。对原始 before 的最终独立 RGB 变更总数为 917,918（初轮 917,881，补充 166 处中 37 处为新增位置）。原有完整验证通过 8 角色/256 帧，ZIP 739 entries，161,419,936 字节，SHA `86ebe6bd9616037001ea221446b7bc6c221dfba24e4e5934e0fa784e6e683933`。

当前只读复现：

```powershell
python -B qdao_festival_refinement_20260910/edge_exports/verify_rebuild.py --trial
python -B qdao_festival_refinement_20260910/edge_exports/audit_final_delivery.py
```

首条已通过 12 张代表图，含原始 before → 初轮算法 → 本补充算法的月兔最终逐像素比较。省略 `--trial` 重算全 198 张独立底图；第二条只更新本目录上层的终检 JSON，不改图片。`repair.py` 和 `publish.py` 是首发入口，当前交付后不要重复覆盖；`publish.py` 有源哈希前置防护。全包 finalizer/verifier 后必须运行 `refresh_binding.py` 再打包，以保留初轮与补充的当前哈希关联。没有游戏引擎或在线运行测试声明。
