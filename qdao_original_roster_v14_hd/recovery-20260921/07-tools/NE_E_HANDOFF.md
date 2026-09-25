# 07 月影少女 NE / E 当前交接

更新时间（UTC）：2026-09-23T12:39:25.849362+00:00

**仍在制作，两个方向均未宣布完整离线验收通过；未做客户端接入。**

- 当前实际文件：NE、E 各16张行走和1张独立站立，共34张1024透明PNG。
- 当前34张输出SHA全部匹配记录：True；记录的原生来源SHA互不重复：34/34。
- 原生来源尺寸均1254×1254。历史清理删除的raw只能按文字/清理证据追溯，不代表可重新读像素。新生成raw保留在07-generation各attempt目录。
- NE已修02/03比例、06尺寸、07/08比例与脚踝相位、13/14前摆与15反侧蹬离；旧13-v3只迁至12一槽，见ne-reassignment-20260923.json。
- E04是旧1024候选的0.9647812166488794整幅等比缩小，来源SHA及旧记录在ne-e-review/E04-scale-20260923.json；没有伪称新AI原生图。
- E01/09、03/11经双人复核发现近远腿未清楚交换，正在修E06前摆至13承重过渡。E09-r20260923a/b/c/d/f不选；e是正确近腿抬膝的姿势参考，不能同时计入多个槽。
- NE07-r20260923a/b、NE08-r20260923a的头比修正过度，不选；当前07c/08b重新以NE09正常比例作实际参考，未用自动头宽缩放。
- 内置工具未披露实际型号/质量，actualModel/actualQuality为null。未调用收费API。
- 预览页：ne-e-review/index.html；深浅GIF各16×30ms=480ms（最终选槽后需再重建）。IAB曾实播深浅512及部分1024/接缝，后续修改不能沿用旧验收。

## 当前逐槽选择（以此表及实际sidecar为准）

