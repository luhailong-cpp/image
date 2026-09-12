# v11 六角色透明边导出修复验收

2026-09-12 完成并发布。本记录只覆盖 v11 的 23、24、25、26、28、29 六角色透明边 RGB 污染及其整包衍生，不代表全项目的 UI、场景和 v9 精修全部完成。

## 交付结果

- 303 项正式媒体修复并重新导出：255 PNG、48 GIF；涉及 195 张独立底图（192 行走帧及 25／26／28 肖像），共修改 917,881 个 RGB 像素。
- 六角色合计 306 项正式媒体中，23／24／29 肖像保留原字节。27／30 全部 102 项正式媒体也保持原审查哈希。整包共 408 项正式媒体，303 项更新、105 项保留。
- 六角色全部 258 PNG 的 Alpha 逐像素不变，48 GIF 的解码二值 Alpha 逐像素不变；512 × 512 行走画布、脚底 y=471、横向锚点 x=256 ±0.5、八方向和每方向四帧顺序均未改变。
- strip、cardinal／diagonal sheet 均由同一组干净 PNG 帧逐像素拼接。GIF 为四帧、每帧 120 ms、循环 0，色彩来自相同 PNG；不透明区域解码 RGB 平均绝对误差上限 3.805（8 位通道单位）。
- 当前角色 manifest／qc、新的六份 `processing/festival-edge-approval.json`、24 张浅／深底接触表、总览 JPG、动作总览 GIF、整包 manifest／validation／ZIP／download.json 已同步。
- 原有 `verify_delivery.py` 已通过八角色、256 帧、408 正式媒体，errors 为空。最终独立脚本还核对 ZIP 中 408 项正式媒体和 46 项清单／验收／总览文件均与当前工作目录逐字节同哈希。

最终下载包：[qdao-roster-v11-final.zip](../../qdao_chibi_roster_v11/qdao-roster-v11-final.zip)，161,095,220 字节，738 entries；SHA-256：

```text
4cf2fe9f9b6cd23f024038dbd0bca1668e03f52eb7ab04afc4abcefb0186446f
```

## 方法与保护范围

本轮按 `generate2dsprite` 的已有素材后处理范围执行，没有新生图或手绘新细节。来源是已验收 AI 原画及正式独立帧的不可变 before 快照；沿用项目既有 27／30 去边方法，扩充保护色逻辑。主体风格仍为道家 Q 版，原有灯笼、红结、月兔、桂花、粉莲与服饰点缀原样保留。

实现位于 [repair_v11_edges.py](repair_v11_edges.py)。以 `dom = min(R, B) - G` 与距透明边的距离定位品红底混色，仅从同一张原图附近已有前景取 RGB。普通边缘使用 17 × 17 透明邻域（8 px 半径）；23／24／25／26 也处理明确强品红的内部间隙。供体 Alpha 至少 240、向内一像素、`dom < 5`；按 8／16／32 像素范围寻找符合品红混色关系且距离较近的原图供体。

28／29 单独保护丁香／粉色服饰：黑发区域按头部位置和连通性限定，身体仅选择高置信强底色，保留有意粉紫配色。29 垂发的末版修正要求供体同时属于头部连接的中性深色区域且 `dom < 5`，避免把旧紫边当成新颜色传播。诊断中的“强品红像素数”不是全图归零门槛；有意服色仍允许满足颜色阈值。

处理器断言 Alpha 全等、未选择像素全等、全透明像素的隐藏 RGBA 全等，且单图 RGB 改动不超过画布 4%。逐图修改遮罩在 `masks/`，参数、供体距离和文件哈希在 [stage.json](stage.json)。未重定位、缩放或改变轮廓。

GIF 有历史量化例外：旧编码器曾把极少数边缘前景映射到透明索引，因此旧 GIF 二值 Alpha 与 PNG 的 Alpha≥128 门槛并非处处等价。本轮从旧 GIF 解码取得原二值 Alpha，并从干净 PNG 取得 RGB；量化后仅对旧透明区域使用索引 0，前景误落到索引 0 时改取最近的非零调色板颜色。这样同时保持 PNG 完整 Alpha 和 GIF 既有二值透明。每帧例外数量在 [derived.json](derived.json) 内 `preserved_legacy_gif_threshold_exceptions`，不是新增缺口。

## 目视验收与记录归属

