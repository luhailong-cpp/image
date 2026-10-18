import json,hashlib,re
from pathlib import Path
from datetime import datetime,timezone
OUT=Path(__file__).parent
ROOT=Path('D:/work/image');BASE=ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production';PROD=BASE/'parallel-production-20261013'
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):
 p=Path(p);return {'file':p.as_posix(),'sha256':sha(p)}
def save(n,d):
 p=OUT/n;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def pos(st):
 m=re.search(r'(r\d+_c\d+)_[ps](\d+)_(\d+)',st);return m[1],int(m[2]),int(m[3])
s=read(OUT/'snapshot.json');native={n['id']:n for n in s['native']};selected=s['selectionMap'].copy();supp=[]
# Complete the r02_c02 explicit selection evidence omitted by the initial inventory pass.
# These records predate the frozen source images; no new production is inferred.
for p in sorted((PROD/'island-west-residences/qa').glob('r02_c02*.json')):
 d=read(p)
 if d.get('selectedForContinuedProduction',d.get('selectedForContinuation',False)):
  st=d['stem'];n=native[st];assert n['sha256']==d.get('sha256',d.get('sourceSha256'))
  selected['|'.join(map(str,pos(st)))]=st;supp.append({'source':info(p),'content':d})
for h in s['holds']:selected.pop('|'.join(map(str,pos(h['coordinate']))),None)
for t in s['tiles']:
 if t['tileId']=='r02_c02':
  matrix=[[None]*4 for _ in range(4)]
  ss=[native[st] for key,st in selected.items() if key.startswith('r02_c02|')]
  for n in ss:matrix[n['subrow']-1][n['subcolumn']-1]={k:n[k] for k in ['id','file','sha256']}
  t['selectedCoreMatrix']=matrix;t['coreCount']=len(ss);t['fullCoverage']=len(ss)==16
s['selectionMap']=selected;s['metadata']+=supp
s['counts']['selectedCoreCount']=sum(t['coreCount'] for t in s['tiles'])
s['selectionEvidenceSupplement']={'reason':'Initial snapshot retained baseline r02_c02 selection only; explicit existing selectedForContinuedProduction quick reviews supply9 additional effective selections. Two coordinate holds still override older provisional continuation.','initialCount':145,'correctedCount':s['counts']['selectedCoreCount'],'recordCount':len(supp)}
assert s['counts']['selectedCoreCount']==154
save('snapshot-v02.json',s)
qa=[];issues=[]
def issue(id,tile,why,evidence,box=None):
 v={'id':id,'tileId':tile,'finding':why,'status':'pending_repair','evidence':info(OUT/evidence),'formalAccepted':False}
 if box:v['tileLocalBox']=box
 issues.append(v)
for b in s['boards']:
 name=b['name'];status='locally_continuous_in_checked_crops';finding='该原比例裁片内主要轮廓连续；仅限本批所列裁片范围。'
 if name.startswith('r02_c03-') and ('internal' in name or 'crossings' in name):
  status='failed_local_geometry';finding='金边、红梁和蓝瓦出现阶梯截断，集中在南侧及s04_04相关交界；该源仍未有效选中，不能据完整候选图宣称通过。'
 elif name.startswith('r02_c04-') and ('internal' in name or 'crossings' in name):
  status='local_repairs_pending';finding='局部金色屋檐与蓝瓦交接有切角/阶梯，树叶及地面存在清晰度变化；主体连续不等于内部验收通过。'
 elif name=='r02_c03-r03_c03-external-100pct':
  status='failed_retained_strip_geometry';finding='第1段保留带内蓝瓦和金边仍出现矩形截断，延续此前失败问题；不因拼接线附近连续而改判通过。'
 elif name=='r02_c04-r03_c04-external-100pct':
  status='geometry_continuous_material_pending';finding='红梁、灯笼及花枝轮廓基本衔接；第2段部分叶片清晰度变化保留复核。'
 qa.append({'id':name,'status':status,'finding':finding,'evidence':info(b['file']),'panels':b['panels'],'nativeScale100Percent':True,'viewedAtUtc':now(),'formalAccepted':False})
