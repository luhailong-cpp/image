# S01–03 头脸尺度修正结果

完成5次内置AI调用，保存5张原生1254×1254 RGBA与各自prompt/request/receipt/png.generation.json。结果仅完成头脸尺度修正；承重鞋位仍有偏差，未作整体静态通过、动态通过或客户端通过。未改选择清单及全局导出。

S01-v3、S02-v3、S03-v3的头脸已按S09-v1固定尺度重画，03→04与16→01的体积跳变改善。S01与S02的支撑腿位于画面左（解剖右腿），S03同侧中撑并抬起画面右的左腿。左手抱葫芦、右空手身份保持，无明显多余肢体。

仍未解决：三张候选的承重鞋alpha≥128下边界为1212/1211/1209，比各自旧帧低27/17/30原生像素；S09为1187。若沿用现有记录的原生地面y≈1164，新鞋位明显偏低。此数字仅作诊断，未按bbox或最低脚底做任何对齐、缩放、平移。S02承重压缩幅度也偏小；16→01头部竖向轨迹仍需播放检查。

- **01-v2.png**：rejected_static。头脸过度放大且整身脚位下移，alpha下缘1242；不能采用。 SHA256：3a51a299aa467b43a1c0257a0676a9e44d4d8cd8c26692d23cbfd80be4e1749c。

- **01-v3.png**：head_scale_corrected_grounding_unresolved。头脸与S09同档，右腿画面左前伸、左腿后折、右空臂后摆；16→01缩头问题改善。前鞋位置比旧01低27原生像素，接地未通过。 SHA256：1d1ae1d6bdc6146b239ed672dec8d3bfdb8bebbf49e9fd38ce320ae6d19a7b7d。

- **02-v2.png**：rejected_static。尺度保持但错误保留S09左腿（画面右）承重，阶段错误；不能采用。 SHA256：6ce446ac7451463cdaaf27ca49a43fc85b28beafcf8a95dba1a78b9f8963c9fc。

- **02-v3.png**：head_scale_corrected_grounding_unresolved。恢复右腿画面左承重，左腿后折，头脸尺度稳定；缓冲幅度较小，鞋位比旧02低17原生像素，接地与压缩仍未通过。 SHA256：109a3d24ca5a4b1ee40743d8c4e7bbf0079328469408ed5b267a7dd04005bb06。

- **03-v3.png**：head_scale_corrected_grounding_unresolved。右腿画面左中撑、左腿画面右前抬，右空手与左抱葫芦保持；头脸接近S04，鞋位比旧03-v2低30原生像素，接地未通过。 SHA256：3ee7d71674f670dde084492b598aafc7518e3c280dae55783fd17dd36e9e2aab。

01/02均已尝试两版，本轮不继续重试。统筹应先检查地线和根锚，再决定选用/定向修脚；不能用三张新候选直接宣称跑步完成。完整逐图结果见 scale-correction-review.json。模型与质量仅配置目标为本批Sunburst/max，实际值未确认。
