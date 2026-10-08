from pathlib import Path
from PIL import Image,ImageDraw
import json,sys,hashlib,datetime
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parents[2]));import production as p
for name in ['s3','s4']:
    old=R/'references'/f'{name}-input.png';new=R/'native'/f'{name}.png'
    sheet=Image.new('RGB',(1254,688),(24,24,24));d=ImageDraw.Draw(sheet)
    for i,(label,fp) in enumerate([('BEFORE',old),('AFTER',new)]):
        d.text((8,i*344+4),f'{name} {label} native crop x0..1254 y467..787; old joint at row160',fill='white')
        sheet.paste(Image.open(fp).convert('RGB').crop((0,467,1254,787)),(0,i*344+24))
    dest=R/'qa'/f'{name}-center-before-after-native.png';sheet.save(dest);p.derived(dest,[old,new],{'method':'integer crop1254x320 at sourcey467..787, vertical before/after stack','resize':False,'sourceBoxLTRB':[0,467,1254,787]})
    rec=p.read(str(new)+'.generation.json');rec['visualInspection']={'at':p.stamp(),'scope':'actual displayed1254x1254 full output and native center crop','result':'roof central rectangular material edge removed, roof diagonal grooves and silhouettes retained; full quilt returns pending','note':'s3 left overlap x0..115 contains residual wall/water rectangular edge at y627; use s2-v2 ownership and inspect' if name=='s3' else 'shaded tile continuous through oldy627; overlap alignment and outer returns require quilt review'};p.write(str(new)+'.generation.json',rec)
print('s3/s4 native QA ready')
