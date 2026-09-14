# 韩湘子 NE-01 原画比例修正

选用 `final-raw.png`（内置 ImageGen 真实1254原画），或 `final-cell.png`（整幅正方形统一1254→443）。没有 bbox fit、局部程序缩放、镜像或插帧。

头型已按同向正常原格复核，保留原手脚相位、布衣和左腰笛子。原画与正常参考、最终候选见 `before-after-native.png`。来源及全部尝试见 `final-provenance.json`，指标见 `measurements.json`，视觉检查见 `visual-qc.json`。

最终原格可见高度 403px；下身相对原稿的最佳整幅平移诊断 [0, -5]，轮廓IoU 0.9823。此诊断未改动输出像素，交父流程用共同scale与v3定位处理。

`qc-*` 仅透明边缘检查，不直接导入。没有改正式30、候选24或处理代码，完整八帧循环与游戏内起停验证仍由父流程完成。
