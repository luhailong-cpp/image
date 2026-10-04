from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parent
pick={1:('SE-left-toeoff-v2.png','left forefoot contact/reach; toe down-forward'),2:('../generation/run-SE-14/native.png','left loading; flexed knee, flat boot under body'),3:('SE-left-mid-margin-v3.png','left mid-support, flat sole, right recovery foot off ground; straight spear margin repaired'),5:('SE-left-toeoff-v3.png','left late forefoot/push candidate; heel raised and foot drawn under pelvis'),9:('SE-right-contact-v1.png','right early contact; knee slightly more extended before loading, sole near-flat'),10:('SE-right-load-v2.png','right loading; mild support-knee bend and elbow cushion, left boot lifted'),11:('SE-right-load-v1.png','right mid-support; screen-left leg vertical bearing, opposite knee raised'),13:('SE-left-toeoff-v1.png','actual RIGHT toe-off candidate despite filename: right leg rearward, heel raised, opposite left knee forward'),14:('../generation/run-SE-03/native.png','short airborne left-knee advance'),15:('../generation/run-SE-10/native.png','left forward recovery reach'),16:('../generation/run-SE-12/native.png','left late reach/precontact')}
entries=[]
pick[2]=('SE-left-late-v2.png','observed left early/mid loading: flat support boot farther forward than next mid-support; requested late phase was not returned')
pick[4]=('../generation/run-SE-14/native.png','left late weight transfer candidate: support ankle shifted under pelvis, knee flexed before heel rise')
pick[12]=('SE-right-precontact-v2.png','observed RIGHT late support/early lift despite request/name: right ankle shifts rear-left and heel rises, opposite left knee lifted')
pick[6]=('SE-right-flight-v2.png','short flight: right thigh from screen-left hip drives forward, left leg screen-right folds behind; both boots lifted')
pick[7]=('SE-right-reach-v1.png','right front reach: same screen-left thigh unfolds, toe lifted/sole visible; left heel tucked behind')
pick[8]=('SE-right-precontact-v3.png','right heel/contact preparation: front knee unfolds and sole turns nearly flat; left boot still trails off ground')
pick[15]=('SE-15-scale-v2.png','left forward airborne reach; native head/body/weapon baseline matches original14, no per-frame scaling')
pick[16]=('SE-16-scale-v2.png','left descending precontact: sole rotates towardflat and foot lowers; same native head/body/weapon baseline as14/15, right recovery boot remains lifted')
for n,(f,phase) in sorted(pick.items()):
 p=(root/f).resolve()
 if not p.exists(): continue
 with Image.open(p) as im: size=list(im.size); mode=im.mode
 entries.append(dict(slot=f'run-SE-{n:02}',path=f,absolutePath=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),nativeSize=size,mode=mode,observedPhase=phase,status='provisional static selection',dynamicPassed=False))
out=dict(updatedAt=datetime.now(timezone.utc).isoformat(),status='partial phase selection; not approved full cycle',direction='SE',expectedCount=16,presentSelectedCount=len(entries),registrationApplied=False,finalTimingMs=None,trialTimingMs=[480,640,720,800],entries=entries,pendingSlots=[n for n in range(1,17) if n not in pick],clientTested=False)
(root/'selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
out.update(frameMs=75,cycleMs=1200,finalTimingMs=1200,phaseWeightsApplied=False,normalTimingStatus='latest user specified uniform16x75ms',incompleteCyclePlaybackForbidden=True)
out.pop('trialTimingMs',None)
out['status']='all16 native phase candidates selected; fixed full-cycle playback approval pending' if len(entries)==16 else 'partial phase selection; incomplete cycle playback forbidden'
(root/'selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
(root/'STATUS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(count=len(entries),pending=out['pendingSlots'])))
