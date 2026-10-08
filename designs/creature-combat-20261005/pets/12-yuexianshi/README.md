# 月弦师 · 战斗动作素材

本包仅使用 Image 原有月弦师：栗发长侧辫、靛蓝象牙丝衣与浅蓝纱袖，左手托月牙弦琴、右手拨弦。包含 E 斜前朝右下和 W 真斜后朝左上的受击、普攻、施法；没有移动序列。

**68 张 PNG 齐全，技术检查通过；2026-10-08 加严静态连续性复核未通过，当前包需要修正。** 确认 E 普攻01鞋位离群，以及 W 受击/普攻收势与原戒备脚位不统一，详见 [验证结果](VERIFICATION.md)。旧记录中“静态通过”仅是此前检查结果，以本次结论为准。六组实际连播仍因浏览器安全策略拦截而未验；未接入客户端。

## 成品与预览

|动作|每向帧数|帧时长|每向总时长|正式目录|
|---|---:|---:|---:|---|
|受击 hit|6|40 ms|240 ms|[E](runtime/hit/E) / [W](runtime/hit/W)|
|普攻 attack|12|30 ms|360 ms|[E](runtime/attack/E) / [W](runtime/attack/W)|
|施法 cast|16|45 ms|720 ms|[E](runtime/cast/E) / [W](runtime/cast/W)|

[交互预览](preview.html)：六组独立播放、正常速度、0.25 倍慢放、暂停、上一帧/下一帧和帧滑条；所有图来自正式 PNG，不插值。`preview/` 另有六组联系表与各组 normal / quarter-speed APNG，便于单独打开。APNG 编码帧数和时长检查不代表已经目测连播。

2026-10-08 收尾复核：12 个 APNG 共 136 个解码帧逐一与正式 PNG 的 512 像素等比缩放结果比较，像素、顺序及正常/慢放时长全部一致；68 张正式帧的清单、逐图记录及 SHA 也一致。见 [交付复核](delivery-verification.json)，可运行 `verify_delivery.py` 重做这项检查。此检查确认预览使用最终帧，实际连播仍待人工验收。

正式图为 1024×1024 RGBA，原生生成均为 1254×1254。统一将整张原生画布缩至 960×960，置于 1024 画布 `(32,16)`；同向跨动作使用同一变换，不按每张最低脚重对齐。合同锚点顶部原点 `[512,942]`，左下 pivot `[0.5,0.08]`。独立姿态中的自然肩胸、膝部、抬跟和衣发反应未靠整图平移制作。

## 来源与模型

所有正式姿态均由内置 `image_gen` 单帧绘制/编辑；没有付费 API/CLI、镜像、复制帧或插值补帧。每次实际附原 E/W 身份图及人物属性主要画法样板，阶段连续性另附本组原生前帧。身份源在旧静态包，只读保留；没有读取客户端、兄弟目录或另一电脑。

目标为配置中的 `gpt-image-2.5-sunburst / max`，官方文档核对见 [model-verification.json](records/model-verification.json)。内置工具没有 model/quality 选择器，也未在返回中披露，因此每帧 `submittedParameters.model/quality`、`actualModel/actualQuality` 均为 `null`，不能据目标值宣称实际锁定了型号或档位。

逐帧索引规则：`runtime/<action>/<E|W>/<NN>.png` → `records/<action>-<E|W>/<NN>.generation.json`，其中索引实际 prompt、引用路径与 SHA、工具 receipt、原生来源 SHA、配置快照及固定导出操作。拒稿和定点修复保留独立文字证据。完整索引见 [manifest.json](manifest.json)；[SHA256SUMS](SHA256SUMS) 为正式图哈希。

## 检查与继续接入

[技术检查](technical-validation.json)核对尺寸、RGBA/alpha、缺帧、重复像素、记录/当前引用与 SHA；[根静态复核](records/root-static-review.json)与各组记录保存实际视觉观察。独立 AI 帧仍有细微衣发轮廓变化，动态节奏需通过正常和慢放继续确认。浏览器拒绝原文见 [证据](records/cast-E/browser-policy-rejection.json)。

`build_delivery.py` 重建清单、校验与联系表；`build_animations.py` 只将正式帧按顺序封装 APNG。此包未接入 Unity、FairyGUI、服务端或客户端战斗系统；接入要依据 [MERGE_HANDOFF.md](MERGE_HANDOFF.md)，不得把本素材验收等同游戏运行通过。

交付压缩包包含正式 PNG、全部预览、清单、逐图来源文字和检查脚本。解压后可打开 `preview.html`，运行与预览均不依赖已删除的宿主原生图；历史身份/画法引用仍记录其在 Image 项目中的原路径。验收时分别播放全部正常速度与 0.25 倍，核查方向、持琴左右手、脚位与收势；如发现异常，记录动作、E/W 方向与帧号。

按项目素材保留规则，68 张正式帧及当前身份/画法引用核实后，已删除本批次 78 张宿主原生图、拒稿与中间图，详见 [清理记录](cleanup.json)。保留 68 张正式 PNG、6 张联系表、12 个 APNG 预览及完整文字证据；旧身份与主要画法源继续保留。记录中的历史原生路径仅用于溯源，已清理文件不再是运行或预览依赖。
