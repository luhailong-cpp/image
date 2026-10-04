# 当前时序入口复核

结论：未发现会把跑步恢复为旧快档的当前入口。仅只读检查，未执行重建、finalizer或最终verify。

- timing_profile、register_frame、build_preview、build_review_media、finalize_delivery均使用16帧×75ms＝1200ms。当前128份run来源侧车同样为75ms，交付时序注释均为1200ms。
- 动态重建只生成normal/slow：跑步写APNG，正常精确75ms、慢放300ms。GIF量化分支排除run；旧finalizer里的GIF文件名仅为删除候选，不会恢复GIF。
- template/index的播放器代码仅LF/CRLF换行格式不同；当前index原始脚本SHA与此前48项通过的Node VM测试完全一致。播放器默认1×，无旧run-cycle；gallery仅normal/slow，默认normal且引用APNG。
- 当前16个APNG逐帧解码正确：正常16×75ms、慢放16×300ms。旧run GIF剩余0个。
- 受击240ms、普攻360ms、施法720ms未变；E/W正常战斗GIF实际总时长吻合，施法仍以40/50ms交替表达45ms逻辑帧。

文件SHA、APNG编码和逐组侧车摘要见同名JSON。N/NE仍可能有后续来源更新，本次仅确认读取时的时序；不扩展为当前视觉或客户端接地验收。
