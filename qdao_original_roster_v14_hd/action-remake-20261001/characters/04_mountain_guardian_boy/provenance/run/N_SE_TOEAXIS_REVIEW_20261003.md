# 山岳守卫 N / SE 脚向复核与定点修正

记录时间：2026-10-03T18:32:52.011568+00:00

按自身足跟到趾尖方向与小腿自然对齐判断；07仅作视觉对照，不是整套或某方向已通过金标。保留不外撇帧，不缩小两腿间距代替修脚向。

本轮完成SE第01、02、03、11、12、13、14、15、16帧局部AI脚向修正；N16帧、SE04–10保留。全部新图实际查看后才register替换；每次实际附上当前目标、07对应正式帧、04画像、04对应idle与designs画法共5张参考。

N02有一次试验返回，但没有可确认的脚向改善，未替换正式帧。不能以鞋面装饰外观单独判定鞋头朝向；原N脚掌轴线未见明显两侧外撇，故保留。

SE修正集中在杖侧前靴：原鞋尖偏向屏下/左或正对镜头，现脚跟上左→鞋尖右下，朝向与SE移动相容。上身、膝位和腿间距保留，未通过挤拢双腿掩盖脚向。01–03的承重及14–16→01循环需按新预览动态复核。

N/SE连图和全部试播GIF已重建。grounded720使用[40,70,60,40,40,30,30,50]×2=720ms，grounded_slow=2880ms；实际GIF时长与新正式来源SHA已核对。浏览器动态观感由根窗口继续，本文件不宣称客户端接入。

9张替换正式PNG均1024 RGBA、原生1254 RGBA。内置模型和质量实测未确认；目标为GPT Image 2.5 Sunburst/max。原生、未采用N测试稿、逐图文字证据全部保留。

| 槽位 | 新正式SHA256 | 原生SHA256 |
| --- | --- | --- |
| frames/run/SE/frame_01.png | `b7292a1c1527f89abf2c58680a24e4fdfa2e80c07880300a9a9cc346b679137c` | `52e80a13896782de70cb9af71744aa20e66ea8b9546bf3e64dae17a9a8735e72` |
| frames/run/SE/frame_02.png | `ef79055d2dfdb4532ed1a70e92aac057560b74472c4a0644d0fb72ca364f3129` | `a7afdbd0e111f51fdac6da5d5b18eb5cca83a0cb917fda50b5f3f3f5d677dc24` |
| frames/run/SE/frame_03.png | `fd7e3e74bbabf68028562c7dc981084ae1d3c1b00133878c6175051c75bb796b` | `92e0160e6016469801c718236815c585d1185d9b68a70d45a996b6faa8bcf7fc` |
| frames/run/SE/frame_11.png | `077bc0f7238718ee43f8abad44d47daf3169f0c103dcf7f9178144a7246765c1` | `f3e2c38ab8611f674ab6ddcaff63c3a82a2968384bdc5358cc4d39bd130cc239` |
| frames/run/SE/frame_12.png | `9215686d9a389f0084aed128f10c36d069b064cf18bda4fcaa423c5601e45b83` | `9f1387e453cecff23464bfff5949812d5cebb22106acfc0b7c940bee24562f50` |
| frames/run/SE/frame_13.png | `e35117fd5818ead8670655b67402468b7dabbea945513271718e49ecd388f1a3` | `c0708db668d393a981fdd67232e70a87077982cae466b0f2a80eaa180489ae58` |
| frames/run/SE/frame_14.png | `184ff8636b610934575029b97ad7947a39ffa50a8a00144cb70d6ca13ce19acb` | `eda62b4bb863aa481423b74ef4e05f5f0f216b02a708d116b48a052ac3018056` |
| frames/run/SE/frame_15.png | `b0cbfdf84801387b4035f2f31d3329684c1f270e914ea6daadcae6313d647fad` | `79ff7d3a6cabe4c126bac2938fe13ead8259e2ec8ab6b57d82fe6a6ca691083f` |
| frames/run/SE/frame_16.png | `e4202a1707f34e550f93549aad668a74fcbd9dd833f21e3b21589f93f76b252d` | `e95654012af9bd79d07a497e60522bbbcf502aa274f8cffce3f123dca5eb494d` |

[逐帧保留/替换与来源JSON](N_SE_toeaxis_review_20261003.json)
