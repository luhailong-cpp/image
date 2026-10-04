# NW / SW 支撑足修正最终候选交接

更新：2026-10-04T19:15:40.474783+00:00

本轮选定 32 张候选，其中 14 张新修、18 张沿用。已实际查看 2 张完整连图，支撑足别已核实；这是供父线程统一导出和动态审核的选帧，不是全角色完成声明。未在客户端接入，也未完成本子任务的浏览器动态验收。

当前唯一选帧入口：nw-sw-supportfix-selection.json。旧 nw-sw-grounding-selection.json 仅保留为旧来源，旧 review 的通过结论不得继承。

固定整张原图 1254×1254 缩为 940×940，放到 1024×1024 的 (42,49)；不得按每帧包围盒或最低像素重新对齐。16 帧 × 75ms = 1200ms。

NW：左足支撑 15/16→01/02→03/04→05/06；右足支撑 07/08→09/10→11/12→13/14。SW：上述第一条为右足，第二条为左足。前/中/后仍是实际空间验收，不以标签充数。

## 最终新候选

| 槽位 | 候选 |
|---|---|
| run/NW/05 | run-NW-05-supportfix-v3 |
| run/NW/06 | run-NW-06-supportfix-v3 |
| run/NW/07 | run-NW-07-supportfix-v4 |
| run/NW/08 | run-NW-08-supportfix-v4 |
| run/NW/09 | run-NW-09-supportfix-v1 |
| run/NW/10 | run-NW-10-supportfix-v2 |
| run/SW/05 | run-SW-05-supportfix-v2 |
| run/SW/06 | run-SW-06-supportfix-v2 |
| run/SW/07 | run-SW-07-supportfix-v1 |
| run/SW/08 | run-SW-08-supportfix-v1 |
| run/SW/09 | run-SW-09-supportfix-v1 |
| run/SW/10 | run-SW-10-supportfix-v1 |
| run/SW/11 | run-SW-11-supportfix-v1 |
| run/SW/12 | run-SW-12-supportfix-v1 |

其余 18 张旧来源和 SHA 已原样带入 selection。32 张均有各自独立 SHA；完整文件检查见 nw-sw-supportfix-validation.json。

## 必须如实保留的动态复审项

- 右支撑足别已修正；09 到 10 的纵向相对足位仍有小幅前退，四段位置差异偏小。须父线程实际动态审核。
- 05/06 已从重复左支撑换为远右支撑，接地靴仍较接近身下，后侧推蹬幅度较弱。须动态审核是否达到身体经过支撑足的感觉。
- 沿用旧候选，11 到 12 扇手由后向前改变较大；本轮不宣称手部过渡已动态通过。

可选 NW 顺序（未应用）：07=NW10-supportfix-v2、08=NW08-supportfix-v4、09=NW07-supportfix-v4、10=NW09-supportfix-v1。这会使接地足相对位置更顺，但有手部相位代价；父线程须看动态后决定。

## 预览与来源

- nw-sw-supportfix-preview.html：两方向独立播放，默认 1×，75ms/帧；支持暂停与逐帧。
- nw-sw-NW-supportfix-contact.png、nw-sw-SW-supportfix-contact.png：最终 32 张静态连图。
- 新图走宿主内置 image_gen，目标 GPT Image 2.5 Sunburst / max。实际提交没有型号/质量选择器，实际返回值未披露，actualModel/actualQuality 保持 null。
- 28 张本轮 supportfix 生成候选均有逐图 request/prompt/receipt/generation 文字记录；入选 14 张。最终正式导出并确认引用完整后，由父线程统一清理不再需要的中间 PNG。
