from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).resolve().parents[2];P=R/'provenance/run-north'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selpath=R/'selection/run-north.json';sel=json.loads(selpath.read_text(encoding='utf8'));changes=[]
for row in sel['frames']:
 p=R/row['file'];im=Image.open(p);a=im.getchannel('A');h=a.histogram();noise=h[1]+h[2]
 if not noise:continue
 originalrec=R/row['generationRecord'];rec=json.loads(originalrec.read_text(encoding='utf-8-sig'))
 before=sha(p); originalrecsha=sha(originalrec); originalrecordpath=row['generationRecord']
 im.paste((0,0,0,0),(0,0),a.point(lambda x:255 if x<=2 else 0));im.save(p)
 after=sha(p);now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 record={'file':row['file'],'sha256':after,'generatedAt':now,'tool':'Pillow deterministic export cleanup','route':'postprocess',
  'configSnapshot':rec['configSnapshot'],'submittedParameters':{'model':None,'quality':None},
  'actualModel':rec.get('actualModel'),'actualQuality':rec.get('actualQuality'),
  'unverifiedReason':'No new AI call. Original built-in model/quality not disclosed; inherited original evidence.',
  'evidence':rec['evidence'],'sourceSubmittedParameters':rec['submittedParameters'],
  'width':1024,'height':1024,'sourceNativeSize':row['sourceNativeSize'],'nativeSize':row['sourceNativeSize'],'format':'PNG/RGBA',
  'derivedFrom':{'file':row['file'],'sha256':before,'generationRecord':originalrecordpath,'generationRecordSha256':originalrecsha,
   'sourceRetained':False,'reason':'Replaced delivery PNG after alpha-only cleanup; historical text record retained under user retention policy.'},
  'operation':'Only pixels with existing alpha<=2 reset RGBA to0. No resizing/crop/translation/mirror/interpolation or changes to alpha>2 pixels.',
  'alphaNoiseCleanup':{'thresholdInclusive':2,'nonzeroLowAlphaPixelsRemoved':noise,'higherAlphaPixelsChanged':False}}
 path=P/f"run-{row['direction']}-{row['frame']:02}-alpha-cleanup-20261003.generation.json"
 path.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
 row.update(sha256=after,generationRecord=path.relative_to(R).as_posix(),generationRecordSha256=sha(path))
 changes.append({'slot':f"run/{row['direction']}/{row['frame']:02}",'beforeSha256':before,'sha256':after,'pixelsCleared':noise,'record':path.relative_to(R).as_posix()})
selpath.write_text(json.dumps(sel,ensure_ascii=False,indent=2),encoding='utf8')
(P/'alpha-cleanup-closeout.json').write_text(json.dumps({'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changedFrames':len(changes),'changes':changes},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'changedFrames':len(changes),'pixelsCleared':sum(x['pixelsCleared'] for x in changes)},ensure_ascii=False))

