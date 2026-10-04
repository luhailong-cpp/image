from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[2];P=R/'provenance/run-north'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
selectionPath=R/'selection/run-north.json';selection=json.loads(selectionPath.read_text(encoding='utf8'))
beforePixels={x['file']:sha(R/x['file']) for x in selection['frames']}
changed=[]
for row in selection['frames']:
 if row['direction']!='E' or row['frame'] not in [1,2,3,10,11,13,14]:continue
 recordPath=R/row['generationRecord'];record=json.loads(recordPath.read_text(encoding='utf8'))
 assert record['route']=='postprocess'
 sourcePath=R/record['derivedFrom']['generationRecord']
 sourceSha=sha(sourcePath)
 assert sourceSha==record['derivedFrom']['generationRecordSha256']
 source=json.loads(sourcePath.read_text(encoding='utf-8-sig'))
 assert source['sha256']==record['derivedFrom']['sha256']
 assert source.get('prompt') and source.get('references')
 oldRecordSha=sha(recordPath)
 record['prompt']=source['prompt']
 record['references']=source['references']
 record['sourceGenerationEvidence']={'file':record['derivedFrom']['generationRecord'],'sha256':sourceSha,
  'sourceImageSha256':source['sha256'],'originalTool':source.get('tool'),'originalRoute':source.get('route'),
  'evidence':source.get('evidence'),'inheritance':'prompt/references copied from verified original generation record; this record remains deterministic alpha-only postprocess; no new AI call.',
  'actualModel':source.get('actualModel'),'actualQuality':source.get('actualQuality')}
 assert record['actualModel'] is None and record['actualQuality'] is None
 recordPath.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
 row['generationRecordSha256']=sha(recordPath)
 changed.append({'slot':f"run/E/{row['frame']:02}",'record':row['generationRecord'],'previousRecordSha256':oldRecordSha,
 'generationRecordSha256':row['generationRecordSha256'],'sourceGenerationRecordSha256':sourceSha,'imageSha256':row['sha256']})
assert len(changed)==7
selectionPath.write_text(json.dumps(selection,ensure_ascii=False,indent=2),encoding='utf8')
technicalPath=P/'technical-current.json';technical=json.loads(technicalPath.read_text(encoding='utf8'))
lookup={f"run/{x['direction']}/{x['frame']:02}":x for x in selection['frames']}
for row in technical['frames']:
 chosen=lookup[row['slot']];recPath=R/chosen['generationRecord'];rec=json.loads(recPath.read_text(encoding='utf8'))
 assert sha(recPath)==chosen['generationRecordSha256']
 assert sha(R/chosen['file'])==chosen['sha256']
 assert rec.get('prompt') and rec.get('references')
 row['generationRecord']=chosen['generationRecord'];row['generationRecordSha256']=chosen['generationRecordSha256']
 row['promptAndReferencesPresent']=True
 if rec.get('sourceGenerationEvidence'):row['sourceGenerationEvidence']=rec['sourceGenerationEvidence']
technical['updatedAt']=now
technical['metadataCompatibility']='All48 current records have top-level prompt/references. Seven alpha-only records inherit verified source generation evidence; actual model/quality stay null.'
technicalPath.write_text(json.dumps(technical,ensure_ascii=False,indent=2),encoding='utf8')
cleanupPath=P/'cleanup-closeout.json';cleanup=json.loads(cleanupPath.read_text(encoding='utf8'))
deletionPath=R/'audit/cleanup-rejected-20261003.json';deletion=json.loads(deletionPath.read_text(encoding='utf8'))
removed={x['file']:x for x in deletion['deleted']};count=0
for row in cleanup['files']:
 if row.get('disposition')!='pending_parent_manifest_reference_removal':continue
 assert row['file'] in removed and removed[row['file']]['sha256']==row['sha256']
 assert not (R/row['file']).exists()
 row['disposition']='deleted_by_parent_after_current_reference_verification'
 row['deletionEvidence']={'file':'audit/cleanup-rejected-20261003.json','sha256':sha(deletionPath),'atUtc':deletion['atUtc']}
 count+=1
