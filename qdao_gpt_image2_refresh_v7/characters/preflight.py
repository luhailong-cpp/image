from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json
r=Path.cwd(); out=r/'qdao_gpt_image2_refresh_v7/characters'
files=[]
for d in ['q_daoist_character_pack_4096','character_move_8dir','qdao_chibi_pets_v1','qdao_ui_redesign_v5/pet']:
 files+=sorted((r/d).glob('*.png'))
files += [r/'qdao_chibi_game_pack_v4/source/hero-matte.png',r/'qdao_chibi_game_pack_v4/hero-transparent_1024.png',r/'q_daoist_character_highest_transparent_4096_fixed.png',r/'q_daoist_hero_chibi_headband_v3.png']+list(r.glob('q_lidazui_hair_daoist_variant_*.png'))
rows=[]
for p in files:
 with Image.open(p) as im:
  rows.append({'path':p.relative_to(r).as_posix(),'size':list(im.size),'mode':im.mode,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'alpha_range':list(im.getchannel('A').getextrema()) if 'A' in im.getbands() else None})
(out/'baseline.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
portraits=sorted(p for p in (r/'q_daoist_character_pack_4096').glob('*.png') if p.name[:2].isdigit() and int(p.name[:2])>0)
def board(ps,name,cols=4):
 b=Image.new('RGB',(cols*340,((len(ps)+cols-1)//cols)*370),'#e8e6df'); draw=ImageDraw.Draw(b)
 for i,p in enumerate(ps):
  im=Image.open(p).convert('RGBA'); im.thumbnail((320,335)); x=(i%cols)*340+(340-im.width)//2;y=(i//cols)*370+10
  b.paste(im,(x,y),im); draw.text(((i%cols)*340+8,(i//cols)*370+348),p.stem[:35],fill='black')
 b.save(out/'references'/name)
board(portraits[:12],'roles-01-12.jpg');board(portraits[12:],'roles-13-22.jpg')
board(sorted((r/'qdao_chibi_pets_v1').glob('*transparent*.png'))+[r/'qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png'],'pets.jpg',2)
print(json.dumps({'baseline_files':len(rows),'reference_boards':3}))
