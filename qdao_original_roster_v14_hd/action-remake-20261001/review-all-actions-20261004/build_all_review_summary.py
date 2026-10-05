import collections,datetime,hashlib,json
from pathlib import Path

BASE=Path('D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001')
OUT=BASE/'review-all-actions-20261004'
roster=json.loads((BASE/'roster.json').read_text(encoding='utf-8'))
inventory=json.loads((OUT/'inventory-summary.json').read_text(encoding='utf-8'))
inv={r['id']:r for r in inventory['characters']}
def read(rel):
    p=OUT/rel
    return json.loads(p.read_text(encoding='utf-8')) if p.is_file() else None
def evidence(rel):
    p=OUT/rel
    return dict(path=p.as_posix(),exists=p.is_file(),sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
A=read('group-a/audit.json'); C={cid:read(f'group-c/{cid}/static-review.json') for cid in ['10_crimson_spear_girl','14_short_hair_snow_summoner_girl']}
R15=read('15-static-review-20261005.json');R20=read('20-static-review-20261005.json');A17=read('group-a-17/audit.json')
B=read('group-b/review.json') or read('group-b/static-review.json') or read('group-b/audit.json')
Bchanges=read('group-b/concurrent-changes.json')
prelim=read('preliminary-findings-20261005.json')
rows=[]
summary_text={
'00_reference_topright_boy':'已见全部组；未确认新的明显横向外撇或断手，保持正确帧；接地推进及循环待正常速度连播。',
'01_ice_sword_girl':'NE03→04→05、E02→03→04、SW04→05剑臂/胸肩转角待连播；S04/05/06露底原误判已排除；肖像左手蓝符必须保留。',
'02_fire_talisman_boy':'run/E03→04及cast/E03→04扇/铃前后极值切换待核；保持自然后蹬；窗口正在修图，清单SHA同步未完成。',
'03_lotus_healer_girl':'确认run/N03灯孤立降至髋侧、N04回胸，优先修03邻接；SE10→11→12、W03→04灯/肘腕待连播；窗口另报SE03足轴局修中。',
'04_mountain_guardian_boy':'确认run/W03→04、10→11胸背/盾近远侧突换；NW03→04→05杖手腰侧至过肩待平顺。窗口修图中；快照21个清单SHA不一致使用实际PNG。',
'05_celestial_musician_girl':'已实际看14组；N10→11→12起伏与E/W04→05支撑位置变化待连播；部分新修图追加缩略图目检仅覆盖其新图。',
'06_thunder_caster_boy':'已实际看14组；暂未确认新的横向外翻或持手交换；袍袖遮关节需注明；窗口部分新修图尚待清单SHA同步。',
'07_moon_shadow_assassin_girl':'cast/W06→07高低双刀手在一帧内交换，持手数量仍正确，需现有施法速度连播核定过渡；不得沿用“全部方向已正确”旧判断。',
'08_alchemy_prodigy_boy':'已实际看14组；NW07→08提前换足原疑已排除：同足段跨16/01→02/03→04/05→06/07，08换足合理；窗口自报E02持瓶手过渡修中。',
'09_bamboo_archer_girl':'确认run/NW01/02对03/04、10→11、15支撑腿身份变化与现行交接相位冲突，已单帧核对NW10/11；先追踪真解剖足及相位/顺序。NE03→04靴型、E09→10弓角待连播；1张并发新图仅追加缩略图目检。',
'10_crimson_spear_girl':'NE03、09→10及NW10→11→12衔接待连播；E/W04→05、12→13换足原猜测降为解剖身份待追踪，不能凭最低鞋或前后位置强制重排；暂未确认持枪脱握。',
'14_short_hair_snow_summoner_girl':'SE02/03/04支撑靴轻外撇待同轴核定，可能有SE透视成分；NW11抬跟露底未证横扭；3张并发新图已单帧重看，白狐/右手晶体未确认硬伤。',
'15_water_dragon_scholar_boy':'N10→11、E03→04、W03→04、NW02→03扇/肩身侧过渡待连播；attack/W03并发新图已单帧补看；支撑相位跨循环边界，禁止强制01–08模板。',
'17_ghost_script_calligrapher_boy':'确认run E03→04、E11→12、W03→04、W10→11胸背/道具近远侧突换与cast/E03毛笔孤立折返；cast/W03、08窗口在修；hit/E及attack/W04–06持续轻外撇待核。',
'20_star_formation_master_girl':'NE06→07/08鞋轴变化待区分外扭与自然抬跟；E/W/SW换足猜测撤回确定性，按真实解剖追踪；三卡/星盘手持未确认新硬伤。'
}
for role in roster:
    cid=role['id'];item=dict(id=cid,name=role['name'],inventory=inv[cid],reviewedGroups=0,reviewedFrames=0,reviewStatus='pending',evidence=[],confirmedRepairs=[],pendingChecks=[],excludedMisreadings=[],concurrentSourceChanges=[],summary=summary_text[cid],dynamicAcceptance=False,userAcceptance=False)
    if cid in A['characters']:
        v=A['characters'][cid];item.update(reviewedGroups=v['viewedGroupCount'],reviewedFrames=v['viewedFrameCount'],reviewStatus='static_snapshot_review_complete',confirmedRepairs=v['definitePoseFailures'],pendingChecks=v['followups'],concurrentSourceChanges=v['pngChangedDuringReview'],sourceVersionLimits=v['observedLimits'])
        item['evidence']=[evidence('group-a/audit.json'),evidence('group-a/snapshot.json'),evidence('group-a/REVIEW.md')]
    elif cid.startswith(('05_','06_','07_','08_','09_')):
        # Human-readable coordination evidence: root explicitly confirmed all5 roles/980 frames actually viewed.
        # Do not infer coverage from inventory or staticViewed's initial false value.
        item.update(reviewedGroups=14,reviewedFrames=196,reviewStatus='review_complete_final_report_pending',coverageAuthority='root direct coordination message: B actually reviewed70 groups/980 frames; formal report pending at initial compilation')
        item['evidence']=[evidence('group-b/source-evidence.json'),evidence('group-b/concurrent-changes.json')]
        if B:
            item['reviewStatus']='static_snapshot_review_complete'
            bmap=B.get('characters',{})
            if isinstance(bmap,list):bmap={r.get('id',r.get('character')):r for r in bmap}
            bv=bmap.get(cid,{})
            item['groupBFinalReport']=bv
            item['reviewedGroups']=len(bv.get('viewedGroups',[]))
            item['reviewedFrames']=bv.get('viewedFrames',0)
            item['coverageAuthority']='group-b formal audit: actually viewed source snapshot groups and frames'
            item['confirmedRepairs']=[f for f in B.get('findings',[]) if f.get('character')==cid and f.get('severity')=='confirmed_spec_mismatch']
            item['pendingChecks']=[f for f in B.get('findings',[]) if f.get('character')==cid and f.get('severity')!='confirmed_spec_mismatch']
            for rel in ['group-b/review.json','group-b/static-review.json','group-b/audit.json','group-b/REVIEW.md']:
                if (OUT/rel).is_file():item['evidence'].append(evidence(rel))
            item['evidence'].sort(key=lambda e:'source-evidence' in e['path'] or 'concurrent-changes' in e['path'])
        if Bchanges:item['concurrentSourceChanges']=[r for r in Bchanges['changedSinceViewedSnapshot'] if r['character']==cid]
    elif cid in C:
        v=C[cid];item.update(reviewedGroups=len(v['coverage']),reviewedFrames=v['inspectedFrames'],reviewStatus='static_snapshot_review_complete',pendingChecks=v['findings'],concurrentSourceChanges=v['changedSinceContact'])
        item['evidence']=[evidence(f'group-c/{cid}/static-review.json'),evidence('group-c/source-evidence.json')]
        item['versionReinspection']=v.get('latestChangedFramesActuallyViewed',[])
    elif cid=='15_water_dragon_scholar_boy' and R15:
        item.update(reviewedGroups=R15['static_groups_reviewed'],reviewedFrames=R15['static_frames_reviewed'],reviewStatus='static_snapshot_review_complete',confirmedRepairs=R15['confirmed_additional_art_errors'],pendingChecks=R15['dynamic_checks_dispatched'],concurrentSourceChanges=R15['source_changed_after_snapshot'],versionReinspection=R15.get('changed_frame_reinspection',[]))
        item['evidence']=[evidence('15-static-review-20261005.json'),evidence('root-15/source-evidence.json')]
    elif cid=='17_ghost_script_calligrapher_boy' and A17:
        item.update(reviewedGroups=A17['groupsViewed'],reviewedFrames=A17['framesViewed'],reviewStatus='static_snapshot_review_complete',confirmedRepairs=[f for f in A17['findings'] if f['severity']=='repair'],pendingChecks=[f for f in A17['findings'] if f['severity'] in ['uncertain_axis','known_pending_repair']],excludedMisreadings=[f for f in A17['findings'] if f['severity']=='retain'],concurrentSourceChanges=A17['changedPngDuringReview'])
        item['evidence']=[evidence('group-a-17/audit.json'),evidence('group-a-17/snapshot.json'),evidence('group-a-17/REVIEW.md')]
    elif cid=='20_star_formation_master_girl' and R20:
        item.update(reviewedGroups=len(R20['reviewed_groups']),reviewedFrames=R20['reviewed_frame_count'],reviewStatus='static_snapshot_review_complete',pendingChecks=R20['observations'],concurrentSourceChanges=R20['changed_since_qa_snapshot'])
        item['evidence']=[evidence('20-static-review-20261005.json'),evidence('group-c/source-evidence.json')]
    if cid=='08_alchemy_prodigy_boy':item['excludedMisreadings'].append(dict(sequence='run/NW',transition='07→08',status='resolved_normal_support_boundary',actualPairs=['16/01','02/03','04/05','06/07'],note='08正常换足；不能强制01–08支撑模板'))
    if cid in ['10_crimson_spear_girl','20_star_formation_master_girl']:item['excludedMisreadings'].append(dict(status='withdrawn_deterministic_support_switch_claim',note='低脚/屏幕前后位置不足以确定解剖足身份。保留正确顺序并实际追踪；当前仅作为待核。'))
    rows.append(item)
totals=dict(expectedCharacters=15,expectedGroups=210,expectedFrames=2940,inventoryCharacters=len(rows),inventoryFrames=sum(r['inventory']['frames'] for r in rows),actualStaticCharacters=sum(r['reviewedFrames']>0 for r in rows),actualStaticGroups=sum(r['reviewedGroups'] for r in rows),actualStaticFrames=sum(r['reviewedFrames'] for r in rows),formalReportPending=[r['id'] for r in rows if r['reviewStatus'].endswith('pending')],coverageDoesNotMeanFinalArtPass=True)
assert totals['inventoryFrames']==2940
assert totals['actualStaticGroups']<=210 and totals['actualStaticFrames']<=2940
assert len({r['id'] for r in rows})==15
for row in rows:
    assert row['reviewedGroups']<=14 and row['reviewedFrames']<=196
    assert all(e['exists'] for e in row['evidence'])
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
report=dict(schemaVersion=1,builtAtUTC=now,scope='Coordinator roll-up of independently actually viewed static PNG sequences; all count claims are source-specific and version-bound. No new dynamic or user acceptance claimed.',timing={'run':{'framesPerDirection':16,'frameMs':75,'cycleMs':1200,'directions':['N','NE','E','SE','S','SW','W','NW']},'hit':{'framesPerDirection':6,'frameMs':40,'directions':['E','W']},'attack':{'framesPerDirection':12,'frameMs':30,'directions':['E','W']},'cast':{'framesPerDirection':16,'frameMs':45,'directions':['E','W']}},groundingRule='Same anatomical support foot progresses through four relative contact positions, two independent successive poses per position; phase may cross16→01. No duplicated frames/interpolation/forced01–08 indexing.',alignmentRule='Hip→knee→ankle→foot palm remain in same forward motion plane; natural knee bend and toe-off pitch retained. Shoe yaw away from the limb plane must be corrected even if smooth.',totals=totals,characters=rows,knownWindowRepairs=prelim.get('window_reported_repairs',[]),centralPreviewTechnicalSnapshot={'reportingAuthority':'root direct coordination message at compilation','characters':15,'runDirections':120,'runtimeRunPNG':1920,'manifestSHAInconsistencies':{'02_fire_talisman_boy':12,'04_mountain_guardian_boy':23,'06_thunder_caster_boy':2,'09_bamboo_archer_girl':1},'totalManifestSHAInconsistencies':38,'interpretation':'Windows are writing revisions and manifests may temporarily lag; these are technical source alignment issues, not a blanket pass/fail on artwork. Root sent end-of-task synchronization instructions. No new full filesystem rehash performed for this roll-up.'},limitations=['Static snapshot coverage differs from current ongoing revision coverage. New SHA changes require reinspection; old acceptance is not inherited.','Reviewed2940 snapshot frames does not mean all15 current characters are fully fixed or dynamically accepted.','Occluded hip/knee/hand joints cannot be declared completely visible from contacts.','No other-machine uncommitted content, character PNG edits, new generation, git mutation or client integration performed by coordinator.'])
(OUT/'all-characters-static-review-20261005.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 全角色动作独立静态复核汇总','',f'汇总时刻：{now}。实际所见范围为 **{totals["actualStaticCharacters"]}个角色、{totals["actualStaticGroups"]}组、{totals["actualStaticFrames"]}张快照PNG**。库存目标为15个角色，每个14组、196张，共210组、2940张；数量齐全不能代替美术或动态通过。','', '跑步八方向保持16×75ms=1200ms；受击E/W各6帧×40ms，普攻各12帧×30ms，施法各16帧×45ms。支撑同一只脚沿前落、身下、后侧、蹬离四个相对位置推进，每个位置两张独立连续姿态。相位允许跨16→01，禁止机械套01–08模板。','', '髋、大腿、膝、小腿、踝与脚掌保持同一行进平面；保留自然屈膝和抬跟。持续轻外撇也须核对。单纯露底、最低脚位置变化或衣袍遮挡不能单独证明横扭、换足或缺手。','', '|角色|实际静态覆盖|确认/待核/保留范围|审阅证据|','|---|---|---|---|']
for row in rows:
    e=row['evidence'][0]['path'];label='审阅报告' if 'source-evidence' not in e else '来源快照（正式报告待补）'
    lines.append(f'|{row["id"][:2]} {row["name"]}|{row["reviewedGroups"]}/14组，{row["reviewedFrames"]}/196张|{row["summary"]}|[{label}]({e})|')
lines.extend(['','已确认的局部修点包括莲花医者N03灯柄/肘腕的孤立高度跳变、山岳守卫W相邻帧胸背与盾近远侧切换、灵篆书生E/W跑步四处胸肩/道具转换与cast/E03笔手孤立折返。竹弓少女NW的实际支撑腿链与现行交接标签冲突，先核定真实解剖足、相位与顺序，再决定局修。其余记录中标“待核”的足轴与轨迹疑点要先正常速度连播和真实解剖追踪，不能把疑点直接当成必改的正确帧。','', '炼丹童子NW07→08的提前换足原疑已排除；08是正常换足边界。赤枪少女和星阵少女按最低鞋或屏幕位置猜解剖换足的确定性已撤回，保留真实标足核定。','', '制作窗口仍在修改成品，所有审阅绑定源SHA和时间。唤雪少女SW06、attack/E05/06与水龙书生attack/W03的新图已单帧追加检查；B组并发新图05的17张、06的4张、09的1张共22张已追加新图缩略图目检，不代表完整新序列动态通过。旧联系表不得冒充新SHA验收。','', '主审当前集中预览技术快照为15角色、120跑步方向、1920张PNG可用；02/04/06/09共有38个清单SHA暂未同步已交制作窗收尾。该数字是主审检查时刻的技术状态，本汇总未重新全量散列正在写入的角色目录。','', '本轮全角色静态筛查已实际覆盖全部动作组；新的修图、正常1200ms连播、循环接地、用户观感及客户端位移验收仍需继续，**不宣称最终全部修完或动态通过**。',''])
if totals['formalReportPending']:
    lines.extend(['B组05–09共70组、980张已由主审直接确认实际看过，最终正式审阅文件正在收尾；当前以来源快照和并发变更记录挂接，待文件落盘补入具体结论。',''])
lines.extend([f'[机器汇总]({(OUT/"all-characters-static-review-20261005.json").as_posix()}) · [技术库存]({(OUT/"inventory-summary.json").as_posix()})',''])
(OUT/'ALL_CHARACTERS_STATIC_REVIEW_20261005.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(totals,ensure_ascii=False))
