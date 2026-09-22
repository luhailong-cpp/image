# 04 SW16 步态修订 — 2026-09-21

推荐 **SW16-pose-v3** 进入完整 30ms SW 循环复核。已修正首稿摆动脚跨到屏幕左前的错误；未批准整方向或完整角色。本子任务正好 2 次内置生成、0 次收费 API，未写 canonical 或其他共享 staging manifest。

## 两次修订

- `SW16-pose-v2`：参照 SW15、旧 SW01 和旧 SW13，盾侧左脚回到屏幕右侧，但模型把两靴放得接近同一画面高度，接旧 SW01 仍会改变投影位置。保留原图与全部证据，不选用。
- `SW16-pose-v3`：只使用旧 SW01 与 SW15 两张参考，短提示明确近侧摆动靴在右下、远侧承重靴在左上；近脚虽仍在落下阶段，在斜视地面投影上仍低于远脚。没有使用镜像、复制、插值或局部像素变形制造动作。

本代理实际检查原生 raw、透明输出、深浅底接缝、脚部近景。v3 的摆动盾侧左靴保持屏幕右下，与旧01的两脚位置关系一致；不再跨腿或大面积露出鞋底。鞋角、裤褶与旧01仍有区别。头身、装备、相机和画法延续当前 SW 新帧。`audit_06` 独立审查两张接缝图后也确认上述变化，认为静态脚部衔接可进入循环复核，未宣称动态通过。

## 文件与数值

- 原生 1254×1254；输出 1024×1024 RGBA；固定 `common_scale=.84`，未改单帧 scale。
- 上身轴 x=512，脚底 y=942；未裁切。
- SW15 / v3 / 旧SW01 可见高度：774 / 796 / 792px。v3→旧01仅差4px；15→v3仍有22px变化，需真实连播检查自然起伏和上身衔接。
- raw alpha>8 主体 bbox `[156,39,1108,1199]`，实测占高92.50%、顶部空白3.11%、底部4.39%。**没有完整满足提示词89%和上下5%的目标**，但原生四边未裁切，标准导入/输出安全检查通过；不通过逐帧缩放强行追目标。
- 现有未修改 verifier 的单帧来源与像素复算通过，状态 `partial_sources_pending_visual`；全部来源 SHA-256 绑定见导入报告。
- 本机参考文件、精确 prompt、request、receipt、真实 output_hint/default原路径、native raw 和 provenance 均已保存；默认生成原文件未删除。
- 实际型号/质量为 `host-managed-unverified`；C2PA 软件值 `gpt-image` 不代表已明确锁定2.5或2.0。

[最终透明 PNG](staging/candidate/04_mountain_guardian_boy/walk/SW/16.png) · [全身接缝](seam15-16-01-light.png) · [脚部接缝](feet15-16-01-dark.png) · [视觉数值](visual-summary.json) · [重建记录](staging/candidate/04_mountain_guardian_boy/recovery-bindings/SW16-pose-v3/import-result.json)

输出 SHA-256：`376b8dde932a546c1accb9133d106918afd62797468fad055045db21eec5324f`。
原生 raw SHA-256：`eaf52bedea67450b7f71c547441b41891a45584f2f156ea892efbcb3fecf5bac`。

下一步由主任务把此帧加入独立完整 SW/八方向预览，按30ms检查15→16→01→02；旧01/13与其他旧动作保留，不改为新图。
