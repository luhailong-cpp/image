# 何仙姑 V12

状态：最终视觉复核中，尚未发布到客户端。

交付目标为 N、NE、E、SE、S、SW、W、NW 八方向，每方向八张真实行走姿势、八张独立自然站立图及沿用同一身份的1024透明肖像。角色风格为传统道家Q版，保留何仙姑的莲花、发髻及既定衣饰，不使用梦幻、发光、盔甲或魔法特效。

原画由内置 image_gen 生成。source/phase-01.png 至 phase-08.png 是冻结相位的八视图；cell-repairs.json 记录独立生成的整格修正与相位重排。repair_phase_cells.py 只替换完整原画单格，source/phase-corrected 和 source/corrected-transposed 保留逐格坐标、原生尺寸与SHA来源，不绘制新动作、不镜像、不复制四帧假充八帧。

source/idle-v2.png 是独立站立原画。repair_idle_cells.py 将单独生成的东西向带莲苞站姿整格放回 source/idle-corrected.png，具有同样的来源登记。

rebuild_corrected.ps1 重建所有相位、配对原画与72张正式姿势。全部姿势共用同一缩放系数；每张仅平移到上身水平轴x256和脚底最低像素y471，遵循公共处理器的alignment.version=2。walk与idle单帧512×512RGBA，walk-<DIR>.png横条4096×512。

visual-review.json 记录视觉判断；qc.json的数值通过不代表视觉通过。processing/walk-review.png、idle-review.png及S04-S08-actual-export-compare.png供复核。完整公开验收需运行公共verify_delivery.py，并由根任务审核后接入游戏。