assert count==6
cleanup['updatedAt']=now
cleanupPath.write_text(json.dumps(cleanup,ensure_ascii=False,indent=2),encoding='utf8')
observations=json.loads((P/'phase-observations-current.json').read_text(encoding='utf8'))
basis={
'E':'前掌的圆头和延伸鞋底朝屏幕右侧，与E行进轴一致；后折脚的向下俯仰是摆腿姿态，未见确定的侧向外旋。',
'NE':'前掌伸向画面右前方，绿色花纹后跟杯在后方；NE背面透视中露出的鞋底不作为反向鞋尖证据。',
'NW':'鞋底前掌延伸在画面左前方；支撑靴右侧较大的绿色面和厚金边是后跟杯/跟块，不能误当作朝外鞋尖。摆动脚露底来自屈膝回收。'}
frames=[]
for row in selection['frames']:
 d=row['direction'];f=row['frame'];support,phase,note,confidence=observations['phase'][d][f-1]
 frames.append({'slot':f'run/{d}/{f:02}','file':row['file'],'sha256':sha(R/row['file']),
 'toeAxisFinding':'no_definite_outward_toe_error','kneeAnkleFinding':'no_disconnected_or_forced_outward_axis_identified',
 'basis':basis[d],'supportFoot':support,'phase':phase,'groundingEvidence':note,
 'action':'keep_current_pixels','inspection':'current enlarged16-frame lower-limb sheet; targeted full-size checks of NW01/NW10/NE01/NE10/E02',
 'confidence':'medium_for_projected_yaw; boot heel/forefoot construction and thigh-knee-ankle continuity checked'})
audit={'updatedAt':now,'policy':'No direction of07 or09 is treated as a user-approved template. Independently assess each travel axis. Normal perspective, toe pitch and exposed swing-foot sole are not automatically outward yaw.',
 'method':'Differentiate rounded forefoot, arch and thicker heel block/cup; trace thigh to knee to ankle. Never classify foot yaw by boot screen location or distance between legs alone.',
 'count':48,'confirmedErrorSlots':[],'imagegenCallsThisToeAudit':0,'imagesChanged':0,'result':'no_new_objective_toe_splay_error_identified',
 'reference07':'Requested current runtime/run/E path was unavailable; no07 pixels, pose weights or candidate images were used as acceptance standard.',
 'frames':frames,'evidenceSheets':['provenance/run-north/E-legs-inspection-current.png','provenance/run-north/NE-toe-axis-inspection.png','provenance/run-north/NW-toe-axis-inspection.png'],
 'limits':'Static shoe-axis audit only; no new dynamic/client acceptance claim. Existing phase, preview and micro-head-drift limitations remain.'}
auditPath=P/'toe-axis-audit-current.json';auditPath.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
reviewPath=R/'review-parts/run-north.json';review=json.loads(reviewPath.read_text(encoding='utf8'))
review['toeAxisAudit']={'file':auditPath.relative_to(R).as_posix(),'sha256':sha(auditPath),'confirmedErrorSlots':[],'imagesChanged':0,'result':audit['result']}
for row in review['frames']:
 assert row['sha256']==lookup[row['slot']]['sha256']
 row['toeAxisFinding']='no_definite_outward_toe_error'
review['updatedAt']=now
reviewPath.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf8')
afterPixels={x['file']:sha(R/x['file']) for x in selection['frames']}
assert beforePixels==afterPixels
meta={'updatedAt':now,'changedRecords':changed,'imagesChanged':0,'newImagegenCalls':0,'deletedStatusesUpdated':6,
 'selectionSha256':sha(selectionPath),'technicalSha256':sha(technicalPath),'toeAxisAuditSha256':sha(auditPath),'reviewSha256':sha(reviewPath)}
(P/'metadata-compatibility-repair.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in meta.items() if k!='changedRecords'},ensure_ascii=False))