for v in s['newCrops']:
 status='geometry_continuous_material_pending' if v['id'].endswith('west') else 'locally_continuous_in_checked_crop'
 finding='石缝方向接通，局部重复小块纹理/笔触密度仍不同，保留材质待修。' if v['id'].endswith('west') else '新a02与相邻原生片的石缝或灯笼轮廓在本裁片内连续；不替代全块验收。'
 qa.append({**v,'status':status,'finding':finding,'viewedAtUtc':now(),'nativeScale100Percent':True,'formalAccepted':False})
for name,st,why in [
 ('r01_c03-p44-r01_c04-west-bottom-100pct.png','locally_continuous_in_checked_crop','石墙层线与植被轮廓在现有西邻最下段内衔接；西边其余三段缺邻源。'),
 ('r02_c12-provisional-held-p44-100pct.png','unselected_failed_source_remains_unaccepted','查看现有provisional所含p04_04_v06核心内容；生产记录标其外边几何失败，本次未核其外边，不改失败状态。'),
 ('r02_c12-provisional-p32-south-100pct.png','old_candidate_material_issue_pending','现有4096仍使用p03_02_v02，接缝带可见蓝瓦笔触/色调变化；冻结后v03另列，旧4096不自动变为新版。')]:
 qa.append({'id':name,'evidence':info(OUT/name),'status':st,'finding':why,'nativeScale100Percent':True,'viewedAtUtc':now(),'formalAccepted':False})
issue('west-c03-trim-steps','r02_c03','南侧金边和蓝瓦多处阶梯截断，s04_04仍HOLD。','r02_c03-crossings-100pct.png',[1800,2800,3300,3300])
issue('west-c03-south-retained-strip','r02_c03','与r03_c03相接第1段仍有源保留带矩形截断。','r02_c03-r03_c03-external-100pct.png',[0,3840,1024,4096])
issue('west-c04-gold-foliage','r02_c04','金边切角/阶梯与树叶清晰度变化仍待修。','r02_c04-h-internal-100pct.png',[512,1792,2048,2304])
issue('extension-r04-current-west','r04_c05','s04_02_a02西侧石缝接通，笔触密度变化仍待材质复核。','r04_c05_s04_02_a02-west-100pct.png')
candidates=s['candidates']
for c in candidates:
 t=c['tileId'];c['qaRecord']=(OUT/'visual-review.json').as_posix();c['allPixelsMatchRecordedNativeSources']=True
 c['candidateMatchesFrozenEffectiveSelection']=not c['currentEffectiveSourceMismatch']
 if t=='r01_c04':
  c['status']='internal_checked_locally_continuous_external_incomplete';c['qa']={'internalEdges':{'count':24,'status':'locally_continuous_in_checked_crops'},'internalCrossings':{'count':9,'status':'locally_continuous_in_checked_crops'},'southExternal':{'segments':4,'status':'locally_continuous_in_checked_crops'},'westExternal':{'segments':1,'status':'bottom_segment_locally_continuous_three_segments_missing_neighbor'},'eastExternal':'missing_neighbor','north':'map_outer_edge_not_whole_map_accepted','formalAccepted':False}
 elif t=='r02_c03':c['status']='failed_internal_trim_steps_and_south_retained_strip_hold_p44';c['qa']={'internalEdgesReviewed':24,'crossingsReviewed':9,'southExternal':'failed_retained_strip_geometry','eastExternal':'locally_continuous_in_checked_crops','formalAccepted':False}
 elif t=='r02_c04':c['status']='internal_geometry_material_repairs_pending';c['qa']={'internalEdgesReviewed':24,'crossingsReviewed':9,'northAndWestExternal':'locally_continuous_in_checked_crops','southExternal':'geometry_continuous_material_pending','eastExternal':'not_reviewed_missing_complete_neighbor','formalAccepted':False}
 elif t=='r03_c05':c['qa']={'sourcePixelReplay':'pass','previous24InternalAnd9CrossingChecks':'source_hashes_unchanged_reused','producerInternal':'pending_local_surface_repairs','external':'west_and_south_geometry_broadly_connect_surface_pending_north_east_unchecked','formalAccepted':False}
 elif t=='r04_c05':c['qa']={'sourcePixelReplay':'pass_for_old_candidate','oldCandidate':'stale_s04_02_a01_is_superseded_by_a02','currentSourceDelta':'three_adjacent_edges_viewed_geometry_continuous_material_pending_west','formalAccepted':False}
 else:c['qa']={'sourcePixelReplay':'pass','candidate':'contains_unselected_p04_04_v06_and_older_p03_02_v02','producerStatus':'known_external_geometry_failure','formalAccepted':False}
 for tile in s['tiles']:
  if tile['tileId']==t:
   tile['candidateFile']=c['file'];tile['candidateSha256']=c['sha256'];tile['qaStatus']=c['status']
   # file/sha256 at tile level are reserved for an adopted complete production tile.
   tile['file']=None;tile['sha256']=None
