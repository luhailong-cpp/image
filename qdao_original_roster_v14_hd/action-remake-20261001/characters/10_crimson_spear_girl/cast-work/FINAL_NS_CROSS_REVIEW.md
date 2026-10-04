# N / S 最终独立交叉审阅

审阅范围：角色 10 当前 `source-selection.json`、`candidate-inventory.json` 指向的 N / S 各 16 张；按 `run-playback-proposals.json` 的实际试播顺序判断。只读交叉审查，不改图、不改选择、不改公共清单。本文件是本轮唯一写入。

## 结论

没有发现足以要求重画的明确脚尖外撇、额外手脚、腿侧交替错误或循环倒序。建议保留当前这 32 张。这里的结论针对完整静态联系表、固定地面联系表及所列原图放大检查；没有声称完成客户端内动态验收。

当前 N 的 09 → 08 调序有实际姿态依据；S 必须使用既定播放排列，不能恢复文件号顺序后据此判定腿序。两组排列各包含 1–16 恰好一次，32 张原生图 SHA 均独立，来源和清单匹配，都是 1254×1254 RGBA。正常时长按用户最新要求为 16×75 ms = 1200 ms，均匀时长；没有建议恢复旧速度或相位权重。

## 本次实际看的证据

角色 10 完整联系表：`preview/run-N-contact.jpg`、`preview/run-S-contact.jpg`；S 完整实际播放顺序与固定地面图：`preview/run-S-grounding-contact.jpg`。联系表来源记录已核对当前选图。

角色 10 额外全分辨率查看：N06-v2、N08、N09、N10-v2、N14、N16；S02-v2、S03、S05-v5、S08-v2、S12-v3、S16。以下坐标为 1254 原图中的目视近似范围，不是程序提取关节或地面求解结果。

角色 09 先核实 `manifest.json` 的 run/N、run/S 两段确实引用 `runtime/run/N/01.png` 至 `16.png` 和 `runtime/run/S/01.png` 至 `16.png`；32 张实际 runtime SHA 与清单一致，清单每帧 75 ms。实际看了 `preview/qa/run-N-contact.png`、`run-S-contact.png` 及其来源记录，并追加查看 `runtime/run/N/06.png`、`runtime/run/S/05.png` 原图。参考的是对应方向的脚掌、膝踝与交替关系，不复制角色 09 的持弓方式或自由手臂。

## N：脚掌、双手与次序

实际播放槽：`01,02,03,04,05,06,07,09,08,10,11,12,13,14,15,16`。

- 01–05 的主要支撑侧在画面左；06 的双腿折回、07 的下降之后，09 开始画面右腿伸出，08 为随后更低的身体/右腿承接，10–13 延续右腿阶段，14–15 转回，16 画面左腿伸出接回 01。没有把同一条腿连续伪标为两次相反支撑。
- N09 画面右靴约 x=642–738、y=960–1187，鞋长轴近竖直；N08 同侧靴约 x=636–735、y=985–1206，同样近竖直。抬起的画面左靴在两张中保持折回，并非突然变成第三条腿。09 → 08 的先伸出、后下降关系合理，不能因编号 08 小于 09 就倒放。
- N06-v2 两个鞋底分别约 x=537–628、y=866–1008 与 x=645–715、y=905–979，跟随屈膝折回；鞋底露出主要是后视与踝屈，不构成脚尖朝画面两侧张开的明确 V 字。
- N10-v2 的画面右靴承接较低、另一靴折回；N14 两靴都抬起。N16 画面左靴约 x=547–641、y=965–1192，低靴长轴近竖直，另一靴斜露鞋底在 x=670–788、y=875–1025。右侧抬靴有透视旋转，但未见低脚向外横摆或膝踝反折的证据，不据此重画。
- 全段能辨认两条腿和两只手。N 高握手位于画面左上，低握手位于画面右下，两手仍在同一枪杆上；袖口到握手连接可见。后视长发遮住局部上臂是正常遮挡，没有把遮挡当成缺手，也没有要求像竹弓那样松开一手摆臂。

## S：脚掌、双手与次序

实际播放槽：`04,06,07,01,03,09,10,11,13,14,15,12,02,05,16,08`。

