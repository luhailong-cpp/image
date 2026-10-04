# 星阵少女当前交付工具

当前素材入口为 `selection.json` 与 `merge-manifest.json`，游戏帧位于 `runtime/`。共196张1024×1024 RGBA；其余动作分选表属于历史制作记录，不再覆盖当前选表。

重建预览和核验交付：

```powershell
& 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl/tools/build_delivery.py' --rebuild
```

此入口只读取当前runtime成品，不再缩放成品，不需要已按素材保留要求清理的原生图片。原生尺寸、SHA、提示词、参考证据及模型记录保留于generation文字记录与provenance/selected-native-source-index.json。

统一参数由timing.py维护：run为16×75ms＝1200ms；hit为6×40ms；attack为12×30ms；cast为16×45ms。慢放4倍，无额外尾帧停留。八方向预览支持128/256/512显示、暂停与逐帧。build_sequence_previews生成各组联系表及正常/慢放APNG；build_overview生成八方向合览。

export_preview、merge_current_selections和write_handoff在检测到正式交付状态后不会恢复历史候选或旧时长。build_delivery首次promote要求14组离线审核记录，并校验196个槽、源图与生成记录SHA、RGBA与尺寸；之后rebuild只核验成品。

本机固定完整画布922×922缩放及(51,40)偏移，根点(512,922)，没有bbox或最低像素贴地。旧生成/选帧脚本是过程记录，不作为当前重建入口。

客户端未接入；本机离线审核不替代游戏内移动位移、根点及用户最终观感验收。
