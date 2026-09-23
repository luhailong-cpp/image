请恢复制作06_thunder_caster_boy（雷法少年）的角色移动图。

工作目录：D:\luyuan\wuxingqitan\image。
先读AGENTS.md、designs/README.md、config/image-generation.json、docs/IMAGE_MODEL_POLICY.md、README接手说明，以及：
- qdao_original_roster_v14_hd/HANDOFF_20260919_PAUSED.md（9月20日保留15名范围优先；用户已恢复，不继续旧暂停指令）
- qdao_original_roster_v14_hd/mixed-preparation/client-integration-20260921/RETAINED_ROSTER_STATUS.md
- qdao_original_roster_v14_hd/recovery-20260921/README.md
检查本角色最新交接和当前文件，以实时库存为准，避免重复其他窗口已完成工作。旧E:/work路径必须逐文件核实到本机D路径；历史请求/回执不伪改。

本窗口只完成指定的一名角色，不自动继续下一名。先核查原图、已有帧和未导入raw，处理残边和错误步态，再补缺帧。
每名固定8方向N/NE/E/SE/S/SW/W/NW，每方向16张真实行走帧（128张），另8张独立站立图。新动作原生完整单帧至少1024×1024，交付1024×1024透明PNG。保持原角色身份、服装装备、人物比例和脚底锚点；风格参考沿用designs中相近用途的已确认成图，不改变本角色形象。禁止复制、镜像、插值、扭曲或平移同姿势凑帧。已有旧动作原字节保留，旧512不放大冒充新高清。
优先使用内置GPT Image2.5，2.0也接受。入口不披露实际型号/质量时如实记录host-managed/unverified，不因确认型号反复停工，不调用收费API。逐图保存真实raw、精确prompt、请求/回执、实际尺寸、SHA和来源；不以提示词或配置目标冒充实际返回型号。
制作30毫秒/帧（480毫秒/圈）的八向循环预览，逐帧检查交替迈腿、支撑脚、比例、残边和15→16→01→02首尾衔接，深浅底/正常与放大均检查。先完成素材与离线预览验收，再写清本角色交接、选用稿/拒稿、准确库存及剩余问题；文件齐全不等于美术通过，不宣称未做的Unity/正式客户端验收。
00–03和已有旧动作保留；只在保留15名范围工作，不恢复11/12/13/16/18/19/21/22。不覆盖其他窗口工作，不做Git提交、推送或清理。完成本角色后告知我可以开下一窗口。

本角色接手快照：
canonical旧S16walk+8idle及E01/02/03/05/09五张HD，共21walk+8idle；另外E04/06/13的原生raw已存在，并在recovery-20260921/06-audit隔离处理，先核查使用，不要重复生图。计入这3张后24walk、还缺104walk：E07/08/10/11/12/14/15/16，另N/NE/SE/SW/W/NW各16张。先读recovery-20260921/06-audit/README.md与generation/06_thunder_caster_boy/PAUSED_HANDOFF_20260919.md（均相对qdao_original_roster_v14_hd）。E03紫边待修；E09只选第二稿，第一稿拒收。原生1254，固定scale .88；import_pending.py需先读并核验当前库存再决定是否使用。

本机已核实原始肖像：
D:\luyuan\wuxingqitan\image\q_daoist_character_pack_4096\06_thunder_caster_boy_transparent_4096.png
