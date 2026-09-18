from PIL import Image
from pathlib import Path
p=Path(r'E:\work\image\qdao_original_roster_v13\generation\00_reference_topright_boy\W-repair03')
for f in p.glob('*-source-cell.png'):Image.open(f).convert('RGB').save(f.with_name(f.name.replace('-source-cell.png','-reference.jpg')),quality=88)