- 开始的 04/06/07/01 维持画面右腿支撑与画面左腿前摆；03 是换侧的短腾空/转接；09/10/11/13/14/15/12 是画面左腿阶段；02/05 再次短腾空；16/08 画面右腿伸出承接，回到 04。上述是实际可见相位范围，不把每张请求中的标签当成真实接触测量。
- S03 两靴最低点分属约 y=1120 和 y=995，较本方向支撑靴常见 y≈1180 有可见间隙，符合换侧短腾空。两个靴尖朝画面下方，没有横向向外撇成 V 字。
- S02-v2 两膝弯曲，双靴集中约 y=945–1075；S05-v5 两靴集中约 x=512–760、y=923–1080。两张都是真正抬脚的转接，不能因接触表没有逐帧贴地而把它们判作漏接地。S05 靴轴随弯膝轻微倾斜，未见靴尖明显朝画面两侧打开。
- S12-v3 画面左低靴约 x=485–589、y=958–1170，另一膝抬起，靴尖均沿下方；这是左腿阶段尾部。S16 和 S08-v2 的画面右低靴分别约 x=604–721、y=943–1177 和 x=601–720、y=946–1193，趾盖/鞋底前后关系朝 S；没有明显向画面右横撇。
- 16 → 08 → 04 的接续保持同一右侧支撑腿，不是跨回另一只脚；02/05 的离地后先接 16，也没有把支撑/腾空顺序颠倒。接地静态关系足以支持保留此排列，实际滑动感仍应在固定方向配准后的 1200 ms 循环中判断。
- 全段是两条腿、两只手。画面左的低握手和画面右的高握手都连到同一枪杆，肩肘随持枪角度变化。没有确认到额外手掌或突然换握侧。角色 09 单手弓的自由臂摆幅不能作为角色 10 双手枪必须匹配的要求。

## 与用户认可的 09 的对应关系及边界

09 的 N 全组以及原图 N06 也会清楚显示抬脚鞋底，鞋底可见本身不等于外八；09 的 S 全组与原图 S05 中靴尖主要顺着画面下方，左右腿交替承担低位。角色 10 当前 N/S 与这种方向关系一致，没有拿腿间距变窄代替脚掌方向检查。

本轮不提出重画槽。`run-playback-proposals.json` 当前仍写 `trial-order-not-approved`、`formalExportOrder=false`，这是根任务最终导出/接入时需要明确处理的状态，不是图片缺陷；本子任务按授权不修改。最终 1200 ms 动态播放及客户端接地验收由 ROOT 统一完成，本审查不以静态结果代替它。

## 本轮来源快照

下表按实际播放位置列出来源。SHA 是本轮现场读取 PNG 计算，并与 candidate-inventory 比对；有显式 source-selection 的槽也核对路径一致。32 张 SHA 互不相同。

