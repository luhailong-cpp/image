"""Read-only asset inventory and review contact sheets. Never modifies source art."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import argparse, base64, hashlib, io, json, re, subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
EXTS={'.png','.jpg','.jpeg','.webp','.gif','.svg','.bmp','.tif','.tiff','.avif','.ico','.tga','.dds','.psd'}
SKIP={'.git','node_modules','.venv','venv','__pycache__'}

def owner(p):
    s=p.as_posix(); top=p.parts[0]
    if top in {'.work','designs','client_ui_refresh_20260908'}: return 'client_designs'
    if top=='exact_qdao_slices' or top.startswith('q_daoist_login_ui_') or s.startswith(('qdao_gpt_image2_refresh_v7/ui/','qdao_ui_redesign_v5/components/','qdao_ui_redesign_v5/hud/')): return 'ui'
    if top in {'character_move_8dir','q_daoist_character_pack_4096','qdao_asset_refresh_v6','qdao_chibi_pets_v1'} or s.startswith('qdao_ui_redesign_v5/pet/'): return 'actors'
    if top=='qdao_gpt_image2_refresh_v7' and not any(x in s for x in ['/scene','/background','/city','/screen']): return 'actors'
    return 'scenes'

def open_art(p):
    if p.suffix.lower()!='.svg': return Image.open(p).convert('RGBA')
    data=p.read_text(encoding='utf-8-sig')
    tree=ET.fromstring(data)
    images=[e for e in tree.iter() if e.tag.split('}')[-1]=='image']
    others=[e for e in tree.iter() if e.tag.split('}')[-1] in {'text','path','rect','circle','polygon','line','ellipse'}]
    if len(images)==1 and not others:
        href=images[0].get('href') or images[0].get('{http://www.w3.org/1999/xlink}href','')
        if href.startswith('data:image/') and ';base64,' in href:
            return Image.open(io.BytesIO(base64.b64decode(href.split(';base64,',1)[1]))).convert('RGBA')
    return None

def preview(im, w=260, h=210):
    im=im.copy(); box=im.getchannel('A').getbbox()
    if box and (box[2]-box[0])*(box[3]-box[1])<im.width*im.height*.8: im=im.crop(box)
    im.thumbnail((w,h),Image.Resampling.LANCZOS)
    out=Image.new('RGB',(w,h),'#e9e1ce'); d=ImageDraw.Draw(out)
    for y in range(0,h,16):
        for x in range(0,w,16):
            if (x//16+y//16)%2: d.rectangle((x,y,x+15,y+15),fill='#ded8c9')
    out.paste(im,((w-im.width)//2,(h-im.height)//2),im)
    return out

def inventory():
    all_paths=[]; folders=[]
    for base,dirs,files in __import__('os').walk(ROOT):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and Path(base,d)!=OUT)
        rel=Path(base).relative_to(ROOT)
        folders.append({'path':rel.as_posix(),'visual_count':sum(Path(f).suffix.lower() in EXTS for f in files)})
        all_paths.extend(Path(base,f) for f in files if Path(f).suffix.lower() in EXTS)
    records=[]; seen={}; group_reps={}; (OUT/'thumbs').mkdir(exist_ok=True)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
    for i,p in enumerate(sorted(all_paths),1):
        rel=p.relative_to(ROOT); data=p.read_bytes(); sha=hashlib.sha256(data).hexdigest()
        r={'id':f'A{i:04d}','path':rel.as_posix(),'folder':rel.parent.as_posix(),'top_folder':rel.parts[0] if len(rel.parts)>1 else '[root]','owner':owner(rel),'extension':p.suffix.lower(),'bytes':len(data),'sha256':sha}
        try:
            im=open_art(p)
            if im is None:
                r.update(review_type='svg_code',representative=r['id'])
            else:
                r['size']=list(im.size)
                r['alpha_extrema']=list(im.getchannel('A').getextrema())
                # Hash of decoded pixels relates PNG wrappers, metadata variants and exact aliases.
                vh=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest(); r['visual_hash']=vh
                key=(r['owner'],vh); r['representative']=seen.get(key,r['id'])
                r['review_type']='direct_visual' if key not in seen else 'pixel_identical_alias'
                if key not in seen:
                    seen[key]=r['id']; group_reps.setdefault(r['owner'],[]).append(r)
                    preview(im).save(OUT/'thumbs'/f'{r["id"]}.jpg',quality=90)
                im.close()
        except Exception as e: r.update(review_type='read_error',error=str(e),representative=r['id'])
        records.append(r)
    pages=[]
    for group,reps in group_reps.items():
        (OUT/'contacts'/group).mkdir(parents=True,exist_ok=True)
        for offset in range(0,len(reps),16):
            batch=reps[offset:offset+16]; page=offset//16+1
            sheet=Image.new('RGB',(1120,1120),'#f6f2e9'); d=ImageDraw.Draw(sheet)
            d.text((15,10),f'{group} / page {page:02d} / full path in inventory.json',fill='#252c27',font=font)
            for n,r in enumerate(batch):
                x=10+(n%4)*280; y=38+(n//4)*267
                im=Image.open(OUT/'thumbs'/f'{r["id"]}.jpg'); sheet.paste(im,(x,y))
                label=f'{r["id"]}  {r["size"][0]}x{r["size"][1]}'
                name=Path(r['path']).name
                d.text((x,y+212),label,fill='#173e32',font=font)
                d.text((x,y+230),name[:34],fill='#343b38',font=font)
                if len(name)>34:d.text((x,y+246),name[34:68],fill='#343b38',font=font)
                r['contact_page']=f'contacts/{group}/{page:02d}.jpg'
            path=OUT/'contacts'/group/f'{page:02d}.jpg';sheet.save(path,quality=91)
            pages.append({'owner':group,'page':page,'path':path.relative_to(OUT).as_posix(),'ids':[r['id'] for r in batch]})
    index={r['id']:r for r in records}
    for r in records:
        rep=index[r['representative']]
        if 'contact_page' in rep:r['contact_page']=rep['contact_page']
    result={'root':ROOT.as_posix(),'scope':'All on-disk folders including hidden .work; excludes Git internals, installed dependencies and this audit output. No original images modified. SVG with single embedded image reviewed through decoded pixels; other SVG require source/render review.','records':records,'folders':folders,'pages':pages}
    (OUT/'inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'files':len(records),'folders':len(folders),'owners':{g:{'files':sum(r['owner']==g for r in records),'visual_representatives':len(rs),'pages':sum(p['owner']==g for p in pages)} for g,rs in group_reps.items()},'nonvisual':[{k:r[k] for k in ['id','path','review_type']} for r in records if r['review_type'] in {'svg_code','read_error'}]},ensure_ascii=False,indent=2))

def emit(path,width):
    p=Path(path)
    if not p.is_absolute():p=ROOT/p
    im=open_art(p)
    if im is None:raise RuntimeError('SVG needs renderer')
    im.thumbnail((width,width),Image.Resampling.LANCZOS)
    out=Image.new('RGB',im.size,'#e9e1ce');out.paste(im,(0,0),im)
    stream=io.BytesIO();out.save(stream,format='JPEG',quality=90)
    print(base64.b64encode(stream.getvalue()).decode())

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['inventory','emit']);ap.add_argument('path',nargs='?');ap.add_argument('--width',type=int,default=1120);args=ap.parse_args()
    if args.mode=='inventory':inventory()
    else:emit(args.path,args.width)