save('visual-review.json',{'reviewedAtUtc':now(),'newInternalSeamSegmentCount':72,'newCrossingCount':27,'newExternalSegmentCount':17,'newExtensionChangedCoreEdgeCount':3,'newDiagnosticCropCount':2,'reviews':qa,'reusedIndependentChecks':s['reusedChecks'],'scope':'原比例裁片检查，未做整图或正式验收；未通过问题持续待修。'})
save('repair-queue.json',{'issues':issues,'producerHolds':s['holds'],'otherProducerPendingSurfaceIssues':[{'tileId':c['tileId'],'producerQa':c.get('producerQa')} for c in candidates if c.get('producerQa')],'formalAcceptedCount':0})
# One terminal recheck: stop at this frozen batch rather than repeatedly catch production.
records=s['native']+s['candidates']+[m['source'] for m in s['metadata']]+s['rules']
checks=[]
for v in records:
 p=Path(v['file']);h=sha(p) if p.exists() else None;checks.append({'file':v['file'],'expectedSha256':v['sha256'],'currentSha256':h,'unchanged':h==v['sha256']})
known={n['file'] for n in s['native']};added=[]
for key in ['island-west-residences','island-east-residences','island-northwest-east-extension']:
 for p in sorted((PROD/key/'native').glob('*.png')):
  if p.as_posix() not in known:added.append(info(p))
lateSelections=[]
knownMeta={m['source']['file'] for m in s['metadata']}
for folder in (PROD/'island-east-residences/selections').glob('*'):
 ss=sorted(folder.glob('selection-v*.json'))
 if ss and ss[-1].as_posix() not in knownMeta:lateSelections.append({'source':info(ss[-1]),'selectedCoreCount':read(ss[-1])['selectedCoreCount'],'notIncludedInFrozenSelectedSourceMatrix':True})
