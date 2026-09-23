import json, argparse
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
HERE=Path(__file__).resolve().parent
CHAR='17_ghost_script_calligrapher_boy'
def main():
 p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--versions',default='');a=p.parse_args()
 v={1:1,2:2,3:3,4:1,5:3,9:3,13:2}
 if a.versions:v.update({int(k):int(val) for k,val in (s.split(':') for s in a.versions.split(','))})
 out=HERE/('SE-review-'+a.revision);out.mkdir(exist_ok=False)
 rows=[];sel={'character_id':CHAR,'overrides':{}}
 for f in range(1,17):
  attempt=f'walk-SE-{f:02d}-v{v.get(f,1)}';origin=HERE/'staging'/attempt/'candidate'/CHAR
  path=origin/'walk/SE'/f'{f:02d}.png';im=Image.open(path).convert('RGBA');arr=np.array(im);ys,xs=np.where(arr[:,:,3]>8)
  rows.append({'frame':f,'attempt':attempt,'path':str(path),'top':int(ys.min()),'bottom':int(ys.max()),'bbox':im.getbbox()})
  sel['overrides'][f'walk/SE/{f:02d}.png']={'import_result':str(origin/'import-result.json'),'visual_status':'root_selected_unapproved'}
 origin=HERE/'staging/idle-SE-v1/candidate'/CHAR
 sel['overrides']['idle/SE.png']={'import_result':str(origin/'import-result.json'),'visual_status':'root_selected_unapproved'}
 for mode,color in [('dark',(30,38,46)),('light',(240,238,228))]:
  canvas=Image.new('RGB',(2048,2240),color);legs=Image.new('RGB',(1536,1376),color)
  d=ImageDraw.Draw(canvas);dl=ImageDraw.Draw(legs)
  for i,row in enumerate(rows):
   im=Image.open(row['path']);sm=im.resize((512,512),Image.Resampling.LANCZOS);x=i%4*512;y=i//4*560
   canvas.paste(sm,(x,y+40),sm);d.text((x+10,y+10),row['attempt'],fill='white' if mode=='dark' else 'black')
   crop=im.crop((280,670,720,1014)).resize((384,300),Image.Resampling.LANCZOS);x=i%4*384;y=i//4*344
   legs.paste(crop,(x,y+30),crop);dl.text((x+10,y+5),str(row['frame']),fill='white' if mode=='dark' else 'black')
  canvas.save(out/(mode+'.png'));legs.save(out/(mode+'-legs.png'))
 (out/'measurements.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 (out/'selections.json').write_text(json.dumps(sel,indent=2),encoding='utf-8')
 print(json.dumps({'out':str(out),'rows':rows},ensure_ascii=False))
if __name__=='__main__':main()
