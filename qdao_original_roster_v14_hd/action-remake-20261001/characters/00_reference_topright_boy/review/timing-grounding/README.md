# E向跑步当前节奏预览

打开 [index.html](index.html)：正常1×为1200ms/圈、16帧各75ms；慢放0.25×为4800ms/圈、各300ms。支持暂停、从01重播、上一帧、下一帧和滑块。240/512像素均显示完整画布，名义地线未校准且不移动人物。

当前输出只有 adopted-1200 一个模式，normal/slow × 240/512 共4张透明动画WebP。页面及 review-data.json 只列当前产品；旧快档动画已按清理台账移除，派生文字记录作为历史证据保留；本工具不删除文件。

每张WebP配套来源及SHA记录；validation.json 核验16帧顺序、实际RIFF编码时长、透明度、画布、循环边界、逐帧控制和来源一致性。

修改导出与manifest后运行：python -X utf8 tools/render_timing_previews.py

脚本先要求manifest中八方向共128张run均为75ms且周期1200ms，否则停止；再按当前E01–E16及SHA重建。脚本不改manifest、正式PNG、原生图片或战斗时长，不读取旧权重建议。此输出不代表已观看动态或完成客户端验收。