recheck={'checkedAtUtc':now(),'unchangedCount':sum(v['unchanged'] for v in checks),'changedFrozenInputs':[v for v in checks if not v['unchanged']],'allFrozenSourceImagesUnchanged':all(v['unchanged'] for v in checks if v['file'].endswith('.png')),'lateNativeFiles':added,'lateSelectionFiles':lateSelections,'countsAreFrozen':True}
save('source-recheck.json',recheck)
save('current-candidates.json',{'createdAtUtc':now(),'frozenAtUtc':s['frozenAtUtc'],'candidates':candidates,'formalAcceptedCount':0,'fileNote':'Actual4096 images already exist; all remain candidates. r04_c05 image is stale. r02_c03 and r02_c12 contain an unselected held/failed core.','lateDelta':recheck})
old=read(Path(s['baseline']['file']));delta={k:{'baseline':old['counts'].get(k),'frozenCurrent':v,'change':v-old['counts'].get(k,0)} for k,v in s['counts'].items() if isinstance(v,int)}
summary={'schemaVersion':2,'status':'frozen_incremental_audit_complete','createdAtUtc':now(),'frozenAtUtc':s['frozenAtUtc'],'counts':s['counts'],'tiles':s['tiles'],'deltaFromResumeV03':delta,'snapshot':info(OUT/'snapshot-v02.json'),'selectionEvidenceSupplement':s['selectionEvidenceSupplement'],'sourceRecheck':recheck,'currentCandidatesFile':(OUT/'current-candidates.json').as_posix(),'visualReviewFile':(OUT/'visual-review.json').as_posix(),'repairQueueFile':(OUT/'repair-queue.json').as_posix(),'formalAcceptedCount':0,'adoptedTileCount':0,'generationPerformed':False,'productionWrites':False,'sharedGitTouched':False,'coverageSemantics':'coreCount counts unique effective explicit production selections; saved versions/unique coordinates are separate. fullCoverage does not imply adopted or accepted. file/sha256 at tile level remain null without adoption; candidateFile/candidateSha256 and currentCandidates list actual4096 candidate paths.'}
save('summary.json',summary)
lines=['# 八仙岛并行三区增量检查（2026-10-16）','',f"本批冻结 {s['counts']['selectedCoreCount']} 个有效选中核心、{s['counts']['savedUniqueCoreCount']} 个已存唯一坐标、{s['counts']['savedNativeVersionCount']} 个版本。14 块中4块选中满16、8块部分、2块无选中核心；正式验收与整块采纳均为0。相较 resume-v03 增加110个有效选中核心、91个唯一坐标、103个版本。",'',f"冻结时间（UTC）：{s['frozenAtUtc']}。只读生产源，零生图、零AI修图、未操作共享Git。",'','[规范14块清单](summary.json) · [实际4096候选路径及QA](current-candidates.json) · [原比例检查证据](visual-review.json) · [待修清单](repair-queue.json)','', '|坐标|有效选中核心|已存唯一坐标|版本数|当前QA|','|---|---:|---:|---:|---|']
for t in s['tiles']:lines.append(f"|{t['tileId']}|{t['coreCount']}/16|{t['savedUniqueCoreCount']}|{t['savedVersionCount']}|{t.get('qaStatus','核心不全，未作完整块验收')}|")
lines+=['','本批可优先查看 r01_c04：24条内部缝、9个交汇、南边4段及西边最下1段未见明显断接。西边另3段、东边缺完整邻源，因此保持外边未完成状态。','']
for c in candidates:lines.append(f"- [{c['tileId']} · 4096候选]({c['file']})：`{c['status']}`。SHA-256 `{c['sha256']}`。")
lines+=['','6张现有4096均已验证每个像素来自记录的原生源，合计100,663,296像素无差异；西区使用重叠区择缝，扩展及东区为整数核心直拼，无缩放、羽化或绘制。原像素一致只证明来源，视觉质量另记。','','r02_c03保留金边/蓝瓦截断、南边保留带失败及未选s04_04；r02_c04局部金边切角和树叶清晰度过渡待修。扩展r03_c05复用哈希未变证据，材质仍待修；r04_c05已存4096使用旧s04_02_a01，当前已选a02只补看受影响三条边，未重建生产候选。东区r02_c12的provisional含1个未选失败核心，不计16个有效选中核心。','','初次索引快照遗漏r02_c02的新增明确续作QA，已在snapshot-v02补入9个有效选中核心，仍排除两处HOLD；summary.json采用校正后的154。','','检查期间生产继续。末次源哈希核对与冻结后新增文件见[source-recheck.json](source-recheck.json)；新版本不自动套用旧候选或旧检查。']
p=OUT/'review.md';assert not p.exists();p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'counts':s['counts'],'recheck':{k:v for k,v in recheck.items() if k not in ['lateNativeFiles','lateSelectionFiles']},'lateNativeCount':len(added),'lateSelectionCount':len(lateSelections),'outputs':['summary.json','current-candidates.json','review.md']},ensure_ascii=False,indent=2))
