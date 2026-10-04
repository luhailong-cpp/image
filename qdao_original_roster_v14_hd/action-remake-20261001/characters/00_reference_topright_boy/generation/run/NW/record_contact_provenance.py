from pathlib import Path
import json,hashlib
from PIL import Image
p=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy/generation/run/NW')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
inv=json.loads((p/'inventory.json').read_text(encoding='utf-8'))['images']
sel=json.loads((p/'selection.json').read_text(encoding='utf-8'))
for name,rows in [('selected-contact.jpg',[x for x in inv if x['selectedCandidate']]),('inventory-contact.jpg',inv)]:
 f=p/name;im=Image.open(f)
 data={'file':name,'sha256':sha(f),'width':im.width,'height':im.height,'format':'JPEG','operation':'Diagnostic contact sheet only: each complete source canvas uniformly downsampled to fit 314x314; no bbox crop, asset alignment or asset editing','derivedFrom':[{'file':x['file'],'sha256':x['sha256'],'generationRecord':x['file']+'.generation.json'} for x in rows],'actualModel':None,'actualQuality':None,'note':'Derived diagnostic, no image model called for contact sheet; original model evidence follows each source record.'}
 Path(str(f)+'.generation.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('contact provenance saved')

