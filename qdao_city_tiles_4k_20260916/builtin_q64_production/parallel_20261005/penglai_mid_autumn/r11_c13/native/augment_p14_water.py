from pathlib import Path
import json,hashlib
F=Path(__file__).resolve().parent
suffix="\nCritical water continuity: the true native TOP115 water is the authority. Continue its SAME broad cobalt cells and cyan wave strokes downward at the exact crossing points and similar widths. Do not keep a ruler-straight blue-to-gold switch at y115. Transition gradually into the existing warm reflection farther down the current area, with no extra light source, no noisy tiny grid of flecks, and no new wave pattern replacing the real north contours. Keep both existing wooden posts and the diagonal pale stone curb in their exact positions."
call=json.loads((F/'p14.call.json').read_text(encoding='utf-8-sig'));call['prompt']+=suffix
(F/'p14.prompt.txt').write_text(call['prompt'],encoding='utf-8')
(F/'p14.call.json').write_text(json.dumps(call,ensure_ascii=False,indent=2),encoding='utf-8')
req=json.loads((F/'p14.request.json').read_text(encoding='utf-8-sig'));req['submittedParameters']['prompt']=call['prompt'];req['promptSha256']=hashlib.sha256((F/'p14.prompt.txt').read_bytes()).hexdigest()
(F/'p14.request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
