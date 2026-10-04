from pathlib import Path
import json,hashlib
from PIL import Image
b=Path(__file__).resolve().parent
p=b/'selected-candidates.json'
s=json.loads(p.read_text(encoding='utf-8'))
for e in s['selected']:
 f=b/e['source']; im=Image.open(f); e['absolutePath']=str(f).replace('\\','/');e['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();e['nativeSize']=list(im.size);e['mode']=im.mode;e['alphaExtrema']=list(im.getchannel('A').getextrema());e['generationRecord']=str(f)+'.generation.json'
 r=json.loads(Path(e['generationRecord']).read_text(encoding='utf-8'));r['review']={'status':'static_candidate_selected_pending_dynamic_review','runtimeReady':False,'notes':e['note']};Path(e['generationRecord']).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
p.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':len(s['selected']),'uniqueSha':len(set(e['sha256'] for e in s['selected'])),'native1254rgba':all(e['nativeSize']==[1254,1254] and e['mode']=='RGBA' for e in s['selected']),'selection':str(p)},ensure_ascii=False))

