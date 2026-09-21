# 05 天音少女 NE 审计与预览 — 2026-09-21

结论：**NE 16 帧库存齐全，但视觉需要返工，不批准；05 全角色仍缺 64 张 walk。** 本轮未生图、未调用收费 API、未更改原 candidate、未接入客户端。

## 本轮证据

- [只读来源审计](NE-source-audit.json)：12 张新增帧的 generation raw 与 candidate source raw 字节一致；全部原生 1254×1254、正式候选 1024×1024 RGBA。精确 prompt 与 receipt actual_request 逐字节一致；所有 `E:/work/image/...` 参考都映射至本机 `D:/luyuan/wuxingqitan/image/...`，文件存在并记录 SHA。旧电脑 `C:/Users/luyua/.../generated_images` 原默认输出路径在本机不存在，只作为历史路径保留。
- [独立重建诊断](NE-independent-reconstruction-shadow.json)：12/12 新帧的五阶段图与最终像素通过现有未修改 verifier 的单帧复算。使用 `evidence-shadow` 内独立证据副本，原因见下一节；这不提升当前 candidate 的正式门禁状态。
- [30ms GIF](NE-16-30ms.gif)、[无损 WebP](NE-16-30ms.webp)、[逐帧网页](preview.html)：16 帧，各 30ms，总 480ms。浏览器启动了正常播放，确认帧标签与画面切换，并逐帧查看 03、04、16；15/16/01 的暗底和白底大图另做直接审查。
- [暗底接触表](NE-16-contact-dark.png)、[白底接触表](NE-16-contact-white.png)、[暗底首尾接缝](NE-seam-15-16-01-dark.png)、[白底首尾接缝](NE-seam-15-16-01-white.png)、[关键帧](NE-keys-01-05-09-13-dark.png)。直接检查新增 NE03、NE16 的 1024 透明 PNG，并对照原始人物参考。

旧 NE01/05/09/13 的 512 PNG 与旧独立 idle 保留。预览只在显示时统一画布；不能把显示放大当原生 HD，也没有复制、镜像或插值制造动作帧。16 个实际帧的像素哈希互异，只证明无字节重复，不单独证明步态正确。

## 来源元数据的换行阻碍

原 candidate 上的现有 `verify.verify` 对 12 张均返回 `Source mapping changed`。本机 `frame-sources.json` 为 LF，其实际 SHA 是 `4c924a79f2b3a656aa05fb8433cf8d26a3b08709920974a478424c0c386b4421`；把换行还原为 CRLF 后，SHA 精确等于 manifest 记录的 `886eaaf04592ee033465048bd473c45dda3c5a4c437024581592120ec51eb6cb`。其中 11 个 receipt 也存在同样转换，恢复 CRLF 后精确匹配原记录；NE08 receipt 本机字节已匹配原记录，无需转换。

因此只在本次 `evidence-shadow` 中复制必需输入并恢复这 12 个 JSON 的历史字节，未重写任何 SHA 声明、未放宽 verifier、未修改 live candidate。副本每个转换前后 SHA 均有记录。正式流程若要修复，应审慎恢复历史字节或按项目新鲜绑定规范处理，不能直接把旧报告当当前正式通过。

## 视觉发现

1. **NE03 与前后相位不连续，需要重画。** NE03 屏幕左靴抬起、右靴支撑；NE04 则立即变为右靴抬起、左靴支撑，连续 30ms 的 03→04 出现摆动腿切换。NE03 不能作为 01→05 的平滑过渡。冠顶也相对 02 下移 27 像素，然后 04 上移 22 像素（均按 1024 同世界画布量度）。此处不能用重排、镜像或插值修补。
2. **15→16→01 首尾接缝不通过。** 固定脚底 y=942、上身轴 x=512 时，15/16/01 的可见身高为 777/766/810 像素；16→01 冠顶跳升 44 像素，在 512 预览中仍是 22 像素。15、16 的头身、衣摆与下一张旧 01 的比例/高度衔接有明显突变。建议至少重画 16，并连同 14、15 逐帧复查，保持旧 01 与旧 13 不变。
3. **身份大体保持，但不能代表整组通过。** 原角色的紫色高发髻、莲花金冠、紫白金边衣、灯笼裤、紫金琴与后右视角延续。16 个文件未见缺身体或贴画布边缘。NE01/09 的接触靴相反、NE05/13 的抬脚相反，旧关键帧继续保留。
4. **透明边缘仍需局部复查。** 暗/白底缩小接触表未见整块残留背景；直接 1024 PNG 中，NE03 与 NE16 发髻、右侧头发轮廓、靴边存在零星高饱和粉紫点线。角色本身有大量紫色与半透明飘带，不能全局去紫或把统计中的所有 magenta 当污染。建议按 raw→keyed→cleaned 同坐标检查这些轮廓，安全清理后重建；本审计不操作正式图像。

这些观察足以阻止当前 NE 视觉批准。已制作并操作 30ms 预览，不声称通过长时间连续播放验收，也不声称任何 Unity 或客户端运行通过。

## 后续顺序

1. 在 04 完成后，先处理 05 当前 NE03、NE16 及相关边缘/接缝；继续保留旧 01/05/09/13 与旧动作。
2. 重新绑定本轮实际 source/prompt/receipt，逐像素重建并审查 30ms 完整 NE 循环。
3. NE 通过后补 SE/SW/W/NW 各 16 张真实帧，共 64 张。旧 8 张独立 idle 已存在，保持不动。不得以镜像补方向。
4. 仅在素材与预览通过后更新混合组装/验收；客户端接入不在本轮任务范围。

## 复现

本机 `py -3` 未发现安装，系统 `python` 缺 Pillow。使用已核实的宿主依赖运行时：

```powershell
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' qdao_original_roster_v14_hd/recovery-20260921/05-audit/audit_and_preview.py
& 'C:\Users\Administrator\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' qdao_original_roster_v14_hd/recovery-20260921/05-audit/reconstruct_in_evidence_shadow.py
```

上述脚本仅在当前 `05-audit` 目录写审计/预览/证据副本。网页通过相对路径引用原动作，可本地打开；本次校阅的临时 localhost 服务结束后关闭。PNG 与动画均是审查附件，不是替换正式素材。
