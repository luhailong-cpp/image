from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
HERE=Path(__file__).resolve().parent
RECOVERY=HERE.parents[1]
ROOT=HERE.parents[3]
out=RECOVERY/'10-generation/NE09-v5'
out.mkdir(exist_ok=False)
refs=[RECOVERY/'10-work/references/identity-inspection-1024.png',ROOT/'designs/jubaozhai-ui/02-characters.png',RECOVERY/'10-generation/NE09-v3/raw.png',RECOVERY/'10-generation/NE01-v2/raw.png']
roles=['authoritative-original-identity','confirmed-main-style','edit-target-preserve-right-leading-gait','exact-direction-camera-and-spear-lock']
prompt='''Use case: precise-object-edit. Create one final transparent 1024x1024-or-larger native game walk sprite, slot NE09 for crimson spear girl. Image1 is identity reference and Image2 is main style reference only. Image3 is the EDIT TARGET: preserve its genuine RIGHT-foot-leading short walk phase and the long spear pointing to SCREEN UPPER LEFT with butt toward SCREEN LOWER RIGHT. Image4 is the EXACT CAMERA AND UPPER-BODY reference. Correct Image3 to face slightly MORE AWAY FROM CAMERA to match Image4 back view: hide the exposed right ear behind the right hair mass, show the same amount of symmetrical back-head, and have twin tails hang to the sides of the back as in Image4. DO NOT CHANGE THE STRIDE to Image4: anatomical RIGHT near boot is still the leading boot on SCREEN RIGHT upper ground depth, anatomical LEFT far boot trails lower-left with heel raised. Track each knee to its own hip. Left hand grips high near blade, right hand low near waist; shaft is straight. Preserve the red/ivory/gold costume, brown buns with gold/turquoise ornaments, boots and all intricate polished hand-painted materials. Gently upright grounded tiny-step walk. Complete single character and weapon fit inside canvas with margin. No labels, no sprite sheet, no floor, no shadow. Genuinely transparent alpha, clean antialiased edges without isolated colored pixels or yellow/red/magenta halos. No mirrored parts, no copying another animation phase, no duplicated hands, no extra spear.'''
(out/'prompt.txt').write_text(prompt,encoding='utf-8')
req={'status':'prepared_for_submission','character':'10_crimson_spear_girl','slot':'NE09','startedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen__imagegen','actual_request':{'prompt':prompt,'referenced_image_paths':[p.as_posix() for p in refs]},'submittedParameters':{'model':None,'quality':None},'configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8')),'referenceRoles':roles,'reference_bindings_at_start':[{'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'purpose':role} for p,role in zip(refs,roles)]}
(out/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'archive':out.as_posix(),'actual_request':req['actual_request']},ensure_ascii=False))
