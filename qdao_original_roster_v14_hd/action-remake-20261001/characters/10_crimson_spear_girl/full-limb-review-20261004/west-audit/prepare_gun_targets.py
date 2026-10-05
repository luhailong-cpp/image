from pathlib import Path
from PIL import Image
import json,hashlib
r=Path(__file__).resolve().parents[2];o=r/'full-limb-review-20261004/run-NW/inputs';o.mkdir(parents=True,exist_ok=True)
for n in (7,8,9,10):
    src=r/f'runtime/run/NW/{n:02d}.png';dst=o/f'gun{n:02d}-1254.png'
    Image.open(src).convert('RGBA').resize((1254,1254),Image.Resampling.LANCZOS).save(dst)
    Path(str(dst)+'.generation.json').write_text(json.dumps({'file':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'operation':'Full-canvas uniform 1024 to 1254 reference resize; no crop or pose editing','derivedFrom':[{'file':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'generationRecord':str(src)+'.generation.json'}]},ensure_ascii=False,indent=2),encoding='utf8')
src=json.loads((r/'full-limb-review-20261004/west-audit/frame-status.json').read_text(encoding='utf8'))
rows=[]
for q in src['rows']:
    slot=q['frame'];status='failed' if q['status']=='fail' else ('uncertain' if q['lower']['status']=='uncertain' or slot in ('run/W/08','run/W/13') else 'passed-visible-limbs')
    rows.append({'slot':slot,'file':str(Path(q['file']).relative_to(r)).replace('\\','/'),'sha256':q['sha256'],'status':status,'observation':q['lower']['reason']+' 上肢：'+q['upper']['reason'],'limits':'衣袖/头发遮挡的肩肘或远手不声称完整可见；可见肢体未见明确错不代表遮挡内解剖已证实。','componentChecks':{'lower':q['lower'],'upper':q['upper']}})
(r/'full-limb-review-20261004/west-audit/audit.json').write_text(json.dumps({'scope':'48 current runtime frames, pre-repair audit','frames':rows},ensure_ascii=False,indent=2),encoding='utf8')
print('4 targets + 48 audit frames ready')
