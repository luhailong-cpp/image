# 06 雷法少年：正在收尾，24张旧图修边已获授权

本窗口只负责06_thunder_caster_boy。当前`06-final`已合并128walk+8idle，112张高清行走通过来源重建、透明边界与离线图像/循环复核；其中旧S16与idle8仍为512原字节版本，残边未通过，不能把当前混合包宣布为136张全部美术通过。

2026-09-23 用户在最终放大检查后明确选择：**“继续修好旧图成品：允许修复最终版本，同时保留旧文件原字节”**。因此继续以24张旧图各自姿势为依据做内置AI边缘修复，原生完整单帧>=1024，最终导出1024；原V13/candidate/06_thunder_caster_boy/walk/S及idle仍原字节保留。新请求不授权更改其他角色，也不进行Git提交、推送或Git清理。

当前分工和后续第一步：S01–08位于06-tools/work-S-first-final；S09–16位于work-S-second-final；idle8位于work-idle-final。原图/精确prompt/request/receipt/尺寸SHA进入06-generation，batch采用S01-edge-final-v1、idle-N-edge-final-v1等，实际型号/质量仍未披露，收费API为0。各自独立工作树避免manifest并发覆盖。第一步是核验每组首张原生图的姿勢、体量与干净透明边缘，再完成其余帧；最后合并重做S16循环、idle深浅检查以及全包SHA/独立来源核验。

06-tools/assemble_final.py --restored可以在全部24张完成后生成complete-restored-v2快照并更新06-final；该命令明确允许新修复版进入交付目录，但不改旧V13原文件。import_restored_idle.py支持独立站立导入；alpha_verify新增idle_only仅检查该站立的来源和独立重建，不冒充整角色通过。

用户已将原图保留方案交由本窗口判断，已说明采用验收后精简：保留最终游戏图、设计、预览和完整文字来源，删除06原图、拒稿、回退与加工中间图。**目前尚未执行删除**；06-final/cleanup-plan.json只是24张再修之前的旧清理计划，须在修复验收后重新生成，不得直接执行。旧24文件按最新单独授权继续保留原字节。

最终应交付128张行走+8张独立站立、16个真实16帧×30ms GIF及完整离线检查，更新本交接为最终结果后停止。Unity/正式客户端导入、实际镜头/场景、联网流程与发布未验收。不得自动继续其他角色。


## 最新在制快照（2026-09-23，本轮仍在执行）

24张旧动作均已修边生成原生1254，并导出1024；所有旧24文件仍原字节不动。idle8已冻结，SW选idle-SW-edge-final-v2，其他7选v1，来源重建及深浅放大检查通过。S01–08冻结，S03选edge-final-v3、其他v1。S09–12/14选v1；S13由根选edge-final-v2，已导入并深浅/同画布对照通过。S15 v1体型偏小、v2过大、v3垂直比例不合适，不选，子任务review_s_first8正在做v4；S16 v1偏小、v2略大，子任务restore_idle8正在做v3。15/16新版只归档，由根串行导入，避免shared manifest覆盖。13/15/16初始子任务已停止，禁止重复生成13。

112张其他方向已通过并冻结。最终包06-final目前仍是旧混合临时版本，尚未运行assemble_final.py --restored；不可拿其库存声称136高清通过。下一步核查S15-v4/S16-v3是否已归档，读取新回复、导入并同画布检查；接着assemble_final.py --restored，再运行verify_final.py和final_notes.py、实际浏览器验收。finish_delivery.py需在browser-review.json实际通过之后运行。清理尚未执行，cleanup-plan必须验收后重新生成。当前没有额度/API阻塞，不需要用户逐帧回复。
