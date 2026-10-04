# 本角色制作工具

- build_preview.py：只读正式帧和逐图记录，生成manifest.technical.json与preview/index.html。
- build_review_media.py 动作 方向：用当前正式完整画布生成连图及动态预览，自动绑定来源SHA。跑步使用APNG，normal逐帧精确75ms、16帧1200ms；slow为0.25×逐帧300ms、16帧4800ms。跑步旧GIF与480/640/720/800ms快档已退役；战斗动作继续使用原GIF。
- timing_profile.py：本角色八向跑步按用户最新要求统一16帧×75ms＝1200ms，不再使用分相位加权时长。受击240ms、普攻360ms、施法720ms不变。
- register_frame.py：从真实原生PNG导出1024并绑定来源。替换必须明确提供旧PNG的SHA。
- generate_native_function.js、record_native.py：本批真实内置生成及原生登记辅助，需在可用工具环境运行；不构成外部API授权。
- finalize_delivery.py：仅在实际视觉复核完成、最新库存审计及根视觉核准均绑定当前SHA后使用。全量预检通过才写入；--cleanup按用户保留规则清理本角色provenance中的原生/拒稿/重复预览，保留成品与所有文字证据，以实际删除结果同步保留状态。完成后不要重复运行以重写历史状态。
- finalize_bamboo_followup.py：本轮局部补修的交付入口。默认或--check只读核验全部196帧、当前SHA视觉核准、旧删源快照/台账及新原生整画布LANCZOS重现；--apply才写审核与交付清单、清理本轮provenance下PNG/GIF并按实际删除结果同步fileRetained。须先由根窗口实际审图并写入provenance/audit/bamboo_final_visual_approval_20261003.json，工具不创建或推断视觉核准。独立保留本轮snapshot/ledger，不覆盖旧证据；已有本轮snapshot/ledger时拒绝盲目重跑。
- validate_timing_1200_player.cjs：用本机Node VM执行preview/index.html实际播放器脚本，模拟DOM/RAF验证八向1200ms、慢放、暂停、逐帧及战斗原时长；只写测试审计，不修改产品文件，也不替代浏览器或客户端验收。

正式素材不依赖制作期native图片。清理后用build_preview.py和build_review_media.py重建预览即可，勿用生成历史脚本覆盖成品。

verify_delivery.py读取review.json.rootVisualApproval中的当前核准路径与SHA，兼容首轮交付和本轮补修所用的同一绑定字段；验证196张当前PNG/sidecar/核准SHA、当前预览来源及GIF/APNG实际编码帧时长，输出provenance/audit/final_delivery_verification.json，不自动判断美术。正常跑步APNG和浏览器播放器均为精确、均匀75ms；0.25×慢放APNG逐帧300ms。旧跑步GIF的来源文字移入provenance/retired-previews/timing1200/，图片删除结果另有SHA审计。

本轮源码、时序及预览同步复核由根窗口进行，当前状态见上级STATUS.md。浏览器保留正常速度、慢放、暂停与逐帧。09竹弓少女是用户确认的最新动作参照，只比较同向脚掌轴线、膝踝和相位，不照抄弓箭手手部或武器操作。

本机存在D:/work/mmorpg-client；本角色未接入、未运行客户端验收。制作与预览工具的通过不等于客户端运行通过。

