> 清理后更新：本目录现保留 5/16 张选用原生小片，旧失败 PNG 已删除，下面旧数量是清理前冻结值。用户已明确授权删除旧原图和回退图。此要求覆盖本交接中早先的全部原图／失败版保留要求；当前仅保留最新选用图、未完区域必需小片、布局／材质设计和当前验收证据，历史来源 SHA 与文本记录保留。

# r08_c09 停止制作交接

选用待拼接来源 5/16 张，保留原生 PNG 共 9 张，其中 4 张为不选用旧版。没有完整 4096 候选，没有整块接缝或正式验收通过。

本交接由主窗口直接核对磁盘记录汇总。子执行者此前发生响应流中断，主窗口已停止其继续执行；旧宿主生图是否仍在运行无法核实，状态记为 unknown。没有原图及真实完成回执的调用不计完成。新窗口可以先核对是否可恢复结果，再决定补绘，不得伪造回执。

## 选用来源（仅续作，不是验收通过）

| 内部坐标 | 文件 | PNG SHA-256 |
| --- | --- | --- |
| r01_c01 | `native/r01_c01.v2.png` | `7e1dd07284143fd56c7a4bacbbd8dd8764366af3ba824c72c5d28a759bd18442` |
| r01_c02 | `native/r01_c02.v2.png` | `8aead099648f5d187d13bb052f8507e1f052645284b1257f47c96e57fdb1b04a` |
| r01_c03 | `native/r01_c03.v2.png` | `a13cc66058df1f6574473f2e4b86aa6d9ef50370df10c5b8cb42043af910a686` |
| r01_c04 | `native/r01_c04.v2.png` | `9cd349a576f845d7e644bf4fed6593188961b6431ae54d4bc4d374f65dd1d0df` |
| r02_c01 | `native/r02_c01.v2.png` | `a44635a66d95b24a370a6fc8ff5d8308939a9383a616e1fc5451faa771add75b` |

精确记录及 SHA 见 [handoff-state.json](handoff-state.json)。

## 待完成

`r02_c02`、`r02_c03`、`r02_c04`、`r03_c01`、`r03_c02`、`r03_c03`、`r03_c04`、`r04_c01`、`r04_c02`、`r04_c03`、`r04_c04`

当前 plan.json 的 outputFile 是各坐标拟用的 v2 路径，不表示 16 张均已生成。磁盘只有首排四张 v2 和 r02_c01.v2，其余 11 张不存在。

从 requests/r02_c02.v2.request.json 开始，逐个读取真实准备好的 request，调用 image_gen。第 1 张是几何引导；第 2 张 references/clean-stone-material-native-crop.png 是 r09_c09 v6 的原像素材质裁切；第 3 张是 designs 成图。旧 v1 用的较大整体参考导致碎纹，不再选用。

真实返回后保存 requests/<版本>.receipt.json，含与对应 request 完全相等的 request、真实 response.output_hint 和 completedAtUtc（宿主观察时间，不是服务器生成时刻），再运行 native_tools.py save <版本名>，例如 native_tools.py save r02_c02.v2。16 个拟选 outputFile 均存在且完成来源记录后才能运行 native_tools.py assemble，再运行 native_tools.py qa 生成原像素板，随后必须实际看板并写真实检查结论。这些命令不会自动提供美术通过；现有 prepare 不重跑覆盖。

命令使用 `C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`，在本目录运行相应脚本。图像生成必须通过实际 image_gen 工具调用；Python 只用于来源保留、几何参考、组装和检查。

## 材质与验收边界

以最新干净 v2 的实际提示为参考：第 1 张只约束几何，把整片碎纹、云斑、白脉、细裂纹替换为宽缓稀疏色调；保留真实砖缝、雕刻和道路。x=230/y=1024 等处可能是参考拼贴材质分界，不应画成新的边。风格输入实际使用 designs/guild-ui-v2/source/guild-overview.png，只取画法，不加 UI／文字／道具。

新图原生输出为 1254²，核心 1024、halo 115、相邻 overlap 230，拼成 4326 后裁成 4096。不能把布局引导放大后当成品。先查 6 条内部全长缝、9 个内部交点，再查底邻全长与未来左右邻居及真实四块交点；最近镜头、布局和导航未通过。

当前 configured model/quality 是目标，实际后端型号和质量未披露，保留 null；服务器生成时刻未披露，宿主观察时间单独记。旧版图片已按用户授权清理；请求、回执、来源 SHA、当前计划和必要参考保留。
