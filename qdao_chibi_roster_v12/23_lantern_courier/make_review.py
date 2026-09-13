"""Make labeled visual-QA sheets from existing exports; no sprite artwork is drawn."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root.parent))
from process_roster import DIRECTIONS,load_processor,DEFAULT_PROCESSOR,write_json,sha
folder=root/'processing'; folder.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
frames={d:[Image.open(root/'walk'/d/f'{i:02d}.png').convert('RGBA') for i in range(1,9)] for d in DIRECTIONS}
paths=[]
for start in range(0,8,2):
    pair=DIRECTIONS[start:start+2]
    out=Image.new('RGB',(2048,2192),(238,237,227)); draw=ImageDraw.Draw(out)
    for section,d in enumerate(pair):
        y0=section*1096; draw.text((18,y0+12),d+' : 01 -> 08',font=font,fill=(25,58,53))
        for i,im in enumerate(frames[d]):
            x=i%4*512; y=y0+58+i//4*512
            out.paste(im,(x,y),im)
            draw.text((x+16,y+8),str(i+1).zfill(2),font=small,fill=(25,58,53))
    p=folder/f'visual-walk-{pair[0]}-{pair[1]}.jpg'; out.save(p,quality=94); paths.append(p)
idle=Image.new('RGB',(2048,1096),(238,237,227)); dr=ImageDraw.Draw(idle)
for i,d in enumerate(DIRECTIONS):
    im=Image.open(root/'idle'/f'{d}.png').convert('RGBA'); x=i%4*512;y=i//4*548
    idle.paste(im,(x,y+32),im); dr.text((x+16,y+8),d+' / independent idle',font=small,fill=(25,58,53))
p=folder/'visual-idle.jpg';idle.save(p,quality=94);paths.append(p)
edge=Image.new('RGB',(1536,1024)); chosen=[frames['N'][1],frames['E'][2],frames['SW'][6]]
for row,color in enumerate([(248,246,234),(25,33,38)]):
    for col,im in enumerate(chosen):
        edge.paste(color,(col*512,row*512,(col+1)*512,(row+1)*512));edge.paste(im,(col*512,row*512),im)
p=folder/'visual-edges.jpg';edge.save(p,quality=97);paths.append(p)
preview=[]
for phase in range(8):
    out=Image.new('RGBA',(1280,640))
    for i,d in enumerate(DIRECTIONS):out.paste(frames[d][phase].resize((320,320),Image.Resampling.LANCZOS),(i%4*320,i//4*320))
    preview.append(out)
load_processor(DEFAULT_PROCESSOR).save_transparent_gif(preview,folder/'animation-overview.gif',60)
write_json(folder/'visual-evidence.json',{'status':'prepared_for_manual_visual_review','sprite_pixels_unchanged':True,'direction_order':list(DIRECTIONS),'walk_frame_order':list(range(1,9)),'files':[{'path':str(p.relative_to(root)),'sha256':sha(p)} for p in paths]})
print(json.dumps({'review_files':[str(p) for p in paths],'animation':str(folder/'animation-overview.gif')}))