| 槽 | 实际来源attempt | 输出SHA256 |
|---|---|---|
| idle/NE.png | idle-NE-v2 | 8375d0d55678ccea5ad698a15d88bf5c625f54d8e6293be5121df07f82db53ac |
| walk/NE/01.png | walk-NE-01-v3 | a32a487fba445317202c924382b1f173fcc9f17b57e490cf12cd49f160c3fbe8 |
| walk/NE/02.png | walk-NE-02-v6 | 2f81b1965626c14145446ad96019f1fb8811971641bb36e721d0d49a1cfd2901 |
| walk/NE/03.png | walk-NE-03-v2 | 9d5986adc649b157226b03d25536a4a17e6bbc4849a2334454dd6f0a0b40f6cf |
| walk/NE/04.png | walk-NE-04-v2 | 9f96b8a85d18a61b15cac93bd49313b8687795dcaeef7182f26e4b245fde8626 |
| walk/NE/05.png | walk-NE-05-v1 | cf616c878a0b756b1ced0f16594f21cc37a8abb9c389c4c8d2f4bf43a6444a28 |
| walk/NE/06.png | walk-NE-06-r20260923a | c266b7abca82469e0c321c9391ffe2f59a840564c8a569a9b5ed2769d7525b0f |
| walk/NE/07.png | walk-NE-07-r20260923c | 979fc0964ed51313457ba0373431b24837bdf49716e848e06db881af2528cbc5 |
| walk/NE/08.png | walk-NE-08-r20260923b | 47468f339617356004f9db1097b9c4d869dc0864a5e3a9973619a79cb1902fa1 |
| walk/NE/09.png | walk-NE-09-v1 | 5211e5a4838f5bb32718964e8de21e3a19397f70de065d796e051f8730e89b73 |
| walk/NE/10.png | walk-NE-10-v1 | b059b26e110b393cde6f35055a6fab89185a3ed33febaffb3dc2bbc9a18b5cdd |
| walk/NE/11.png | walk-NE-11-v1 | 7c989bc275be3052a679c6b117f7a670661535a57529e70fd573571dc1368763 |
| walk/NE/12.png | walk-NE-13-v3 | e0f899cf614e2785ff519e4b4fe7feacd32fc2c04c0bb7dfa7a765883133ef80 |
| walk/NE/13.png | walk-NE-13-r20260923c | 2500b8317329bdd1abf5cea84bbaed3c7349c241a26a5499b43cbdb453e284d0 |
| walk/NE/14.png | walk-NE-14-r20260923d | 2b467837c5ccc6e0ab6927b5798a64ccc230dcb08dc738af002572beb399ddfa |
| walk/NE/15.png | walk-NE-15-r20260923c | 7516cc3109ad2d2a6e6de65e74e95237beb4b2d28f21f99e702968f6e40b5dd3 |
| walk/NE/16.png | walk-NE-16-v1 | 432c78a2bc8d6afbbaf46434f688b33dc4a98b9f2526fd6fc24489025fa7e93e |
| idle/E.png | idle-E-v2 | cb18fc244dd0553439d0907b87816ea1cd390a30a07906bfd37b3c1dd3a18915 |
| walk/E/01.png | walk-E-01-v1 | 8bc9da7f79aa4f5697087f86136d2781f2bddc88ac84d0c74a91993fab25cd76 |
| walk/E/02.png | walk-E-02-v2 | 86ff50060b92e9b2228b6dc0aa96b520672a612d7da83f6a5175166e9cc33dc8 |
| walk/E/03.png | walk-E-03-v1 | 84ac2afb9661c55bc9a11e99147ee625bacf8265efbe6d01a5f92bd4116f906a |
| walk/E/04.png | walk-E-04-v1 | ed42a6a668b289639b9056a12248f3a8ab4b6691aaf42de7ce78bc7861b1a7b8 |
| walk/E/05.png | walk-E-05-v1 | 18109cdcf54f9f58b647fd6c5f8c9f8bd79abc5863e07c7c56e8bb7e7e640b15 |
| walk/E/06.png | walk-E-06-v1 | 104fd494b67c8ff0dfd87d1f79199ef9f3a25645fdfb24d59ded5bc24757c75d |
| walk/E/07.png | walk-E-07-r20260923a | 0d427535e5d8b0d66c2a9989786ae5397a36383884139b1a7a485f888b46a97f |
| walk/E/08.png | walk-E-08-v1 | 0c2b48bf33fe6f5a5891b34c64056bdd4487da2458bab7839a089b53785faf35 |
| walk/E/09.png | walk-E-09-v1 | b4576ef176f64e432f2862b8ded8d5a1fab13e9a6dc4fa903a636e997b83ebe0 |
| walk/E/10.png | walk-E-10-v1 | 3a58b298608e06ebf1ce86725e537cf117745d3adf3bb15a2570975e9dab0b33 |
| walk/E/11.png | walk-E-11-v1 | 571ac8b49abc4e97abaf1c52784ce9e9c957d37be32761f5526f873f3e498634 |
| walk/E/12.png | walk-E-12-v2 | 53a37d5933984c236cad822e2de4fe4b5c881c6ffeb9f3c1e5e3e35593f35761 |
| walk/E/13.png | walk-E-13-v3 | adf7bbe193eb60e797a7ef745d3b34fb1fff04027163b42cf60be49bbc69830d |
| walk/E/14.png | walk-E-14-r20260923b | 4e3ee5a115bf7eabd1d0271fb3bac523d172f27563cb625597fcf8e936e62a6a |
| walk/E/15.png | walk-E-15-v1 | b90f9e37fb76908061bc1864613d8960424eb673ff47aea72bfac8b242f4bd33 |
| walk/E/16.png | walk-E-16-v1 | 76a2183954a179ef21b76019a56a0ef05d401fdb12add9fca01f704e2ac40af7 |

## 恢复第一步

先读本表及各attempt/result.json，处理已经成功但未导出的唯一raw；再完成E反侧腿过渡，不重复生成或把拒稿计为完成。生成入口现可用，当前不是工具额度阻塞。

以下是旧交接，仅保留历史；库存、选择与保留规则以本节和最新用户要求为准。
<!-- HISTORICAL_NE_E_HANDOFF -->
# 07 月影少女 NE / E 方向交接

> 2026-09-23用户覆盖旧保留规则：原图、拒稿及回退图片已清理，本文逐槽选择和问题文字保留；下文“不可删除/原图保留/不可变预览”是历史做法，现不再适用。当前预览为`../07-delivery-preview/current-review-20260923/index.html`，来源删除情况见`cleanup-20260923.json`。34张NE/E当前候选PNG仍在，完整美术验收仍未通过。

范围：只涉及 `07_moon_shadow_assassin_girl` 的 NE、E 两个方向。状态更新于 2026-09-21；本文件不代替角色总交接，不宣布角色整体完成。

## 当前状态

- 46 张真实内置 image_gen 单帧 raw：NE 27、E 19。46 个不同 SHA-256，全部原生 1254×1254 透明 PNG。
- 当前选入 34 张诊断候选：NE/E 各 16 walk + 1 独立 idle，全部 1024×1024 RGBA。
- 原图逐张保留于 `../07-generation/<attempt>/raw.png`，另有不可变归档 `archives/<attempt>/`。归档副本不能计作新生图。
- 本次累计 12 张未选稿；拒稿、请求和返回记录均保留。所有候选仍待美术复核。
- **尚未通过真实步态/连续循环验收。** 库存齐、文件不同、GIF 时长正确都不等于美术合格。

