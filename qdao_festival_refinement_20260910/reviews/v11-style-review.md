# v11道家Q版节庆风格独立审查

审查时间：2026-09-12T08:03:59.061995+00:00。本次只审查图片、写审查文件，没有修改任何游戏图片。

**8位人物的设计都适宜保留，但本批不能记作全部精修验收完成。** 新发现6位人物的透明轮廓有紫红污染：23、24、25、26、28、29的32动作帧，以及25、26、28的肖像。共255份PNG需要清理或随源帧重建，48份GIF需要随后重导；其余105份正式媒体保留。

## 逐角色结论

| 人物 | 实看要点与保留理由 | 正式媒体处理 |
|---|---|---|
| 23 灯穗小使 | 圆脸雀斑少女、齐刘海双辫、大头短肢，姜黄斗篷、枣红短衣和米白裤，身份与其他角色清楚区分。 手提暖纸花灯、灯下红穗、腰间红结与辫梢玉珠已经自然连接春节和元宵。 灯笼是职业法器并兼具节庆点缀；保持现在的黄红米白比例，不添加月轮或额外灯笼。 | 保留1，待处理50 |
| 24 年轻吕洞宾 | 年轻无须剑仙，直黑发束髻、剑形发簪、深玉绿背心与腰带、米白短袍、黑裤，背剑和金葫芦可辨。 剑柄红结长穗和腰间葫芦红结为小面积春节饰物；道家身份优先。 沿用年轻吕洞宾，保留白衣层次、深玉绿和红穗，不复活已弃用的24号老者，也不强加花灯遮挡剑与葫芦。 | 保留1，待处理50 |
| 25 狮鼓护卫 | 方脸粗眉、短直硬发、壮实矮身护卫，狮头肩甲、腰鼓和太极玉扣构成独立职业轮廓。 狮鼓、结绳与红穗已具春节舞狮鼓乐气息。服装红色本来就是职业配色，米白及暗裤仍保留层次。 保留狮鼓护卫的既定红衣与软暖金狮甲；不要为统一调色把他改成与其他人物相同的玉绿袍，也不再增加红金装饰。 | 保留0，待处理51 |
| 26 桂香药婆 | 丰润年长药婆，直灰发盘髻、竹斗笠、药草背篓、靛蓝米白短袍和太极腰扣，年龄体态具有差异。 发髻与背篓黄色桂花式小花、衣角花枝纹样和局部红结，自然呼应中秋桂花及春节小饰。 药草与桂花主题已经充分，保留亲切年长造型、竹木质感和低饱和蓝白服装，不新增月兔或大红灯笼。 | 保留0，待处理51 |
| 27 墨鸢游侠 | 较修长但仍大头短身的游侠，直黑高马尾、墨灰玉绿短袍、风筝背具与佩剑，脸型和气质独立。 腰间一小束红穗、玉色系带与风筝意象为克制的迎春呼应；主体仍是清雅道家游侠。 墨灰玉绿与小红穗已经平衡；保留风筝、束发和冷静表情，不用红衣或灯笼覆盖既定职业造型。 | 保留51，待处理0 |
| 28 月兔机关师 | 齐刘海直黑短发的小机关师，紫丁香上衣、杏色短裤、玉色鞋，扳手和木工具箱清楚可辨。 兔形发夹、衣胸与工具箱月牙、少量红扣结穗已明确呼应中秋并兼顾春节。 月兔机关主题已完整；保留紫丁香与杏色的角色差异，不强制改成玉绿同款，也不追加大月盘或大量金饰。 | 保留0，待处理51 |
| 29 何仙姑 | 年轻何仙姑，黑直发盘髻、柔和心形脸、青玉淡粉莲花衣、莲花发饰及背后莲苞，仙家身份可辨。 玉珠短流苏与少量暖金莲扣形成温和装饰。莲花主要是何仙姑身份元素，不把它误记为桂花或专属中秋符号。 保留仙家莲花和清雅青粉色，不要求每人同时具备三个节日符号；额外灯笼、兔耳或月盘会削弱职业识别，因此不添加。 | 保留1，待处理50 |
| 30 韩湘子 | 年轻无须笛仙，直黑半束发和天蓝发带，天蓝云纹短袍、米白领口、藏蓝裤，腰笛与金花玉饰独立可辨。 腰间小金花簇、绿叶及玉饰对桂花/中秋作克制呼应，云纹与浅暖金边仍保持道家清雅。 保留天蓝笛仙身份与细小金花挂件，不再增加红灯笼或夸张月轮；不以预览颜色阈值代替真实植物鉴定。 | 保留51，待处理0 |

