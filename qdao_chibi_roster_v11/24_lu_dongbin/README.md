# 年轻吕洞宾 · 八方向移动素材

已完成并验收：1024×1024 RGBA 透明立绘、八方向各四张 512×512 RGBA 行走帧、8 张 2048×512 RGBA 横条、8 个四帧 GIF，以及 2 张 2048×2048 RGBA 方向总表。正式资源共 51 个文件。

- 方向：S、SW、W、NW、N、NE、E、SE；每方向按 01→02→03→04 循环，每帧 120ms。
- 脚点目标：(256,471)，左上原点；alpha>8 的脚底行均为 y=471，横向估计脚点误差≤0.5px。
- 正方向总表排行：S、W、E、N；斜方向总表排行：SW、NW、NE、SE；每行四帧从左到右。
- PNG 为正式完整 RGBA；GIF 为量化色彩和二值透明的预览。

`manifest.json` 列出 51 个正式文件的哈希、帧序、时长与来源。`qc.json` 的数值及视觉验收均为 passed；`processing/visual-review.jpg` 是最终导出接触表。32 帧哈希全部不同，横条与两张总表均已逐格核对，像素与逐帧 PNG 一致。

本角色为年轻、无须、黑直发道髻的原创 Q 版吕洞宾。S、N 和四个斜向针对下排重复领步做了局部姿态修订；W、E 沿用原有可用方向图。只保留现有年轻人物造型作为身份依据。

原画全部来自内置 image_gen。八张独立 2×2 方向原图原生均为 1254×1254，2048 总表与 512 帧为等比重采样导出，不冒称原生生成细节。每方向四帧共用一个等比缩放，再进行整套共同缩放和落脚平移；没有逐帧独立缩放、镜像、旋转、复制补帧或代码绘制人物。工具未提供 model/quality 参数，不声称强制设置 high。

当前来源为 `sources/walk_*_2x2.png` 与 `sources/portrait.png`。实际提示词保存在 `prompts/`；旧下排重复版本保存在 `sources/*review_previous.png`，仅用于来源追溯。完整来源、缓存记录及修订说明见 `sources/generation-history.json`。

可在本目录复现：

```powershell
python -X utf8 assemble_directions.py
python -X utf8 ../process_roster.py --character-dir . --portrait sources/portrait.png --cardinal sources/cardinal_assembled.png --diagonal sources/diagonal_assembled.png --portrait-prompt prompts/portrait.txt --cardinal-prompt prompts/cardinal_assembled.txt --diagonal-prompt prompts/diagonal_assembled.txt --duration 120
python -X utf8 supplement_manifest.py .
python -X utf8 validate_artifacts.py .
```

重新处理会把视觉状态改回待复核，需重新看图后记录结论。本包仅交付图片素材，尚未接入客户端；按 manifest 的每方向四帧契约使用。
