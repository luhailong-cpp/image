# 灯穗小使 · 23

2026-09-11完成：八向行走32帧、独立全身立绘和全部51项PNG/GIF交付已通过数值及视觉检查。西南第4帧已由内置image_gen修成左膝抬起、右腿落地，与第2帧正确交替；东北第3帧的此前修复保留。验收见qc.json与delivery-verification.json，32帧接触表见processing/visual-review.jpg。

双辫、雀斑圆脸、姜黄短斗篷、朱红短袍、左手提圆花灯的道家Q版少女，配少量元宵与暖金云纹。

## 正式资源

- portrait.png：1024×1024 RGBA独立全身立绘。
- walk/{S,SW,W,NW,N,NE,E,SE}/01.png至04.png：512×512 RGBA，每方向四帧，共32帧。
- walk/<方向>/strip.png：2048×512 RGBA四帧横条，共8张。
- walk/<方向>/walk.gif：四帧，每帧120ms，共8个透明预览。
- walk-cardinal.png：2048×2048，行顺序S/W/E/N。
- walk-diagonal.png：2048×2048，行顺序SW/NW/NE/SE。

脚点以画布左上为原点，目标(256,471)，输出可见脚底y=471。PNG为正式RGBA资源；GIF为调色板和二值透明预览。manifest.json列出51项正式图片与动画文件及哈希。

## 来源与重建

所有人物原画来自内置image_gen。source/origins.json记录生成缓存；source/assembly.json记录原画完整主体裁框与每方向四帧共用等比缩放。原生方向表均1254×1254，每表四帧；输出512画布和1024立绘属于重新采样，不声称额外原生细节。实际提示词保存在prompts目录。

最后修复记录为source/SW-final-repair.json，提示词为prompts/walk-SW-final-repair.txt。source/SW.png是当前采用的原画，source/SW-before-final-repair.png保留此前来源用于核对。2026-09-10的三次内置连接失败已在2026-09-11成功重试后解除。

重建顺序为本目录assemble_directions.py→包级process_roster.py（portrait/cardinal/diagonal输入分别为source/portrait.png、source/cardinal_assembled.png、source/diagonal_assembled.png；对应prompts同名文本；--duration 120）→本目录supplement_manifest.py（传入本角色目录）→本目录verify_delivery.py。重新生成原画后，仍需人工视觉检查再更新qc.json。

装配器只清理洋红、提取完整原画主体、统一尺寸和脚点，未绘画、镜像、旋转或复制凑动作。verify_delivery.py核验哈希、RGBA尺寸、无碰边、四帧唯一性、脚点、横条一致性及GIF的120ms时长；视觉检查另确认角色身份、朝向、腿部交替和完整轮廓。

本包为图片资源交付，未接入Unity客户端；四帧动作合同需由客户端按manifest接入。
