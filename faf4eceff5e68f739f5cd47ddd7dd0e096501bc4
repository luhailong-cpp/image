from pathlib import Path
from PIL import Image,ImageDraw
r=Path(r'E:\work\image\qdao_original_roster_v13');c=r/'candidate/00_reference_topright_boy';out=r/'review/00_reference_topright_boy'
spec=[('Original restored portrait',r/'baseline/q_daoist_character_pack_4096/00_reference_topright_boy_transparent_4096.png'),('Dedicated S idle',c/'idle/S.png'),('New walk S01',c/'walk/S/01.png'),('New walk S09',c/'walk/S/09.png')]
board=Image.new('RGB',(1536,420),(38,44,45));draw=ImageDraw.Draw(board)
for i,(label,p) in enumerate(spec):
 im=Image.open(p).convert('RGBA');im.thumbnail((384,384),Image.Resampling.LANCZOS);board.paste(im,(i*384+(384-im.width)//2,(384-im.height)//2),im);draw.text((i*384+12,394),label,fill='white')
board.resize((1200,328)).save(out/'identity-and-opposite-contact-review.jpg',quality=90)
print(out/'identity-and-opposite-contact-review.jpg')
