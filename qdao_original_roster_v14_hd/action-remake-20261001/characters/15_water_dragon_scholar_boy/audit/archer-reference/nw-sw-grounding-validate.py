from pathlib import Path
from PIL import Image
import json,hashlib
B=Path(__file__).resolve().parents[2]
s=json.loads((B/'audit/archer-reference/nw-sw-grounding-selection.json').read_text(encoding='utf-8-sig'))
rows=s['rows'];checks=[]
for r in rows:
 p=Path(r['file']);actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==r['sha256']
 with Image.open(p) as im:
  assert im.mode=='RGBA'
  assert im.size==((1024,1024) if r['export'].get('retainedRuntime') else (1254,1254))
  alpha=im.getchannel('A');bbox=alpha.getbbox()
  checks.append({'slot':r['slot'],'key':r['candidateKey'],'size':im.size,'sha256':actual,'alphaBBox':bbox})
 record=B/r['generationRecord'];g=json.loads(record.read_text(encoding='utf-8-sig'))
 assert g.get('actualModel') is None
 if 'grounding' in (r['candidateKey'] or ''):
  assert (B/g['prompt']).exists()
  assert (B/g['evidence']['toolResult']).exists()
assert len(set(r['sha256'] for r in rows))==32
report={'frameCount':len(rows),'uniqueFiles':len(set(r['sha256'] for r in rows)),'reusedPreviousCandidates':sum('grounding' not in (r['candidateKey'] or '') for r in rows),'newSelectedCandidates':sum('grounding' in (r['candidateKey'] or '') for r in rows),'durationMs':16*75,'clientIntegrated':False,'dynamicPlaybackObserved':False,'checks':checks}
(B/'audit/archer-reference/nw-sw-grounding-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print({k:v for k,v in report.items() if k!='checks'})

