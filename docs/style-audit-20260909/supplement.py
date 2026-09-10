"""Append files added during the read-only audit without renumbering the frozen inventory."""
from audit_tools import *
from datetime import datetime, timezone

d=json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
previous_path=OUT/'supplement.json'
previous=json.loads(previous_path.read_text(encoding='utf-8')) if previous_path.exists() else {'records':[],'pages':[]}
known={r['path']:r for r in d['records']+previous['records']}
hashes={r.get('visual_hash'):r['representative'] for r in d['records']+previous['records'] if r.get('visual_hash')}
new=[]; changed=[]
for base,dirs,files in __import__('os').walk(ROOT):
    dirs[:]=sorted(x for x in dirs if x not in SKIP and Path(base,x)!=OUT)
    for name in sorted(files):
        p=Path(base,name)
        if p.suffix.lower() not in EXTS:continue
        rel=p.relative_to(ROOT).as_posix(); data=p.read_bytes(); sha=hashlib.sha256(data).hexdigest()
        if rel in known:
            if sha!=known[rel]['sha256']:changed.append({'path':rel,'id':known[rel]['id'],'current_sha256':sha,'reviewed_sha256':known[rel]['sha256']})
            continue
        i=len(previous['records'])+len(new)+1; rid=f'X{i:04d}'
        r={'id':rid,'path':rel,'folder':p.parent.relative_to(ROOT).as_posix(),'top_folder':p.relative_to(ROOT).parts[0],'owner':'supplement','extension':p.suffix.lower(),'bytes':len(data),'sha256':sha,'representative':rid}
        try:
            im=open_art(p)
            if im is None:r['review_type']='svg_code'
            else:
                r['size']=list(im.size); r['alpha_extrema']=list(im.getchannel('A').getextrema())
                vh=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest();r['visual_hash']=vh
                if vh in hashes:r.update(review_type='pixel_identical_alias',representative=hashes[vh])
                else:
                    hashes[vh]=rid;r['review_type']='direct_visual'
                    preview(im).save(OUT/'thumbs'/f'{rid}.jpg',quality=90)
                im.close()
        except Exception as e:r.update(review_type='read_error',error=str(e))
        new.append(r)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
reps=[r for r in new if r['review_type']=='direct_visual'];pages=[]
(OUT/'contacts'/'supplement').mkdir(parents=True,exist_ok=True)
for offset in range(0,len(reps),16):
    batch=reps[offset:offset+16]; npage=len(previous['pages'])+offset//16+1
    sheet=Image.new('RGB',(1120,1120),'#f6f2e9');draw=ImageDraw.Draw(sheet)
    draw.text((15,10),f'Supplement / page {npage:02d} / new files during review',font=font,fill='#173e32')
    relpage=f'contacts/supplement/{npage:02d}.jpg'
    for n,r in enumerate(batch):
        x=10+n%4*280;y=38+n//4*267
        sheet.paste(Image.open(OUT/'thumbs'/f'{r["id"]}.jpg'),(x,y))
        draw.text((x,y+212),r['id']+' '+str(r['size']),font=font,fill='#173e32')
        name=Path(r['path']).name
        draw.text((x,y+230),name[:34],font=font,fill='#343b38')
        r['contact_page']=relpage
    sheet.save(OUT/relpage,quality=91);pages.append({'owner':'supplement','path':relpage,'ids':[r['id'] for r in batch]})
previous['records']+=new;previous['pages']+=pages
previous['snapshot_utc']=datetime.now(timezone.utc).isoformat()
previous['changed_since_review']=changed
previous['missing_since_review']=[r['path'] for r in known.values() if not (ROOT/r['path']).exists()]
previous_path.write_text(json.dumps(previous,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'added':len(new),'direct':len(reps),'pages':pages,'changed':changed,'new_files':[{'id':r['id'],'path':r['path'],'representative':r['representative']} for r in new]},ensure_ascii=False,indent=2))
