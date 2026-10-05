# 本角色当前工具

当前时序入口timing_profile.py：16张独立跑步帧，每帧60ms、每圈960ms。战斗hit40ms、attack30ms、cast45ms保持。

- build_review_media.py 动作 方向：以正式整画布生成连图和动画并绑定来源SHA。run normal为16×60ms APNG，slow为16×240ms APNG；战斗GIF保持规格总时长。
- build_preview.py：读取全部正式图、当前sidecar及原生/删源证明，重建manifest.technical.json与preview/index.html。每次最终sidecar更新后必须再运行，刷新嵌入记录SHA。
- register_frame.py：按当前规格导出1024RGBA；替换须旧PNG SHA守卫。不会自动美术通过。
- generate_native_function.js、record_native.py：宿主管理内置生图与真实提交/回执登记，无收费API授权含义。
- finalize_video_axis_followup.py：本轮专用已执行的75→60迁移/交付/清理入口。先人工审核196当前SHA并提供56项用途白名单，--check全量预检，--apply一次性同步runtime、sidecar、review、delivery和frames.sha256。已有snapshot/ledger会拒绝盲重跑；不要为重建预览再次finalize。
- verify_delivery.py：核对196正式PNG/sidecar、当前核准、technical记录SHA、42份预览来源及编码时长、960时序与frames.sha256，输出final_delivery_verification.json。技术成功不是自动美术审批。
- validate_timing_960_player.cjs：用Node VM执行实际index播放器，测试正常960ms、0.5×1920ms、0.25×3840ms、暂停、逐帧和战斗原时长；当前48/48通过。

历史finalize_delivery、finalize_bamboo_followup、finalize_stancepairs_followup、apply_run_timing_1200和1200验证文件只保留作历史证据。旧75ms写入入口有时序门禁，不能作为当前重建命令。旧竹弓对照工具已停用，当前图源以本角色frames为准。

预览重建顺序：各方向build_review_media → build_preview → verify_delivery → validate_timing_960_player。无需原生图片；保留的SHA绑定清理前快照和台账验证来源。任何新图替换都必须重新人工核准、更新当前交付清单；不能只换PNG后用旧清单宣布完成。

W的解剖支撑侧因裙甲遮挡未确认，runtime和HTML均如实标注。客户端未接入，离线时序及人工审图不证明世界坐标锁脚。
