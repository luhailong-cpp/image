# 五行奇谈 · 全库 Q 版美术更新

本轮按用户要求遍历素材目录，以 `60134a6` 的 369 个已跟踪视觉文件为基线。需要更新的旧人物、物件、界面切片、九宫格控件和场景均在原路径替换，保持原像素尺寸；已确认的新版道童、主城与 v5 视觉稿保留。最终覆盖状态见 [全库验证](validation.json)，制作前范围见 [逐文件审计](../docs/ART_ASSET_AUDIT.json)。

## 交付入口

| 内容 | 文件与记录 |
|---|---|
| 六张标准宽屏界面／场景，入场云气与遮罩映射 | [v5 说明](../qdao_ui_redesign_v5/README.md)、[过场清单](../qdao_ui_redesign_v5/transition_manifest.json) |
| 39 套 SVG＋透明 PNG 控件，包含全部十枚圆徽标 | [通用组件](../qdao_ui_redesign_v5/components/README.md) |
| 50 张原路径切片，以及高分辨原子控件和徽标 | [切片与九宫格](../exact_qdao_slices/README.md) |
| 12 张旧选服画面及独立透明分层 | [图层与布局](../q_daoist_login_ui_uncropped_highres_final_layers/README_NATIVE_Q5.md) |
| 124 枚物件／法器图标，600×600 RGBA；原布局 FairyGUI 图集 | [图标交付](icons/README.md) |
| 22 个逐张重绘职业人物＋2 个统一道童参考，4096×4096 RGBA | [人物包](../q_daoist_character_pack_4096/README.md) |
| 7 张根目录旧道童兼容输出 | [道童兼容映射](hero_compat_manifest.json) |
| 8 方向×4 帧道童行走，1254×1254 RGBA | [动作、脚底锚点与帧序](../character_move_8dir/README.md) |
| 灵玥与三只早期宠物的独立透明静态素材 | [灵玥](../qdao_ui_redesign_v5/pet/README.md)、[三只宠物](../qdao_chibi_pets_v1/README.md) |

## 尺寸与制作方式

人物、物件、动作和新增场景使用内置 `image_gen`，原生 UI 延续项目 SVG 构建系统。透明清理、切格、缩放、对齐与图集重建通过本地确定性处理完成。逐项提示词、来源标识、真实原生尺寸和处理记录随各包保存。

保持大小指原文件的像素画布与路径不变。4096 人物、600 图标和 1254 动作帧包含由较小原生图片重采样的输出，具体尺寸在记录中披露；没有将放大尺寸冒称为原生 AI 分辨率。高分辨 UI 框板与图标从原生 SVG 光栅化，避免先放大小尺寸 PNG。

旧人物 a/b/c 路径统一复用已确认金发带道童，属于身份兼容输出；22 个职业人物保留各自发型、配色、法器和角色主题。三只早期宠物与灵玥的已确认有底设定图保留，透明站立图另存。

## 清理和验证

按用户要求删除旧切格母图、旧图集预览与诊断截图；本轮 `.work` 中的母图副本、透明整板、切格副本和 GIF 不进入交付。删除记录见 [cleanup.json](cleanup.json)。正式运行图集、独立 PNG、可重建 SVG、被构建脚本使用的来源及已确认参考图保留。

```powershell
python qdao_ui_redesign_v5/export_ui.py --check
python qdao_asset_refresh_v6/icons/build_atlas.py --check
python -B qdao_asset_refresh_v6/pets/build_manifest.py
python q_daoist_character_pack_4096/build_manifest.py
python qdao_asset_refresh_v6/verify_delivery_contracts.py
python qdao_asset_refresh_v6/verify_assets.py
node exact_qdao_slices/build_native_q5.mjs --check --sharp '<已安装 node_modules>/sharp'
git diff --check
```

全库检查覆盖基线文件是否被替换、原像素尺寸、PNG 可解码、RGBA、SVG 解析和文档链接。各包另有逐项哈希、图集像素、锚点和图层合成验证；[跨包核验](contracts_validation.json)确认92个已接受文件逐字节保留，并检查32帧、9个道童兼容输出和12张UI。最终图经过视觉检查。

本仓库交付美术。v5 登录、选服、选角整屏保留为视觉参考；原生控件、独立人物／宠物和旧选服透明分层供客户端使用。完整界面适配、真实服务数据、按钮事件、动作播放、碰撞／导航和引擎内验收仍需在实际客户端工程实施。
