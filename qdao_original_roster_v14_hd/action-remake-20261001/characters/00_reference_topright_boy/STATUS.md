# 00 金发带道童当前状态

本角色继续制作中。PNG 已生成、候选导出、技术检查、美术通过、客户端接入分别计算；现有图片不表示完整帧组已经完成。只在本角色目录续作，另一台电脑未提交内容没有取用。

<!-- CURRENT_SNAPSHOT_START -->
待首次实扫更新。
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
