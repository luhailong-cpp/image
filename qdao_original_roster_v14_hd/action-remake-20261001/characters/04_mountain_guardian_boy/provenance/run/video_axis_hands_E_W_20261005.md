# E/W 跑步肩肘、手腕与握持复核（2026-10-05）

W04–12 九帧已用内置 image_gen 独立修正，并以旧 SHA 校验替换正式图。E16帧及 W01–03、W13–16 共23帧保留。已实际查看 E/W32张原图、各候选原生图和最终 W16连图，逐帧当前 SHA 与人工观察见 [JSON审计](video_axis_hands_E_W_20261005.json)。

- W统一为左臂盾近侧、右手杖远侧；03→04、12→13不再胸背翻面。肩肘腕连接与握杖接触通过静态复核。盾后手指合理遮挡，不声称每指皆可见。
- 首轮 W05/07/08 仍保留错误胸面、W10多余后臂/杖段，拒用；第二轮 W05/07/08 把目标前摆/后支撑姿态改掉，拒用。最终05/07/08用第三稿，10用第二稿，其余用首稿。
- W实际可见接地靴：01–04、09–12是屏幕左前靴；05–08、13–16是屏幕右后靴，屏幕左靴前摆。原运行标注“01–08左脚、09–16右脚”仅保留为相位意图，**实际解剖归属未确认**：髋根被裙甲遮挡、两腿装束相同，不能用旧文字证明同一支撑腿连续。04→05、12→13也未据旧标签自动判定通过。
- 32张正式图均为1024 RGBA，32个不同像素SHA，均与来源记录一致。9次替换均通过旧SHA守卫。
- 仅更新了 W 静态连图。遵照root分工，不改任何时序脚本/全局metadata，不重建75ms动画；root统一迁移60ms并重建8向APNG。
- 本审计为静态及连图审查。客户端未接入，世界空间锁脚未验收，整套动态最终验收由root处理。
- 目标为 GPT Image 2.5 Sunburst / max；宿主未披露型号/质量，实际model/quality均null。每稿有真实submission、receipt及原生来源记录。
- 未执行清理、Git或共享状态修改。所有native/拒稿仍在本角色目录供root统一核实清理。

| 槽位 | 采用稿 | 正式SHA256 |
|---|---|---|
| W04 | video_axis_hands_W_04_attempt01.png | 29750ea1e68057a404104d273e4bf728655b6bfbd775953ce6374d84e167c530 |
| W05 | video_axis_hands_W_05_attempt03.png | d693da95557b3c4b565364d0cafab29cdaa19ca7a9839c1915a77bce4483c5fe |
| W06 | video_axis_hands_W_06_attempt01.png | 0ae4ede649c2ae79912aa6676c9449d8093aa235248fe7feb7cd3f38eff2d897 |
| W07 | video_axis_hands_W_07_attempt03.png | 1702634b81c9bbcbc8ec37148d0e9e78d30664cee12eecf4dc692a9739728d4c |
| W08 | video_axis_hands_W_08_attempt03.png | 4e8dbe821abd31265b56d5cc6e4d96742458363b096fc4df0ab0721b6c10c355 |
| W09 | video_axis_hands_W_09_attempt01.png | 4a7ab69e7f97aa2c5d8a4ec6359bd106f3f518fb3ab2a86456e506de6e8c7ee4 |
| W10 | video_axis_hands_W_10_attempt02.png | 65b8ad59b8da36e3e526fe07299ff253dbfd357eb840f528d1421aa469084aca |
| W11 | video_axis_hands_W_11_attempt01.png | 8d1657ba20ef03d73859f1d9736950960d62d8c81ad7d584d3dd152e9317edbe |
| W12 | video_axis_hands_W_12_attempt01.png | bcd5701c2a76e2aefffc106b6a17667ab84ca4340b5d81c3c8cd035ba4db0dcd |

静态连图：`preview/run_W_contact.png`。截至本审计，手部/相机无明确未通过项；解剖支撑身份与客户端世界坐标锁脚保持未确认。