本轮实际查看了六角色肖像及 S01 的浅／深底前后对比、29 S01 垂发放大局部、六角色全部 192 帧的 12 张深底接触表、28／29 全部 64 帧的四张浅底接触表，以及实际解码 GIF 的六角色 S 向四帧（24 帧）预览。发布后也查看了重建的八角色总览。黑发紫边改善，28 丁香衣和杏色裤、29 粉莲及青粉衣、红结和职业物件保留；帧间颜色一致。

另一审查代理独立查看了 28／29 初期试样，指出 29 垂发残色，促成了供体条件收紧；该意见仅属于该试样，不冒称该代理独立批准最终全批。最终批量批准由 `check_cleanup_impact` 记录。全部 50 张前后对比页虽已生成，并未逐页目视；实际目视覆盖如上。未做游戏引擎导入或运行测试。

- [before.json](before.json)：384 项原正式媒体、清单、历史 QC、总览／包和构建入口快照；最终审计重新检查所有快照哈希。`before/` 中旧 QC 保持原文。
- [stage.json](stage.json)：198 张独立底图的数值结果，其中三肖像原样保留。
- [derived.json](derived.json)：306 项六角色正式媒体的尺寸、Alpha、帧顺序、锚点与 GIF 结果。
- [gif-validation.json](gif-validation.json)：48 GIF、192 解码帧的 RGB 和透明检查。
- [visual-approval.json](visual-approval.json)：绑定当前 stage、derived、GIF 检查哈希的本轮实际视觉批准。
- [publication.json](publication.json)：303 媒体与 42 清单／新验收证据的发布及发布后核对，共 345 项。
- [final-verification.json](final-verification.json)：当前全部 408 正式媒体、保留范围、ZIP 和元数据的一致性终检。

`stage.json`／`derived.json` 的状态保留为当时“待目视”阶段事实，`publication.json.next` 保留当时发布后待打包事项；它们都是被后续批准引用哈希的不可变阶段记录。当前完成状态应读取 `visual-approval.json`、`final-verification.json` 及正式整包 `manifest.json`／`validation.json` 的 `festival_edge_export`。旧 `processing/visual-review.jpg`、旧 pipeline／frame-transform／delivery-verification 记录仍属于历史生产证据，不用于冒充本轮文件的视觉批准。

## 可复现入口

在 `E:/work/image` 执行下列命令。第一条从不可变 before 重算六肖像及六个正面首帧，并与正式文件逐像素比较；本轮已运行，12 张通过。省略 `--trial` 可只读重算全部 198 张独立底图。第二条重新审计现有包与全部正式文件，只覆盖本目录的 `final-verification.json`，不改媒体。

```powershell
python -B qdao_festival_refinement_20260910/edge_exports/verify_rebuild.py --trial
python -B qdao_festival_refinement_20260910/edge_exports/audit_final_delivery.py
```

初次执行的生成流程为 `repair_v11_edges.py --trial` → 局部目视迭代 → `repair_v11_edges.py --stage` → `rebuild_delivery.py build` → 数值与目视批准 → `rebuild_delivery.py publish`。二次查看请使用上面的只读命令；stage／publish 会验证当前源仍等于 before，已发布后再次运行会安全拒绝。需要从头重建时应在隔离副本恢复 before 对应正式输入，不覆盖当前交付。

全包衍生沿用 `qdao_chibi_roster_v11/finalize_pack.py`、`verify_delivery.py` 和 `package_delivery.py`。整包清单和 validation 的本轮 `festival_edge_export` 必须在 finalize／verify 后保留或重新绑定再打包；不能仅重跑旧 finalizer 便认为本轮批准仍已关联。打包器仅增加包含 `processing/festival-edge-*.jpg` 的规则，旧打包器已冻结在 before 内。

本轮验收文件 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| 整包 manifest.json | `3d59b0fe961ef8d4731b2de3c7a48dbc378ab0a62196b14c80825d75eb8aad40` |
| 整包 validation.json | `a74dce00fc3e5643098838d285faa8e9e7a47ab38e8189724a8301da3d4747cf` |
| visual-approval.json | `660e0bffb0607d4682f2f82e0fea2ea80768f10de120e42abc5e61af0d090d2d` |
| final-verification.json（初次终检） | `20828c3bcee65e3dd0ddc6b6c0045baf1da1051e5456bdf620d17056fda34843` |

重新运行终检会更新其 UTC 时间和该 JSON 自身哈希，不影响任何正式媒体与批准记录。
