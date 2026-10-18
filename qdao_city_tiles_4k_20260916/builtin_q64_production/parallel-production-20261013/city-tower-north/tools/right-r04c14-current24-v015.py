from pathlib import Path
import json,hashlib
from PIL import Image
B=Path(r'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\parallel-production-20261013\city-tower-north');out=B/'qa/right-r04c14-current24-v015';out.mkdir()
cp=B/'versions/right-r04c14-roof-tone-native-v001/r04_c14-candidate.png';im=Image.open(cp).convert('RGB');old=B/'versions/right-r04c14-assembly-v005/r04_c14/assembly/seams-100pct';baseqa=json.loads((B/'qa/right-r04c14-concentrated-qa-v005.json').read_text('utf-8'))
rows=[]
for q in baseqa['seams']:
 pair=q['pair'];r=int(pair[0][1]);c=int(pair[0][2]);o=q['orientation'];fn=o+'-'+'-'.join(pair)+'.png'
 if o=='vertical':box=[c*1024-192,(r-1)*1024,c*1024+192,r*1024]
 else:box=[(c-1)*1024,r*1024-192,c*1024,r*1024+192]
 cr=im.crop(box);prev=Image.open(old/fn).convert('RGB');same=cr.tobytes()==prev.tobytes()
 if not same:
  with (out/fn).open('xb') as f:cr.save(f,format='PNG')
 rows.append({'pair':pair,'orientation':o,'crop':box,'unchangedFromV005':same,'evidence':str(old/fn if same else out/fn),'previousStatus':q['status'],'currentStatus':q['status'] if same else 'changed_pending_recheck','pixelSha256':hashlib.sha256(cr.tobytes()).hexdigest()})
with (out/'index.json').open('x',encoding='utf-8') as f:json.dump({'candidate':str(cp),'candidateSha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'formalAcceptedCount':0,'seams':rows},f,indent=2)
print(json.dumps({'changed':sum(not x['unchangedFromV005'] for x in rows),'unchanged':sum(x['unchangedFromV005'] for x in rows),'index':str(out/'index.json')}))