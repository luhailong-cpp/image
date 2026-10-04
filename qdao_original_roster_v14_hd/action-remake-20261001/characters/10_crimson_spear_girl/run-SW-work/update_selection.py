from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parent
phases={11:'B(screen-right hip) loading: mildly flexed support knee, sole flat, A knee airborne',12:'B(screen-right hip) mid-support: shin near vertical, sole flat; A(screen-left hip) raised knee'}
entries=[]
phases[14]='B toe-off: screen-right-origin leg extends rearward, heel up and toe down-left, A knee raised; selectedv2 retains13 upperbody placement. Oldv1 retained as review alternate.'
phases[13]='B late support: ankle rearward to screen-right between12 and14; heel raised modestly, forefoot facing SW/down-left; A knee lifted'
phases[9]='B first-contact: right-origin leg advances down-left beneath pelvis, sole nearly/full flat; A remains raised. Requested precontact returned early contact.'
phases[10]='B early load: same right-origin sole flat under pelvis, mild knee cushion, A raised, connected2hand grip retained'
phases[15]='A(screen-left hip) forward bent-knee short flight, B trails; independent original07 reassigned after actual review'
phases[16]='A(screen-left hip) forward reach/descent with upturned heel-leading sole, B trails; independent original requested09 reassigned'
for n,phase in sorted(phases.items()):
 p=root/f'run-SW-{n:02}.png'
 if not p.exists():continue
 with Image.open(p) as im:size=list(im.size);mode=im.mode
 r=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf8'));h=hashlib.sha256(p.read_bytes()).hexdigest();assert h==r['sha256']
 entries.append(dict(slot=f'run-SW-{n:02}',path=p.name,absolutePath=p.as_posix(),sha256=h,nativeSize=size,mode=mode,observedPhase=phase,status='provisional static selection',dynamicPassed=False))
out=dict(updatedAt=datetime.now(timezone.utc).isoformat(),direction='SW',ownedSlots=list(range(9,17)),selectedCount=len(entries),expectedOwned=8,entries=entries,missingOwned=[n for n in range(9,17) if n not in phases],basis='../generation/run-SW-04/native.png',legDefinition=dict(A='screen-left hip / anatomical right',B='screen-right hip / anatomical left'),registrationApplied=False,fullSequencePassed=False,clientTested=False)
(root/'selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
out.update(frameMs=75,cycleMs=1200,phaseWeightsApplied=False,normalTimingStatus='latest user specified uniform16x75ms',incompleteCyclePlaybackForbidden=True)
(root/'selection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
(root/'STATUS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(count=len(entries),missing=out['missingOwned'])))
