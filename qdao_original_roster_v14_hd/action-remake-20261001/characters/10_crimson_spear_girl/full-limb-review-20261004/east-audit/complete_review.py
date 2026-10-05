from pathlib import Path
import json,hashlib,datetime
w=Path(__file__).parent;root=w.parents[1]
p=w/'frames.json';data=json.loads(p.read_text(encoding='utf-8'));notes=json.loads((w/'frame-notes.json').read_text(encoding='utf-8'))
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
for row in data['frames']:
 slot=row['slot'];_,direction,number=slot.split('/');n=int(number)
 assert sha(root/row['file'])==row['sha256'],'runtime changed '+slot
 row['reviewStatus']='fail' if slot=='run/E/14' else 'passed'
 row['upperLimbs']='passed';row['lowerLimbs']=row['reviewStatus'];row['weaponContinuity']='passed'
 row['lowerObservation']=notes[direction][n-1]
 row['upperObservation']={'E':'Near arm shoulder-elbow-wrist reaches lower shaft grip; far arm reaches upper grip; palms visibly wrap the same shaft, no additional hand or detached wrist.','NE':'Back-view shoulder plates and sleeve directions lead to two separate visible wrists; hair occludes portions of forearms but grips attach to the continuous upper/lower black shaft.','SE':'Both shoulders connect through bent sleeved arms to two grips; wrist axes and thumb/finger wrapping remain coherent under changing spear angle.'}[direction]
 row['qa']=[f'{direction}-full.jpg',f'{direction}-{1 if n<9 else 9:02d}-{8 if n<9 else 16:02d}-upper.jpg',f'{direction}-{1 if n<9 else 9:02d}-{8 if n<9 else 16:02d}-lower.jpg']
 if slot=='run/E/14':
  row['acceptedRepair']={'file':'full-limb-review-20261004/run-E/14-v1/native.png','sha256':'9fb60fa15ecbc1df8ba19e18c0cd7a52f49771e28334ad57b49adb8a19b3ee2b','status':'passed','reason':'Near right free thigh foreground restored; far left support thigh behind; original shoe positions retained.'}
data['status']='completed-static-review-one-accepted-repair-awaiting-integration'
data['reviewedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
data['counts']={'sources':48,'passed':47,'uncertain':0,'fail':1,'acceptedNewRepairs':1,'upperLimbPassed':48}
data['limitations']=['Static contact and adjacent-frame review only; root performs final normal-speed integrated playback.','Hidden shoulder/elbow portions are assessed by continuous sleeve and wrist silhouettes, not asserted visible bones.','No micro ankle angles inferred from low-resolution reference video.']
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(data['counts']))

