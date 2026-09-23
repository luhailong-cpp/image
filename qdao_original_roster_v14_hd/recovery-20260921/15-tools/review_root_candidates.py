"""Process only root-owned S/SW candidates and build source-bound review sheets."""
import argparse, json, subprocess, sys, hashlib
from pathlib import Path
from PIL import Image, ImageDraw

R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('direction',choices=['S','SW']);p.add_argument('--select',action='store_true');a=p.parse_args()
rows=[]
for n in range(1,17):
    d=R/'15-generation'/f'{a.direction}{n:02d}-walk-v1'
    if not (d/'raw.png').exists(): continue
    cmd=[sys.executable,str(R/'15-tools/archive_frame.py'),'--generation-dir',str(d),'--source',str(d/'raw.png'),'--request-json',str(d/'request.json'),'--receipt-json',str(d/'receipt.json'),'--direction',a.direction,'--kind','walk','--frame',str(n),'--process']
    if a.select:cmd.append('--select')
    result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
    if result.returncode:print(n,result.stderr[-500:]);continue
    path=d/'processing-fixed088-v1/final.png'
    rows.append((n,path)); print(f'{a.direction}{n:02d} processed'+(' selected' if a.select else ' unselected'))
out=R/'15-review';out.mkdir(exist_ok=True)
for bg,name in [((240,234,220),'light'),((24,34,44),'dark')]:
    sheet=Image.new('RGB',(4*256,4*280),bg);draw=ImageDraw.Draw(sheet)
    feet=Image.new('RGB',(4*340,4*260),bg);df=ImageDraw.Draw(feet)
    for n,path in rows:
        im=Image.open(path).convert('RGBA');x=((n-1)%4)*256;y=((n-1)//4)*280
        small=im.resize((256,256),Image.Resampling.LANCZOS);sheet.paste(small,(x,y+24),small);draw.text((x+8,y+5),f'{a.direction}{n:02d}',fill=(80,160,180))
        crop=im.crop((342,710,682,970));xf=((n-1)%4)*340;yf=((n-1)//4)*260;feet.paste(crop,(xf,yf),crop);df.text((xf+8,yf+5),f'{a.direction}{n:02d}',fill=(80,160,180))
    sheet.save(out/f'{a.direction}-candidates-{name}.png');feet.save(out/f'{a.direction}-feet-{name}.png')
(out/f'{a.direction}-sources.json').write_text(json.dumps([{'frame':n,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for n,path in rows],indent=2),encoding='utf-8')
