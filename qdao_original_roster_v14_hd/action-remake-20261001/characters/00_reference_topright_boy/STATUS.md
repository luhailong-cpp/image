# 00 金发带道童当前状态

本角色继续制作中。PNG 已生成、候选导出、技术检查、美术通过、客户端接入分别计算；现有图片不表示完整帧组已经完成。只在本角色目录续作，另一台电脑未提交内容没有取用。

<!-- CURRENT_SNAPSHOT_START -->
核对时间：2026-10-02T07:24:50.968381-04:00（America/New_York）。本段由 tools/audit_provenance.py 实扫更新。

当前候选导出 **57/196**，缺 **139** 槽；本批本角色 generation 实际原图 **4** 张。正式美术通过 **0**；客户端 **未接入、未运行**。

| 动作/方向 | 实际导出帧号 | 缺失帧号 | 帧时长 / 完整段时长 |
| --- | --- | --- | --- |
| run/N | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/NE | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/E | 01、04 | 02、03、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/SE | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/S | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/SW | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/W | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| run/NW | 无 | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 30 / 480 ms |
| hit/E | 01、02、03、04、05、06 | 无 | 40 / 240 ms |
| hit/W | 01、02、03、04、05、06 | 无 | 40 / 240 ms |
| attack/E | 01、02、03、04、05、06、07、08、09、10、11、12 | 无 | 30 / 360 ms |
| attack/W | 无 | 01、02、03、04、05、06、07、08、09、10、11、12 | 30 / 360 ms |
| cast/E | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15、16 | 无 | 45 / 720 ms |
| cast/W | 01、02、03、04、05、06、07、08、09、10、11、12、13、14、15 | 16 | 45 / 720 ms |

当前本批原图（逐图来源、完整路径及导出链见 [来源审计](review/provenance-completion.json)）：

| 文件 | SHA-256 | 已关联导出 |
| --- | --- | --- |
| [generation/combat/attack/W/06-v3.png](generation/combat/attack/W/06-v3.png) | `527ff10ab675ab3c0596ee1a3a8274ee095b8e3fc17a1f3919083a86d6cf21e8` | 未导出；待选帧/验收 |
| [generation/run/E/01-v5.png](generation/run/E/01-v5.png) | `0335d08d84cd367c85a43fb72dd69980a45befd970d9ab1de1a1758a315b4dc6` | 未导出；待选帧/验收 |
| [generation/run/E/04-v1.png](generation/run/E/04-v1.png) | `ecc55b1b0e7dea0d3f2077e106a229d679e7f2e71cacba773df263f0a6927a06` | frames/run/E/04.png |
| [generation/run/E/09-v3.png](generation/run/E/09-v3.png) | `703ab6983638bbcd29488af9806644205168a508c7bd85f6bb6ea56d208e5a83` | 未导出；待选帧/验收 |

已确认失败请求 6 项（原始网络错误证据保留）；无完成证据请求 3 项（unknown，不等同于已确认失败）。

- `generation/combat/attack/W/06-v1.request.json` — `confirmed_failure`；SHA `46b18acd30cdc2e76aab1eb552faa90e3a9cefb054396a9ba700a871a8f424ab`。
- `generation/combat/attack/W/06-v2.request.json` — `confirmed_failure`；SHA `15f79062b2d44e7fca1cdbd8b10929ed62b80bda705b618c82ab3c164fde5fb2`。
- `generation/combat/cast/W/16-v1.request.json` — `confirmed_failure`；SHA `5a4f35dbfa78cba8797b994877eb7d284b61a8330c1b5194e223d22232b5209e`。
- `generation/combat/cast/W/16-v2.request.json` — `confirmed_failure`；SHA `fd301a6b0279b4605f81bdf5d0d375e3d524243abf3cf044a7699b86ebec4d12`。
- `generation/run/N/01-v1.request.json` — `confirmed_failure`；SHA `4369161b44a6161fc9f1b1c1ffcd092d42851e587181ed1261f72a668bd045c5`。
- `generation/run/N/01-v2.request.json` — `confirmed_failure`；SHA `cb1890b901b4b6b3ec504771eeb236648b3c9a4100c0ceb8349269f5ce8fe0b5`。
- `generation/combat/cast/W/16-v3.request.json` — `unknown_no_completion_receipt`；SHA `5d13252494f0ca7d776eece32b29a35e01f57aa5ffbec9dab5efc6ca81df8fa0`。
- `generation/run/E/09-v2.request.json` — `unknown_no_completion_receipt`；SHA `65b205d98eb8e51761d040eb5f6a4a50020cee35ea04f4537da01db2866eda03`。
- `generation/run/N/01-v3.request.json` — `unknown_no_completion_receipt`；SHA `68659a615a528a35f695bc357bb30c97903a2771d499d906e005de1241a05eff`。

当前索引/源SHA问题 0 项。逐项文件、源PNG、生成记录与回执SHA均在 `review/provenance-completion.json`。
旧 `current-validation.json` 的 57 张检查仅适用于其原始快照；新增原图、替换及当前动态美术结果须另行刷新。
<!-- CURRENT_SNAPSHOT_END -->

## 当前仍须处理

- 跑步旧 E01-v4、新 E04-v1 和 E09-v3 的头脸相对身体、战斗母版比例不一致，三张均需按 [比例复核](review/scale-audit.md) 修正。新版本的到盘与选择情况见上表；新版本需重新绑定 SHA 审核，不能自动继承旧结论或当作修复通过。
- `hit/W/03`：双鞋站位突跳，须核对根点与支撑关系；`attack/E/10`：双鞋平底基线偏高，须核对地面和收招衔接。
- `cast/W/02`、`cast/W/05`：右手轨迹存在提前抬高/前伸后回收，须正常速与慢速判断并定向修正。详情见 [战斗复核](review/combat-reviewed.md) 与 [施法复核](review/cast-review.md)。
- 补齐上表空槽；不复制、镜像、插值填数。全套跨动作比例、固定根锚、手脚交替、持物连续、首尾衔接和透明边缘尚未最终验收。
- 现有 HTML 支持正常速度、¼ 慢速、逐帧；旧控件检查为 Node 简化 DOM，不是实机浏览器动态美术验收。`file:` 浏览器打开曾被 URL 策略拒绝，原始说明在 `review/current-validation.json`；不把离线页面存在当作播放已验收。

固定根锚 `(512,942)` 与现行整画布变换仅是待复核候选，详见 [合并交接](MERGE_HANDOFF.md)。所有最终美术与客户端状态保持如实记录。

更新库存与文字快照（仅写本角色审计 JSON 和本文件/交接中的快照区；不生图、不改 PNG、不改历史来源）：

```powershell
& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy/tools/audit_provenance.py'
```
