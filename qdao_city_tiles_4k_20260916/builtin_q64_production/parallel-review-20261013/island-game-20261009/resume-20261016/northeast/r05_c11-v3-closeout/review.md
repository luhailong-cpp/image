# r05_c11 v3 独立检查收尾

本张内部检查通过，北边灯笼金棱仍待修，正式验收未通过。该结论仅绑定下列v3哈希；本批完成后停止追查新版本。

当前核实的4096×4096图：[r05_c11-localfinish-v3-20261016.png](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/tiles/r05_c11-localfinish-v3-20261016.png)。

SHA256：`4bfa9fc5ab25793c6bbd750c6da6ea66ede8dd083c9097fd9051ed1d8051a47d`。

v3相对v2的差异框为图块局部 `[2944,185,3968,1280]`，世界框 `[43904,16569,44928,17664]`。差异框外像素完全相同，前185行亦相同。16个1254原生核心源加2处原生修补裁片，按记录原尺寸摆放可逐像素重建当前4096图；无缩放、羽化或程序绘制细节。实际生图型号未返回。

49份内部检查裁片均已核实文件哈希且与当前v3裁切像素完全一致，分别覆盖16核心、24缝、9交点。40项未变的通过证据直接复用，9项变化的实际像素范围及8处修补四边已原尺寸查看，其余未变部分复用已有检查。

原 x3072／y1024 的矩形清晰度边界已消除：灯笼左侧栏柱旁窄铺地、阶面灰缝和阴影恢复连续，两处修补的四边及交汇未见新增断点或直线材质框。旧v2虚化问题不再列为当前v3待修。

| 范围 | 当前QA |
|---|---|
| 内部16核心、24缝、9交点 | 通过；绑定49份当前像素证据 |
| 北边 r04_c11，第1—3段 | 当前邻图hash与裁片像素一致，复用通过 |
| 北边第4段 | 未通过；灯笼金棱粗细和横向小台阶仍开放 |
| 东边 r05_c12-sol-v1，4段共4096 | 第1—2段本次实看通过，第3—4段复用hash绑定通过 |
| 西边 r05_c10 | 缺完整邻图，待外接验收 |
| 南边 r06_c11 | 缺完整邻图，待外接验收 |
| 东北四邻交点 | 中心花叶／朱柱轮廓连续；左侧北缝金棱细节同样待修 |

- [v3变化区及四边原尺寸图](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/resume-20261016/northeast/r05_c11-v3-closeout/v3-changed-region-and-perimeters-100pct.png)
- [原x3072／y1024交点原尺寸图](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/resume-20261016/northeast/r05_c11-v3-closeout/v3-old-focus-junction-x3072-y1024-100pct.png)
- [北边第4段金棱证据](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast/qa/r05_c11-localfinish-v3-20261016-changed/external-top-4-100pct.png)
- [完整源图hash、逐条内部／外接QA与输入复核](D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-review-20261013/island-game-20261009/resume-20261016/northeast/r05_c11-v3-closeout/summary.json)

收尾复核本批 109 项唯一输入，109 项哈希未变，0 项变化。原生产源、选源账本和Git均未修改；本审查零生图、零AI修图。
