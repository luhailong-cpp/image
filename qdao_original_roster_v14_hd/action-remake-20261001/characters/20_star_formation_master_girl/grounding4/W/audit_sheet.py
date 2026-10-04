from PIL import Image,ImageDraw
from pathlib import Path
b=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/20_star_formation_master_girl")
for d in ['W','SW']:
 files=list((b/'grounding4'/d).glob('*.png'));files=[p for p in files if not p.name.endswith('-native.png')]
 out=Image.new('RGB',(4*300,((len(files)+3)//4)*335),(232,229,220));draw=ImageDraw.Draw(out)
 for i,p in enumerate(sorted(files)):
  im=Image.open(p).convert('RGBA');im.thumbnail((300,300));out.paste(im,((i%4)*300,(i//4)*335),im);draw.text(((i%4)*300+10,(i//4)*335+303),p.stem,fill='black')
 out.save(b/'grounding4'/d/'audit-sheet.jpg')

