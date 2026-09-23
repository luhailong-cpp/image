from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
R=Path(__file__).resolve().parents[1]
base=json.loads((R/'14-generation/NE15-v3/request.json').read_text(encoding='utf-8'))
jobs={
 'NE01-v3':(1,'NE15-v3','This is the first heel contact. Keep the SCREEN-RIGHT boot visibly LOWER than the SCREEN-LEFT boot, as in image3. The right-screen boot stays at the back toward the viewer with part of its sole showing. The left-screen boot stays farther from the viewer and higher in the picture, and its heel now lands; its knee is nearly straight. Do not swap which boot is higher. Rear-right direction remains exactly image3.'),
 'NE02-v4':(2,'NE03-v2','This is the preceding loading pose just before image3. The screen-LEFT leg stays the straight planted support. The screen-RIGHT leg bends less than image3 and its boot has its toe still touching the ground behind while its heel lifts. Keep the right sole visible. Make the left knee slightly less bent than image3. Preserve the screen side of each leg exactly.'),
 'NE16-v3':(16,'NE15-v3','This is the instant after image3, immediately before forward heel contact. Keep the SCREEN-RIGHT boot visibly LOWER than the SCREEN-LEFT boot, as in image3. The right-screen boot stays extended backward toward viewer with its heel raised and toe supporting. The left-screen shin straightens slightly more, its ankle flexes upward and heel approaches ground ahead, still farther from viewer and higher in picture. The left sole must not face viewer. Only the right boot shows its sole. Do not swap their image positions or cross the legs.')
}
for n,(f,anchor,action) in jobs.items():
 a=R/'14-generation'/n;a.mkdir(exist_ok=False)
 refs=[*base['actual_request']['referenced_image_paths'][:2],str(R/f'14-generation/{anchor}/raw.png')]
 prompt=('Draw a new 1254x1254 transparent RGBA single game walk frame, by carefully editing image3 to the adjacent gait instant specified below. Image1 is original identity; image2 is the approved main art style; image3 is the current exact camera, size, upper body, clothing and leg-side reference. Keep head/body ratio, hair, ears, plain purple back bow, carried fox, snowflake and upper body of image3 fixed. Keep white boots with plain rear seams.\n'+action+'\nFresh natural knee and ankle articulation and tiny cloth response; do not copy, mirror, warp or translate the old pose. Do not repaint the other half of the stride. One foot always supports. Full-body with transparent margin; genuinely transparent background, no ground or shadow or text.\n')
 req={**base,'started_at':datetime.now(timezone.utc).isoformat(),'slot':{'kind':'walk','direction':'NE','frame':f},'actual_request':{'prompt':prompt,'referenced_image_paths':refs},'referenceBindings':[{'path':p,'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in refs]}
 (a/'prompt.txt').write_text(prompt,encoding='utf-8');(a/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(n)
