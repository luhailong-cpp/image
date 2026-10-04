from pathlib import Path
from PIL import Image
import json,hashlib,datetime
root=Path(__file__).parent
rows=[]
for d in ('E','W'):
 for n in range(1,7):
  suffix='-v2' if n==4 or (d=='W' and n in (5,6)) else ''
  p=root/f'hit-{d}-{n:02d}{suffix}.png'; im=Image.open(p); side=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
  rows.append({'file':p.name,'direction':d,'frame':n,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nativeSize':[im.width,im.height],'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema(),'generationRecord':p.name+'.generation.json','status':'native_candidate_single_frame_inspected','formalExport':False,'dynamicAccepted':False,'sourceHashMatches':hashlib.sha256(p.read_bytes()).hexdigest()==side['sha256']})
out={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timezone':'America/New_York','targetSlots':12,'currentNativeCandidates':len(rows),'successfulGenerations':13,'supersededProjectImagesRemoved':1,'failedCalls':2,'nativeSize':[1254,1254],'intendedExport':[1024,1024],'intendedVirtualRoot':[512,942],'frameDurationMs':40,'clipDurationMs':240,'actualModel':None,'actualQuality':None,'formalExported':0,'dynamicAccepted':0,'clientIntegrated':False,'review':'STATUS.md','files':rows}
out.update(successfulGenerations=17,supersededProjectImagesRemoved=3,latestReview='2026-10-03 E/W04 recoil restored; W05/W06 body location and recovery continuity redrawn; all current feet inspected for heading.')
(root/'review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'count':len(rows),'allSHAValid':all(r['sourceHashMatches'] for r in rows),'allNativeRGBA':all(r['nativeSize']==[1254,1254] and r['mode']=='RGBA' and r['alphaExtrema']==(0,255) for r in rows)},ensure_ascii=False))