| 方向 | 播放位 | 槽 | 当前来源（相对角色 10） | SHA-256 |
|---|---:|---:|---|---|
| N | 01 | 01 | `generation/run-N-01/native.png` | `4c13bfa0fa7044cf8eb6154a0a1bb51ce3be8d61d30375b2fa72c72790e48f2c` |
| N | 02 | 02 | `generation/run-N-02-v2/native.png` | `bc21368476451055165ecdea38179e5c59207619322fe7a38530b1bb5052d75d` |
| N | 03 | 03 | `generation/run-N-03/native.png` | `3eeeb54ae749cb0e40a8d518428965865e0bf81cd1341e2566f6016be58f6870` |
| N | 04 | 04 | `generation/run-N-04/native.png` | `f8f8342c210c1d7b009a2fbf192611891e07cfcf8a10364b03ce35bdd8dd70ec` |
| N | 05 | 05 | `generation/run-N-05/native.png` | `81d552609c94b1f8adbb1e008e25ae90b516bf8a2296f57cc4ed9cbf0e959852` |
| N | 06 | 06 | `generation/run-N-06-v2/native.png` | `8b47282f655d2961b0b08d9e4aecc360a1644e570d7c9e565e4e71a235573c36` |
| N | 07 | 07 | `generation/run-N-07-v2/native.png` | `84e5c993dfc317453ee346ec5c9a7f3ddfb996eebbcda1fbdb8422f8dbcaf7ba` |
| N | 08 | 09 | `generation/run-N-09/native.png` | `f697e6a13eb551e3335044caf4a06c6e42c1f13560dd71f80c49df662542bcfe` |
| N | 09 | 08 | `generation/run-N-08/native.png` | `7ab0d57fcad008dedbb99773f02406e2057b18ad1a3ea2628f65bcd94fdce3bc` |
| N | 10 | 10 | `generation/run-N-10-v2/native.png` | `549aae6919d4471dc654910f3ac17846db63a17e9821d92f9503024fb41b712d` |
| N | 11 | 11 | `generation/run-N-11/native.png` | `70590c20a223d338e3a2f824c327f18f6c408f4612878f0675bbe23bde19742e` |
| N | 12 | 12 | `generation/run-N-12/native.png` | `b7f6cb2397322b41507679e633eaa365bd5a8be40b872d7ce003d1896a825445` |
| N | 13 | 13 | `generation/run-N-13/native.png` | `77f6fa9ee01037208fef3efe06ddae5ba9a6bbc09304d4ac04ee102779dc1bcb` |
| N | 14 | 14 | `generation/run-N-14/native.png` | `4dae61b0cc5494fca9e32298cfc46c0fa4166aa33a0d73a5a0595a89b4f9b6c4` |
| N | 15 | 15 | `generation/run-N-15/native.png` | `a4a8e4d4b53a197d1dd391f2b3292cbd4db5bf7caa077f20ec19bb71633f8791` |
| N | 16 | 16 | `generation/run-N-16/native.png` | `11ec790baa4d989ffe5b15e625bdd48d5b05364a25401784d256b12580cc5f3c` |
| S | 01 | 04 | `generation/run-S-04/native.png` | `caec3b8a4d72642ab2b6302c7aab8e8c0d6379f024434421404672909c0ca765` |
| S | 02 | 06 | `generation/run-S-06-v3/native.png` | `8a5fe98a4a90fb51640f1614a1f57c67effef98ae660b8063afaa8481a966cd4` |
| S | 03 | 07 | `generation/run-S-07/native.png` | `d8960a63064ce870dfae9a0eb8f636d439eb36fc38ff792ba46b1cf3b556ec36` |
| S | 04 | 01 | `generation/run-S-01-v3/native.png` | `589d29a81254e53dedf3c9a4f8b4d1b8cad1211b2db4fc645469767037a55a64` |
| S | 05 | 03 | `generation/run-S-03/native.png` | `6044ab7ea6083d821b783123051e6a7a024606c64de2777386ea8a17708104d2` |
| S | 06 | 09 | `generation/run-S-09-v3/native.png` | `d58a718e8765cec21f3924ea0d17c8e0461b8134c869e7d4307ec18521df659c` |
| S | 07 | 10 | `generation/run-S-10/native.png` | `94c53626bd06e06130bc358a88b6f78169e1a1cbca51295e771283546f4253ec` |
| S | 08 | 11 | `generation/run-S-11/native.png` | `b2b9fd3c4fb64d2a5826dec576f65fd8b5d0615c1e0cf4ba0e2fe1b5f4bfbe86` |
| S | 09 | 13 | `generation/run-S-13/native.png` | `190548711e8c792a18a1dfd4d59f75193d07c9211d1c53e80bf99ec37705a1b0` |
| S | 10 | 14 | `generation/run-S-14-v4/native.png` | `be8f73081c1c6d89feada0394820e0b3a8494aa545f2e5ce65db1f8e9089b27e` |
| S | 11 | 15 | `generation/run-S-15/native.png` | `4dc4efc3cd8149f91fd86dced095e41a6c85cd68265ce966766087f3f6a299cc` |
| S | 12 | 12 | `generation/run-S-12-v3/native.png` | `57781aa7181befe4d19f125152f72cb876f74b2f541366fe44be524273474797` |
| S | 13 | 02 | `generation/run-S-02-v2/native.png` | `8b960eae4517cbdb0744ac6d8e0ac67b51848ce3e7fbc4897d079c785894cd85` |
| S | 14 | 05 | `generation/run-S-05-v5/native.png` | `36de3ae95da24da5404d27e8b2e1bb14335404cc1b1ba175e760390e6d850b87` |
| S | 15 | 16 | `generation/run-S-16/native.png` | `effda33260f7a660b4888f2903fa2ad763727601d688970d1e7bcb65a992bfb1` |
| S | 16 | 08 | `generation/run-S-08-v2/native.png` | `cde36588088ae7460893717fffa24fa176c131b47b63fb913b8f4c2bef47d33a` |

审阅记录 UTC：2026-10-04T05:39:32.534933+00:00
