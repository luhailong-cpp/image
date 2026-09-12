# 月兔机关师 · 八方向移动素材

已完成并验收：1024×1024 RGBA 透明立绘、八方向各四张 512×512 RGBA 行走帧、8 张 2048×512 RGBA 横条、8 个四帧 GIF，以及 2 张 2048×2048 RGBA 方向总表。正式资源共 51 个文件。

- 方向：S、SW、W、NW、N、NE、E、SE；每方向按 01→02→03→04 循环，每帧 120ms。
- 脚点目标：(256,471)，左上原点；alpha>8 的脚底行均为 y=471，横向估计脚点误差不超过 0.5px。
- 正方向总表按 S、W、E、N 排行；斜方向总表按 SW、NW、NE、SE 排行。每行四帧从左到右。
- 正式 PNG 为完整 RGBA；GIF 为色彩量化和二值透明的预览格式。

`manifest.json` 列出 51 个正式文件的哈希、方向顺序、时长和原生来源；`qc.json` 的数值与视觉验收均为 passed。`processing/visual-review.jpg` 是最终导出接触表。逐帧 PNG 与横条、总表的对应像素已核对一致，32 帧哈希全部不同。

原画来自内置 image_gen，八张独立 2×2 方向图原生均为 1254×1254。2048 总表及 512 帧为等比重采样导出，不冒称原生生成细节。每个方向四帧共用一个等比缩放，再进行整套共同缩放与脚点平移；没有逐帧独立缩放、镜像、旋转、复制补帧或代码绘制人物。工具未提供 model/quality 参数，未声称强制设置 high。

`sources/walk_*_2x2.png` 是当前采用的八张来源；`prompts/` 保留实际提示词。N、NW、NE 沿用此前修正版，SE 最终只对接触步姿态做定点编辑。历史图、未采用的修图和缓存来源见 `sources/generation-history.json`，不会进入正式成品清单。

可在本目录复现：

```powershell
python -X utf8 assemble_directions.py
python -X utf8 ../process_roster.py --character-dir . --portrait sources/portrait_raw.png --cardinal sources/cardinal_assembled.png --diagonal sources/diagonal_assembled.png --portrait-prompt prompts/portrait.txt --cardinal-prompt prompts/cardinal_assembled.txt --diagonal-prompt prompts/diagonal_assembled.txt --duration 120
python -X utf8 supplement_manifest.py .
python -X utf8 validate_artifacts.py .
```

重新处理会将视觉状态改回待复核，必须重新看图后记录人工视觉结论。本包仅交付图片素材，尚未接入客户端；四帧契约按 manifest 使用。
