# 天音少女05：精确续作记录

本文件记录交接时的实际落盘状态。没有完成八方向，没有视觉封存，没有stage或正式接入。最后原窗口停止了新生图和导入。以同目录 HANDOFF_STATE.json 和 HANDOFF_05_SOURCE_MAP.tsv 的SHA及实际文件为准。

## 已有素材与待做

ID：05_celestial_musician_girl；common_scale固定0.84；root_px=[256,471]，alignment_version=2。
现有64张交付候选PNG：52walk +8独立idle+原肖像+3方向strip。
- S：01–16齐。
- E：01–16齐。
- N：01–16齐。
- NE：只有01/05/09/13。
- SE/SW/W/NW：各0张。
- 仍缺76张walk，其中NE12张，SE/SW/W/NW各16张。
- 全部8方向独立idle已齐，肖像从原4096完整降采样1024。
- S/E曾在新色键配置下各独立重建17张通过，数值和来源合格、视觉仍pending。记录在candidate/.../review/validation-S.json和validation-E.json；其manifest SHA是当时快照，后续N/NE增加使当前manifest不同，不能当全角色封存。
- N验证曾启动，但交接时validation-N.json不存在且进程已不在，因此N还应重新验证。不能称它已通过。
- 根窗口尚未做05最终浏览器全帧实看、完整136源重建、fresh-review/approve或Unity。

本人的candidate根：
E:/work/image/qdao_original_roster_v13/candidate/05_celestial_musician_girl
原始生成根：
E:/work/image/qdao_original_roster_v13/generation/05_celestial_musician_girl

## 形象锁定

原4096 SHA：f8cd360988a1d5d9b6aebb81d9868b5d4692aa520d7fcae1af9d525bf70e12f8。
原图来自baseline，不重新设计肖像。
紫眼、紫色大高髻和长发、浅紫莲花金珠头冠、额间花钿、紫珠耳饰；白/浅紫/金纹道袍，玉绿腰结、紫色灯笼裤、白紫小靴。
双手抱同一条扁长紫色中式琴，金色卷纹与平行琴弦。解剖右手拨琴、左手托上端。琴随身体转向，背面大部分被遮住。不要改成吉他、横笛或换手。
参考完整原图 references/05_celestial_musician_girl/original-whole-reference.jpg。
每方向原生idle整格参考在同目录 N/NE/E/SE/S/SW/W/NW-idle-wholecell.jpg（S如无该命名，可从idle原生源格提取；不可把局部腿裁图当整体生成参考）。
多方向参考一起喂图曾导致NE画成NW，最好每次只给目标方向的真实整格idle，或该方向的四个真实关键帧。

## 刚修复的重要问题：紫色衣料被色键误删

旧通用100/150色键对05部分E帧误删裤腿，源cell完整，keyed开始出现洞。证据：
- candidate/05.../review/E06-processing-inspection.jpg
- candidate/05.../review/chroma-profile-comparison.jpg
- 修复后E-purple-preserved-review.jpg、S-purple-preserved-review.jpg

已为公共pipeline添加显式 --chroma-profile purple-preserve，记录chroma_thresholds=[50,75]；默认standard仍[100,150]。verify独立读取并限制这两组参数重放；vendor、源格边界/尺度/alpha<=8规则没改。
05目前60个源记录（52walk+8idle）全部使用[50,75]，后续05每次import必须继续显式传此参数。
已用 tools/05_reprocess_chroma.py 从原始真实源格重处理当时全部40张，完成退出0，严格边界检查全部通过。不要再次运行该一次性脚本：它断言原阈值与备份不存在。
重处理前完整候选备份：history/05-before-purple-preserve-20260917。
旧00–03没有重加工；01正式publisher用新verify完整重建136旧100/150记录并与封存结果一致，已验证兼容。

## 真实源格→帧映射

最可靠的机器可读索引：HANDOFF_05_SOURCE_MAP.tsv，以及candidate/.../processing/frame-sources.json。
每批generation子目录含prompt.txt、raw.png、tool-result.json；candidate/source保留不可变副本。receipt含工具真实output_hint和raw SHA，不要编造工具结果或实际模型ID。

### S（完整）

