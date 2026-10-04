# 灵篆书生完整动作预览

直接用浏览器打开 [delivery.html](delivery.html)，无需服务器。保持preview与runtime目录相对关系；全部196帧从runtime读取。支持八方向跑步和E/W受击、普攻、施法，正常播放、四分之一慢放、暂停和逐帧检查。

[八方向跑步动图](run-current-1200ms.webp)为16帧各75ms，共1200ms，240px整画布显示。

旧入口重定向到正式预览。manifest-preview.json只保留导出时的选图/来源历史快照；其中staging路径可能已按素材保留规则清理，正式预览不读取这些路径。不要再用旧build_preview.py覆盖入口。
