from PIL import Image
from pathlib import Path
r=Path('E:/work/image/qdao_original_roster_v13');im=Image.open(r/'generation/00_reference_topright_boy/idle-eightdir-v1/raw.png').convert('RGBA');flat=Image.new('RGB',im.size,(255,0,255));flat.paste(im,(0,0),im);flat.thumbnail((1250,650));flat.save(r/'review/00_reference_topright_boy/idle-eightdir-reference.jpg',quality=72,optimize=True)