## 透明边发现与验收边界

已查看全部8张肖像和256姿势的现成接触表/方向表；另放大6张独立帧比较边缘。紫红边在发梢、帽缘、袖口等轮廓可见，正式PNG像素也存在高alpha、甚至alpha=255的紫红污染，因此不是把透明底预览颜色当作真实背景。25、26、28肖像中alpha≥128的强紫红像素分别为948、909、1616。六位人物的全部动作帧都出现同类高数量诊断命中。

27号的单份PNG最多6个零散颜色阈值命中，实看没有其他六人那样的连续紫红轮廓；该阈值用于辅助定位，不能作为零容忍的自动重绘规则。30号正式PNG此阈值命中为0。两者保留当前已完成的边缘处理。

408份实际文件全部与当前各自manifest哈希匹配；肖像、帧、条带、方向表的PNG尺寸和RGBA模式正确，64份GIF均为512×512、4帧、每帧120ms。上游原有passed记录仍作为上游验收来源保留，本次发现补充到精修待办，不据此声称已完成修复。

修复须保留画布、alpha、帧序、脚底(256,471)、姿势与服饰配件。先处理3张受影响肖像与6人共192独立帧，再重建对应60份条带/方向表和48份GIF；不重画整套角色，不增加更多节庆饰物。

本审查不是Unity/客户端运行验收，也未对64份GIF做独立动态观感验收。没有生成或编辑图像；现成JPG接触表仅为核对证据，不能冒称当前游戏截图。

## 查看证据

- **23 灯穗小使**：
  - [portrait.png](E:/work/image/qdao_chibi_roster_v11/23_lantern_courier/portrait.png)，SHA-256 `f1c80e2ce1b13d9597f4a87c715797b353b631c2263f05da77d59f7bdd9155ed`。
  - [visual-review.jpg](E:/work/image/qdao_chibi_roster_v11/23_lantern_courier/processing/visual-review.jpg)，SHA-256 `5d5972707f3707dedbada94358c7073600f9c1ed32dc98b83e5669fce311dfde`。
  - [01.png](E:/work/image/qdao_chibi_roster_v11/23_lantern_courier/walk/S/01.png)，SHA-256 `5a72d15e02e1fa3a0546e49a51886a0fb6a027ed882ca30824abff6d71ce540f`。
- **24 年轻吕洞宾**：
  - [portrait.png](E:/work/image/qdao_chibi_roster_v11/24_lu_dongbin/portrait.png)，SHA-256 `ea2228db505fbc057da4b4056d08e9bd00ddc0832921e1b37b148ac703b43989`。
  - [visual-review.jpg](E:/work/image/qdao_chibi_roster_v11/24_lu_dongbin/processing/visual-review.jpg)，SHA-256 `1d3593420ae02c4b826cdb79932ddd3629696c580b74ab4f63f4bf0db8a5313d`。
  - [01.png](E:/work/image/qdao_chibi_roster_v11/24_lu_dongbin/walk/S/01.png)，SHA-256 `fd59fdbb4f036bce3186d5ef3ba6c819db9a9fa7a2fb9d6898267531cc10d587`。
- **25 狮鼓护卫**：
  - [portrait.png](E:/work/image/qdao_chibi_roster_v11/25_lion_drum_guard/portrait.png)，SHA-256 `17802495476168c0675fd6e576be560e7f22844a1e9bfcfd225e14368a6bc4e5`。
  - [visual-review.jpg](E:/work/image/qdao_chibi_roster_v11/25_lion_drum_guard/processing/visual-review.jpg)，SHA-256 `425dd29ecb36b97cea3bb292ab53b83691fb87caa7391d00ad0dddd955553501`。
