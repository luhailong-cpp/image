# 灯穗小使 · 23

双辫、雀斑圆脸、姜黄短斗篷、朱红短袍、左手提圆花灯的道家Q版少女。少量元宵与暖金云纹点缀。

当前状态：32帧与51项图片/动画文件已导出，数值和文件合同通过；视觉复查发现西南第4帧抬腿未正确交替，仍待一处内置生图修正。勿视为整套最终验收通过。最新状态见 STATUS.md 与 qc.json。

## 正式资源

- portrait.png：1024×1024 RGBA独立全身立绘。
- walk/{S,SW,W,NW,N,NE,E,SE}/01.png 至04.png：512×512 RGBA，每方向四帧，共32帧。
- walk/<方向>/strip.png：2048×512 RGBA四帧横条，共8张。
- walk/<方向>/walk.gif：四帧，每帧120ms，共8个透明预览。
- walk-cardinal.png：2048×2048，行顺序S/W/E/N。
- walk-diagonal.png：2048×2048，行顺序SW/NW/NE/SE。

脚点以画布左上为原点，目标(256,471)，输出可见脚底y=471。PNG为正式RGBA资源；GIF为调色板和二值透明预览。

## 来源与重建

所有人物原画来自内置image_gen。source/origins.json记录生成缓存，source/assembly.json记录完整主体裁框与每方向四帧共用等比缩放。source目录保留已用原图与历史修订图；prompts保存实际生成提示词。原生方向表为1254×1254，每表四帧；输出512画布和1024立绘属于重新采样，不声称额外原生细节。

assemble_directions.py仅清理洋红、提取完整原画主体、统一尺寸和脚点，未绘画、镜像、旋转或复制凑动作。随后使用包级process_roster.py处理方向总表；supplement_manifest.py补充原生来源；verify_delivery.py验证输出哈希、RGBA尺寸、无碰边、四帧唯一性、脚点、横条一致性及GIF的120ms时长。manifest.json列出全部51项正式图片与动画文件。

东北第3帧已完成对侧腿接触的定点修复。西南第4帧待修，提示词为prompts/walk-SW-final-repair.txt；内置生图连续三次报connection failed。修好后需重新构建与视觉验收。

本包为图片资源交付，未接入Unity客户端；四帧动作合同需由客户端按manifest接入。
