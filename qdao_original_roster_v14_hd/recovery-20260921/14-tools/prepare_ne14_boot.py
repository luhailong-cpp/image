from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
R=Path(__file__).resolve().parents[1]
a=R/'14-generation/NE14-v3';a.mkdir(exist_ok=False)
q=json.loads((R/'14-generation/NE14-v2/request.json').read_text(encoding='utf-8'))
refs=q['actual_request']['referenced_image_paths'][:2]+[str(R/'14-generation/NE14-v2/raw.png')]
p='Edit image3 precisely: preserve the entire snow summoner girl, exact rear-right camera, size, pose, bent elevated SCREEN-LEFT boot and planted SCREEN-RIGHT boot. The only correction is remove the large snowflake ornament and all frontal lacing from the back of the planted boot at SCREEN RIGHT. Show its plain white rear boot panel with a subtle vertical seam, purple sole and existing fur cuff and small side tassel. Do not reverse the boot direction. Both knees, ankles and feet stay in the same articulated walk pose. Image1 is identity and original costume; image2 is approved rendering style. Preserve white fox, crystal, short hair, ears, lilac layered robes and plain rear sash bow exactly. Output one complete 1254x1254 transparent RGBA sprite, clean edges, no background or text.\n'
q.update(started_at=datetime.now(timezone.utc).isoformat(),actual_request={'prompt':p,'referenced_image_paths':refs},referenceBindings=[{'path':s,'sha256':hashlib.sha256(Path(s).read_bytes()).hexdigest()} for s in refs])
(a/'prompt.txt').write_text(p,encoding='utf-8');(a/'request.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