- S-keys-v1：2×2 cells0/1/2/3 → 1/5/9/13。
- S-interval01-05-v1：cells0/1/2 → 2/3/4。
- S-interval05-09-v1：只取cells2/3 → 7/8；cells0/1腿相反，已拒用。
- S-frame06-v2：原生1×1 cell0 → 6。
- S-interval09-13-v1：cells0/1/2 → 10/11/12。
- S-interval13-01-v1：cells0/1/2 → 14/15/16。
S正面1为画面左脚领先，9为画面右脚领先；5/13抬相反脚。已看整套缩略序列，仍需正常/放大浏览器和循环实看。

### E（完整）

- E-frame01-v2 /05-v2 /09-v2 /13-v2：各原生1×1 → 对应帧。
- E-interval01-05-v2：cells0/1/2 → 2/3/4。
- E-interval05-09-v2：cells0/1/2 → 6/7/8。
- E-interval09-13-v2：cells0/1/2 → 10/11/12。
- E-interval13-01-v2：cells0/1/2 → 14/15/16。
- 早先E-keys-v1镜头过于正面三分之四，未导入，不能回用或偷偷归成SE。
E1/9外轮廓相似，但来源设计为远腿/近腿相反领先；最终必须放大看裤腿交叠、近腿遮挡、靴子深浅，不能只凭文件不同认定步态正确。E4/5抬脚幅度接近，最终播放检查是否顿挫。抠色缺口已修好。

### N（完整候选，验证尚未完成）

- N-frame01-v2 /05-v2 /09-v2 /13-v2：各1×1，对应帧。
- N-interval01-05-v2、05-09-v2、09-13-v2、13-01-v2：各cells0/1/2依次→2/3/4、6/7/8、10/11/12、14/15/16。
- N-keys-v1落地关键帧画成明显抬脚/露鞋底，整批没有导入。
N1/9新图是真正相反脚前后站位、鞋跟背面朝相机且鞋底向下；N5/13低抬膝、对侧承重。过渡全已切出，但尚未实看最终完整contact/浏览器播放。尤其检查抬脚高度是否逐帧递进而非长时间卡在同一姿势、15/16/1是否顺畅。
可用整段审阅图：review/N-full-contact-review.jpg（只生成预览，不代表已实际验收）。
原窗口最后的N verify与W参考显示调用被续接打断，不能用旧session状态推断成功。

### NE（四个关键帧）

- NE-keys-v2：2×2 cells0/1/2/3 → 1/5/9/13，已导入。
- 镜头正确为后右三分之四，已看到生成原图；近/远腿的膝盖与靴子遮挡还需随完整序列复核。
- refs：generation/.../NE-accepted-key-references 已准备。
- NE-keys-v1与另外N/NW参考混用后画成朝左，明确拒用。
- NW-keys-v1虽朝左，但接触帧抬得过高、近远腿不清楚，整批未导入。
- 不要因为N/NE/NW旧raw存在，就把它们计入交付或直接发布。

## 接手顺序和命令

在E:/work/image/qdao_original_roster_v13工作：
1. 先读S/E/N/NE当前实际图与frame-sources；查HANDOFF_05_SOURCE_MAP.tsv。
2. 对N运行方向验证，查看当前S/E/N完整序列；别重复已完成的40张重抠。
3. NE补12过渡；SE/SW/W/NW各从正确idle确定1/5/9/13再补12。每次真人工目检，错朝向/同腿循环/断道具/源格触边都真实重绘。
4. 最后8向完整后再全角色浏览器审阅与approve。

示例（占位符必须换成真实路径/映射，别原样运行）：
    python -X utf8 -B tools/verify.py --character 05_celestial_musician_girl --direction N
    python -X utf8 -B tools/pipeline.py import-walk --character 05_celestial_musician_girl --direction NE --chroma-profile purple-preserve --rows 2 --cols 2 --source-cell-indices 0,1,2 --output-frames 2,3,4 --source <真实raw> --prompt <实际prompt> --receipt <真实tool-result> --batch-id <唯一批次>
    python -X utf8 -B tools/prepare_references.py --character 05_celestial_musician_girl --direction NE --name accepted-key-references
    python -X utf8 -B tools/verify.py --character 05_celestial_musician_girl

浏览器脚本参照tools/01_browser_final_candidate.cjs与01_browser_full_sequence.cjs，复制为05专属脚本并改ID和证据路径，不覆盖01证据。头less Edge真实浏览器捕获实际canvas，检查每张加载SHA、16×30ms/480ms、暂停/逐帧/循环、normal/large、idle。
脚本通过不等于艺术通过，必须实际打开并看每方向全16帧以及1/5/9/13与15/16/1，发现问题继续image_gen重画。
