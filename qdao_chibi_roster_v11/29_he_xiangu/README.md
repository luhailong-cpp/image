# 何仙姑 · 八方向移动素材

原创道家 Q 版何仙姑：清灵心形脸、黑色直发低髻与莲簪、薄荷玉绿藕粉短袍、深绿灯笼短裤、短靴和腰侧莲花。

交付包含 `portrait.png`（1024×1024 RGBA），八方向 S、SW、W、NW、N、NE、E、SE，每方向四张 `walk/<方向>/01.png`–`04.png`（512×512 RGBA）、一张 `strip.png`（2048×512）和四帧 `walk.gif`（120ms/帧）。脚锚点为左上原点 (256,471)，横坐标按下半身像素估计，误差不超过半像素。两张 2048×2048 总表分别为 `walk-cardinal.png`（S/W/E/N）及 `walk-diagonal.png`（SW/NW/NE/SE），每行四帧。

所有创作原画来自宿主内置 image_gen。`sources/assembly.json` 保留原生尺寸、哈希和每帧来源，`prompts/` 保留实际提示词。每个方向四帧共用一个等比缩放，再统一导出与落脚；没有逐帧独立缩放、镜像、旋转、变形或复制静态人物补帧。2×2 来源原生画布为1254×1254；最终512格与2048总表为重采样排布，不冒称原生细节。

NW采用第一轮步态修订。NE保留原图第1–3帧及修订图第4帧：修订图第3帧因莲花换边未采用。SE保留已纠正朝向的第1–3帧，采用第二轮修订的第4帧以明确交换抬脚。其他已修订方向为 S、W、SW。来源选择与理由见 `sources/final-selection.json`；保留的 original/correction 来源不全部进入成品。

`manifest.json` 是正式成品清单及哈希，`qc.json` 是数值与视觉验收；`processing/artifact-validation.json` 检查文件规格，`processing/visual-review.jpg` 展示全部32帧，`processing/walk-preview.gif` 展示八方向同步预览。GIF是量化、二值透明预览，正式美术使用 RGBA PNG。

这是四帧手绘步态素材。未接入或修改客户端，客户端应按 manifest 的四帧和120ms契约播放。

重建：运行本目录 `assemble_directions.py`，然后以 sources/portrait.png、sources/cardinal_assembled.png、sources/diagonal_assembled.png 调用父目录 process_roster.py，设置 --duration 120 并传入对应 prompts；随后运行 supplement_manifest.py 与 review_assets.py。重建是确定性图片后处理，不调用付费 API。
