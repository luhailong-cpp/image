from pathlib import Path
import json, hashlib, shutil
from datetime import datetime, timezone
from PIL import Image,ImageDraw
ROOT=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl')
P=ROOT/'provenance/run-north'
selected=['01-v2','02-v2','03-v2','04-v3','05-v1','06-v1','07-v3','08-v1','09-v1','10-v1','11-v1','12-v2','13-v1','14-v2','15-v1','16-v1']
notes=[
'Right heel/sole rim under right hip; left folded recovery sole; left arm high forward, right low back. Forward hand partly occluded by scarf/head, grip traceable.',
'Right support flatter and knee bent; left recovery sole raised. Left wrist/fist now exposed below scarf; right arm trails. Grip repaired.',
'Right midstance support; left boot begins lowering through recovery. Both hands near waist with clear links. More distinct arm progression.',
'Right late support, heel raised, left boot lifted forward; corrected prior premature left support. Right arm rises, left arm lowers.',
'Right toe-off extended backward, left boot small under hip; right arm forward and left backward.',
'Brief flight, both soles visible. Forward left sole perspective remains less clear than ideal; requires sequence playback.',
'Left leg extends toward landing, right recovery sole raised. Reduced prior head-position drop; left boot heel/sole edge improved.',
'Left pre-contact or initial contact: left boot lower than N07; right folded recovery. Exact contact event needs playback with perspective ground.',
'Left contact beneath hip, right folded recovery. Right arm forward, left backward.',
'Left support/absorption, right recovery raised. Right forearm forward; two blades.',
'Left midstance, right recovery lowering; hands pass neutral. Left knee weight readable.',
'Left late support heel lift, right boot small and lifted under right hip. Left arm forward, right arm backward.',
'Left toe-off extended behind, right boot lifted and foreshortened. Clear two hands/two daggers.',
'Brief flight after left toe-off; right boot heel now visible, left sole trails. Both off ground by pose; screen y alone not proof.',
'Right pre-contact descent; left recovery sole folds up, opposite arms. Extension reaches near ground sooner than intended N15 phase.',
'Right pre-contact/initial contact joining N01; left recovery raised. Left grip visible but scarf crosses blade; no extra hand.'
]
rows=[]
contact=Image.new('RGB',(1440,1568),(210,217,222));draw=ImageDraw.Draw(contact)
for i,(name,note) in enumerate(zip(selected,notes)):
 f=ROOT/'staging/run/N'/f'{name}.png'
 side=Path(str(f)+'.generation.json')
 if not side.exists():
  rec=P/f'run-N-{name}.generation.json'
  shutil.copy2(rec,side)
 else: rec=side
 im=Image.open(f);im.load()
 a=im.getchannel('A');mask=a.point(lambda v:255 if v>8 else 0)
 edges=sum(v>8 for v in list(a.crop((0,0,im.width,1)).getdata())+list(a.crop((0,im.height-1,im.width,im.height)).getdata())+list(a.crop((0,0,1,im.height)).getdata())+list(a.crop((im.width-1,0,im.width,im.height)).getdata()))
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 record=json.loads(side.read_text(encoding='utf-8-sig'))
 assert record['sha256']==sha
 rows.append({'frame':i+1,'file':str(f),'sha256':sha,'generationRecord':str(side),'sourceRecord':str(rec),'dimensions':list(im.size),'mode':im.mode,'alphaExtrema':a.getextrema(),'bboxAbove8':mask.getbbox(),'boundaryPixelsAbove8':edges,'staticFindings':note,'staticAnatomyReview':'two_arms_two_hands_two_legs_two_daggers_traceable','sequenceStatus':'pending_dynamic_review'})
 tile=Image.new('RGBA',(360,360),(210,217,222,255));tile.alpha_composite(im.resize((360,360),Image.Resampling.LANCZOS))
 x=(i%4)*360;y=(i//4)*392
 contact.paste(tile.convert('RGB'),(x,y));draw.text((x+12,y+364),f'N {i+1:02} / {name}',fill=(0,0,0))
contactfile=P/'N-selected-contact.jpg';contact.save(contactfile,quality=94)
result={'character':'07_moon_shadow_assassin_girl','direction':'N','reviewedAt':datetime.now(timezone.utc).isoformat(),'selectedCount':16,'nativeHD':True,'independentImagegenInputs':True,'dynamicReviewed':False,'clientIntegration':'not_performed','rootTargetNormalized':[0.5,0.94],'rootTargetMeaning':'fixed virtual root target, actual projected soles vary by perspective; not pixel-ground validation','runTiming':'720 ms trial pending parent playback; do not use old 480 ms as acceptance','frames':rows,'remainingReview':['Run at 640/720/800 ms and verify landing/weight','N06 forward foot sole perspective and N15/N16 contact timing need real playback','Compare N07 head position to N06/N08 at game size','Cross-direction silhouette and ground/root calibration pending parent'],'rejectedCandidates':['01-v1','02-v1','03-v1','04-v1','07-v2'],'allSelectedHashesDistinct':len(set(r['sha256'] for r in rows))==16}
(P/'N-selection-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(Path(str(contactfile)+'.derivation.json')).write_text(json.dumps({'file':str(contactfile),'sha256':hashlib.sha256(contactfile.read_bytes()).hexdigest(),'operation':'contact sheet of fixed-full-canvas 360px thumbnails, neutral background; not animation input','derivedFrom':[{'file':r['file'],'sha256':r['sha256'],'generationRecord':r['generationRecord']} for r in rows]},indent=2),encoding='utf-8')
print(json.dumps({'selected':16,'opaqueBoundaryPixels':sum(r['boundaryPixelsAbove8'] for r in rows),'uniqueHashes':result['allSelectedHashesDistinct'],'report':str(P/'N-selection-review.json'),'contact':str(contactfile)}))

