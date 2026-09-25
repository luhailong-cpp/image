from pathlib import Path
import json
from PIL import Image, ImageDraw
import numpy as np
HERE=Path(__file__).resolve().parent
CHAR='17_ghost_script_calligrapher_boy'
OUT=HERE/'nne-e-static-review-v2'; OUT.mkdir(exist_ok=True)
choice={'N':{8:2,10:2,14:2},'NE':{6:2,9:3,13:3},'E':{5:2,9:3,10:4}}
selection={'character_id':CHAR,'overrides':{}}; metrics={}
for d,versions in choice.items():
    records=[]
    for n in range(1,18):
        v=versions.get(n,1) if n<17 else (2 if d=='N' else 1)
        attempt=f'walk-{d}-{n:02d}-v{v}' if n<17 else f'idle-{d}-v{v}'
        imp=HERE/'staging'/attempt/'candidate'/CHAR/'import-result.json'
        record=json.loads(imp.read_text(encoding='utf8')); path=Path(record['path']); im=Image.open(path).convert('RGBA')
        a=np.asarray(im)[:,:,3]; ys,xs=np.where(a>8)
        metrics[record['slot']]={'attempt':attempt,'top':int(ys.min()),'bottom':int(ys.max()),'width':int(xs.max()-xs.min()+1),'sha256':record['sha256']}
        selection['overrides'][record['slot']]={'import_result':imp.as_posix(),'visual_status':'static_reviewed_pending_dynamic'}
        records.append((attempt,im))
    for mode,col,ink in [('dark',(30,38,46),'white'),('light',(240,238,228),'black')]:
        can=Image.new('RGB',(2048,5*560),col); draw=ImageDraw.Draw(can)
        for i,(label,im) in enumerate(records):
            x=i%4*512;y=i//4*560; draw.text((x+10,y+10),label,fill=ink); small=im.resize((512,512),Image.Resampling.LANCZOS);can.paste(small,(x,y+35),small)
        can.save(OUT/f'{d}-all-normal-{mode}.png')
        for batch in range(5):
            chunk=records[batch*4:batch*4+4]
            can=Image.new('RGB',(2048,2*1080),col);draw=ImageDraw.Draw(can)
            for i,(label,im) in enumerate(chunk):
                x=i%2*1024;y=i//2*1080;draw.text((x+14,y+14),label,fill=ink);can.paste(im,(x,y+45),im)
            can.save(OUT/f'{d}-{batch+1}-enlarged-{mode}.png')
        can=Image.new('RGB',(2048,560),col);draw=ImageDraw.Draw(can)
        for i,n in enumerate([15,16,1,2]):
            label,im=records[n-1];small=im.resize((512,512),Image.Resampling.LANCZOS);can.paste(small,(i*512,35),small);draw.text((i*512+10,10),label,fill=ink)
        can.save(OUT/f'{d}-seam-{mode}.png')
(OUT/'selections.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf8')
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf8')
print(OUT)
