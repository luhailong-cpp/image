from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];d=B/'r12_c06/repairs-resume-20261012/right-ground-inlay-20261016-v01'
assert not (d/'tool-result.json').exists()
r=json.loads((d/'request.json').read_text(encoding='utf-8'))
r['prompt']=r['prompt'].replace('Remove the incorrect lone thin horizontal join at y645','Remove the CURRENT WRONG descending-right diagonal joint running from x280,y0 through x560,y260 to x940,y645; replace it with only the original rising-right seam stated above. Remove the incorrect lone thin horizontal join at y645')
(d/'prompt.txt').write_text(r['prompt'],encoding='utf-8');r['promptSha256']=hashlib.sha256((d/'prompt.txt').read_bytes()).hexdigest()
r['plannedNativeSelectionWindow']=[0,0,1254,700];r['plannedWindowReason']='Restore only original upper ground, leave lower blue-gray strip and gold architecture unchanged.'
(d/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r))