## 当前选用

NE idle：`idle-NE-v2`。NE walk 默认 `walk-NE-<两位帧号>-v1`，以下覆盖：

| 帧 | 当前 attempt | 修正目的 |
| --- | --- | --- |
| 01 | walk-NE-01-v3 | 与 09 相反接触腿 |
| 02 | walk-NE-02-v3 | 保持右侧后靴，修复 01→02 突然换腿 |
| 04 | walk-NE-04-v2 | 右靴靠近支撑脚进入 passing |
| 07 | walk-NE-07-v2 | 原稿统一对齐后顶端越界，重新生成留白 |
| 13 | walk-NE-13-v3 | 与前半圈承重脚不同，但前摆程度仍不足 |

E idle：`idle-E-v2`。E walk 默认 `walk-E-<两位帧号>-v1`，仅 02 使用 `walk-E-02-v2`，修复原 02 的突然转胸及摆臂反转。所有替换前候选均保存在 `selection-history/`。

## 美术问题与已知拒稿

1. NE 原 01/02/03 出现后腿轮流切换；02-v3 和 04-v2 已改善该段，最新整段还需动态复核。02-v3 头部略增大，不能因腿势修正就忽略尺度变化。
2. NE 12→13→14→15 前摆不足、部分脚掌继续朝向观看者；中间相位推进不够清楚。13-v4 虽把左靴向内收近，仍未实现要求的前摆/隐藏鞋底，未选用。
3. E 12/13/14 的第三参考来自独立 idle，整体显得小于 01–11、15–16；11→12 与14→15有明显尺寸/身形跳变。全帧等比头部量测校准可以做诊断，但不能修复头身比例、镜头、躯干或动作错误。本代理未对 NE/E 应用此校准。
4. E 的 16 帧腿部有接触、承重、抬脚、前摆变化，但 01/09 的深度与相反承重还须逐帧确认；不能只因摆臂不同而判断换腿成功。
5. 原始图边缘有极低 alpha 的高饱和彩点；导出脚本只清除 alpha≤8 的限定杂点。完整100%深浅底边缘验收、武器/手腕连续性以及实时浏览器原速/慢速播放尚未完成。

未选稿包括 NE idle-v1（头背身前），NE01-v1/v2（未反相），NE02-v1/v2（与临帧突换腿），NE04-v1（passing不足），NE07-v1（导出越界），NE13-v1/v2/v4（前摆/反相不足），E idle-v1（躯干偏正面），E02-v1（突然转胸/摆臂）。这些记录不可删除、覆盖或当作验收通过。

## 最新预览和结构证据

当前不可变预览：`../07-delivery-preview/ne-e-diagnostic-v3/index.html`。

- NE/E 的深浅底 GIF 均 16 帧，每帧 30ms，周期480ms；保存后重新读取时长，`interpolation=false`。
- 深浅底联系表、15/16/01/02 接缝图、runtime 副本、manifest、structural-report 均在该 revision 内。
- manifest SHA-256：`aade516ae1179495371ae0d9a79c0c4983766be7dc4b4862413931105f370c77`。
- 此预览同时快照其他方向当时已选文件：全局64 walk、5 idle、67缺槽。该全局快照不是 NE/E 数量，也不是全部角色完成状态。
- 该快照 allOutput1024RGBA=true；69张来源SHA与裁边像素SHA都各不相同。精确哈希/镜像检查只是结构证据，不能证明动作连续。

## 生成与归档证据

每个 attempt 的 `request.json` 保存真实提交参数、UTC开始时间、配置快照、角色槽；`prompt.txt` 与真实 prompt 一致；`result.json` 保存真实工具 output_hint 和收到结果的UTC；`raw.png.generation.json` 保存原生尺寸、SHA、参考图哈希与来源路径。

目标配置是当时 `config/image-generation.json` 的 `gpt-image-2.5-sunburst` / `max`；实际工具接口没有 model/quality 参数，也没有披露实际值，故 submitted model/quality、actualModel/actualQuality 均为 null。不能把配置目标或提示词当成实际锁定证据。

NE02-v3、NE04-v2 的参考顺序改为动作 edit target 第一、原肖像1024等比检查副本第二、已确认风格图第三；所有参考真实附送，调整理由是模型在原顺序下反复擅自换腿。记录精确保留该差异，未改写历史。

本代理的 result.json 为 receivedAt/output_hint 格式；使用工具 `archive` 的显式原图路径、kind/direction/frame归档，而非伪造状态字段。export 只做限定透明杂点清理、原生图整体等比降采样及整数对齐至[512,942]；未镜像、插值、变形、复制姿势或程序生成动作图。

没有 Git 提交、客户端接入、正式美术批准，也没有继续其他角色。
