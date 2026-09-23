from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

REC=Path(__file__).resolve().parents[1]
ROOT=REC.parents[1]
jobs={
 'NE01-v2':(1,'N01-v2','LEFT heel has just touched ground ahead, LEFT knee nearly straight. RIGHT leg extends back toward viewer with RIGHT heel raised and toe touching. Left boot is higher on the image than right boot, right sole partly visible. This is first contact, not the preceding heel-hover pose.'),
 'NE02-v3':(2,'N02-v1','LEFT foot rolls flat from its heel ahead and accepts body weight, LEFT knee softens slightly. RIGHT heel rises at the back while RIGHT toe remains touching. Left boot is higher on the image than right boot. Compared to the third reference, the left boot is now flat and right heel is more raised.'),
 'NE14-v2':(14,'N14-v1','RIGHT leg is the straight supporting leg at screen right, RIGHT foot still planted near center below body. LEFT knee bends and moves forward away from camera, its LEFT boot elevated ahead at screen left. LEFT boot is higher and smaller in depth, with only a thin sole edge, not a big backward-facing sole. This is bent-knee forward swing, earlier than the nearly extended leg in reference3.'),
 'NE16-v2':(16,'N16-v1','RIGHT toe is the rear supporting foot at screen right with heel raised. LEFT shin finishes extending forward away from camera, LEFT heel hovers just above ground immediately before landing. Left boot is higher up the image at screen left; right boot is lower at screen right with visible heel/sole. This is the last pre-contact phase, more extended and lower left heel than reference3. At least one toe touches ground, no jumping.')
}
for name,(frame,phase,action) in jobs.items():
 arc=REC/'14-generation'/name
 arc.mkdir(exist_ok=False)
 refs=[REC/'14-reference/identity-1024.png',ROOT/'designs/jubaozhai-ui/02-characters.png',REC/'14-generation/NE15-v3/raw.png',REC/f'14-generation/{phase}/raw.png']
 prompt=('Generate ONE new transparent RGBA 1254x1254 full-body game sprite of character14 snow summoner girl. Image1 is original identity. Image2 is approved main rendering style. Image3 is the exact required NE rear-right camera, framing, upper body and costume. Image4 supplies ONLY the leg-phase relationship, redrawn at image3 camera. Preserve image3 head scale, ears, short silver bob, left-side snowflake hair ornament, plain purple rear cloth bow, layered lilac white fur robes, white boots, fox cradled on left arm and crystal snowflake held by right hand. No front buckle on the back. Keep body proportions and silhouette size exactly as image3.\n'
 + f'Create a distinct new natural WALK frame {frame:02d}/16, not a duplicate. Required leg action: {action}\n'
 + 'Direction is walking away toward screen upper-right with head and torso staying rear-right, do not turn toward viewer. Keep the left-screen boot to the left of the right-screen boot; do not cross the legs. Render fresh knee/ankle articulation with subtle cloth response. Maintain moderate chibi steps and stable carrying arms. A new generated pose is required, never mirror, transform, slide, stretch or reuse an existing pose. No extra limbs. Clean alpha edges, no colored fringe, no floor, no cast shadow, no text, no checkerboard or background. Entire ears, boots, fox and crystals visible inside generous transparent margins.\n')
 req={'tool':'image_gen__imagegen','route':'builtin','started_at':datetime.now(timezone.utc).isoformat(),'slot':{'kind':'walk','direction':'NE','frame':frame},'actual_request':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs]},'submittedParameters':{'model':None,'quality':None},'configSnapshot':json.loads((ROOT/'config/image-generation.json').read_text(encoding='utf-8-sig')),'referenceBindings':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in refs]}
 (arc/'prompt.txt').write_text(prompt,encoding='utf-8')
 (arc/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(name)
