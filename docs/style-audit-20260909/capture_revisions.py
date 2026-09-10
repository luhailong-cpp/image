from audit_tools import *
from datetime import datetime,timezone
d=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
s=json.loads((OUT/'supplement.json').read_text(encoding='utf-8'))
byid={r['id']:r for r in d['records']+s['records']}; records=[];pages=[]
(OUT/'contacts'/'revisions').mkdir(exist_ok=True,parents=True)
for change in s['changed_since_review']:
    old=byid[change['id']];p=ROOT/old['path'];im=open_art(p)
    r=dict(old);r.update(previous_sha256=old['sha256'],sha256=hashlib.sha256(p.read_bytes()).hexdigest(),representative=old['id'],review_type='revised_direct_visual',revision=True)
    r['size']=list(im.size);r['alpha_extrema']=list(im.getchannel('A').getextrema());r['visual_hash']=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest()
    preview(im).save(OUT/'thumbs'/f'{r["id"]}-revised.jpg',quality=92)
    r['thumbnail']=f'thumbs/{r["id"]}-revised.jpg'
    records.append(r)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
for offset in range(0,len(records),16):
    batch=records[offset:offset+16];page=offset//16+1;rel=f'contacts/revisions/{page:02d}.jpg'
    sheet=Image.new('RGB',(1120,1120),'#f6f2e9');draw=ImageDraw.Draw(sheet)
    draw.text((15,10),'Changed during audit / current revision / page '+str(page),font=font,fill='#173e32')
    for n,r in enumerate(batch):
        x=10+n%4*280;y=38+n//4*267
        sheet.paste(Image.open(OUT/r['thumbnail']),(x,y));r['contact_page']=rel
        draw.text((x,y+212),r['id']+' '+str(r['size']),font=font,fill='#173e32')
        draw.text((x,y+230),Path(r['path']).name[:34],font=font,fill='#343b38')
    sheet.save(OUT/rel,quality=92);pages.append({'owner':'revisions','path':rel,'ids':[r['id'] for r in batch]})
(OUT/'revisions.json').write_text(json.dumps({'captured_utc':datetime.now(timezone.utc).isoformat(),'records':records,'pages':pages},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'records':len(records),'pages':pages}))
