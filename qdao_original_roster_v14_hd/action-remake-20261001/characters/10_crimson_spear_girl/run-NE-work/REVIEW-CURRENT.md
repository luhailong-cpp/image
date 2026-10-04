# NE 跑步当前源选择与实审

按最新要求每帧75ms、16帧1200ms均匀播放；不分权重。当前仅选择已实际复核的负责槽，不把错误侧或低脚版本充数。

- run/NE/04 run-NE-work/run-NE-04.png：{'phase': 'LEFT midstance', 'evidence': '左腿屏左支撑底1146，右膝回折鞋底可见，双手完整。'}
- run/NE/09 run-NE-work/run-NE-09-v2.png：{'phase': 'RIGHT low airborne pre-contact', 'evidence': '右脚最低1138，共同地面1155上方约17px；是低位预触，不是高腾空。'}
- run/NE/10 generation/run-NE-02/native.png：{'phase': 'RIGHT initial contact', 'evidence': '根目录原NE02实图实际右支撑，唯一调配至10，未复制；LEFT后折。'}
- run/NE/11 run-NE-work/run-NE-11-v2.png：{'phase': 'RIGHT compression', 'evidence': '右膝屈曲、头和骨盆压低，右靴1163；LEFT后折，地面接近12。'}
- run/NE/12 run-NE-work/run-NE-12-v3.png：{'phase': 'RIGHT midstance', 'evidence': '右腿屏右支撑底1165，左膝后折鞋底可见；与04明确异侧。'}
- run/NE/13 run-NE-work/run-NE-13-v5.png：{'phase': 'RIGHT late support heel raise', 'evidence': 'v5正确RIGHT支撑/LEFT后折；右踝抬跟、前掌承重，最低1158接共同地面1155；完整枪尾右界1230。'}
- run/NE/14 run-NE-work/run-NE-14-v4.png：{'phase': 'RIGHT toe push', 'evidence': 'v4右靴足跟抬起，前掌蹬离，最低1145，比共同面高10px属离地过渡；左腿仍后折，下一段腾空。完整枪尾右界1242。'}
- run/NE/15 run-NE-work/run-NE-15.png：{'phase': 'LEFT leading short flight', 'evidence': '两膝弯曲、两靴露底并离地，最低1103，共同地面1155上方52px；不能照prompt声称100px。'}
- run/NE/16 run-NE-work/run-NE-16-v2.png：{'phase': 'LEFT terminal short flight', 'evidence': 'v2双膝弯曲、两靴真正离地，最低1102，约53px净空；与15同为短飞行高度，不虚称明显下降。左右轴顺NE，握手完整。'}

固定整方向配准：1254→860，直接合成1024时translation=(-30,150)，native虚拟根(790,1155)映射(512,942)。不逐帧最低脚对齐。完整16帧仍由统筹合并后正常/慢放复核。
