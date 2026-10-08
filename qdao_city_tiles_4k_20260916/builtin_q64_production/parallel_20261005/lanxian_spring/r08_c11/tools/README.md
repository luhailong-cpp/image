# r08_c11 原生制作工具

工具本身不生图、不更改总进度、不自动验收。原生输入为 4×4 张 1254×1254 PNG，步长 1024，halo 115，重叠 230。默认按第 4 行至第 1 行、每行第 1 列至第 4 列制作；每个任务必须有已登记的左邻和下邻。同一依赖前沿可并行，不能跨过依赖。

固定外邻由严格校验的 manifest 提供：西邻 `r08_c10/selected-v2/delivery.manifest.json`，南邻 `r09_c11/selected/delivery.manifest.json`。要求 tile 身份正确、`qualifiedComplete4KCandidate: true`、输出 PNG 的 SHA 与 manifest 一致。南邻未选定时直接 WAIT，绝不回退到 hardcut。首个 job 创建时固定两份 manifest 与图片的 SHA；后续改变必须先审查，工具不会悄悄换源。

运行步骤（以下命令在本 tools 目录执行，Python 使用项目现有运行时）：

1. `python check_ready.py` 只读检查选定邻图、区域引导及已登记原生依赖。区域引导固定为 `../regional/shared-region1254.png`。未满足前提时报告具体原因。
2. `python prepare_native.py 4 1 --analyze-only` 保存西/南 230×230 原生重叠角区对照与数值。实际查看对照和当前区域裁图。
3. `python prepare_native.py 4 1 --description "实际查看到的本裁图内容" --corner-owner core-split --corner-reason "与已查看的区域引导一致，上115行保留west、下115行保留south；可见叶片阶差仍需原生绘制复核"`。有差异必须明确选择 `west`、`south` 或 `core-split` 并给出理由，不会默认自选。`core-split` 仅用于 230×230 引导角区，上 115 行 west、下 115 行 south；在 r04_c01 对应 native y=1139、tile extended y=4211，工具会核对 `../corner-source-ownership.json`，保证与区域引导坐标一致。这是来源分配而非接缝通过，已知叶片阶差不能当成真实物体边线复制。完全相等时可以省略 native owner/reason。工具仅将区域引导放大作 guide；外邻和原生上下文均保持 1:1，指南放大像素不得进入成图。
4. 实际查看生成的 guide、角区对照及 `designs/gameplay-ui/04-guild.png` 后，通过内置 imagegen 使用 job 内 prompt 和两张参考图。保存真实工具回执和实际完成时间；使用上级现有 `lanxian_spring/tools/register_job.py --job <job.json> --result <真实回执.json> --source <实际输出.png> --generated-at <带时区时间>` 登记。实际型号/质量未披露时保持 null。不得将 guide 登记为原生输出。
5. 重复第 4 行西至东，再第 3、2、1 行。`check_ready.py` 会报告当前所有依赖已满足的单元。已存在的 job、guide、prompt 或 native 均禁止覆盖。
6. 16 张均登记后执行 `python assemble.py --analyze-only`，查看 115×115 的西南外 halo 交集。再执行 `python assemble.py --corner-owner <west或south> --corner-reason "具体复核理由"`。此外 halo 必须单独显式选择，不能继承 native 的 `core-split`，也不接受 `core-split` 参数；比较结果相等也不能跳过显式选择。第一次输出为 `assembly_hardcut`，后续使用新的 `--output-name`，不能覆盖已有候选。

装配中，4096 核心逐像素来源于 16 张原生图。只固定西侧及南侧各 115 像素的外 halo，分别取西邻 extended 的 `[4096,0,4211,4326]` 和南邻 extended 的 `[0,115,4326,230]`。冲突的西南 115×115 交集按独立显式 owner 决策处理；记录会同时保留两来源差异、选择原因，以及每一整边实际是否 byteEqual，绝不声称冲突来源都相等。该小角实际对应对角 r09_c10 的 core，最终四块交点还须与其 selected 复核；选择 west/south 只是当前候选来源，不是对角验收。工具保存原生归属蒙版并逐像素验证；零放大、零移位、零调色、零羽化、零模糊。

装配产生 45 张 1:1 复核图：24 段内缝、9 个内交点、4 段西邻、4 段南邻、4 个外角。所有 QA 默认未查看、未通过；必须实际复核。数值差异不能替代视觉检查，hardcut 不属于已选合格候选。发现色差或形体接缝后，另建范围明确、带来源与蒙版的修补流程；本工具不会自动进行或自动接受修补。北邻、东邻和导航/客户端验收仍另行完成。
