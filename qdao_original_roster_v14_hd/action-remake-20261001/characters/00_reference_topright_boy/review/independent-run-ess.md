# E / S / SE 跑步独立静态审核

按 selected-new.json 的当前48帧审核；实际查看三方向contact页及26张重点原生PNG，未播放浏览器/GIF，未进行动态或客户端验收。S03/11/12、SE04/11/12/15均按当前v2核实；完整路径与SHA见同名JSON。

结论：1项确定静态必修，3项动态核对。未见明确多余肢体或葫芦换手；S/SE左右腿交替和右空手相反摆向可辨。

## ESS-01 · S向前后三帧与后半循环头脸尺度不一致，16→01有缩头跳变

分类：confirmed_static_must_fix。

同为1254×1254原生画布。S01/S03的耳到耳脸宽、两眼间距及头颅体积小于S04及S09/S11/S12/S13/S14/S16；S16→S01中，不只是头部上下位移，脸宽和眼间距也一起缩小。目测约一成，属人工估计，不是自动分割测量。

相邻帧和首尾接续发生固定部位的体积变化，不能用支撑压低、腿脚透视或正常腾空解释。正常播放是否明显尚待确认，但静态尺度不一致本身已确认。

建议：以选定S方向母版统一头颅、耳脸与眼间距的实际体积，保留两腿交替、右空手反向摆臂以及左手抱葫芦；重画尺度偏离部分，勿逐帧缩放整图或用最低脚底对齐。优先并排修验03→04和16→01，再回看04–16是否属于同一档尺度。

对应当前源图：

- generation/run/S/16-v1.png — SHA256 21f2859c7caad544fc2715bd7eac7c8ae6d69c8543e316f61ba258ee1a4a1908
- generation/run/S/01-v1.png — SHA256 566fabefbf11a4f4ec18baeae44398e42210212ffc5f592ae837a60544f82633
- generation/run/S/03-v2.png — SHA256 1922617d128ea9b598c9d6d5e0b3adcc4865345d85add9e172408645ded0ce24
- generation/run/S/04-v1.png — SHA256 b3dd9e5bd667099a797171ab78fc302c57d90d59863dd1d22a27c85d3878c116

## ESS-02 · E向异侧承重和10→11右臂过中线时机需跟踪确认

分类：dynamic_confirmation_needed。

E01与E09前后腿轮廓非常接近；上半/下半循环右空手确实分别后摆/前摆，但宽松裤腿遮挡不足以仅凭关键帧明确证明每一步的解剖左右身份。E11中撑时右拳已明显落到肩后，10→11跨度大。未把这些读图歧义写成确定换腿错误。

建议：逐帧跟踪同一大腿从髋部到鞋的连续遮挡；01右脚、09左脚接地必须清楚。若10→11明显甩臂跳变，让11右上臂经过躯干旁的中间姿态，12再到后摆；左手始终稳抱葫芦。

对应当前源图：

- generation/run/E/01-v5.png — SHA256 0335d08d84cd367c85a43fb72dd69980a45befd970d9ab1de1a1758a315b4dc6
- generation/run/E/09-v4.png — SHA256 7e51047c8ca0ad07087dbfeb0834cad4389a3a80d6d74f5eb5c52c388625bb01
- generation/run/E/10-v1.png — SHA256 8ca326eabe532d21811444e76bf4177c661707c74a4e4157df0d2dfd87468d43
- generation/run/E/11-v1.png — SHA256 81778ac672cd810d8a87fca17147e3b2c5001ee025981f6926a7678ab644a1d4

## ESS-03 · 接触—缓冲—蹬地需带统一地面检查承重

分类：dynamic_confirmation_needed。

三向都能读出接触、异侧膝前送和后脚蹬地的意图。04/12的后鞋均接近末端触地姿态；透明原图没有地面证据，SE04前伸鞋较低且伸得较直，单帧看有跨步腾空感。未把双脚不同屏幕高度直接当作错误。

建议：在统一根锚和地线下比较640/720/800ms，逐帧确认01/09接触、02/10屈膝承重、03/11压低中撑，04/12由后脚趾推出后才进入05/13腾空。若蹬地帧悬空，修后脚踝/鞋尖与骨盆运动，不能将每帧整体贴地。SE04如过早伸直前腿，保留前膝抬起并收小腿，到后续腾空再伸出。

对应当前源图：

- generation/run/E/04-v2.png — SHA256 b3b083b2f528ac84d861ae2dd3268d943a4b1241512b81d9c33357eb86ddae2d
- generation/run/E/12-v1.png — SHA256 3c07b0132dd6eb438341468a453ffaa56333b28bf9de45b03f7a8b80f99c1860
- generation/run/S/04-v1.png — SHA256 b3dd9e5bd667099a797171ab78fc302c57d90d59863dd1d22a27c85d3878c116
- generation/run/S/12-v2.png — SHA256 4ca8c494e18a2f5d8157dacff365e507f5124ed26190f99ac91b42143ae8d829
- generation/run/SE/04-v2.png — SHA256 14b45aedfb21410e688fbec58d4ea0802b40db36db01ff56b159154eb8e64bd7
- generation/run/SE/12-v2.png — SHA256 22d362861fad2607e621eb48c14b412682aefe7ec3cd17b1e538ecc1bfd9e579

## ESS-04 · E/SE首尾的落脚角度与速度未获动态验收

分类：dynamic_confirmation_needed。

E16前鞋翘起而E01趋平，SE16和SE01几乎同一右脚前伸轮廓；静态未见必须修的换手、多腿或左右颠倒。末帧停顿、落脚滑动、身位小跳不能靠contact页排除。

建议：循环连续播放至少数圈，再慢速逐帧16→01→02；确认预接触到脚掌压实与髋部通过连贯，避免16和01重复停住。不得因为图像相似就直接判为复制或拒稿。

对应当前源图：

- generation/run/E/16-v2.png — SHA256 a281ecafc35e4dbc8b963aedbcd7f7b89c76bd205faef6a97e32baeb7fa21319
- generation/run/E/01-v5.png — SHA256 0335d08d84cd367c85a43fb72dd69980a45befd970d9ab1de1a1758a315b4dc6
- generation/run/SE/15-v2.png — SHA256 11ecef993be36db9c547aa19ea275c02fd14047a757d020740cf4849d5d06703
- generation/run/SE/16-v1.png — SHA256 c59fa8c63fa78fecae7fd6ce03169c7ed6c2ef0320da5d1cdd00761e7354a75f
- generation/run/SE/01-v4.png — SHA256 edc2a92214cb771efaf04c7db80f0efb28bf641683258adaa5f533c98d5049a9

旧phase-plan只用于动作相位，480ms不视为当前正常节奏。待在640/720/800ms预览里完成承重、脚滑、头身运动和16→01检查。体积约一成是人工估计，未宣称分割测量。审核没有修改PNG、选择清单或导出。
