from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parents[2]
rows=[]
for d in ['S','SW','SE']:
 for n in range(1,17):
  p=R/'run'/d/f'{n:02}.png'
  im=Image.open(p)
  rec=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
  src=R/rec['derivedFrom']['file']
  sr=json.loads(Path(str(src)+'.generation.json').read_text(encoding='utf-8-sig'))
  native=Image.open(src)
  assert im.size==(1024,1024) and im.mode=='RGBA',(d,n,im.size,im.mode)
  assert min(native.size)>=1024,(d,n,native.size)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'],(d,n,'export hash')
  assert hashlib.sha256(src.read_bytes()).hexdigest()==rec['derivedFrom']['sha256'],(d,n,'native hash')
  assert sr.get('actualModel') is None and sr.get('actualQuality') is None,(d,n,'actual evidence')
  refs=sr.get('submittedParameters',{}).get('referenced_image_paths',[])
  assert any(Path(x).as_posix().endswith('designs/jubaozhai-ui/02-characters.png') for x in refs),(d,n,'style ref')
  rows.append({'file':p.relative_to(R).as_posix(),'sha256':rec['sha256'],'selectedNative':src.relative_to(R).as_posix(),'nativeSha256':rec['derivedFrom']['sha256'],'nativeSize':list(native.size),'generationRecord':str(src.relative_to(R))+'.generation.json','actualModel':None,'actualQuality':None})
assert len({x['sha256'] for x in rows})==48
assert len({x['nativeSha256'] for x in rows})==48
result={'scope':'S/SW/SE 48 selected independent source mapping and current official-file SHA snapshot; parent final manifest is authoritative after registration','count':48,'technicalChecks':'passed 1024 RGBA exports, unique native and output hashes, native >=1024, linked native source/hash, style attached, actual model/quality unconfirmed','visualStatus':'static reviewed including local shoe-axis fixes; final combined sequence acceptance remains parent responsibility; see per-direction phase-review.json and run/S/shoe-axis-review.json','frames':rows}
(R/'run/S/south-selected.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'count':48,'uniqueNative':48,'uniqueExports':48,'technical':'passed'}))
