from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat()
inventory=json.loads((OUT/'north-input-inventory.json').read_text(encoding='utf-8-sig'))
metrics={r['slot']:r for r in json.loads((OUT/'north-candidate-registration.json').read_text(encoding='utf-8-sig'))}
timing=json.loads((ROOT/'run-timing.json').read_text(encoding='utf-8-sig'))
reasons={
 'run/E/03':'左持瓶手从前举经过身侧低位再后摆，修补旧03到04直接从胸前跳到背后的过渡；右手丹炉与下肢相位保持。',
 'run/E/11':'左持瓶手从后摆经过腰侧低位再前举，修补旧10到11直接跳到胸前的过渡；右手丹炉与下肢相位保持。',
 'run/NE/03':'左持瓶手经腰侧低位并由躯干/背包自然遮挡，再进入后摆，旧胸前持瓶姿态改为低位经过；右丹炉与双腿保持。',
 'run/NE/11':'左持瓶手先经腰侧低位自然遮挡，再进入前举，减少直接从后摆跳到胸前；右丹炉与双腿保持。'}
selection={}
for slot,reason in reasons.items():
 m=metrics[slot];p=ROOT/m['source'];rec=Path(str(p)+'.generation.json')
 record=json.loads(rec.read_text(encoding='utf-8-sig'));assert record['sha256']==hashlib.sha256(p.read_bytes()).hexdigest()
 record.update(visualStatus='static_reviewed',staticReviewed=True,reviewedAt=stamp,reviewNotes=reason,dynamicAccepted=False,exported=False)
 rec.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
 selection[slot]={'source':m['source'],'reason':reason,'staticReviewed':True,'sha256':m['sourceSHA256'],'generationRecord':rec.relative_to(ROOT).as_posix(),'inputRuntimeSHA256':m['runtimeInputSHA256'],'headAbove450AlphaIoU':m['headAbove450AlphaIoU'],'legsBelow760AlphaIoU':m['legsBelow760AlphaIoU']}
rows=[]
for inp in inventory:
 p=ROOT/inp['runtime'];assert hashlib.sha256(p.read_bytes()).hexdigest()==inp['sha256']
 _,d,n=inp['slot'].split('/');frame=int(n)
 hand='解剖右手丹炉、左手绿瓶保持；肩袖连接与握持可辨，无换手、多肢或明确腕反折。'
 leg='髋膝踝至鞋掌按该方向前后迈步，保留自然屈膝与透视；当前接地侧和抬脚侧可区分。'
 status='retain_current'
 if inp['slot'] in reasons:hand=reasons[inp['slot']];status='candidate_static_reviewed'
 if d=='NE' and frame in [13,14,15]:
  leg='按整条髋—膝—踝—鞋长轴复看，屏幕左下支撑靴鞋头偏屏幕右形成过强侧向钩转；需保留抬跟推蹬而收回NE纵深。已转交full_combat修正，不在本选表冒报通过。'
  status='repair_delegated_to_full_combat'
 rows.append({**inp,'phase':timing['directions'][d]['phases'][frame-1],'frameMs':75,'handsReview':hand,'legsReview':leg,'decision':status,'visualEvidence':[f'preview/run-{d}-contact.png',f'provenance/limbs-20261004/north-{d}-{1 if frame<=8 else 9:02d}-{8 if frame<=8 else 16:02d}-hands.jpg',f'provenance/limbs-20261004/north-{d}-{1 if frame<=8 else 9:02d}-{8 if frame<=8 else 16:02d}-legs.jpg']})
review={'reviewedAt':stamp,'scope':['run/N','run/NE','run/E','run/SE'],'reviewedFrameCount':64,'method':'Re-read current runtime: four full contact sheets, all 64 hands and legs in sixteen enlarged regional sheets; suspicious full native runtime views; four candidate full-canvas exports reviewed in final E/NE sheets. No old acceptance reused as pixel verification.',
 'referenceReview':{'fullVideoDecoded':418,'consecutiveVideoRanges':[[0,31],[88,119],[148,179],[283,314]],'sourceEvidence':'provenance/limbs-20261004/north-video-source-review.json','userScreenshot':'C:/Users/luyua/AppData/Local/Temp/codex-clipboard-7cc4bf22-e4cf-4c35-8ac6-a37fd85f4037.png','limitation':'Video character small and partly occluded; useful for same-direction motion plane/continuity/contact, cannot prove every finger/toe detail.'},
 'timing':'Unchanged 16 distinct frames x75ms=1200ms. No copies or 60ms; current old slots reviewed before parent cyclic renumbering.',
 'supportSeamChecks':{d:{'old16to01':'same anatomical RIGHT support foot','old07to08':'RIGHT final push to LEFT initial contact','evidence':'N/NE support screen-right switches to screen-left; E/SE rear right support transfers to forward left boot without changing anatomical ownership.'} for d in ['N','NE','E','SE']},
 'confirmedHandIssuesRepaired':list(reasons),'candidateCount':4,'retainedWithoutEditCountWithinScope':57,'delegatedFootRepairSlots':['run/NE/13','run/NE/14','run/NE/15'],
 'groups':{'run/N':'All 16 preserved; bottle and cauldron left/right stable, front/back contact half cycles and ankle axes readable.','run/NE':'03/11 low hand passing candidates selected. 13/14/15 support boot plane transferred for required foot correction; remaining 11 preserved.','run/E':'03/11 low hand passing candidates selected; remaining 14 preserved.','run/SE':'All 16 preserved; existing03/11 already have low bottle passing, forearm/hand attachment and boots follow SE depth.'},
 'registration':'Native1254 RGBA candidate -> fixed whole-canvas1024 offset0 solely for QA, no crop fitting/warp/body translation. Head alpha IoU0.979–0.988; legs0.967–0.977, small redraw residuals remain, no large scale/pose change.',
 'unresolvedOwnedItems':[],'unresolvedDelegatedItems':['NE13/14/15 foot alignment pending full_combat; not included as passed here'],'browserValidatedByThisAgent':False,'clientValidated':False,'staticCandidateReview':True,'rows':rows,
 'writeStatus':'This agent stopped writing after review/selection closure; parent may merge or review candidates.'}
(OUT/'north-selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'north-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'north-NE13-v1.failed-request.json').write_text(json.dumps({'recordedAt':stamp,'prompt':'provenance/limbs-20261004/north-NE13-v1.prompt.txt','status':'failed','error':'image generation failed: connection failed: error sending request','outputImage':None,'runningCell':None,'retrySubmitted':False,'transferredTo':'full_combat'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':len(selection),'reviewed':len(rows),'handCandidates':list(selection),'footRepairDelegated':review['unresolvedDelegatedItems'],'stoppedWriting':True},ensure_ascii=False))
