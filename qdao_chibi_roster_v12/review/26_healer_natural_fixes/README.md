# 药师自然步态候选（待主任务视觉验收）

仅改30张原相位：全八向04/08共16张，以及N/NE/E/SE/SW/W/NW的02/06共14张。S02/06离地幅度合理，保留；所有01/03/05/07保持原格。共34张walk和8张idle整格RGBA完全一致，头像保持原PNG哈希。正式26目录未写入。

原有道家Q版采药婆婆身份不改：笑眼圆脸、草帽、靛蓝布道袍、背竹篓和草药；朴素材质，无梦幻/魔法效果。原画问题是抬膝/后勾过高，与v2强行鞋底对齐引起的头部Y跳动分开处理。低腿真实重新绘制，没有拉腿、镜像、变形插值或重复帧。

修复原格命名oldphaseXX；所有修复沿用旧相位后，再按髋膝遮挡和对侧摆臂统一RIGHT先迈。E/SE原01本来RIGHTfirst，保持原序。N/NE/S/SW/W/NW原01是LEFTfirst，整圈轮转05,06,07,08,01,02,03,04。S旧提示的right是画面右，不能当解剖右。完整计划见phase-plan.json。

15次真实builtin image_gen全部保存原生输出和手写提示。generation-provenance.json逐次记录原生输出路径/SHA、保存原图、可见参考和提示，以及30个最终选格的裁框/RGBA哈希与整格缩放。N04摆臂错误、NE08多余鞋、NW04多余手、SE06错误变前触地的退稿均留档；最终只选对应完成格。

原画统一443方格；只对原生画布等比整格降采样，未做逐人物fit。72张最终共用原commonScale=1.0120481927710843，alignment v3按各方向idle固定头部ROI平移；world root仍(256,471)，脚的前后透视可以绕root变化。鞋底Y差仅观察，不按帧强拉齐。

assemble_candidate.py只写candidate-stable-body/26_osmanthus_healer；verify_assembly.py独立复算生成原图裁格、整格LANCZOS、相位轮转、64配对源格和42保留格。候选rebuild_candidate.py可重建、运行显式v3和独立verify。未seal、未发布，最终接入由主任务验收执行。

export-evidence/*-all-nine.png是3x3原512RGBA整幅画布联系图；对应jpg仅同比例预览，未按内容裁切；另有八向walk与idle-to-walk GIF。candidate-validation-summary.json记录最终manifest、QC、verifier和证据哈希。
