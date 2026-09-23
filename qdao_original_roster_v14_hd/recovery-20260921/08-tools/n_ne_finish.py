"""Private N/NE completion helper: evidence, selection, and review composites only."""
from pathlib import Path
import argparse, json, sys
from datetime import datetime, timezone
from PIL import Image, ImageDraw
from process import process, GEN, OUT, RECOVERY, read, write

def selected(d, f):
    return f'walk-{d}-{f:02d}-v' + ('2' if (d, f) in [('N',2),('N',8),('NE',9)] else '1')

def inventory():
    for d in ('N','NE'):
        attempts = sorted(p for p in GEN.glob(f'walk-{d}-*') if (p/'raw.png').exists())
        attempts += [GEN/f'idle-{d}-v1']
        for p in attempts:
            if not (OUT/p.name/'source.json').exists(): print(json.dumps(process(p.name)))
        sheet = Image.new('RGB',(2048,((len(attempts)+3)//4)*544),(30,38,46))
        draw = ImageDraw.Draw(sheet)
        for i,p in enumerate(attempts):
            im=Image.open(OUT/p.name/'frame.png').convert('RGBA').resize((512,512))
            x,y=(i%4)*512,(i//4)*544
            sheet.paste(im,(x,y+32),im); draw.text((x+10,y+8),p.name,fill='white')
        dest=RECOVERY/'08-delivery-preview'/'n-ne-work'
        dest.mkdir(exist_ok=True)
        sheet.save(dest/f'{d}-existing-review.jpg',quality=94)

def prepare(d, f):
    attempt=f'walk-{d}-{f:02d}-v1'
    p=GEN/attempt
    if p.exists(): raise ValueError('Attempt exists: '+attempt)
    phases={
      'N':{
        11:'RIGHT SUPPORT / LEFT TOE-OFF: right leg supports the body, left knee flexes and left boot leaves the ground behind; left sole visible but moving slightly upward and inward from frame10. Small continuous step, no kick.',
        12:'LEFT EARLY SWING: right planted support leg, left knee bending and moving forward; left boot draws beneath the left hip, no longer extended toward the camera. Sole turns downward. Both knees remain on their own screen sides.',
        13:'LEFT PASSING: right foot supports, left bent knee has moved alongside right knee; left boot suspended close beneath the pelvis with its sole downward. This is a narrow natural passing pose, not the broad contact pose.',
        14:'LEFT LATE SWING: left thigh comes forward away from camera, left shin begins extending; its toe points away and boot is higher on the image than right support boot. Right heel begins mild lift.',
        15:'LEFT PRECONTACT: left leg extends farther forward away from camera, left heel approaching ground ahead; right leg begins trailing and heel lifts. Not yet the full frame01 contact. Keep frame01 proportions.',
        16:'LEFT TERMINAL SWING: left heel almost touches down ahead, right foot behind with a modest heel lift and toe contact. This is exactly the small intervening pose between frame15 and frame01; do not duplicate either.'},
      'NE':{
        11:'ANATOMICAL LEFT SUPPORT / RIGHT TOE-OFF: left foot forward planted toward upper-right, anatomical right foot trails toward lower-left and lifts from toe with bent knee; right sole visible. Keep the modest frame10 stride and distinguish the two legs.',
        12:'ANATOMICAL RIGHT EARLY SWING: left foot remains planted support; anatomical right knee flexes and draws forward from its lower-left trailing position toward pelvis, right boot suspended, its sole starts turning down. Do not straighten or lengthen legs.',
        13:'ANATOMICAL RIGHT PASSING: anatomical left planted leg supports the torso. Right knee passes beside it, right boot briefly tucked under pelvis, small separation, sole downward. Keep true rear three-quarter NE view.',
        14:'ANATOMICAL RIGHT LATE SWING: right thigh advances toward upper-right, right shin extends naturally, right boot now just ahead of left support boot but still suspended. Left heel starts lifting.',
        15:'ANATOMICAL RIGHT PRECONTACT: right leg reaches modestly forward toward upper-right, right heel descends almost to floor. Left leg trails toward lower-left and heel lifts; right knee remains bent slightly.',
        16:'ANATOMICAL RIGHT TERMINAL SWING: right heel about to land forward toward upper-right, left boot trailing lower-left rolling onto toe. Make a smooth tiny step between frame15 and frame01 contact, not a duplicate.'}}
    prev=GEN/(selected(d,f-1) if f<=11 else f'walk-{d}-{f-1:02d}-v1')/'raw.png'
    refs=[str(prev).replace('\\','/'),str(GEN/'references/identity-1024.png').replace('\\','/'),str(GEN/'references/style-1280.jpg').replace('\\','/'),str(GEN/f'idle-{d}-v1/raw.png').replace('\\','/')]
    if f>=15: refs.append(str(GEN/f'walk-{d}-01-v1/raw.png').replace('\\','/'))
    view='EXACT REAR, travelling straight away from camera. Anatomical left stays IMAGE LEFT; anatomical right stays IMAGE RIGHT.' if d=='N' else 'EXACT REAR THREE-QUARTER NE, travelling diagonally away toward IMAGE UPPER-RIGHT. Keep the same right ear profile and backpack visibility.'
    prompt=f'Use case: identity-preserve. Create exactly ONE native full single-frame sprite, square 1024x1024 or larger, genuine transparent alpha PNG. Frame {f:02d}/16 of a 30ms walk cycle. Image 1 is the preceding actual frame; keep its head size, torso proportions, camera, materials and hand props. Image 2 is original identity. Image 3 is primary confirmed painted style reference, not UI content. Image 4 is neutral direction/proportion anchor.'
    if f>=15: prompt+=' Image 5 is the upcoming frame01; smoothly bridge toward its pose and keep identical proportions.'
    prompt+=f' View: {view} New articulated gait phase: {phases[d][f]} Redraw the pose as a new genuine single animation frame. Keep short round chibi limbs, brown bun and gold ribbon, orange/gold robe, white trousers, teal/gold boots, brown backpack with scrolls and herbs. Anatomical RIGHT hand carries the bronze jade-gold cauldron and anatomical LEFT hand carries the green potion bottle; preserve both, never swap hands. Hold head and upper body almost stationary, with tiny natural hem/tassel movement only. Match original detailed clean hand-painted game finish. Roomy clear margins around whole character; no cropping, background, ground shadow, text or effects. Do not mirror, duplicate, interpolate, stretch, rotate or translate the previous whole image; solve new hip, knee and ankle articulation. Keep all limbs anatomically connected.'
    write(p/'request.json',{'slot':f'walk/{d}/{f:02d}','tool':'image_gen__imagegen','route':'builtin','parameters':{'prompt':prompt,'referenced_image_paths':refs},'startedAt':datetime.now(timezone.utc).isoformat(),'configSnapshot':read(RECOVERY.parents[1]/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; tool schema exposes neither model nor quality selector.'})
    (p/'prompt.txt').write_text(prompt,encoding='utf-8')
    print(json.dumps(read(p/'request.json'),ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('mode',choices=['inventory','prepare']); p.add_argument('--direction');p.add_argument('--frame',type=int);a=p.parse_args()
    inventory() if a.mode=='inventory' else prepare(a.direction,a.frame)
