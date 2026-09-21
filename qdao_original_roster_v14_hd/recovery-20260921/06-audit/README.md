# 06 雷法少年原图恢复审计（2026-09-21）

本目录为隔离审计。没有修改正式 `candidate/06_thunder_caster_boy`、公共管线、原始生成证据、00–03、旧 S / idle 或客户端；没有新增绘图、收费 API、镜像、插值或复制姿势。当前范围沿用 2026-09-20 的 15 名角色。

## 核实结果

- 9 个归档原图（含明确拒稿 E09-v1）全部 1254×1254、PNG CRC 正常、SHA 与暂停库存和旧 provenance 完全一致；8 个有效目标姿势，未把拒稿计为第 9 帧。
- 请求正文与逐批 prompt 相同。旧 `E:/work/image` 已实地映射为 `D:/luyuan/wuxingqitan/image`，所有参考文件存在。拒稿 E09-v1 引用的旧用户 generated_images 路径通过 E01 receipt 中精确同名 output_hint 映射到归档 E01 raw，未假设旧用户目录存在。
- 实际型号仍为宿主管理、未披露。PNG 创建元数据为 ChatGPT / gpt-image，不代表明确锁定 2.5、2.0 或 max；未验证 C2PA 签名。
- E04 / E06 / E13 在本目录独立快照按原 V14 管线重建，1×1、common_scale=.88、实际缩小因子 .7185964912280702、1024×1024 RGBA、脚底 [512,942]，原生不放大。三个新重建均通过逐阶段独立像素检查。
- 已有 E02 / E03 / E05 / E09 的 prompt 与 receipt 在本机均为 LF，而记录保存同文本 CRLF SHA，因此直接运行严格 verifier 会失败。8 个文本文件各自只做 LF→CRLF 即精确命中原记录 SHA。本审计只在隔离副本还原这些历史字节，保存每个 current/expected SHA 和来源绑定；未改 live 原件、记录或门禁。随后 8 张全部通过独立像素重建。先前失败报告保留，不能把本次隔离通过冒称 live 字节通过。

证据入口：[原图与参考审计](source-audit.json)、[第一轮严格检查](audit-summary.json)、[历史换行字节核对](snapshot-text-reconciliation.json)、[字节还原后独立重建](reconciled-verification-summary.json)。

## 目视结论与缺口

E04 为窄步交叉过渡，后靴离地、近靴支撑；E06 为摆腿前伸下降；E13 为较明显的近腿高抬。人物身份、东向、法杖／符牌、两只靴子均可辨，输出未裁切。E04 的头顶与总高略高于 E03，属于需要补齐后连续检查的相邻相位变化；未对单帧做身体包围盒缩放。

E03 在深浅底放大都能看到发尖、黄带、下颌和衣边上的细紫／粉残边，不能给予边缘合格标记。原管线重建仍会保留它；像素重建通过不等于美术通过。新重建 E04 / E06 / E13 的 1024 输出已逐张看过，未见 E03 那样明显的连续紫边；仍应随齐套 E 方向统一验收。

[深底总览](E-available-dark.png)、[浅底总览](E-available-light.png)、[E03 深浅底近景](E03-edge-closeup.png)、[逐帧与 30 ms 不完整周期预览](index.html)。预览缺槽为明确空白，不延用上一张图，不假称完整动画；本轮未做浏览器动态验收。

正式候选仍只有 E01 / 02 / 03 / 05 / 09。三个 raw 若由主任务导入，E 尚缺 07 / 08 / 10 / 11 / 12 / 14 / 15 / 16；N / NE / SE / SW / W / NW 各缺 16。06 仍须真实补画 104 张 walk，E03 还需处理残边。旧 S16 帧和 8 idle 保留。15 / 16 / 01 首尾接缝与完整 480 ms 步态尚无法验收。

## 精确导入入口

`import_pending.py` 默认只做来源哈希、空槽、原生和固定比例检查；只有 `--apply` 才写 06 的三个候选槽。它在进程内关闭共享 preview 索引更新，不修改公共脚本。任何目标已存在或源文件变化均先拒绝，避免覆盖别的窗口成果。新增帧导入后逐帧 strict verify，仍只标记 pending_visual。

```powershell
Set-Location 'D:\luyuan\wuxingqitan\image'
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'qdao_original_roster_v14_hd/recovery-20260921/06-audit/import_pending.py'
# 主任务确认准备导入时执行；本审计没有执行下面这一行。
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'qdao_original_roster_v14_hd/recovery-20260921/06-audit/import_pending.py' --apply
```

本机 `py -3` 未发现安装的 Python，使用工具返回的 bundled Python。不得直接复制本审计目录的 manifest 覆盖 live。现有 E02/03/05/09 的文字字节绑定需要主任务以单独、保真方式处理，不能静默重写历史哈希或把本快照报告套给 live。
