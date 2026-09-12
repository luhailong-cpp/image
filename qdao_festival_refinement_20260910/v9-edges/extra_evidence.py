from pathlib import Path
import json,argparse
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--ids',nargs='*');args=ap.parse_args()
for r in json.loads((HERE/'stage.json').read_text())['records']:
 if args.ids and r['character_id'] not in args.ids:continue
 examples=r.get('distant_examples',[])
 if not examples:continue
 x,y=examples[0]['pixel'];old=Image.open(ROOT/r['before_path']).convert('RGBA');new=Image.open(ROOT/r['staged_path']).convert('RGBA')
 page=Image.new('RGB',(1280,400),'#e8e1d4');dr=ImageDraw.Draw(page);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
 for c,(im,label,bg) in enumerate([(old,'BEFORE LIGHT','#f5edde'),(old,'BEFORE DARK','#19332d'),(new,'AFTER LIGHT','#f5edde'),(new,'AFTER DARK','#19332d')]):
  dr.text((c*320+3,3),r['character_id']+' '+label,font=font,fill='#243b31');dr.text((c*320+3,23),f'{x},{y} / distance {r["max_donor_distance"]:.1f}',font=font,fill='#243b31')
  crop=im.crop((x-80,y-80,x+80,y+80)).resize((320,320),Image.Resampling.NEAREST);back=Image.new('RGBA',crop.size,bg);back.alpha_composite(crop);page.paste(back.convert('RGB'),(c*320,65))
 path=HERE/'evidence'/(r['character_id']+'-farthest.jpg');page.save(path,quality=97)
 print(path.relative_to(ROOT).as_posix())
