from pathlib import Path
from datetime import datetime, timezone
from PIL import Image,ImageDraw,ImageFont
import copy,json,hashlib
B=Path('D:/work/image/qdao_city_tiles_4k_20260916');P=B/'builtin_q64_production/parallel_20261005';A=P/'parent_audit_20261008'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def dump(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();ip=A/'verified-current-index.json';old=read(ip);assert old['summary']['completePixelCandidateCount']==53
before=ref(ip);numbers={'tianyong_festival':'01','lanxian_day':'02','lanxian_spring':'03','donghai_day':'04','donghai_lantern':'05','penglai_day':'06','penglai_mid_autumn':'07'}
threads={'tianyong_festival':'01a10bad-0c92-7f93-8a5b-4ae4ec120204','lanxian_day':'01a10baf-7a48-7811-ba55-23983983a89d','lanxian_spring':'01a10bb2-5cf3-7db0-a7f1-5c85ef972ed1','donghai_day':'01a10ba3-b9ef-7c02-b277-345815c70f88','donghai_lantern':'01a10ba6-0b1f-75d0-b1ef-9137fcf00fed','penglai_day':'01a10ba6-e6fa-7390-b78d-21394b0a60ef','penglai_mid_autumn':'01a10ba7-d61e-7742-870d-85174acc5a1e'}
removed={'lanxian_day','lanxian_spring'};apps=[copy.deepcopy(a) for a in old['appearances'] if a['appearance'] not in removed];assert sum(len(a['entries']) for a in apps)==39
active=[a['appearance'] for a in apps]
hist=A/'historical-seven-appearances-53-before-cancellation.json';assert not hist.exists();oldpreview=A/'overview-seven-appearances-53-historical.jpg';assert not oldpreview.exists();oldpreview.write_bytes((A/'overview.jpg').read_bytes())
dump(hist,{'recordRole':'historical_cancelled_scope_snapshot_not_current_delivery','archivedAtUtc':now,'reason':'User explicitly cancelled appearances02 and03; retained for evidence only.','originalIndex':before,'preservedPreview':ref(oldpreview),'snapshot':old})
receipt=P/'town-cancellation-thread-receipt-20261008.json';assert receipt.exists()
scope={'schemaVersion':1,'authority':'latest_explicit_user_scope','effectiveAtUtc':now,'effectiveDateUserTimezone':'2026-10-08','userTimezone':'America/New_York','userInstructionsVerbatim':['02、03 都取消','取消吧'],'supersedes':'Earlier seven-appearance production requirements, old dispatch list and historical manifests; these do not reauthorize removed appearances.','status':'five_appearances_in_production_two_cancelled','activeAppearanceIds':active,'activeAppearances':[{'originalNumber':numbers[a['appearance']],'appearance':a['appearance'],'title':a['title'],'threadId':threads[a['appearance']]} for a in apps],'removedAppearances':[{'originalNumber':numbers[a['appearance']],'appearance':a['appearance'],'title':a['title'],'threadId':threads[a['appearance']],'productionCancelled':True,'includedInCurrentDelivery':False,'previousVerifiedCandidateCount':len(a['entries'])} for a in old['appearances'] if a['appearance'] in removed],'targetCityCount':5,'targetCityPixels':[65536,65536],'targetTilePixels':[4096,4096],'targetTilesPerAppearance':256,'targetTotalTiles':1280,'currentVerifiedCandidateCount':39,'currentMissingTiles':1241,'countBasis':ref(hist),'route':'builtin_image_gen_only','paidApiAllowed':False,'preserveExistingImagesAndProvenance':True,'removedAppearancesMayBeRepublished':False,'threadStateEvidence':ref(receipt),'threadStateNote':'Separate root receipt is authoritative for stop/archive actions. This scope edit sent no task messages and made no thread-state changes.','futurePublicationRule':'Use only activeAppearanceIds in production and current delivery. Any new coordinate requires a separate source audit.','historicalDispatchIndex':'dispatch-index.json'}
scopepath=P/'production-scope.json';dump(scopepath,scope)
for a in apps:a['originalNumber']=numbers[a['appearance']]
I={'schemaVersion':2,'createdAt':old['createdAt'],'updatedAt':now,'observedAt':now,'snapshotScope':'按用户最新取消要求，仅保留原编号01/04/05/06/07五套；39/1280完整像素候选，另附五个同坐标父修补。来源沿用取消前已核验53块快照，不计任何未审计新图。','productionScope':ref(scopepath),'appearances':apps,'summary':dict(old['summary'],completePixelCandidateCount=39,targetTileCount=1280,missingFullPixelCoordinates=1241,targetCityCount=5),'historicalSevenAppearanceSnapshot':ref(hist),'scopeChange':{'userInstructionsVerbatim':scope['userInstructionsVerbatim'],'removedAppearanceIds':sorted(removed),'removedCandidateCount':14,'remainingSelectedEntriesUnchanged':True,'newCoordinatesAdded':0,'imagesDeleted':0,'imageSourcesModified':0},'sourceAudits':[s for s in old['sourceAudits'] if '/town/' not in s['path']],'qaPolicy':old['qaPolicy'],'modelPolicy':old['modelPolicy'],'parentRepairPolicy':old['parentRepairPolicy'],'parentRepairPackage':copy.deepcopy(old['parentRepairPackage']),'latestCompleteCoordinateCountAudit':ref(scopepath),'latestDeltaAudit':ref(scopepath),'activeIncompleteWork':{'note':'继续五套当前制作。02/03 已取消，不再纳入当前制作或交付。未完成片段与未经审计新图不计数。'},'aggregationRevalidation':{'scope':'Selection filtering only; active entries, source SHA strings and parent repair package preserved verbatim from the53 snapshot. No new artwork QA claimed.','sourceSnapshot':ref(hist),'retainedCompleteCoordinateCount':39,'cancelledCompleteCoordinateCount':14,'parentRepairAlternativeCount':5}}
assert I['parentRepairPackage']==old['parentRepairPackage'];assert len([e for a in apps for e in a['entries'] if 'parentRepairCandidate' in e])==5
# Preserve original numbering; this is a mechanical preview only.
W,H=1808,1470;im=Image.new('RGB',(W,H),'#eef2f7');dr=ImageDraw.Draw(im)
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if b else 'C:/Windows/Fonts/msyh.ttc',n)
dr.text((28,20),'五套主城 · 当前制作范围',font=font(32,True),fill='#1d2d44');dr.text((28,70),'完整像素候选 39 / 1280  |  原编号02、03已取消  |  5套均未完成  |  灰格为缺块',font=font(20),fill='#4d5c70')
sources=[];groups=[]
for j,a in enumerate(apps):
 x,y=28+(j%2)*888,116+(j//2)*450;dr.rounded_rectangle((x,y,x+864,y+426),radius=16,fill='white',outline='#d9e1eb',width=2);dr.text((x+18,y+16),f"{a['originalNumber']}  {a['title']}",font=font(24,True),fill='#1d2d44');dr.text((x+694,y+18),f"{len(a['entries'])} / 256 块",font=font(21),fill='#476483')
 coords={(int(e['tileId'][1:3]),int(e['tileId'][5:7])):e for e in a['entries']};r0,r1=min(r for r,c in coords),max(r for r,c in coords);c0,c1=min(c for r,c in coords),max(c for r,c in coords)
 dr.text((x+18,y+48),f'范围 r{r0:02d}–r{r1:02d} / c{c0:02d}–c{c1:02d} · 缩略预览，不是原尺寸验收',font=font(14),fill='#778392');size=min(112,784//(c1-c0+1),336//(r1-r0+1));gx,gy=x+(864-(c1-c0+1)*size)//2,y+71+(336-(r1-r0+1)*size)//2;holes=[]
 for r in range(r0,r1+1):
  for c in range(c0,c1+1):
   px,py=gx+(c-c0)*size,gy+(r-r0)*size;tid=f'r{r:02d}_c{c:02d}';e=coords.get((r,c))
   if e:
    assert sha(e['path'])==e['sha256'];src=Image.open(e['path']).convert('RGB');assert src.size==(4096,4096);im.paste(src.resize((size,size),Image.Resampling.LANCZOS),(px,py));src.close();sources.append({'appearance':a['appearance'],'originalNumber':a['originalNumber'],'tileId':tid,'path':e['path'],'sha256':e['sha256'],'destinationRectXYWH':[px,py,size,size],'resampling':'LANCZOS downsampling only'})
   else:holes.append(tid);dr.rectangle((px,py,px+size-1,py+size-1),fill='#5d697a');dr.text((px+size//3,py+size//3),'缺块',font=font(20),fill='#dce1e9')
   dr.rectangle((px,py,px+size-1,py+size-1),outline='#edf0f4');dr.rectangle((px+2,py+2,px+73,py+18),fill='#1d2d44');dr.text((px+4,py+2),tid,font=font(11),fill='white')
 groups.append({'appearance':a['appearance'],'originalNumber':a['originalNumber'],'missingCoordinatesInsideBBox':holes})
x,y=916,1016;dr.rounded_rectangle((x,y,x+864,y+426),radius=16,fill='#1d2d44');dr.text((x+28,y+30),'当前五套候选总数',font=font(25,True),fill='#dce5ef');dr.text((x+28,y+82),'39 / 1280',font=font(58,True),fill='white');dr.text((x+28,y+164),'尚缺完整像素图块 1241 块',font=font(24,True),fill='#f5c963')
for n,t in enumerate(['正式验收：0 块    整套完成：0 / 5','原编号保留：01、04、05、06、07。','02小镇日景、03小镇春节已从交付范围移除。','已制图片和来源记录保留，未删除素材。','5个同坐标父修补不重复计数；接缝仍需检查。']):dr.text((x+28,y+224+n*33),t,font=font(19),fill='#dce5ef')
assert sha(ip)==before['sha256'];im.save(A/'overview.jpg',quality=94,subsampling=0)
I['preview']={'path':(A/'overview.jpg').as_posix(),'sha256':sha(A/'overview.jpg'),'pixels':[W,H],'createdAt':now,'kind':'mechanical-downsample-contact-sheet-only','notGameAsset':True,'notWholeCity':True,'sourcePixelsGenerated':False,'sourcePixelsModified':False,'sources':sources,'groups':groups,'visualReview':{'status':'pending_layout_review'}};dump(ip,I)
S=read(B/'status.json');S['historicalScopeBeforeTownCancellation']={'recordedAtUtc':now,'plannedMapVariants':7,'plannedTotalDeliveryTiles':1792,'candidateCount':53,'index':ref(hist),'priorScopeDecision':copy.deepcopy(S['scopeDecision']),'priorAllSevenMapVariantsComplete':S.pop('allSevenMapVariantsComplete',False),'priorFullCityReferenceCount':S['fullCityReferenceCount'],'priorAllSevenSourceHandoffsReady':S['handoff'].pop('allSevenSourceHandoffsReady',None)}
S.update(status='five_city_appearances_in_progress_two_cancelled',updatedAtUtc=now,scope='Five active appearances01/04/05/06/07:39 verified complete-pixel4K candidates of1280;1241 missing,0 formal accepted,0/5 complete cities.02/03 cancelled; existing artwork/provenance retained.',plannedMapVariants=5,plannedTotalDeliveryTiles=1280,allActiveMapVariantsComplete=False,generated4KCandidateCount=39,currentSelectedCandidateCoordinateCountAllAppearances=39,currentBatchSha256=sha(ip),candidatePreviewSha256=sha(A/'overview.jpg'),candidatePreviewMeaning='39-coordinate active five-appearance snapshot.02/03 excluded after explicit cancellation. Five parent repair alternatives add zero.',fullCityReferenceCount=5)
S['productionScope']=ref(scopepath);S['fullCityReferenceCountMeaning']='Five references are in active production scope; seven historical reference images remain preserved.';S['scopeDecision']={'pending':False,'userResponseReceived':True,'decision':'User cancelled02小镇日景 and03小镇春节; continue original01/04/05/06/07 only. Builtin route, no paid API.','userInstructionsVerbatim':scope['userInstructionsVerbatim'],'authority':ref(scopepath),'productionAccepted':0,'currentCompletePixelCandidateCount':39,'remainingFullPixelCoordinates':1241};S['candidateFiles']=[Path(e['path']).relative_to(B).as_posix() for a in apps for e in a['entries']]
S['continuationWork']['productionScope']=ref(scopepath);S['continuationWork']['remaining']='Finish only active appearances01/04/05/06/07, remaining seams/junctions, shared geometry/navigation and client validation.';S['continuationWork']['dispatchIndexMeaning']='Historical seven-task creation log, not current authorization.';S['handoff']['allActiveSourceHandoffsReady']=True
S['activeProductionRun'].update(updatedAtUtc=now,appearances=active,productionScope=ref(scopepath),currentCompletePixelCandidateCount=39,remainingFullPixelCoordinates=1241,targetCityCount=5,targetTotalTiles=1280,countMeaning='39 active complete-pixel coordinates from the verified53 snapshot after removing14 cancelled town coordinates; historical baseline counters do not define active scope.')
S['latestContinuation'].update(updatedAtUtc=now,currentWorkingCoordinates=39,role='verified_partial_five_appearance_snapshot_with_parent_repair_alternatives',productionScope=ref(scopepath),latestLiveDelta=ref(scopepath));S['latestContinuation']['checkpoint']['sha256']=sha(ip);S['baselineSelectionCountMeaning']='Current candidateFiles contain39 active coordinates. Cancelled town candidates and earlier seven-appearance counts are preserved in historical evidence only.';S['counterMeaning']='39 unique complete-pixel4K candidates out of current1280 target, not formal acceptance. Five parent repairs add zero;02/03 excluded by user cancellation.';S['candidateVisualReview']={'status':'pending','actuallyViewed':False,'file':I['preview']['path'],'sha256':I['preview']['sha256'],'scope':'New five-card overview requires layout view.'};dump(B/'status.json',S)
session=read(P/'parent-session-20261008.json');session.update(task='Continue five active city appearance maps01/04/05/06/07 and deliver when actually complete',productionScope=ref(scopepath),activeAppearanceIds=active,cancelledAppearanceIds=sorted(removed),targetTotalTiles=1280,targetAppearanceCount=5,latestVerifiedCompletePixelCandidates=39,missingCompletePixelCandidates=1241,scopeUpdatedAtUtc=now);session['mobileStorageEstimateScope']='Existing estimate may describe historical seven-appearance scope; recalculate for current5/1280 before quoting.';session['doNot']=['Do not produce or publish cancelled02/03 appearances','Do not count partial alpha canvases or rejected-source assemblies','Do not relabel upscaled guide pixels as native detail','Do not overwrite active child selections','Do not treat local seam QA as whole-city or client acceptance','Do not recreate already-created task windows'];dump(P/'parent-session-20261008.json',session)
rows='\n'.join(f"| {a['originalNumber']} {a['title']} | {len(a['entries'])} | {256-len(a['entries'])} | 0 |" for a in apps)
(A/'README.md').write_text(f'''# 五套主城当前候选汇总

**当前39/1280块完整像素候选，尚缺1241块。正式验收0块，整套完成0/5。**

用户于2026-10-08明确要求“02、03 都取消”“取消吧”。当前仅制作与交付原编号01/04/05/06/07；02小镇日景与03小镇春节已移出范围，已有图片及来源证据保留。最新范围以[权威范围文件](../production-scope.json)为准，旧七套文档不再授权继续两套小镇。

| 套图 | 完整像素候选 | 尚缺/256 | 正式验收 |
|---|---:|---:|---:|
{rows}

[统一索引](verified-current-index.json) · [范围变更校验](scope-cancellation-validation.json) · [五处同坐标父修补](parent-repair-current-overlay-v3.json)

![五套当前区域缩略预览](overview.jpg)

总数仅从已核验53块快照移除两套各7块，未加入任何未审计新图。当前39块的选择、图像来源哈希、局部QA限制以及五处父修补保持不变；缩略图只用于查看区域布局，不表示完整地图或原尺寸验收。

渔村元宵日景铺地几何同步仍待完成；仙岛中秋r09_c14西侧树叶接缝尚未通过，北/东/南缺邻图。其他已记录的接缝、整城、寻路和客户端限制继续有效。

[取消前53块历史索引](historical-seven-appearances-53-before-cancellation.json)仅留作证据，不是当前交付清单。[取消任务的线程状态回执](../town-cancellation-thread-receipt-20261008.json)由父任务另行记录，本次范围编辑没有发送任务消息。
''',encoding='utf-8')
prows='\n'.join(f"| {a['originalNumber']} {a['title']} | `{a['appearance']}` | [来源]({a['appearance']}/handoff.json) | [进度]({a['appearance']}/progress.json) |" for a in apps)
(P/'README.md').write_text(f'''# 五套主城制作

用户于2026-10-08明确取消02小镇日景、03小镇春节。后续只制作与交付原编号01/04/05/06/07；[production-scope.json](production-scope.json)是当前权威范围，覆盖旧七套要求。每套256张4096×4096，整图65536×65536，继续内置生图、GPT Image2.5目标配置，不使用付费API。

| 任务 | 内部资产ID | 交接 | 当前任务进度 |
|---|---|---|---|
{prows}

[当前39块候选汇总与预览](parent_audit_20261008/README.md) · [统一索引](parent_audit_20261008/verified-current-index.json) · [五处同坐标父修补](parent_audit_20261008/parent-repair-current-overlay-v3.json)

**39/1280个完整4K候选，尚缺1241；正式验收0、完整城市0/5。** 本次仅按取消要求从已核验53块快照排除两套各7块，不加入未审计新图；父修补不增加坐标。

两套取消图的全部已有图片、来源与检查记录保留，未删除素材。[历史53块索引](parent_audit_20261008/historical-seven-appearances-53-before-cancellation.json)及[旧七任务创建记录](dispatch-index.json)仅供追溯，不能恢复已取消的制作范围。[线程状态回执](town-cancellation-thread-receipt-20261008.json)由父任务记录。

每张新图继续记录目标配置、真实提交参数、实际披露值与来源；内置未披露的实际型号/质量保持未确认。
''',encoding='utf-8')
bp=B/'README.md';t=bp.read_text(encoding='utf-8');_,rest=t.split('\n\n',1);bp.write_text('> **当前入口（2026-10-08范围变更）：仅保留原编号01/04/05/06/07五套，39/1280完整4K候选，尚缺1241，正式0、整套0/5。02小镇日景与03小镇春节已按用户要求取消，已有素材保留。** [当前汇总](builtin_q64_production/parallel_20261005/parent_audit_20261008/README.md) · [权威范围](builtin_q64_production/parallel_20261005/production-scope.json) · [五处父修补](builtin_q64_production/parallel_20261005/parent_audit_20261008/parent-repair-current-overlay-v3.json)\n\n> 以下旧正文和七套计数仅为历史资料；与当前权威范围冲突时，以最新范围为准，不再制作或交付02/03。\n\n'+rest,encoding='utf-8')
proof={'createdAtUtc':now,'status':'scope_updated_preview_layout_pending','scope':ref(scopepath),'historical53Snapshot':ref(hist),'activeIndex':ref(ip),'activeAppearanceIds':active,'originalNumbers':[numbers[a] for a in active],'target':1280,'completeCandidates':39,'missing':1241,'formalAccepted':0,'wholeCitiesComplete':0,'targetCityCount':5,'removedAppearanceIds':sorted(removed),'removedCandidates':14,'unauditedNewCoordinatesAdded':0,'sourceEntriesAndHashesPreserved':True,'fiveParentRepairAlternativesPreserved':True,'parentOverlay':old['parentRepairPackage']['path'],'parentOverlaySha256':old['parentRepairPackage']['sha256'],'imagesDeleted':0,'artworkModified':False,'historicalPreviewPreserved':ref(oldpreview),'currentPreview':ref(A/'overview.jpg'),'threadStateEvidence':ref(receipt),'taskMessagesSentByScopeEditor':0,'legacyPublisherScopeGuardAdded':True,'previewLayoutActuallyViewed':False};dump(A/'scope-cancellation-validation.json',proof);dump(A/'latest-publication-validation.json',proof)
print(json.dumps({'scope':ref(scopepath),'index':ref(ip),'count':39,'target':1280,'previewPending':True}))
