from pathlib import Path
from PIL import Image, ImageDraw
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl")
OLD=Path(r"D:/work/image/qdao_original_roster_v14_hd/recovery-20260921/20-final")
for d in ['NE','NW']:
 s=Image.new('RGB',(1280,1360),(226,231,237));p=ImageDraw.Draw(s)
 for n in range(1,17):
  im=Image.open(OLD/f'walk/{d}/{n:02}.png').convert('RGBA');im.thumbnail((320,320))
  x=((n-1)%4)*320;y=((n-1)//4)*340
  s.paste(im,(x,y),im);p.text((x+8,y+319),f'{d} {n:02}',fill=(12,12,12))
 s.save(B/f'provenance/run-NENW-oldwalk-{d}-audit.jpg')

