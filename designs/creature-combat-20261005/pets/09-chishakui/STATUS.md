# 赤砂魁制作状态

68张正式帧已生成并落盘，六组静态全帧复看及技术检查完成。E/W 各 hit6×40ms、attack12×30ms、cast16×45ms，全部1024×1024 RGBA。连续播放视觉验收待核，客户端未接入。

正式产物位于 runtime/，逐图 .generation.json、prompts/、records/ 和 generation-index.json 已配齐。manifest.json、SHA256SUMS.txt 与最终帧匹配；validation.json 检查68/68、尺寸、alpha、重复、引用、SHA及12个APNG正常/慢放时间轨道通过。preview/index.html 提供六组原速、0.25倍及逐帧控件。

已读并实看TASK要求的两个Image原生身份与已确认主要画法，POSES.md已锁定。内置image_gen逐帧真实调用；目标gpt-image-2.5-sunburst/max，实际参数与返回型号/质量未披露，均记录null。官方目标核对日期2026-10-05；配置文件只读。

唯一项目写入为本目录；未读取客户端/兄弟仓库选对象，无Git提交/推送/切分支。

实际查看了最终六组全帧拼图，重点修订帧另有原生/导出实看记录。未见明显换手、多肢或E/W视角误用；attack W10和cast W08–13已定点修订。仍有生成造成的脚位、轮廓及尺度波动，尤其cast W08–10；详见 VISUAL_REVIEW.md。名义pivot不是实测严格固定脚点。

浏览器安全策略拒绝本地file:协议，没有绕过。实际连续播放美术验收未完成，不能由静态查看或技术检查代替。完整任务状态为“素材与交付包完成，动态视觉待验”。本目录加工中间图按 cleanup.json 清理，逐图模型/质量/来源文字保留；共享身份与风格图保留。宿主生成缓存位于唯一可写目录之外，未纳入包且未改动。
