from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
from datetime import datetime,timezone
ROOT=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/07_moon_shadow_assassin_girl')
OUT=ROOT/'provenance/run-other'
notes={
'W':[
'Near leg forward landing; near arm back and far arm forward. Two secure grips; left temple ornament near-side.',
'Near foot flat, knee flexed, body lower: readable weight absorption; far recovery heel lifts.',
'Near flat foot under body midstance, far knee/heel folded; both hands pass lower waist, no extra hand.',
'Near leg extends back with toe-down shoe; far knee passes forward; near arm now forward. Transition to toe-off readable.',
'Near trailing toe-off, far knee forward and boot lifted; opposite arms. Ground contact exact timing pending playback.',
'Far leg begins forward opening, near leg folds behind; brief airborne transition by pose, not yet flat support.',
'Far shin extended forward, shoe toe up; near heel raised behind. Pre-contact extension.',
'Far leading heel approaches ground; arms oppose near rear leg. Contact boundary requires playback.',
'Far forward contact/near rear leg. Corrected prior same-side arm issue stays resolved.',
'Far foot flat, knee bent and body lower; near rear boot near ground but heel-raised, weight mainly forward.',
'Far flat support below body, near knee lifted and crossing forward; hands transitional, no third hand.',
'Far leg extended back toe-down, near knee forward and boot raised; near arm back/far arm forward.',
'Far toe-off/near knee forward, far boot toe pointing down; both hands connected.',
'New14-v2: near front boot toe-up and clearly above support level, far boot folded up. Short flight now clearer; head rose slightly, compare at playback.',
'Near leg extends front with toe raised, far recovery folds; descending flight or pre-contact.',
'Near heel reaches toward ground joining01; far boot trails, opposite arms retained.'
],
'S':[
'Anatomical left (viewer-right) forward landing, anatomical right folded back. Right arm forward opposite left leg.',
'New02-v2: left boot front with thin bottom rim, knee flexed, right recovery boot raised. More readable left weight absorption.',
'Left support under hip, right boot lifted passing; right hand lowers toward transition. Grips connected.',
'New04-v2: left/viewer-right support continues downward with heel lift, right/viewer-left knee passes with boot lifted. Fixes premature forward-foot contact.',
'Right/viewer-left leads with toe-up sole visible, left boot foreshortened behind. Short flight after left push; grounding depends on perspective.',
'Right leading leg opens toward landing; both boots elevated by pose, exact contact not proven by prompt.',
'Right toe-up reach, left recovery behind; left arm front/right arm back, two blades. Exposed front sole intentional pre-contact.',
'Right boot descends and sole angle flattens; left boot folded behind. Contact transition.',
'Right contact/absorption begins, left leg recovery; left arm forward.',
'New10-v2: right boot flatter with thin sole edge, right knee flexed supporting weight, left boot raised. Head slightly higher than old10; parent playback should compare09/11.',
'Right support under hip, left foot lifted; hands near neutral. Two complete arm-hand-dagger chains.',
'New12-v2: right/viewer-left support continues through heel lift; left/viewer-right knee passes with boot lifted. Fixes early switched contact.',
'Left leads toward camera with toe-up underside, right recovery boot behind; right arm forward. Flight after right toe-off.',
'Left extension descending, right recovery; shoe still angled and cannot be called flat weight support.',
'Left toe-up precontact, right boot lifted, right hand forward. Broad underside correct before heel contact.',
'Left boot lowers/flattens joining01; right folded recovery, opposite hands remain consistent.'
]}
selection={}
for d in ['W','S']:
 rows=[];contact=Image.new('RGB',(1440,1568),(211,218,222));draw=ImageDraw.Draw(contact)
 for i in range(1,17):
  stem=f'{i:02}-v2' if (d=='W' and i==14) or(d=='S' and i in[2,4,10,12]) else f'{i:02}'
  f=ROOT/'staging/run'/d/f'{stem}.png';im=Image.open(f);im.load()
  a=im.getchannel('A');m=a.point(lambda v:255 if v>8 else 0)
  edge=sum(v>8 for rect in[(0,0,im.width,1),(0,im.height-1,im.width,im.height),(0,0,1,im.height),(im.width-1,0,im.width,im.height)] for v in a.crop(rect).getdata())
  sha=hashlib.sha256(f.read_bytes()).hexdigest();side=Path(str(f)+'.generation.json')
  rec=json.loads(side.read_text(encoding='utf-8-sig'));assert rec['sha256']==sha
  rows.append({'frame':i,'file':str(f),'sha256':sha,'generationRecord':str(side),'dimensions':list(im.size),'mode':im.mode,'alphaExtrema':a.getextrema(),'bboxAbove8':m.getbbox(),'boundaryPixelsAbove8':edge,'anatomy':'Two hands, two legs, two daggers with traceable grips; no duplicate limb observed','actualStaticPhase':notes[d][i-1],'dynamicReviewed':False})
  tile=Image.new('RGBA',(360,360),(211,218,222,255));tile.alpha_composite(im.resize((360,360),Image.Resampling.LANCZOS));x=((i-1)%4)*360;y=((i-1)//4)*392;contact.paste(tile.convert('RGB'),(x,y));draw.text((x+12,y+364),f'{d} {i:02} / {stem}',fill=(0,0,0))
 fn=OUT/f'{d}-grounding-selected-contact.jpg';contact.save(fn,quality=94)
 Path(str(fn)+'.derivation.json').write_text(json.dumps({'file':str(fn),'sha256':hashlib.sha256(fn.read_bytes()).hexdigest(),'operation':'full-canvas scaled contact preview only, not animation inputs','derivedFrom':[{'file':r['file'],'sha256':r['sha256'],'generationRecord':r['generationRecord']} for r in rows]},indent=2),encoding='utf-8')
 selection[d]=rows
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'method':'All32 native PNGs individually viewed, contact sheets inspected; targeted5 independent imagegen edits reviewed','staticAnatomyReview':'passed_no_extra_limbs_or_detached_daggers_observed','dynamicReviewed':False,'clientIntegration':'not_performed','rootTargetNormalized':[0.5,0.94],'rootCaveat':'prompt target only, no per-frame alignment performed; perspective and actual shoe poses need parent playback','proposedWeightFrames':[2,3,10,11],'timing':'640/720/800ms comparison pending; 720ms proposed trial, not client setting','frames':selection,'newRepairs':['W/14-v2','S/02-v2','S/04-v2','S/10-v2','S/12-v2'],'remaining':['Parent actual playback normal and slow; shoe contact timing, root scale and head trajectory','S05/13 and W05/13 transition from toe-off to short flight need continuity review','S10 new head placement modestly higher and W14 slight head rise must be assessed dynamically'],'technical':{'selected':32,'uniqueHashes':len(set(r['sha256'] for rows in selection.values() for r in rows)),'opaqueBoundaryPixels':sum(r['boundaryPixelsAbove8'] for rows in selection.values() for r in rows),'native1254RGBA':all(r['dimensions']==[1254,1254] and r['mode']=='RGBA' for rows in selection.values() for r in rows)}}
(OUT/'WS-grounding-selection-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report['technical']))

