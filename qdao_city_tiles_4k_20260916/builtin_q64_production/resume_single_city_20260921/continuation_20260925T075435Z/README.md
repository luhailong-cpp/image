# 2026-09-25 拉取后接续记录

本目录只记录本轮新增核验和一次失败请求，不覆盖共享指针或历史记录。真实项目根为 E:/work/image，旧 D:/luyuan/wuxingqitan/image 仅在读取时映射。

## 当前结果

- Git pull 已于 2026-09-25 07:45:55Z 记录 complete；本轮 07:46:11Z 复核目标 08e567132331fa6c42d2ecf5bf88aaa3d58169e0 已合入 504f54d1554f839450b7e9cf079949bbeeec6b34，目标为祖先，可达缺失对象为 0。
- 拉取后选用完整候选是 **10/256**，246 坐标仍无完整选用候选，正式验收 0。旧交接的 8/248、9/2/5 只属于拉取前快照。
- c07 已有 repaired-v1 完整候选；历史16原生输入导出后已按授权退休，勿按旧缺7片重新生成。
- c08 最新16片齐备，masked-result/r08_c08.png 真实存在，SHA 07981e070d4bff63ba9897cdc639398d7ea782e1ed5be386069725cc13532680，尚未选作完整候选；已有局部修复不能重发。
- c09 最新16片齐备；选用 bottom-material-v2 SHA dbaf9d7e02a8bcccf958d81e0bf5e506c4d558dff553d5abb759abdbc3320cd5。另有 cross-boundary-pair-v1 双图，SHA 94a3c47e0b2f91278e3727c30e15a787237b1eb70c909c8e1573a4378c1b907e / 06d36c552c660eba847255feeabc36dac2270d3025b55c7767683381ad8a5d51，未查完、未选用，勿重复生成。

## 本次实看与请求

查看了已确认风格图 designs/gameplay-ui/04-guild.png、干净原像素材质参考、c08缩略总览及原像素1254裁片。因 view_image 沙箱辅助进程失败，使用获准只读解码显示；1254裁片以同像素JPEG90传输，仅用于判定几何/色阶失败，不作无损清晰度通过证据。

c08 的全局 x3072、y0..1254 已实看存在雕刻断口、金边台阶和直线色差。新请求参考为当前 candidate 精确裁片、已确认风格原图及600像素原生材质裁片；未放大源素材，材质裁片只作外观参考。

内置 image_gen 的唯一请求在读取第一张参考时失败：fs sandbox helper / helper_unknown_error / setup refresh had errors。见 c08-x3072-top.request.json、references.json、config.snapshot.json、c08-x3072-top.tool-error.json。**本轮新增成图0、AI编辑成功0、正式验收0。** actualModel / actualQuality 均为 null；配置目标和真实提交能力分开记录。未调用计费 API/CLI。

## 继续顺序

1. 先恢复宿主内置参考读取能力，再对照 request 和 SHA 复验源图是否变化；本次请求没有返回图，不能计完成。正常读图/生图均报同一宿主错误，未削弱沙箱安全设置。
2. c07从现存repaired-v1接外边。c08从现存masked候选修复已确认问题；重做全6条4096内部缝、9交点与所有受影响外边/四块交点，不继承旧图通过。
3. c09先检查已存在的cross-boundary-pair-v1；它仅改变上块近底y3906以后，不能解决y3469..3904的已知内部色差。其current-review及纠正supplement真实存在，须用Windows扩展长路径读取，原字节SHA匹配指针。
4. 全城480边、225交点仍未完成；布局、导航和实机验收未完成。本机未找到 E:/work/mmorpg-client/Docs/CityTilePublishing.md，完整交付前须由客户端任务提供最新合同并负责接入/实机验收。

## 保护范围

本轮未 git add/commit/push/reset，未启动重复下载，未恢复automation-3，未清理/覆盖其他窗口文件，未改共享JSON。新内容仅在本目录；配置及共享状态原字节快照另存供核验，不修改原件。历史记录中的少数SHA换行差异未擅自纠正，也没有把CRLF归一化匹配当作原字节一致。

