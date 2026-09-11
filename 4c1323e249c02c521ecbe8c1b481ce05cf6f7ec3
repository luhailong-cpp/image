# 图片后处理说明

`process_roster.py` 只处理现有 ImageGen 图，不绘制人物，不伪造或补齐动作帧。每角色需要一张全身形象图、一张 4×4 正方向母表、一张 4×4 斜方向母表。

```powershell
python E:/work/image/qdao_chibi_roster_v11/process_roster.py --character-dir E:/work/image/qdao_chibi_roster_v11/characters/role_slug --portrait C:/path/portrait.png --cardinal C:/path/cardinal.png --diagonal C:/path/diagonal.png
```

可选 `--portrait-prompt`、`--cardinal-prompt`、`--diagonal-prompt` 指定实际提示词文本。也会自动查找角色目录的 `prompts/<类型>.txt`。提示词不会由处理器生成；未提供时如实记为缺失。

- 正方向母表从上到下为 S、W、E、N；斜方向为 SW、NW、NE、SE；每行从左到右为四个真实动作帧。
- 调用安装的 `generate2dsprite.py process` 做洋红清理、最大连通主体选择、透明边缘处理、preserve 缩放和严格结构 QC。临时产物位于 `E:/work/tmp/qdao-roster-v11/<角色名>/`。不向交付目录复制原始缓存图。
- 两张母表先统一到 512 原始格子的相同比例，再给整套 32 帧使用一个公共缩放系数。默认最大可见身高目标 420 px；若宽度或脚部余量不足，全套一并缩小。没有每帧独立身高拟合，没有非等比变形。
- 最终格子是 512×512，低于透明阈值之外的最下方可见像素统一在 y=471，下半身估计脚点 x≈256。锚点以左上为原点。判定阈值 alpha>8；仍保留更淡的抗锯齿边缘，检查整个非零透明包围盒避免裁切。自动脚点不是骨骼识别，必须视觉复核，原图不能含落地影子或粒子。
- 各方向单独检查技能定义的身体面积尺度 CV≤0.08、原始格子的锚点 y 标准差≤0.05；检查各方向平均可见身高 max/min≤1.10。脚底输出高度标准差必须为 0，源图或成品碰边、裁切、空帧、完全重复帧均拒绝。八方向的实际转身及步态是否正确必须另行视觉复核，数值通过不会冒充视觉通过。
- 数值失败返回退出码 2，写入 `qc.json`，不发布本次成品；诊断接触表写临时目录。旧成功文件可能仍存在，以本次 `qc.json` 为准，绝不可把失败结果当作已验收。不要通过放宽数值或逐帧变形掩盖原图问题，应重新生成原图。
- 成品包括透明 `portrait.png`（1024×1024）、`walk/<方向>/01.png` 至 `04.png`、每方向 `strip.png`（2048×512）及 `walk.gif`（默认每帧 125 ms）、两张方向总表。真实交付四帧，不复制成八帧，不镜像代替方向。
- `manifest.json` 记录原生源图尺寸、原图 SHA-256、成品哈希和四帧契约。`processing/` 保存技能元数据、处理参数、共同尺度、帧变换、来源和实际提示词。PNG 才是完整 RGBA 正式资源；GIF 是色彩量化和二值透明的预览。
- 不修改或自动接入 Unity 客户端。现有客户端八帧硬编码不能直接当作四帧资源接口。
