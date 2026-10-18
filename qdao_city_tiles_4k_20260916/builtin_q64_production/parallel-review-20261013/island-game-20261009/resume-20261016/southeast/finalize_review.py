from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, re
from PIL import Image
OUT=Path(__file__).parent;REVIEW=OUT.parent.parent;BASE=REVIEW.parent.parent;PROD=BASE/'island-game-20261009/southeast'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,d):(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
s=read(OUT/'summary.json');tiles={t['tileId']:t for t in s['tiles']};old=read(REVIEW/'resume-v03/southeast/summary.json');oldtiles={t['tileId']:t for t in old['tiles']};ims={tid:Image.open(t['file']).convert('RGB') for tid,t in tiles.items() if t['file']};checks=read(OUT/'source-checks.json')['checks']
def record(p):
 p=Path(p);h=sha(p);checks.append({'file':str(p),'sha256':h,'bytes':p.stat().st_size,'stableDuringRead':True});return h
proof=read(OUT/'source-replay.json')
# r14 c11 is exact ordinary core assembly despite visual defects.
left=read(PROD/'qa/r14_c11-resume-20261013-v01/source-pixel-proof.json');parts=[]
for x in left['sources']:
 assert record(x['file'])==x['sha256'];m=re.search(r'_p(\d)(\d)_',x['file']);r,c=map(int,m.groups());box=[(c-1)*1024,(r-1)*1024,c*1024,r*1024]
 with Image.open(x['file']) as im: equal=im.convert('RGB').crop((115,115,1139,1139)).tobytes()==ims['r14_c11'].crop(box).tobytes()
 assert equal;parts.append({'file':x['file'],'sha256':x['sha256'],'destinationBox':box,'pixelsMatch':True})
proof['newCandidateReplays'].append({'tileId':'r14_c11','candidateSha256':tiles['r14_c11']['sha256'],'sources':parts,'exactCoreReplay':True,'coveredPixels':16777216})
# v04 changes one registered native core. Every other byte of RGB must equal the previously audited v03.
m=read(Path(tiles['r12_c13']['file']+'.generation.json'));assert record(m['baseCandidate'])==m['baseCandidateSha256']==oldtiles['r12_c13']['sha256'];overlay=m['sources'][-1];assert record(overlay['file'])==overlay['sha256'];base=Image.open(m['baseCandidate']).convert('RGB');replay=base.copy()
with Image.open(overlay['file']) as im:replay.paste(im.convert('RGB').crop(overlay['sourceCoreCrop']),(overlay['destinationCore'][0],overlay['destinationCore'][1]))
assert replay.tobytes()==ims['r12_c13'].tobytes()
sailbox=[2816,3474,3328,3986];sailunchanged=base.crop(sailbox).tobytes()==ims['r12_c13'].crop(sailbox).tobytes();assert sailunchanged
proof['newCandidateReplays'].append({'tileId':'r12_c13','candidateSha256':tiles['r12_c13']['sha256'],'baselineCandidate':m['baseCandidate'],'baselineSha256':m['baseCandidateSha256'],'baselineMatchesPriorAuditedV03':True,'newNative':overlay,'coveredPixels':16777216,'exactRGBReplay':True,'unrepairedSailBattenPixelsUnchanged':sailunchanged})
write('source-replay.json',proof)
# Reuse prior narrow edge evidence by pixel identity, including v04's unchanged outer border.
def worldcrop(box,tids):
 im=Image.new('RGB',(box[2]-box[0],box[3]-box[1]));covered=0
 for tid in tids:
  tb=tiles[tid]['worldBox'];b=[max(tb[0],box[0]),max(tb[1],box[1]),min(tb[2],box[2]),min(tb[3],box[3])]
  if b[0]<b[2] and b[1]<b[3]:im.paste(ims[tid].crop((b[0]-tb[0],b[1]-tb[1],b[2]-tb[0],b[3]-tb[1])),(b[0]-box[0],b[1]-box[1]));covered+=(b[2]-b[0])*(b[3]-b[1])
 assert covered==im.width*im.height;return im
prev=read(REVIEW/'resume-v02/southeast-remaining/summary.json');reuse=[];crossreuse=[]
for e in prev['newEdgeReviews']:
 parts=[]
 for x in e['segments']:
  assert sha(x['file'])==x['sha256'];oldim=Image.open(x['file']).convert('RGB');same=oldim.tobytes()==worldcrop(x['worldBox'],e['tiles']).tobytes();assert same;parts.append({'file':x['file'],'sha256':x['sha256'],'pixelsMatchCurrent':True,'status':x['status']})
 reuse.append({'tiles':e['tiles'],'priorStatus':e['status'],'reused':True,'segments':parts})
for x in prev['newCrossReviews']:
 assert sha(x['file'])==x['sha256'];im=Image.open(x['file']).convert('RGB');cx,cy=x['worldPoint'];w,h=im.size;box=[cx-w//2,cy-h//2,cx+w//2,cy+h//2];assert im.tobytes()==worldcrop(box,x['tiles']).tobytes();crossreuse.append({'tiles':x['tiles'],'file':x['file'],'sha256':x['sha256'],'pixelsMatchCurrent':True,'priorStatus':x['status'],'reused':True})
add=read(REVIEW/'resume-v03/southeast/additional-evidence-reuse.json');groups=[]
for g in add['groups']:
 sources=g['sources'];same=all(tiles[x['tile']]['sha256']==x['sha256'] for x in sources);assert same;groups.append({'file':g.get('file',g.get('assembly')),'sources':sources,'candidateHashesMatchCurrent':True,'reused':True,'rebuilt':False})
write('evidence-reuse.json',{'previousV03':str(REVIEW/'resume-v03/southeast/summary.json'),'unchangedFullCandidateCount':sum(t.get('baselineHashUnchanged',False) for t in tiles.values()),'oldRemainingEdges':reuse,'oldCrosses':crossreuse,'groups':groups,'previousQAStatusPreserved':True,'unchangedEvidenceNotReViewed':True})
cm=read(OUT/'crop-manifest.json');issue_map={}
def mark(ids,status,note):
 for i in ids:issue_map[i]=(status,note)
for x in cm['cuts']:
 x.update(actuallyViewed=True,viewedAtOriginalPixelScale=True,reviewedAtUtc=now(),status='local_geometry_and_material_visual_passed')
 if x.get('kind')=='not_passed_sample':x.update(status='prior_producer_failure_confirmed',note='Current native pixels retain material/geometry defects; candidate remains unpassed.')
 if x['id']=='previous-sail-batten':x.update(status='prior_issue_retained_pixels_unchanged',note='Small earlier batten discontinuity retained. v04 repairs only floor wood; this exact source region is unchanged.')
for e in cm['edges']:
 tids=e['tiles'];bad=tids in [['r12_c13','r13_c13'],['r13_c12','r13_c13'],['r13_c11','r14_c11'],['r14_c11','r14_c12']]
 e['status']='geometry_continuous_material_repair_required' if bad else 'local_geometry_and_material_visual_passed'
 e['actuallyViewed']=True;e['sourceHashes']={tid:tiles[tid]['sha256'] for tid in tids};e['formalAccepted']=False
 for x in cm['cuts']:
  if x['id'] in e['segments']:x['status']=e['status']
for x in cm['cuts']:
 if x['kind']=='external_junction_delta':x['status']='geometry_continuous_material_repair_required';x['note']='Water guide rectangle near the southeast or southwest source region remains; cross-junction not passed.'
for b in cm['boards']:b.update(actuallyViewed=True,viewedAtOriginalPixelScale=True,reviewedAtUtc=now())
write('crop-manifest.json',cm)
issues=read(REVIEW/'resume-v03/southeast/repair-queue.json')['issues']
# Split the old composite issue: floor repaired and independently rechecked; sail remains open.
for x in issues:
 if x['id']=='r12_c13-v03-wood-material-pending':x.update(status='partly_resolved_floor_v04_sail_retained',finding='v04 registered 1024 core removes the wood brightness band; 10 changed-region/ownership views passed. Prior lower sail batten pixels are unchanged and its issue remains open.',newEvidence=[str(OUT/'r12_c13-whole-material.png'),str(OUT/'r12_c13-sail-batten.png')])
issues += [
 {'id':'r13_c13-full-v01-internal-not-passed','tiles':['r13_c13'],'status':'material_and_spar_repair_required','finding':'Saved 16-core candidate uses six sources not in current usable selection. Producer records 8 failed seams and 5 failed junctions; representative spar and actual water join confirmed. Never treat complete coverage as passed.','evidence':str(PROD/'qa/r13_c13-right-full-20261013-v01/actual-review.json'),'newEvidence':str(OUT/'known-unpassed-current-samples.png'),'formalAccepted':False},
 {'id':'r14_c11-full-v01-internal-not-passed','tiles':['r14_c11'],'status':'material_repair_required','finding':'North source guide bands, middle water rectangles and rock facets remain unpassed. Actual full north/east edge crops show straight material bands approximately 115 pixels inside current source cores.','evidence':str(PROD/'progress-r14_c11.json'),'newEvidence':[str(OUT/'r13_c11-r14_c11-edge.png'),str(OUT/'r14_c11-r14_c12-edge.png')],'formalAccepted':False},
 {'id':'r13_c13-north-west-full-neighbor-material','tiles':['r12_c13','r13_c13','r13_c12'],'status':'material_repair_required','finding':'Full north/west actual shared-edge contours continue, but p11/p21/p41 water guide regions retain rectangular density/sharpness changes. Four-way point (49152,49152) also remains pending material.','evidence':[str(OUT/'r12_c13-r13_c13-edge.png'),str(OUT/'r13_c12-r13_c13-edge.png'),str(OUT/'cross-49152-49152.png')],'formalAccepted':False}
]
write('repair-queue.json',{'issues':issues,'formalAcceptanceNotGranted':True,'resolvedSubIssues':[{'tileId':'r12_c13','issue':'wood floor straight brightness band','status':'resolved_in_v04_independent_delta_passed','remaining':'prior unchanged sail-batten issue remains'}]})
for tid,t in tiles.items():
 t['selectedNativeCoreCount']=t['coreCount'];t['qaStatus']='missing_selected_native_cores' if t['coreCount']==0 else ('partial_selected_native_coverage' if not t['fullCoverage'] else 'internal_recorded_pass_external_pending')
 t['independentReviewEvidence']=str(OUT/'crop-manifest.json') if tid in s['changedFullCandidates'] else str(REVIEW/'resume-v03/southeast/summary.json')
 t['independentInternalPassed']=None;t['formalAccepted']=False
 if tid in ['r08_c10','r14_c14']:t.update(independentInternalPassed=True,qaStatus='independent_internal_24_seams_9_junctions_passed_external_pending')
 if tid=='r08_c10':t['pending']='East actual full edge passed; north/west/south full neighbors or remaining corners are incomplete. p24-v03 remains a producer quick-status conflict despite new candidate internal pass.'
 if tid=='r14_c14':t['pending']='north r13_c14 has no full candidate; west r14_c13 only 11 selected usable cores. East/south world boundary.'
 if tid in ['r13_c13','r14_c11']:t.update(independentInternalPassed=False,qaStatus='complete_candidate_internal_not_passed')
 if tid=='r12_c13':t.update(independentInternalPassed=False,qaStatus='floor_repair_delta_passed_prior_sail_issue_retained',pending='v04 floor change passed; old sail batten unchanged. Full east neighbor absent; south current candidate unpassed.')
 if tid=='r13_c11':t['qaStatus']='internal_recorded_pass_north_east_material_issues_retained'
 if tid=='r10_c12':t['qaStatus']='producer_local_artwork_acceptance_ready_unchanged_evidence_reused';t['localArtworkAcceptanceReadyAsRecorded']=True
 if t['file']:
  r,c=map(int,re.findall(r'\d+',tid));pending=[]
  for side,nid in [('north',f'r{r-1:02}_c{c:02}'),('south',f'r{r+1:02}_c{c:02}'),('west',f'r{r:02}_c{c-1:02}'),('east',f'r{r:02}_c{c+1:02}')]:
   if nid in tiles and not tiles[nid]['fullCoverage']:pending.append({'side':side,'tileId':nid,'coreCount':tiles[nid]['coreCount']})
  t['incompleteFullNeighborsInZone']=pending
s.update(status='incremental_audit_complete_for_frozen_capture',completedAtUtc=now(),tiles=list(tiles.values()),newVisualEvidence={'cropCount':len(cm['cuts']),'boardCount':len(cm['boards']),'allActuallyViewed':True,'scale':1,'internalSeamsViewed':48,'internalJunctionsViewed':18,'changedRegionViews':10,'oldSailIssueCheck':1,'notPassedSamples':4,'newSharedEdgePairs':7,'newSharedEdgeSegments':28,'newCrossJunctions':2},reuse={'unchangedFullCandidates':16,'oldRemainingEdgePairs':13,'oldRemainingEdgeSegments':52,'oldCrossJunctions':5,'existingLocal8192Groups':2,'noFullMapRebuild':True},issues=issues,coverageTerminology={'coreCount':'unique 1024 grid coordinates covering current candidate, or selected usable coordinates in partial tiles; includes not-passed sources when a complete candidate exists','candidateCoverageCores':357,'usableSelectedCoreCount':350,'difference':'7 candidate-used sources remain excluded by newer quick/usable selection; r08c10 p24-v03 (1), r13c13 (6)','versionCountNeverUsedAsUniqueCoreCount':True},metadataConflicts=[{'tileId':'r08_c10','producerSummaryCallsTileMissing':True,'fullCandidateExists':True,'internalWorkerReviewRecordedPassed':True,'sourceManifestInternalAccepted':False,'selectedUsable':15,'candidateCoverage':16,'resolution':'coverage 16, producer status conflict disclosed; this independent internal review passed actual current candidate.'},{'tileId':'r13_c13','selectedUsable':10,'candidateCoverage':16,'resolution':'candidate full not passed; selected usable count 10 retained separately.'},{'tileId':'r14_c11','producerSummaryCallsTileMissing':True,'fullCandidateExists':True,'internalPassed':False,'resolution':'full pending-repair candidate counted; never formally accepted.'}],reports={n:str(OUT/n) for n in ['current-candidates.json','repair-queue.json','crop-manifest.json','source-replay.json','evidence-reuse.json','saved-unselected.json','source-checks.json','source-stability.json','review.md']})
write('summary.json',s);write('current-candidates.json',{'capturedAtUtc':s['snapshotCompletedAtUtc'],'zone':'southeast','candidates':[{k:v for k,v in t.items() if k not in ['selectedNativeCores','productionRecord']} for t in tiles.values() if t['file']],'formalAccepted':0})
seen={x['file']:x for x in checks};changes=[]
for p,x in seen.items():
 current=sha(p) if Path(p).exists() else None
 if current!=x['sha256']:changes.append({'file':p,'frozenSha256':x['sha256'],'endSha256':current,'includedInFrozenCounts':False})
write('source-checks.json',{'checks':list(seen.values()),'allStableDuringRead':all(x['stableDuringRead'] for x in seen.values())})
write('source-stability.json',{'checkedAtUtc':now(),'checkedInputs':len(seen),'changes':changes,'frozenCaptureRetained':True,'newPostCaptureFilesNotPursued':True})
rows=[]
for tid,t in tiles.items():
 if t['file']:rows.append(f"| {tid} | [{Path(t['file']).name}]({Path(t['file']).as_posix()}) | `{t['sha256']}` | {t['qaStatus']} |")
report=f'''东南本批独立检查完成，冻结于 {s['snapshotCompletedAtUtc']}。目标49块，完整候选21块（生产采用18、其余3），部分3块、空白25块；正式验收0。现有候选像素覆盖357个唯一1024核心；当前可用选中核心350，差7个是完整待修候选使用的未通过来源。版本数量不计作唯一核心。

本批只读原素材和生产记录，仅在本目录保存检查证据。没有生图、AI修图、修改生产源或共享Git，也没有重建整张地图。输入哈希未变的16个完整候选沿用旧检查；13对旧共享边52段、5个交点逐裁片确认当前像素一致，原8192局部拼接2组直接复用。

r08_c10 v02 的24条内部缝和9个交点已按原像素检查通过，实际东侧与 r08_c11 的4段共享边通过。生产简表仍把本块写作缺片，p24-v03快查记录仍待修，均保留为记录冲突；本次内部结论仅绑定表内候选hash。

r14_c14 v01 的24条内部缝和9个交点通过。北侧 r13_c14 无完整候选，西侧 r14_c13 仅11个选中可用核心；这些外边不能宣布通过。东、南为世界边界。

r12_c13 v04 以注册1024原生核心修正木板竖直明暗带，10处变化缝、交点、所有权边和整体裁片通过。与旧v03相比，其余像素不变；旧帆横杆裁片仍为完全相同像素，旧问题继续保留。整块不在本次独立检查中升级为内部全通过。

r14_c11 和 r13_c13 都已保存4096完整候选，内部水纹矩形带、接缝或帆杆仍待修。已实看其实际北/东或北/西共享边，几何延续但材质不通过。r13_c11 北东材质带以及木柱旁旧水面矩形问题未有新源图，继续保留。

本批新查111张原像素裁片：两块66项内部缝/交点、10处木板修补证据、1处旧帆杆、4处待修例证、7对共享边28段、2个四块交点。所有裁片和24张等比例排版板均实际查看。7对共享边中3对局部通过（r08c10/11、r11c13/r12c13、r12c12/13），4对材质待修。2个新增四块交点保持材质待修。

可先查看旧证据及生产状态均未变的 r10_c12，其生产记录为本地画稿验收就绪；正式总验收仍由协调者处理。

[逐块JSON](current-candidates.json)、[待修清单](repair-queue.json)、[实看裁片清单](crop-manifest.json)、[源像素复算](source-replay.json)、[复用证据](evidence-reuse.json)、[输入变化](source-stability.json)。本批结束后发现的更新另列，不追入冻结统计。

| 坐标 | 当前4096原文件 | SHA-256 | 当前QA |
|---|---|---|---|
'''+ '\n'.join(rows)+'\n'
(OUT/'review.md').write_text(report,encoding='utf-8')
print(json.dumps({'summary':str(OUT/'summary.json'),'counts':s['counts'],'newViewedCuts':len(cm['cuts']),'sourceReplayCandidates':len(proof['newCandidateReplays']),'reusedEdges':len(reuse),'reusedCrosses':len(crossreuse),'endChanges':changes},ensure_ascii=False))
