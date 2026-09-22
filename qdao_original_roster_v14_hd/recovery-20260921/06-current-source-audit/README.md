# 06 实时来源与字节基线审计

检查时间：2026-09-21 15:43 UTC。仅新增本审计目录，没有改动正式 candidate、generation 历史证据、旧动作或共享脚本；没有生图。

## 实时库存

- V14 正式目录 `qdao_original_roster_v14_hd/candidate/06_thunder_caster_boy` 只有 E01 / E02 / E03 / E05 / E09，5 张 1024×1024 透明 PNG。
- 旧 S01–16 和独立 idle N / NE / E / SE / S / SW / W / NW 位于 `qdao_original_roster_v13/candidate/06_thunder_caster_boy`，24 张均为 512×512，不能描述为原生 1024。其逐张字节 SHA 基线见 [old-byte-baseline.json](old-byte-baseline.json)。
- 隔离目录 `qdao_original_roster_v14_hd/recovery-20260921/06-audit/candidate/06_thunder_caster_boy/walk/E` 有 01 / 02 / 03 / 04 / 05 / 06 / 09 / 13，8 张 1024×1024。
- 当前正式与旧动作合并为 21 walk + 8 idle；计入待导入 E04 / E06 / E13 后为 24 walk + 8 idle。仍缺 E07 / E08 / E10 / E11 / E12 / E14 / E15 / E16，以及 N / NE / SE / SW / W / NW 各 16，共 104 walk。

## 来源核验

- `generation/06_thunder_caster_boy` 中仍为 9 批 raw，全部 1254×1254，PNG 可完整解码，SHA 与暂停库存及 06-audit 的原图记录相同。未发现新增未登记 raw。
- 其中 E09-single-v1 是既有拒稿；正式 E09 使用 E09-single-v2。拒稿不得作为第 9 个目标姿势。
- V13、V14 和 06-audit 隔离 candidate 的全部 manifest 图像条目均与实时文件 SHA 一致。帧输出范围内未发现完全相同 RGBA 像素；这不是姿势正确性或真实步态的美术批准。
- E02 / E03 / E05 / E09 的 prompt 与 receipt 共 8 份实时文件仍为已知 LF 字节。单纯 LF→CRLF 后能精确命中历史来源绑定 SHA，本审计未写回或重标历史记录。见 [text-byte-checks.json](text-byte-checks.json)。
- 历史记录实际型号仍为 host-managed/unverified；本审计未重新验证 C2PA 签名。

## 待导入精确入口

下列路径相对工作目录 `D:/luyuan/wuxingqitan/image`：

| 目标 | 已归档 raw | 隔离 1024 输出 |
|---|---|---|
| E04 | `qdao_original_roster_v14_hd/generation/06_thunder_caster_boy/E04-single-v1/raw.png` | `qdao_original_roster_v14_hd/recovery-20260921/06-audit/candidate/06_thunder_caster_boy/walk/E/04.png` |
| E06 | `qdao_original_roster_v14_hd/generation/06_thunder_caster_boy/E06-single-v1/raw.png` | `qdao_original_roster_v14_hd/recovery-20260921/06-audit/candidate/06_thunder_caster_boy/walk/E/06.png` |
| E13 | `qdao_original_roster_v14_hd/generation/06_thunder_caster_boy/E13-single-v1/raw.png` | `qdao_original_roster_v14_hd/recovery-20260921/06-audit/candidate/06_thunder_caster_boy/walk/E/13.png` |

审计时上述三个正式目标槽均为空，已读 `06-audit/import_pending.py` 并执行默认 dry-run 通过；未执行 `--apply`。它检查 raw/prompt/receipt 来源字节及空槽，固定 common_scale=.88，原生缩小为 1024，关闭共享 preview 索引更新。应由主任务在实时确认槽位后执行导入，再独立重建与目视检查。

## 证据与验收边界

- [summary.json](summary.json)：当前/旧/隔离逐方向帧号、缺槽和导入路径。
- [inventory.json](inventory.json)：上述四个范围全部文件精确路径、SHA、PNG 尺寸、模式、透明范围与像素 SHA。
- [manifest-checks.json](manifest-checks.json)：实时文件与各自 manifest 逐条比较。
- [raw-checks.json](raw-checks.json)：9 raw 与旧记录、prompt、receipt 字节比较。

本轮是来源与字节审计，没有给予美术批准，没有完成 E03 紫边修复、完整八向 30 ms 动态预览或 Unity/正式客户端验收。旧 S 与 idle 的原字节须保留，现有 512 与新 1024 混合库存须明确披露。
