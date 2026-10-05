import pathlib,json,hashlib,datetime
OUT=pathlib.Path(__file__).resolve().parent
snap=json.loads((OUT/'snapshot.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
changes=[{'action':f['action'],'direction':f['direction'],'frame':f['frame'],'reviewedSha':f['sha256'],'currentSha':sha(f['path'])} for f in snap['frames'] if sha(f['path'])!=f['sha256']]
findings=[
 {'severity':'repair','action':'run','directions':['E','W'],'frames':{'E':['03→04','11→12'],'W':['03→04','10→11']},'finding':'胸前/背肩视角突换，卷轴和毛笔近远侧与肩线同时交换；不像仅在行进方向内摆臂。四组相邻过渡均单帧放大确认。','scope':'调整这些过渡附近肩—肘—腕和道具的连续轨迹，不据此重画整方向。'},
 {'severity':'repair','action':'cast','directions':['E'],'frames':{'E':['02→03→04']},'finding':'03持笔手降至耳侧、毛笔位于头旁后方，02在脸前竖举、04又在脸前斜举，孤立折返。03原尺寸放大确认。'},
 {'severity':'known_pending_repair','action':'cast','directions':['W'],'frames':{'W':['03','08']},'finding':'当前03屏幕右方靴头突然朝镜头；08相对07/09突然宽蹲、笔尾穗接近腕侧。与角色窗口已在修的定位一致，本审查结束仍未检测到新PNG。'},
 {'severity':'uncertain_axis','action':'hit','directions':['E'],'frames':{'E':['01–06']},'finding':'屏幕左方近侧靴头持续偏向镜头，另一靴更向E；严格同一行进轴的微外撇需角色窗口复核。01放大后仍有三分之四透视解释，髋被袍遮挡，不足以直接断定整段腿链错误。'},
 {'severity':'uncertain_axis','action':'attack','directions':['W'],'frames':{'W':['04–06']},'finding':'后方靴头持续偏镜头、前靴向W；宽蹲时小腿与靴头关系需按严格同轴复核，髋遮挡，未强判。'},
 {'severity':'retain','action':'run','directions':['SE'],'frames':{'SE':['04']},'finding':'小图中卷轴似乎消失，原尺寸确认卷轴端与握持手仍在后肩；属于遮挡，保留。'},
 {'severity':'retain','action':'run','directions':['N','NE','E','SE','S','SW','W','NW'],'finding':'完整全身与脚部联系表均已逐组实看。没有把正常抬脚/后蹬露底当外撇。除以上具体问题/待核项，未确认额外靴头突然横转或手指脱离笔杆的硬伤；这不是动态或全解剖通过结论。'}
]
audit={'character':'17_ghost_script_calligrapher_boy','finishedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewSnapshotAtUtc':snap['atUtc'],'manifestPath':snap['manifestPath'],'reviewedManifestSha256':snap['manifestSha256'],'finishManifestSha256':sha(snap['manifestPath']),'groupsViewed':14,'framesViewed':196,'feetSheetsViewed':14,'allCurrentPngHashesMatchedPriorQaAtReview':all(f['priorQaMatch'] for f in snap['frames']),'manifestMismatchesAtReview':[f for f in snap['frames'] if not f['manifestMatch']],'changedPngDuringReview':changes,'scope':'独立静态全身+脚部审查；未播放运行时动画，未见参照视频，长袍遮挡髋不能猜解剖左右；无角色目录写入、无生图。','groups':[{'action':g['action'],'direction':g['direction'],'count':g['count'],'fullViewed':True,'feetViewed':True,'sheetPath':g['sheetPath']} for g in snap['groups']],'singleFramesViewed':['run/E03','run/E04','run/E11','run/E12','run/W03','run/W04','run/W10','run/W11','run/SE04','run/NE14','cast/E03','cast/W03','cast/W08','hit/E01'],'findings':findings}
(OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
body='''# 17 灵篆书生独立静态审查

实际覆盖14/14组、196/196当前正式PNG；14张全身、14张脚部联系表均实看。来源由当前manifest的runtime文件逐张SHA验证，与C组旧QA所记录SHA全部一致，196/196 manifest SHA匹配。完整逐帧证据见snapshot.json；末次复验见audit.json。维持跑步16×75ms与受击6/普攻12/施法16帧。

| 范围 | 具体结论 |
| --- | --- |
| run E03→04、E11→12；W03→04、W10→11 | **需修**：胸前/背肩视角突换，道具近远侧和肩线同时交换。四对均放大原尺寸确认。修附近肩肘腕与道具过渡，不自动全方向重画。 |
| cast E02→03→04 | **需修**：03毛笔突然移到头侧后方、持笔手降到耳侧，04返回脸前斜举，手臂轨迹孤立折返。 |
| cast W03、W08 | 与角色窗在修项目一致：03后靴突然朝镜头；08突然宽蹲且穗偏腕。结束SHA仍是旧图，等待窗口新图后复验，不宣称已修。 |
| hit E01–06 | **同轴待核**：近侧靴头持续偏镜头、另一靴向E；存在三分之四透视解释，长袍遮髋，不足以强判整段腿链错误。 |
| attack W04–06 | **同轴待核**：后靴偏镜头、前靴向W，宽蹲时小腿与靴头关系需严格复核；髋遮挡，不直接要求重画。 |
| run SE04 | 原尺寸卷轴仍在后肩，可见端头与手，遮挡正常，保留。 |
| 其余已见帧 | 未确认额外靴头突然横转或脱握硬伤；正常屈膝/后蹬露底保留。未播放实时动画、未看参照视频，长袍遮髋段仍无法宣称整条髋膝踝链通过。 |

不是成品通过：需要修上述明确过渡，等cast/W03、08新素材复验，并在1200ms运行时检查接地停留与循环。静态足底露出并不单独证明外撇或没有接地。
'''
body+='\n末次复验PNG变化：'+str(len(changes))+'；manifest是否变化：'+str(audit['reviewedManifestSha256']!=audit['finishManifestSha256'])+'。\n'
(OUT/'REVIEW.md').write_text(body,encoding='utf-8')
print(json.dumps({'groupsViewed':14,'framesViewed':196,'feetSheetsViewed':14,'changedPngDuringReview':changes,'manifestChanged':audit['reviewedManifestSha256']!=audit['finishManifestSha256']},ensure_ascii=False))
