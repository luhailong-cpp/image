# 17 灵篆书生 SE 方向交接（2026-09-23）

本代理仅处理 SE。选定 16 张真实独立行走 + 1 张独立站立均已落盘；没有使用复制、镜像、插值或扭曲补槽。旧角色/其他方向/公共状态未改，未提交或推送 Git，未调用收费 API，未删除任何图像。

当前最终待总体验收选稿：`SE-review-v3/selections.json`。版本：01-v1、02-v2、03-v3、04-v2、05-v3、06-v1、07-v2、08-v1、09-v3、10-v1、11-v1、12-v1、13-v2、14-v2、15-v2、16-v2；idle-SE-v1。所有单图归档位于 `../17-generation/<attempt>`；导入来源位于 `staging/<attempt>/candidate/17_ghost_script_calligrapher_boy/`。

离线快照：`../17-delivery-preview/revisions/SE-complete-v3/`，最终透明PNG位于其 runtime/walk/SE 与 runtime/idle/SE.png。manifest SHA256：`2b8127288939d23d8f1b7f289c27ffbb367fb24a9818bc260eccfb3f2df91c74`。该方向有深浅底两份 16×30ms=480ms GIF、16帧总览、15→16→01→02 接缝对照和交互 HTML。完整角色计数显示 16/128 +1/8 及 119 缺槽是该隔离方向快照范围所致，不代表其他方向实时库存。

检查已完成：17张来源均独立完整单帧且原生≥1024，最终1024×1024 RGBA；原图SHA和导出SHA、原字节复制、唯一来源/非精确重复/非镜像、固定0.88整格处理与[512,942]锚点均通过。build_preview numeric_errors为空，audit_runtime 输出在快照 runtime-audit.json。GIF重新打开验证16帧每帧30ms，未混入拒稿或prepared-only请求。

人工静态检查：已看过所有真实返回图、深浅底16帧总览、腿部放大、关键帧1024尺寸深浅底与首尾接缝。01–05 为近侧右腿支撑；06–09 转为远侧左腿前摆与触地；10–13 左腿支撑；14–16 换回近侧右腿前摆，并衔接01落脚。支撑/摆腿关系与装备左右保持，透明轮廓无明显色边、无截断。04/07 原版偏小，已重绘到 v2。15/16 靴底可见是近侧腿前摆/临近脚跟落地的角度变化，最终01转平。

实际动态播放总验收仍由 root 进行，不能把已编码GIF和静态检查当作已经看过30ms实时播放。子代理工具列表没有 CUA/browser 控制。已启动只读本地服务：http://127.0.0.1:18727/recovery-20260921/17-delivery-preview/revisions/SE-complete-v3/index.html （exec session95645）。浏览器可切 SE、30ms/120ms、深浅底、512/1024。最终合包时请在最新固定manifest上记录动态验收。头/发髻和衣袖仍有逐帧细微变化，动态时尤其看06→07→08、09→10和末尾接缝。没有Unity/客户端接入或正式运行验收。

拒用稿：05-v2、02-v1、03-v1/v2、14/15/16-v1 为错误支撑或末尾换腿；04-v1、07-v1 因尺度偏小被后续版替代。前七稿有各自 visual-review.json；04/07 superseded 记录另存。准备但无生成结果的历史请求：05-v1、09-v1/v2、13-v1，不计数。所有已收到 raw 均有对应归档与导入，当前无未处理raw。

逐图请求使用 request.json.actual_request.prompt 原样提交（保留末尾换行），真实参数未暴露型号/质量，记录为 host-managed/unverified；配置目标快照为 gpt-image-2.5-sunburst/max，不能冒称实际返回型号。参考图实际附身份1024预览、SE idle或连续性原图及 designs/jubaozhai-ui/02-characters.png；旧01恢复来源见该原稿recovery-evidence.json，不改旧时间。

新增工具：worker_se.py（只准备SE新请求）、review_se.py（只生成审图合成与选择）。这些工具不生成姿势、没有合成新行走帧。

恢复第一步：读取此最新选稿与快照，在浏览器对SE作30ms实际动态检查；若发现具体接缝/比例问题，仅新建该帧下一版本，保留真实请求/回执后更新选择与新快照，不覆盖本固定快照。
