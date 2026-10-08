from pathlib import Path
import json,hashlib
from PIL import Image
out=Path(__file__).parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
indexp=out/'crop-index.json';idx=json.loads(indexp.read_text(encoding='utf-8'))
assert sha(idx['fragment']['file'])==idx['fragment']['sha256']
im=Image.open(idx['fragment']['file'])
for x in (1024,2048,3072):
 box=(x-384,2688,x+384,3456);p=out/f'junction-x{x}-y3072.png';im.crop(box).save(p)
 idx['crops'].append({'file':str(p),'sha256':sha(p),'size':[768,768],'sourcePositions':[{'tile':'r07_c10','tileLocalLTRB':box}],'reviewPurpose':'Standard1024 grid junction plus actual new/return boundaries y2957/y3133 and nearby column boundaries in the same native crop'})
indexp.write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf-8')
print('3 native junction crops written')
