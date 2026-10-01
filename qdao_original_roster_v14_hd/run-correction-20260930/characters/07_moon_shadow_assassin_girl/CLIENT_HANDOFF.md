# 07 月影少女：独立接入交接（制作中，不可替换）

本目录只负责 `07_moon_shadow_assassin_girl`。当前尚未完成128帧，动态验收未通过，不能据此替换客户端资源。

## 接口与几何

- 最终目标：`candidate/walk/{N,NE,E,SE,S,SW,W,NW}/01.png` 至 `16.png`，128张1024×1024 RGBA。
- 当前库存、来源及SHA以本角色 `manifest.json` 每条记录为准；缺帧明确保留缺失状态，预览不借用邻帧。
- 客户端目标只读基线：`D:/luyuan/wuxingqitan/mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV14/07_moon_shadow_assassin_girl`。
- 保持30ms/帧、480ms/圈，PPU 104，运行pivot `(0.5,0.08)`。1024画布约定根点 `(512,942)`，pivot对应未取整y=942.08。普通TextureImporter的默认PPU100/pivot0.5不是运行值。
- 本批原生1254×1254单帧，统一整画布降采样为1024，再统一上移20px，将生成首稿约94%高度的虚拟地面映射至运行约92%根点。所有帧使用同一变换，禁止单帧脚底对齐或包围盒缩放；真实腾空偏移保留。实际姿态根点仍须视觉验收。

## 来源与复核

逐图 `generation/E/*.png.generation.json` 保存原生SHA、实际请求、参考SHA、工具结果和配置快照；导出图旁来源记录关联原生图与记录SHA。内置工具未披露实际型号/质量，均为null，不把配置目标当实际值。官方本批核对见 `model-verification.json`。

私有导出器 `tools/package.py` 默认只读；显式 `--write` 才在本角色目录输出候选、manifest、离线预览。`generation/selection.json` 是预览选帧，不是美术批准。

预览：`preview/index.html` 提供30ms正常、120ms慢速、128/256/512像素显示与逐帧控制。浏览器工具拒绝本地file协议，未绕行；动态观察尚待完成，详见 `review.json`。

## 完成前剩余事项

补齐并修正E向16帧 → 实际动态观察并通过首个方向 → 其余七方向112帧 → 跨方向身份/比例/左右手/非对称月饰检查 → 刷新128帧manifest与SHA → 由客户端主写者单独接入并运行验收。

本窗口未写客户端、未启动Unity、未修改全局索引或共享配置、未提交或推送。旧候选的审核状态未改；旧试玩证据不替代本次跑步验收。
