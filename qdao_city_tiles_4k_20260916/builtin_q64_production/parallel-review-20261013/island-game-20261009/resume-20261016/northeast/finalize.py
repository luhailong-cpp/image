from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

O=Path(__file__).resolve().parent;R=O.parents[1]
def read(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def write(f,d):Path(f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
s=read(O/'summary.json');c=read(O/'current-candidates.json')
geometry_pending={'edge-8-33-v'}
material_pending={'edge-12-34-v','edge-11-35-h','edge-15-34-v','edge-14-34-h'}
cross_material={'cross-11-34','cross-11-35','cross-12-34','cross-14-34'}
edge_boards={ident:b['file'] for b in s['boards'] for ident in b.get('edgeIds',[])}
cross_boards={ident:b['file'] for b in s['boards'] for ident in b.get('crossIds',[])}
for e in s['newEdges']:
    e.update({'actuallyViewed':True,'viewedAtUtc':now,'viewedVia':edge_boards[e['id']],
              'inspectionTool':'view_image','inspectionDetail':'original','inspectionScale':1,
              'scope':'Only the exact native seam strip; whole-tile layout and missing neighbors remain pending.'})
    if e['id'] in geometry_pending:
        e.update({'status':'requires_grout_geometry_repair','geometry':'not_passed','material':'not_a_whole_material_acceptance',
                  'finding':'p01_02_v3 与 p01_03 中部灰缝接点仍有小错位；复用当前源哈希绑定的生产 failed_geometry_continuity 结论，不升级为通过。'})
    elif e['id'] in material_pending:
        e.update({'status':'geometry_local_passed_material_repair_pending','geometry':'local_contours_continuous','material':'not_passed',
                  'finding':'石板轮廓和灰缝能接上，但矿物斑驳笔触与相邻细密菱格石面在接边附近形成可见材质过渡。'})
    else:
        e.update({'status':'local_visual_passed','geometry':'local_contours_continuous','material':'no_blocking_abrupt_transition_seen_in_this_strip',
                  'finding':'本条原尺寸接边内的石板、花叶、栏板或灯笼轮廓连续，未见缺口或阻塞性平移；此结论不等于整块布局或全外接通过。'})
for e in s['newCrosses']:
    e.update({'actuallyViewed':True,'viewedAtUtc':now,'viewedVia':cross_boards[e['id']],
              'inspectionTool':'view_image','inspectionDetail':'original','inspectionScale':1})
    if e['id'] in cross_material:
        e.update({'status':'geometry_local_passed_material_repair_pending','geometry':'local_contours_continuous','material':'not_passed',
                  'finding':'四邻轮廓可接续，涉及 r04_c09 矿物斑驳／细密纹理切换的核心角仍保留材质待修。'})
    else:
        e.update({'status':'local_visual_passed','geometry':'local_contours_continuous','material':'no_blocking_four_way_cutoff_seen',
                  'finding':'本处四邻轮廓与接缝可接续，未见阻塞性四方空缺或轮廓错接；灯笼整体宽度按原布局问题另留待核。'})
for b in s['boards']:b.update({'actuallyViewed':True,'viewedAtUtc':now,'inspectionTool':'view_image','inspectionDetail':'original'})

repairs=read(R/'resume-v03/northeast-full/summary.json')['repairs']
repairs.append({'id':'coast-r02c13-r02c14-material-band','tiles':['r02_c13','r02_c14'],
    'status':'requires_native_material_repair_hash_unchanged','worldAffectedBox':[52992,7900,53504,8050],
    'finding':'海岸共享竖边的蓝色矩形材质带仍按原独立检查开放；本批候选hash未变，不升级为通过。',
    'evidence':[(R/'root-audit-v01/g02-cross-zone-r02-r03-c13-c14/v-1-segment-4-100pct.png').as_posix()]})
repairs.extend([
 {'id':'r03c09-p12v3-p13-grout-offset','tiles':['r03_c09'],'status':'requires_geometry_repair',
  'worldAffectedBox':[34560,8192,35072,9216],'finding':'p01_02_v3 灯笼身份已更正，右接 p01_03 中部灰缝仍错位。',
  'evidence':[(O/'edge-8-33-v.png').as_posix()]},
 {'id':'r04c09-p14v3-material-transition','tiles':['r04_c09'],'status':'requires_material_repair',
  'worldAffectedBox':[35840,12288,36864,13312],'finding':'p01_04_v3 最佳保留源几何可接，但左侧、上侧原生边附近有矿物斑驳和细密石纹的切换；两次失败返修不算通过。',
  'evidence':[(O/'edge-12-34-v.png').as_posix(),(O/'edge-11-35-h.png').as_posix()]},
 {'id':'r04c09-p43v2-material-transition','tiles':['r04_c09'],'status':'requires_material_repair',
  'worldAffectedBox':[34816,15360,35840,16384],'finding':'p04_03_v2 石板轮廓与绿沿可续接，但矿物斑驳表面在上／右边与菱格纹理形成过渡。',
  'evidence':[(O/'edge-15-34-v.png').as_posix(),(O/'edge-14-34-h.png').as_posix()]},
 {'id':'r04c09-p44-lantern-width','tiles':['r04_c09'],'status':'production_reported_layout_review_pending',
  'worldAffectedBox':[35840,15360,36864,16384],
  'finding':'生产当前选源记录仍报告灯笼左轮廓比原布局窄；本批仅核对接边，不把轮廓连续当作灯笼整体布局已通过。',
  'evidence':[(O/'snapshots/selection-r04_c09.json').as_posix(),(O/'edge-15-35-v.png').as_posix()]}
])
write(O/'repair-queue.json',{'updatedAtUtc':now,'repairs':repairs,'allIssuesRemainNotPassed':True})

# Reuse the two already inspected local groups, checking only their current input hashes.
by={t['tileId']:t for t in c['candidates']};groups=[]
for key in ('g03-main-r03-r04-c11-c12','g04-main-r04-r05-c13-c14'):
    f=R/'root-audit-v01'/key/'manifest.json';g=read(f)
    unchanged=all(x['tileId'] in by and by[x['tileId']]['sha256']==x['sha256'] for x in g['inputs'])
    assert unchanged
    groups.append({'group':key,'currentInputs':[{k:by[x['tileId']][k] for k in ('tileId','file','sha256','dimensions')} for x in g['inputs']],
        'currentInputHashesUnchanged':True,'reusedManifest':f.as_posix(),'reusedManifestSha256':sha(f),
        'qaStatus':g['status'],'existingLocalAssembly':g['output'],'newAssemblyBuilt':False,'formalAccepted':False})
write(O/'ready-groups.json',{'checkedAtUtc':now,'groups':groups,'new4096Candidates':[
    {k:t[k] for k in ('tileId','file','sha256','dimensions','internalQA','externalQA','qaEvidence')}
    for t in c['candidates'] if t['tileId'] in ('r06_c12','r06_c14')]})

for t in c['candidates']:
    if t['tileId']=='r03_c10':
        t['qaEvidence']=[(R/'resume-v03/northeast-full/summary.json').as_posix()]
        t['resolvedOldFinding']='Old stone material band was repaired by the selected overlay and independently passed v03; not inherited as an open v1 issue.'
    if t['tileId'] in ('r06_c12','r06_c14'):
        t['qaEvidence'].append((O/'reused-full-pixel-verification.json').as_posix())
    r,col=int(t['tileId'][1:3]),int(t['tileId'][5:7]);neighbors=[]
    for side,rr,cc in [('north',r-1,col),('east',r,col+1),('south',r+1,col),('west',r,col-1)]:
        nt=f'r{rr:02d}_c{cc:02d}'
        if not (1<=rr<=14 and 1<=cc<=14):state='map_boundary_no_external_neighbor'
        elif nt in s['transferredCoordinates']:state='parallel_owner_material_pending_merge'
        elif nt in by:state='complete_neighbor_available_only_hash_bound_reviewed_edges_pass'
        else:state='complete_neighbor_missing_or_outside_this_batch'
        neighbors.append({'side':side,'tileId':nt if 1<=rr<=14 and 1<=cc<=14 else None,'availability':state,
                          'file':by.get(nt,{}).get('file'),'sha256':by.get(nt,{}).get('sha256')})
    t['neighbors']=neighbors
c['completedAtUtc']=now;c['status']='frozen_batch_review_complete_with_open_issues';write(O/'current-candidates.json',c)

# One final read of current selected inputs; later production changes are recorded,
# not followed into an endless moving-target audit.
inputs={x['file']:x['sha256'] for x in s['selectionSnapshots']}
inputs.update({t['file']:t['sha256'] for t in c['candidates']})
inputs.update({x['file']:x['sha256'] for x in s['partialSourceChecks']})
verification=read(O/'reused-full-pixel-verification.json')
for t in verification['tiles']:
    inputs.update({x['file']:x['sha256'] for x in t['nativeSources']})
changes=[]
for f,h in inputs.items():
    current=sha(f) if Path(f).exists() else None
    if current!=h:
        e={'file':f,'snapshotSha256':h,'currentSha256':current,'kind':'metadata' if f.endswith('.json') else 'source_pixels'}
        if Path(f).name.startswith('selection-') and current:
            q=read(f);e.update({'currentSelectedCoreCount':sum(bool(x) for row in q.get('cores',[]) for x in row),
                              'currentSelectedCores':q.get('cores'),'currentTileId':q.get('tileId'),
                              'liveCandidatePath':q.get('candidatePath'),'liveCandidateClaimedSha256':q.get('candidateSha256'),
                              'liveProductionInternalReview':q.get('internalReview'),
                              'liveProductionReviewPath':q.get('reviewPath') or q.get('reviewRecord'),
                              'liveProductionPendingIssues':q.get('pendingIssues',[]),
                              'liveCandidateNotAuditedInThisFrozenBatch':True})
        changes.append(e)
recheck={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'inputCount':len(inputs),
         'unchangedCount':len(inputs)-len(changes),'changes':changes,'snapshotMetadataStale':bool(changes),
         'frozenSourcePixelsUnchanged':not any(x['kind']=='source_pixels' for x in changes),
         'policy':'Changes after capture remain outside this one frozen QA batch; do not transfer old passes to newer selected matrices.'}
write(O/'source-recheck.json',recheck)
selection_deltas=[e for e in changes if e.get('currentTileId')]
c['currentSelectionDeltas']=selection_deltas
c['snapshotOnly']=True
for t in c['candidates']:
    delta=next((e for e in selection_deltas if e['currentTileId']==t['tileId']),None)
    t['liveSelectionChangedAfterCapture']=bool(delta)
    if delta:
        t['liveSelectionDelta']=delta
        t['qaVersionWarning']='All listed QA findings bind the frozen file/hash only; a newer live candidate is recorded separately and is not audited here.'
write(O/'current-candidates.json',c)
s.update({'completedAtUtc':now,'status':'frozen_batch_review_complete_with_open_issues',
    'sourceRecheck':recheck,'partialVisual':{'edgeSegmentsActuallyViewed':len(s['newEdges']),
    'crossesActuallyViewed':len(s['newCrosses']),'boardsActuallyViewed':len(s['boards']),
    'edgeLocalPassCount':sum(e['status']=='local_visual_passed' for e in s['newEdges']),
    'edgeMaterialPendingCount':len(material_pending),'edgeGeometryPendingCount':len(geometry_pending),
    'crossLocalPassCount':sum(e['status']=='local_visual_passed' for e in s['newCrosses']),
    'crossMaterialPendingCount':len(cross_material)},'reusedNewFullCandidatePixelVerification':(O/'reused-full-pixel-verification.json').as_posix(),
    'readyGroups':(O/'ready-groups.json').as_posix(),'repairQueue':(O/'repair-queue.json').as_posix(),
    'versionNote':'r03_c09 selection pendingIssues mentions superseded p01_02_v2 and old p01_01. Current p01_01_v2/p01_02_v3 join has matching production pass; p01_02_v3/p01_03 still has matching failed geometry record. Full layout disposition remains pending.',
    'reviewFile':(O/'review.md').as_posix()})
write(O/'summary.json',s)

lines=['# 八仙岛东北既有素材增量检查（2026-10-16）','',
 '本批已检查完冻结输入，仍有美术待修和缺块。原东北49坐标已按归属去重：本表统计原制作区39坐标与海岸加速4坐标，东民居6坐标交由 parallel 批合并，未算空块或重复计数。', '',
 f"冻结于 UTC {s['capturedAtUtc']}。43坐标共340个唯一选中1024核心；20张核心完整并已采用的4096候选，2张部分覆盖，21张尚无选中核心，正式全图验收0。制作区39坐标占276核心、16完整、2部分、21空；海岸4张占64核心。", '',
 '## 可先查看的现有 4K 图','',
 '新增完整候选 r06_c12、r06_c14 已有绑定当前候选哈希的49项内部QA。独立核对32张1254源图、32个1024原像素核心摆放，以及98份现有检查裁片与当前4096成图像素完全一致，故复用已通过证据。两张各自北邻4096接边已有当前哈希绑定的通过记录，缺少左／下邻的外接仍待后续。', '',
 f"- [r06_c12，4096×4096]({by['r06_c12']['file']})；内部QA可复用，上邻通过，左／右／下邻未完成。", 
 f"- [r06_c14，4096×4096]({by['r06_c14']['file']})；内部QA可复用，上邻通过，左／下邻未完成，东侧为地图边界。", '',
 '两组现有局部拼接的8张4K输入哈希均未改变，原共享边和四交点通过证据继续有效，外围状态按原记录保留。本批未新建8192图或整图。', '']
for g in groups:
    lines.append(f"- {g['group']}："+'、'.join(f"[{x['tileId']}]({x['file']})" for x in g['currentInputs'])+'。')
lines += ['', '## 本批补查与待修', '',
 '只针对 r03_c09、r04_c09 新选核心补查27条原像素接边与11个四交点，9张100%拼板全部实际查看。22条边及7个十字的局部轮廓／材质检查通过；1条边保留灰缝几何问题，4条边及4个十字保留材质问题。局部通过不等于部分图块整体布局验收。', '',
 '- r03_c09：冻结11/16，p01_02_v3→p01_03 中部灰缝错位仍待修。p01_01_v2→p01_02_v3 本条接边有当前源哈希绑定通过记录；旧 pendingIssues 中提到的 p01_02_v2 为已替换版本，不能把该文字直接当作新版本已失败或已通过。',
 '- r04_c09：冻结9/16。p01_04_v3 上／左侧、p04_03_v2 上／右侧仍有矿物斑驳石面到细密菱格石面的可见过渡；p04_04 灯笼整体宽度保留生产原布局待核，接边连续不能替代整物布局验收。',
 '- r05_c11：候选哈希未变，灯笼下 p01_04 矩形虚化左／下边及北接金色细棱问题继续开放。',
 '- 海岸 r02_c13／r02_c14：候选哈希未变，世界 x53248、y约7900—8050 的蓝色材质带继续待修。原南北接边通过证据与这处竖边缺陷分别保留。', '',
 '## 逐图冻结候选', '', '下表全部绑定冻结版本和实核哈希。冻结后新增／替换的实时选源另列于后，不继承旧问题或旧通过状态。', '', '| 坐标 | 原始4096文件 | SHA256前12位 | 冻结版本QA |', '|---|---|---|---|']
for t in c['candidates']:
    if t['tileId']=='r05_c11':q='内部材质待修；北接细棱待核'
    elif t['tileId'] in ('r02_c13','r02_c14'):q='内部原记录复用；海岸竖边材质待修'
    elif t['tileId'] in ('r06_c12','r06_c14'):q='98裁片之一组验证完成；完整49项内部QA复用，北接通过'
    else:q='当前图哈希未变，复用原内部记录；仅原已查外接有效'
    lines.append(f"| {t['tileId']} | [{Path(t['file']).name}]({t['file']}) | {t['sha256'][:12]} | {q} |")
lines += ['', '## 冻结后变化', '',
 f"收尾复核 {recheck['inputCount']} 项本批输入，{recheck['unchangedCount']} 项哈希未变，{len(changes)} 项变化。冻结源图像素{'未变化' if recheck['frozenSourcePixelsUnchanged'] else '发生变化，按JSON失效标记处理'}。后续生产矩阵只记录为 delta，不移用旧通过结论，也不无限追赶在制版本。", '',
 f"- [冻结后变化和输入哈希复核]({(O/'source-recheck.json').as_posix()})", 
 f"- [逐图完整路径、哈希、尺寸、QA清单]({(O/'current-candidates.json').as_posix()})", 
 f"- [两张新完整图的32原图／98裁片像素核验]({(O/'reused-full-pixel-verification.json').as_posix()})", 
 f"- [完整坐标、27边与11十字检查记录]({(O/'summary.json').as_posix()})", 
 f"- [待修队列]({(O/'repair-queue.json').as_posix()})", '',
 '本批零生图、零AI修图，原生产图与选源账本只读，未操作Git。现存图实际生成型号未返回，不追溯标为2.5。']
for e in selection_deltas:
    tail=f"- 冻结后 {e['currentTileId']} 选中数现为 {e['currentSelectedCoreCount']}/16。"
    if e.get('liveCandidatePath'):
        tail+=f"实时候选已换为 [{Path(e['liveCandidatePath']).name}]({e['liveCandidatePath']})；生产记录声明内部状态 {e.get('liveProductionInternalReview')}。该新图未纳入本批像素／美术检查，旧图问题不能直接套用到新图。"
    else:tail+='新增核心未纳入本批接边检查。'
    lines.append(tail)
(O/'review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':s['status'],'counts':s['counts'],'partialVisual':s['partialVisual'],'sourceRecheck':recheck},ensure_ascii=False))
