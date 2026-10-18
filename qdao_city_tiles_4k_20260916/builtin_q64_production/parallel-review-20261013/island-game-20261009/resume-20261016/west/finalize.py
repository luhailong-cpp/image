exec((__import__('pathlib').Path(__file__).parent/'audit.py').read_text(encoding='utf-8').split('oldraw=')[0])
import numpy as np
j=read(OUT/'prepared.json');tm={t['tileId']:t for t in j['tiles']}
old=read(REVIEW/'resume-v03/west/summary.json');late=read(REVIEW/'resume-v03/west-late/summary.json')
# Recheck only the new effective candidate ancestry. The v5 base is already reviewed v4.
replay=[]
def check_repair(tid,rp,stop_hash=None):
 rec=read(rp);checks=[]
 if 'repairSource' not in rec:
  npz=rec['provenance'];assert sha(npz['path'])==npz['sha256'];mask=np.load(npz['path'])['tile_source_id'];out=np.asarray(Image.open(rec['output']['path']).convert('RGB'));bad=covered=0
  for sid,s in enumerate(rec['sources']):
   assert sha(s['path'])==s['sha256'];src=np.asarray(Image.open(s['path']).convert('RGB'));ys,xs=np.nonzero(mask==sid);sy=ys+115-(sid//4)*1024;sx=xs+115-(sid%4)*1024;b=int(np.count_nonzero(np.any(out[ys,xs]!=src[sy,sx],axis=1)));covered+=len(xs);bad+=b
  checks.append({'kind':'root_native_source_id_replay','tileId':tid,'file':rec['output']['path'],'sha256':sha(rec['output']['path']),'sourceCount':len(rec['sources']),'verifiedPixels':covered,'pixelMismatchCount':bad,'sourceIdPlaneHashMatches':True})
  return checks
 base=rec['base']['image'];repair=rec['repairSource'];maskrec=rec['mask'];assert sha(base['path'])==base['sha256'];assert sha(repair['path'])==repair['sha256'];assert sha(maskrec['path'])==maskrec['sha256']
 if base['sha256']!=stop_hash:checks.extend(check_repair(tid,rec['base']['record']['path'],stop_hash))
 a=np.asarray(Image.open(base['path']).convert('RGB')).copy();b=np.asarray(Image.open(repair['path']).convert('RGB'));mask=np.asarray(Image.open(maskrec['path']).convert('L'));assert set(np.unique(mask)).issubset({0,255});x0,y0,x1,y1=rec['cropBox'];sel=mask==255;a[y0:y1,x0:x1][sel]=b[sel];out=np.asarray(Image.open(rec['output']['path']).convert('RGB'));bad=int(np.count_nonzero(np.any(a!=out,axis=2)));checks.append({'kind':'same_coordinate_binary_repair_replay','tileId':tid,'record':norm(rp),'file':rec['output']['path'],'sha256':sha(rec['output']['path']),'repairSource':repair['path'],'repairSourceHashMatches':True,'maskHashMatches':True,'verifiedPixels':16777216,'pixelMismatchCount':bad,'priorBaseEvidenceReused':base['sha256']==stop_hash})
 return checks
for tid,stop in [('r05_c02','8fcfd28eb1c43e947a29db43a3b00969695187fb6e35b7c3c27b197124f91ecd'),('r07_c04',None)]:replay.extend(check_repair(tid,tm[tid]['candidateStatusRecord']['record']['path'],stop))
save('owner-candidates-pixel-replay.json',{'checks':replay,'allZeroMismatches':all(c['pixelMismatchCount']==0 for c in replay),'note':'Native pixel provenance only; not visual or formal acceptance.'})
# Every board listed here has actually been viewed at original pixel scale in this batch.
for e in j['edges']:
 e.update(actuallyViewed=True,viewedAtOriginalPixelScale=True,status='local_shared_edge_no_obvious_geometry_break',finding='Inspected 128px on either side of the native core boundary; limited local observation only.')
for b in j['boards']:b.update(actuallyViewed=True,viewedAtOriginalPixelScale=True)
for c in j['crossings']:c.update(actuallyViewed=True,viewedAtOriginalPixelScale=True,status='local_junctions_no_obvious_geometry_break')
for e in j['ownerDeltaEdges']:
 if e['identicalToPriorReviewedPixels']:e.update(status='prior_pixel_identical_local_observation_reused',priorPassOrPendingPreserved=True)
 else:e.update(actuallyViewed=True,viewedAtOriginalPixelScale=True,status='local_shared_edge_no_obvious_geometry_break',finding='Current explicit owner candidate actually inspected at original pixel scale; no whole-object or formal acceptance inferred.')
for b in j['ownerDeltaBoards']:b.update(actuallyViewed=True,viewedAtOriginalPixelScale=True)
for c in j['ownerDeltaCrossings']:c.update(actuallyViewed=True,viewedAtOriginalPixelScale=True,status='local_junctions_no_obvious_geometry_break')
focus=read(OUT/'focus-crops.json')
for f in focus:f.update(actuallyViewed=True,viewedAtOriginalPixelScale=True)
save('focus-crops.json',focus)
# Preserve prior unresolved findings; changed former edge inputs are marked for reconciliation.
issues={i['id']:dict(i,origin='prior_frozen_visual_evidence') for i in old['issues']}
issues.update({i['id']:dict(i,origin='prior_west_late_frozen_visual_evidence') for i in late['issues']})
for iid in ['r07c04-north-flower-cut','r07c04-north-paving-material']:
 if iid in issues:issues[iid].update(status='current_pair_material_and_whole_object_reconciliation_pending',currentCandidate=tm['r07_c04']['file'],currentFinding='Current v4 changed this side. New narrow native crops no longer justify copying the old geometry-failure assertion unchanged; whole-object/material closure is still pending.',currentEvidence=norm(OUT/'owner-delta-board-h-01-100pct.png'))
newissues=[
 {'id':'r07c04-r08c04-paving-focus-transition','tiles':['r07_c04','r08_c04'],'status':'material_repair_or_paired_acceptance_required','worldApproxBox':[14336,28544,15360,28928],'finding':'Current paired crop shows a pronounced change from sharp northern paving to soft southern paving in r08_c04; stone outlines continue but material is not closed.','evidence':norm(OUT/'owner-delta-board-h-03-100pct.png'),'origin':'current_actual_visual_review'},
 {'id':'r06c02-row2-retained-leaf-band','tiles':['r06_c02'],'status':'localized_material_and_foliage_shape_review_required','worldApproxBox':[4096,21580,5120,21660],'finding':'The expanded s11/s21 native crop contains a short straight foliage transition approximately 115px below the nominal core boundary, most visible at its left end. Retain for local repair/owner confirmation.','evidence':norm(OUT/'focus-012-r06_c02-s11--r06_c02-s21.png'),'origin':'current_actual_visual_review'},
 {'id':'r12c04-deck-repair-left-edge','tiles':['r12_c04'],'status':'localized_geometry_repair_required','tileApproxBox':[3500,1100,3650,1450],'finding':'Small beam lower-edge step at the left boundary of the deck repair remains a local open item; current 100% context reviewed.','evidence':norm(OUT/'r12_c04-deck-left-repair-boundary.png'),'origin':'current_actual_visual_review_and_production_pending_record'},
 {'id':'r12c04-stair-wall-turn','tiles':['r12_c04'],'status':'layout_reconciliation_required','tileApproxBox':[650,1700,1200,2300],'finding':'The stair/low-wall turn has abrupt course changes and still requires layout reconciliation as recorded by production; native context was inspected.','evidence':norm(OUT/'r12_c04-stair-turn.png'),'origin':'current_actual_visual_review_and_production_pending_record'},
 {'id':'r12c04-stamen-cluster-owner-confirmation','tiles':['r12_c04'],'status':'production_recorded_object_review_pending','finding':'Production requests confirmation of the right stamen cluster. The current flower-center context was inspected, but that limited crop does not close the full-object item.','evidence':norm(OUT/'r12_c04-stamen-context.png'),'productionEvidence':norm(PROD/'southwest/qa/central-r12c04-review-20261013.json'),'origin':'production_pending_item_retained'}]
issues.update({i['id']:i for i in newissues});issues=list(issues.values());save('repair-queue.json',issues)
def touches(issue,tid):return issue.get('tileId')==tid or tid in issue.get('tiles',[]) or tid in issue.get('pair',[])
candidates=[]
for t in j['tiles']:
 if not t['fullCoverage'] or not t.get('file'):continue
 ca=t['candidateStatusRecord'];qr=ca.get('qaRecord',ca) if ca else {};internal=qr.get('internalClosurePassed',qr.get('internalPassed',False));pending=[i['id'] for i in issues if touches(i,t['tileId'])]
 qa={'internalProductionRecordedPassed':internal,'internalEvidence':'existing_current_candidate_hash_unchanged_evidence_reused' if t['priorEvidenceReusable'] else 'changed_regions_and_affected_native_edges_actually_viewed; complete_production_closure_still_pending','outerEdges':'local_shared_edges_checked_or_reused; full_perimeter_pending','pendingRepairIds':pending,'evidenceReused':t['priorEvidenceReusable'],'formalAccepted':False,'nativePixelProvenance':'reused_current_hash_evidence' if t['priorEvidenceReusable'] else 'current_native_pixel_replay_zero_mismatch' if t['tileId'] in ['r05_c02','r07_c04','r12_c04'] else 'diagnostic_exact_native_core_assembly'}
 if t['tileId']=='r07_c04':qa['productionPendingFindings']=qr.get('pendingFindings',[])
 t['QA']=qa
 candidates.append({'tileId':t['tileId'],'zone':t['zone'],'file':t['file'],'sha256':t['sha256'],'dimensions':t['dimensions'],'adopted':t['adopted'],'diagnosticOnly':t.get('diagnosticOnly',False),'QA':qa,'selectedCoreCount':t['coreCount'],'priorEvidence':t['priorEvidence']})
assert len(candidates)==28 and all(c['dimensions']==[4096,4096] for c in candidates)
save('current-candidates.json',{'frozenAtUtc':j['frozenAtUtc'],'scope':'98 NW/SW owner coordinates; parallel reservations counted only by their dedicated worker','candidateCount':len(candidates),'adoptedCount':sum(c['adopted'] for c in candidates),'formalAcceptedCount':0,'candidates':candidates})
# Current-input-only end check, once. Later production edits are a separate delta.
allimages={s['path']:s['sha256'] for t in j['tiles'] for s in t['selectedSources']}
allimages.update({t['file']:t['sha256'] for t in j['tiles'] if t.get('file')});endchanges=[]
for p,h in allimages.items():
 actual=sha(p)
 if actual!=h:endchanges.append({'path':p,'frozenSha256':h,'endSha256':actual})
endmeta=[]
for m in j['metadata']:
 h=sha(m['path'])
 if h!=m['sha256']:endmeta.append({'path':m['path'],'frozenSha256':m['sha256'],'endSha256':h})
save('end-input-check.json',{'checkedAtUtc':now(),'checkedImageCount':len(allimages),'changedImages':endchanges,'changedMetadata':endmeta,'frozenBaselineNotRefreshed':True})
contracts=[]
for s in j['changedSelectedCores']:
 rp=Path(s['path']+'.generation.json');d=read(rp) if rp.exists() else {};tid=s['tileId'];x=(int(tid[5:7])-1)*4096+(s['subcolumn']-1)*1024;y=(int(tid[1:3])-1)*4096+(s['subrow']-1)*1024;box=[x,y,x+1024,y+1024];coords=d.get('coordinates',{}).get('coreGlobalBox');contracts.append({'tileId':tid,'subrow':s['subrow'],'subcolumn':s['subcolumn'],'path':s['path'],'sha256':s['sha256'],'dimensions':s['dimensions'],'nativeSizeValid':s['dimensions']==[1254,1254],'recordedImageHashMatches':d.get('sha256')==s['sha256'],'expectedCoreGlobalBox':box,'recordedCoreGlobalBox':coords,'coordinateRecordMatches':coords==box if coords is not None else None,'actualModel':d.get('actualModel'),'modelEvidence':'actual model not returned' if d.get('actualModel') is None else d['actualModel']})
save('new-core-contract-check.json',contracts)
j.update(status='completed_frozen_incremental_west_review',completedAtUtc=now(),currentCandidates=norm(OUT/'current-candidates.json'),issues=issues,focusCrops=focus,endInputCheck=norm(OUT/'end-input-check.json'),frozenImagesUnchangedAtEnd=not endchanges,metadataChangedAfterFreeze=bool(endmeta),effectiveChangedCandidateCount=3,unchangedAdoptedCandidateCount=24,ownerPixelReplay=norm(OUT/'owner-candidates-pixel-replay.json'))
j['reviewCounts']={'initialNativeSegmentsActuallyViewed':len(j['edges']),'ownerResolvedChangedSegmentsActuallyViewed':sum(e['actuallyViewed'] for e in j['ownerDeltaEdges']),'ownerResolvedPixelIdenticalSegmentsReused':sum(e['identicalToPriorReviewedPixels'] for e in j['ownerDeltaEdges']),'initialBoardsActuallyViewed':len(j['boards']),'ownerDeltaBoardsActuallyViewed':len(j['ownerDeltaBoards']),'nineJunctionBoardsActuallyViewed':4,'focusCropsActuallyViewed':len(focus)+1,'newSelectedNativeCoordinates':len(j['changedSelectedCores'])}
save('summary.json',j)
# Quickly usable stable group: internal/shared edges only; perimeter remains pending.
readyids=['r10_c03','r10_c04','r11_c03','r11_c04'];ready=[c for c in candidates if c['tileId'] in readyids]
save('quick-delivery-group.json',{'tiles':ready,'QA':'Current four 4096 images hash-identical to the prior reviewed group; internal and group shared-edge evidence reused. Whole perimeter and formal acceptance remain pending.','priorGroupEvidence':norm(REVIEW/'southwest-audit-v01/review.md'),'formalAccepted':False})
lines=['# 八仙岛西区：10 月 16 日增量检查','',f"本轮已按一次冻结快照完成西北／西南既有素材检查。98 坐标中，{j['totals']['fullCoverageCount']} 坐标有 16 个有效选中核心、{j['totals']['partialCount']} 坐标为部分覆盖、{j['totals']['emptyCount']} 坐标无本区选中核心；有效核心 {j['totals']['selectedCoreCount']}/1568，缺 {j['totals']['missingCoreCount']}。正式验收仍为 0。独占划拨的 8 个西北坐标由专工另计，本表保留其本区选中数 0，不声称那些坐标没有平行产出。",'',f"现有可查看完整 4096 图 28 张，其中明确采用 27 张、独立诊断硬拼 1 张（r08_c02）。[逐张文件、hash、尺寸与 QA](current-candidates.json)；[98 坐标与证据](summary.json)。",'', 'r05_c02=v5、r07_c04=v4 来自冻结的分工 owner 明确选用清单。汇总 current-adopted 索引仍分别指 v4 和漏列，已记录[选用依据及索引差异](selection-authority-resolution.json)。不按文件新旧推断采用。', '', '可以先查看的稳定四图小组：内部及组内相邻边沿用输入 hash 未变的既有证据，外围仍待齐片验收：','']
for c in ready:lines.append(f"- [{c['tileId']} · 4096×4096]({c['file']})")
lines+=['','新增采用图与 QA：','',f"- [r05_c02 v5]({tm['r05_c02']['file']})：比既有 v4 仅左下 819,133 像素改变；变边、九交点和下部整段原尺寸查看，未见明显的新几何错断。北部旧问题保留，完整生产收口按冻结 owner 状态待定。",f"- [r07_c04 v4]({tm['r07_c04']['file']})：采用 owner 实际版本；已查看变化边及九交点，墙脚／勾缝旧收口项目仍按生产记录待修。南接 r08_c04 存在显著地面清晰度差，保留材质待修。",f"- [r12_c04 当前候选]({tm['r12_c04']['file']})：17 个源的 16,777,216 像素回放 0 不匹配。已查看全部 24 内边与九交点，木梁修补左缘小台阶、台阶转折及花蕊整物确认仍未通过。",'',f"与 v03 相比新增 45 个有效选中核心；另外 {len(j['postBaselineUnselectedNativeFiles'])} 个基线后落盘而未被本次冻结选择采用的源文件单列，不计作新增核心。r03_c01 为 5/16、r06_c02 为 13/16；后者局部叶片留边需核查，未以暂缓当通过。",'',f"初查实际查看 92 段，owner 版本订正后补看 40 个变段、32 段逐像素相同直接复用；所有查看板均保存原像素，没有放大或重建 8192 总览。[待修清单](repair-queue.json)、[新核心合同核对](new-core-contract-check.json)、[新采用图像素回放](owner-candidates-pixel-replay.json)。",'',f"冻结时刻 UTC：{j['frozenAtUtc']}。结束仅复核当前输入，图像 hash {'全部未变' if not endchanges else '发生变化，见结束核对'}；元数据后续变化 {len(endmeta)} 项另记[结束核对](end-input-check.json)，不无限追随生产更新。",'', '本轮生成调用 0，生产目录写入 0，共享 Git 操作 0。']
(OUT/'review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'status':j['status'],'totals':j['totals'],'changedFrozenImages':endchanges,'laterMetadataChanges':len(endmeta),'newCoreContractIssues':[c for c in contracts if not c['nativeSizeValid'] or not c['recordedImageHashMatches'] or c['coordinateRecordMatches'] is False],'replayMismatchCounts':[c['pixelMismatchCount'] for c in replay],'files':[norm(OUT/n) for n in ['summary.json','current-candidates.json','review.md','quick-delivery-group.json']]},ensure_ascii=False,indent=2))
