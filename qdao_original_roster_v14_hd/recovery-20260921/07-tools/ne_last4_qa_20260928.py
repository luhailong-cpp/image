from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
here=Path(__file__).resolve().parent
src=here/'candidate/07_moon_shadow_assassin_girl/walk/NE'
out=here/'ne-last4-qa-20260928';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for n in [13,14,15,16]:
 p=src/f'{n:02}.png';m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'));im=Image.open(p).convert('RGBA')
 pair=Image.new('RGB',(2048,1024))
 for k,bg in enumerate([(30,38,46),(240,238,228)]):
  canvas=Image.new('RGB',(1024,1024),bg);canvas.paste(im,(0,0),im);pair.paste(canvas,(1024*k,0))
 pair.save(out/f'{n:02}-pair.png')
 raw=Path(m['derivedFrom']['path']);req=Path(m['requestEvidence']['path']);res=Path(m['resultEvidence']['path'])
 rows.append({'slot':m['slot'],'attempt':m['attempt'],'sha256':sha(p),'nativeSha256':sha(raw),'nativeSize':list(Image.open(raw).size),'outputSize':list(im.size),'allHashesMatch':sha(p)==m['outputSha256'] and sha(raw)==m['derivedFrom']['sha256'] and sha(req)==m['requestEvidence']['sha256'] and sha(res)==m['resultEvidence']['sha256'],'metrics':m['outputMetrics'],'actualModel':m['actualModel'],'actualQuality':m['actualQuality']})
report={'scope':'07 NE13-16 only','observedAt':datetime.now(timezone.utc).isoformat(),'files':rows,'fullResolutionLightDarkVisuallyReviewed':False,'generationCount':4,'paidApiCalls':0,'requestedTransparentBackground':True,'changes':'Hair ornament occlusion only; four separate genuine native single-image edits using exact root NE08 prompt with frame number changed and each current frame as edit target; identity/style/idleNE references really attached.','retainedLegPhases':{'13':'left screen boot lifted and coming forward; right screen boot planted','14':'left screen boot lowers ahead toward ground, right screen boot planted','15':'right screen heel starts rear lift; left screen foot supports ahead','16':'right rear sole clearly visible; left screen foot supports ahead'},'browserPlaybackPerformed':False,'fullNECycleAcceptance':False,'clientIntegration':False}
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'out':str(out),'allHashesMatch':all(r['allHashesMatch'] for r in rows),'files':[{'slot':r['slot'],'sha256':r['sha256']} for r in rows]}))
