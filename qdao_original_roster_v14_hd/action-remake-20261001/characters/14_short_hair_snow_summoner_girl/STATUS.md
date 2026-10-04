# 14 唤雪少女 · 本轮素材修正与离线验收完成

按用户认可的09竹弓少女实际跑步图重新对照。128张跑步帧中，目前106张较反馈前已替换；当前离线通过196/196，跑步通过128/128。通过状态绑定最终PNG的SHA。

跑步八方向统一1200ms/圈、16帧各75ms；正常预览仅保留此速度，另有¼慢速、暂停和逐帧。受击40ms、普攻30ms、施法45ms每帧不变。

新增验收要求按成品实图逐对核对；膝、踝和脚掌朝向连贯，无外翻。当前接地帧段及审核状态：

最新要求：同一支撑脚依次经过前落脚、髋下承重、稍后支撑、后侧前掌蹬地四个位置，每位置两张不同姿态。01–08为第一只脚持续接地，09–16为另一只脚持续接地；脚位随运动与透视推进，不能向外撇脚。每对150ms，整圈1200ms。

- N：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- NE：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- E：anatomical_left_far 01→02→03→04→05→06→07→08；anatomical_right_near 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- SE：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- S：anatomical_left_screen_right 01→02→03→04→05→06→07→08；anatomical_right_screen_left 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- SW：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- W：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）
- NW：left 01→02→03→04→05→06→07→08；right 09→10→11→12→13→14→15→16（passed_offline_four_spatial_pairs）

入口：[八方向并排](all-directions.html)、[竹弓动作对照](bamboo-reference.html)、[完整动作](index.html)、[节奏与逐帧](timing-grounding.html)。

本轮没有接入或运行游戏客户端，世界位移、根点、阴影和事件仍待客户端验收。完整接入信息见[交接说明](MERGE_HANDOFF.md)。
