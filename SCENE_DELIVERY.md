# 主城与场景重绘 · 完成交付

> 2026-09-12 新增：[蓬莱岛、东海渔村、揽仙镇完整大地图](qdao_large_city_maps_20260912/README.md)。已按最新要求取消统一青绿金配色，另整理[此前5个大地图版本](qdao_large_city_maps_20260912/catalog/已有大地图索引.md)。

2026-09-10批次已完成高清主城地图与用户确认的五类场景美术，统一为Q版道家、玉绿暖金象牙米白，配合春节、元宵、中秋的适量节庆点缀。所有正式文件保存在本image资源目录。

## 高清主城地图

- [6144×6144总图](tianyong_festival_hd_20260910/tianyong_city_master_6144.png)
- [2048总览](tianyong_festival_hd_20260910/tianyong_city_master_preview_2048.png)
- [36张1024×1024切片](tianyong_festival_hd_20260910/Tiles/)
- [主殿原尺寸细节](tianyong_festival_hd_20260910/qa/main_hall_100percent.png)
- [主殿前后对照：左为小稿放大，右为分区重绘](tianyong_festival_hd_20260910/qa/main_hall_before_after.png)
- [构建与验证说明](tianyong_festival_hd_20260910/README.md)

总图由36张原生1254×1254分区重绘，以230像素重叠接缝拼合；未把小稿放大后当作最终高清图。保留原城地标，增加道路和广场留白。PNG尺寸、提示词、来源哈希、切片无损重拼已通过校验，整图和主殿、太极广场、南门等重点细节已查看。

## 五类场景

| 场景用途 | 成图 | 实际原生尺寸 |
|---|---|---|
| 主城横版 | [01_main_city_wide.png](qdao_festival_scenes_20260910/final/01_main_city_wide.png) | 2048×768 |
| 仙山登录背景 | [02_login_landscape.png](qdao_festival_scenes_20260910/final/02_login_landscape.png) | 1931×814 |
| 道观庭院背景 | [03_sanctuary_courtyard.png](qdao_festival_scenes_20260910/final/03_sanctuary_courtyard.png) | 2048×768 |
| 森林石桥战斗场景 | [04_battle_forest_bridge.png](qdao_festival_scenes_20260910/final/04_battle_forest_bridge.png) | 1931×814 |
| 战斗入场插画 | [05_battle_entry.png](qdao_festival_scenes_20260910/final/05_battle_entry.png) | 1932×814 |

[场景审阅总览](qdao_festival_scenes_20260910/scene-review-contact.jpg) · [场景详细交付说明](qdao_festival_scenes_20260910/README.md)

主城横版和道观庭院原来共用一张底图，因此保留两个用途入口，使用同一张新版绘画。其余三类各自重绘。场景保存工具实际返回的原生像素，未插值放大或强行拉伸为旧画布尺寸。原参考、实际提示词和制作记录随包保留。

## 使用状态

旧批次美术已发布到art/festival-city-scenes-20260912分支（0aaed0685ae9e9362e72ae87e20726a7f35b723e）。客户端生产贴图、导航遮罩、前景和背景已在本地接入并通过离线C#编译；Unity实机验证、服务端导航同步及进程重启尚未完成。用户随后转向新增三张完整大地图的制作，运行中的游戏未被中断。