- **26 桂香药婆**：
  - [portrait.png](E:/work/image/qdao_chibi_roster_v11/26_osmanthus_healer/portrait.png)，SHA-256 `9bb854cadeb7e80a795d0fb63afade1d73cb360fe04d7a86dc7b6a3f3e9efb69`。
  - [walk-cardinal.png](E:/work/image/qdao_chibi_roster_v11/26_osmanthus_healer/walk-cardinal.png)，SHA-256 `96dff3d7f4379c880891f8b02796d8ddd109c8ff5e985446516f9248e87bd21d`。
  - [walk-diagonal.png](E:/work/image/qdao_chibi_roster_v11/26_osmanthus_healer/walk-diagonal.png)，SHA-256 `19f284753a7637813f8f018d31d25216b3b39b036b6c7a9d1e8a97bfddf944cf`。
- **27 墨鸢游侠**：
  - [portrait.png](E:/work/image/qdao_chibi_roster_v11/27_ink_kite_ranger/portrait.png)，SHA-256 `fedec64bcf625aa7b9bdc4c1a56fb0b95238fd86824375c03d24a30d7013d104`。
  - [visual-review.jpg](E:/work/image/qdao_chibi_roster_v11/27_ink_kite_ranger/processing/visual-review.jpg)，SHA-256 `6488ce52fbff93f3e84d14511b1ebc75f0d05b6596681bc9b96b06806d67c1e0`。
  - [03.png](E:/work/image/qdao_chibi_roster_v11/27_ink_kite_ranger/walk/S/03.png)，SHA-256 `ad57036b3b974d8218c58feeb49497d87db42c1fc79b0df4fe65e62628ec9160`。
- **28 月兔机关师**：
  - [portrait.png](E:/work/image/qdao_chibi_roster_v11/28_moon_rabbit_artificer/portrait.png)，SHA-256 `eafa6918753f6d0585ce271e7fbce4a9403f20a10020b937d7b54e7bf217f9da`。
  - [visual-review.jpg](E:/work/image/qdao_chibi_roster_v11/28_moon_rabbit_artificer/processing/visual-review.jpg)，SHA-256 `f95481d8a035717df223a0faaa142d29afdbacc452c9333d746704e9611d13ec`。
  - [01.png](E:/work/image/qdao_chibi_roster_v11/28_moon_rabbit_artificer/walk/S/01.png)，SHA-256 `dfa7c44eb3fa75ff3970088fcd16eadcf5b05e86a7fd3ce6251215feb0e24c36`。
- **29 何仙姑**：
  - [portrait.png](E:/work/image/qdao_chibi_roster_v11/29_he_xiangu/portrait.png)，SHA-256 `ad13960429287eaba81d33a8af49845150cd7619bb9a02bf00894af63b3c032e`。
  - [visual-review.jpg](E:/work/image/qdao_chibi_roster_v11/29_he_xiangu/processing/visual-review.jpg)，SHA-256 `0cd31a51479f2eda9b72b79512a5376c2c84182d0ca873b64ae26dcbcac035c5`。
  - [01.png](E:/work/image/qdao_chibi_roster_v11/29_he_xiangu/walk/S/01.png)，SHA-256 `07b1141b45cb6b7407ff0d2bb5c339ecbe2fdcbf441c18b2f808f8a67dd644d1`。
- **30 韩湘子**：
  - [portrait.png](E:/work/image/qdao_chibi_roster_v11/30_han_xiangzi/portrait.png)，SHA-256 `50ca931b2b4ac6e1c4e5f5b087ed1c6cf03a27e19b8648fa0fe09b7b63b70a64`。
  - [visual-review-1.jpg](E:/work/image/qdao_chibi_roster_v11/30_han_xiangzi/processing/visual-review-1.jpg)，SHA-256 `fcb1a1af067592746d4297be2bbc1ad6f49ce2ebcb6e4ede9c2f675b1fd7ceee`。
  - [visual-review-2.jpg](E:/work/image/qdao_chibi_roster_v11/30_han_xiangzi/processing/visual-review-2.jpg)，SHA-256 `20b41fa93ce4cc76e1537dec8fb194058a9b0aebcdd0260742b1822f3e7ba968`。
  - [01.png](E:/work/image/qdao_chibi_roster_v11/30_han_xiangzi/walk/S/01.png)，SHA-256 `5e550576b3fd5b50eb06d7a5356d6fedba040de1b8fc51d4f6c25eb217a49f26`。

逐文件路径、来源manifest哈希、实文件哈希、alpha哈希、处理决定和保留/待修理由均记录于[v11-style-review.json](E:/work/image/qdao_festival_refinement_20260910/reviews/v11-style-review.json)，覆盖408项，不包含已弃用的24号云鹤老人。
