from pathlib import Path
from PIL import Image
import json,hashlib
r=Path(r'E:\work\image\qdao_chibi_roster_v12');p=r/'review/27_ranger_natural_fixes';p.mkdir(exist_ok=True);s=r/'27_ink_kite_ranger/source'
im=Image.open(s/'idle.png').convert('RGBA');size=im.size;im=im.resize((1772,886),Image.Resampling.LANCZOS);im.crop((443,0,886,443)).save(p/'NE-idle-reference.png');im.crop((1329,443,1772,886)).save(p/'NW-idle-reference.png')
(p/'reference-extraction.json').write_text(json.dumps({'source':str(s/'idle.png'),'sha256':hashlib.sha256((s/'idle.png').read_bytes()).hexdigest(),'native_size':size,'normalized_whole_sheet_size':[1772,886],'NE_cell_box':[443,0,886,443],'NW_cell_box':[1329,443,1772,886]},indent=2))
print('Extracted whole idle source cells; retained original source unchanged')

