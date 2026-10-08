# 兰仙镇春节 r09_c10

交付为完整 4096 核心图、4326 外扩图与1254总览的合格候选；正式美术验收、客户端验证和整城完成均为 false。

仅将已有花坛压顶与顶部 halo 中的极小帽面改为朱红漆面、原倒角细金色；桥梁、白石、植被、水面与其他非表面像素按共享日景保留。没有新增物件、占地或通行变化，没有放大、几何变形或整块4K AI 重绘。两次内置 image_gen 实际原生输出均为1254×1254，再按同坐标实体遮罩合成。

- 正式候选：[core4096.png](selected/core4096.png)、[extended4326.png](selected/extended4326.png)、[preview1254.png](selected/preview1254.png)
- [交付清单](selected/delivery.manifest.json)、[加工记录](processing.json)、[视觉复查](qa/final-visual-review.json)
- [南侧压顶逐图模型记录](native/southwest-cap1254.png.generation.json)、[北侧帽面逐图模型记录](native/northwest-cap1254.png.generation.json)
- [南侧完整提示词](southwest-cap.prompt.txt)、[北侧完整提示词](northwest-cap.prompt.txt)、对应 receipt JSON 保存工具回执。
- [配置快照](config-snapshot.json)、[官方核对](official-verification.json)、[共享结构来源](shared-geometry/provenance.json)

实际型号／质量：宿主管理，工具未披露，均记为 null；配置目标不代替实际返回证据。派生交付图旁 *.generation.json 分别索引来源链。

北侧四段正式接缝及两角已按1:1查看；下方两角是本块原像素检查，未代表尚未完成的邻块接缝通过。继承的日景内部接缝沿用既有验证。源图与过程 PNG 清理后，文字中旧路径仅作为来源身份，不能宣称仍可读取或完全重建。

已完成清理：删除本块39张来源快照、过程稿与QA裁图，保留6张成品/技术遮罩。全部文字记录保留；[清理清单](selected/cleanup.manifest.json)与[清理后验证](selected/post-cleanup-verification.json)。独立复核发现的781个叶片遮罩像素已恢复，最终为0个源绿叶像素变化。
