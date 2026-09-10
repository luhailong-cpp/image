"""Build frozen audit previews for formal UI contracts and new v10 art."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib,importlib.util

OUT=Path(__file__).resolve().parent/'ui'
OUT.mkdir(exist_ok=True)
ROOT=OUT.parents[3]
sp=importlib.util.spec_from_file_location('audit',ROOT/'docs/style-audit-20260909/audit_tools.py')
a=importlib.util.module_from_spec(sp);sp.loader.exec_module(a)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
contract=json.loads((ROOT/'qdao_ui_style_recut_v10/contracts/current_files.json').read_text(encoding='utf-8'))
snapshot=json.loads((OUT.parent/'snapshot.json').read_text(encoding='utf-8'))
snap={r['path']:r for r in snapshot['records']}
inputs=[{'path':r['path'],'family':r['family'],'source':'formal_contract'} for r in contract['files']]
inputs += [{'path':r['path'],'family':'v10_draft','source':'new_draft'} for r in snapshot['new_or_changed'] if r['path'].startswith('qdao_ui_style_recut_v10/')]
seen={};records=[];images={}
for i,src in enumerate(inputs,1):
    p=ROOT/src['path'];raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    assert sha==snap[src['path']]['sha256'],src['path']
    im=Image.open(p).convert('RGBA')
    vh=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest()
    id=f'U{i:03}'
    rep=seen.setdefault(vh,id)
    r=dict(src,id=id,sha256=sha,size=list(im.size),pixel_hash=vh,representative=rep)
    records.append(r)
    if rep==id:images[id]=a.preview(im,330,205)
    im.close()
pages=[]
for group in ['formal_contract','new_draft']:
    grouprecs=[r for r in records if r['source']==group and r['id']==r['representative']]
    for start in range(0,len(grouprecs),16):
        pg=f'{group}-{start//16+1:02}.jpg';batch=grouprecs[start:start+16]
        page=Image.new('RGB',(1400,1130),'#f3ecdd');d=ImageDraw.Draw(page)
        d.text((16,12),f'CURRENT UI REVIEW | {group} | {start//16+1}',font=font,fill='#183c30')
        for i,r in enumerate(batch):
            x=(i%4)*350+10;y=(i//4)*272+40
            page.paste(images[r['id']],(x,y))
            d.text((x,y+211),f'{r["id"]} | {r["family"]} | {r["size"]}',font=font,fill='#183c30')
            name=Path(r['path']).name
            d.text((x,y+232),name[:40],font=font,fill='#45433c')
            if len(name)>40:d.text((x,y+250),name[40:80],font=font,fill='#45433c')
            r['contact_page']=pg
        page.save(OUT/pg,quality=94)
        pages.append({'file':pg,'ids':[r['id'] for r in batch]})
byid={r['id']:r for r in records}
for r in records:
    r['contact_page']=byid[r['representative']]['contact_page']
result={'records':records,'pages':pages,'formal_count':158,'draft_count':len(inputs)-158,'pixel_representatives':len(images),'source_assets_modified':False}
(OUT/'inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(inputs),'pixel_representatives':len(images),'pages':pages},ensure_ascii=False))
