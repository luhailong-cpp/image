import json,hashlib,datetime,pathlib
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=pathlib.Path(__file__).parent
ids=['05_celestial_musician_girl','06_thunder_caster_boy','07_moon_shadow_assassin_girl','08_alchemy_prodigy_boy','09_bamboo_archer_girl']
sources={ids[0]:'final/manifest.json',ids[1]:'preview/manifest.json',ids[2]:'manifest.json',ids[3]:'manifest.json',ids[4]:'manifest.json'}
evidence={'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'current manifest PNG static review only; no dynamic/client acceptance','characters':{}}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
for cid in ids:
    base=ROOT/'characters'/cid
    mf=base/sources[cid]; obj=json.loads(mf.read_text(encoding='utf-8-sig'))
    groups={}
    if 'sequences' in obj:
        for seq in obj['sequences']:
            group=(seq['action'],seq['direction'])
            groups[group]=seq['frames']
    else:
        for f in obj['frames']:
            slot=f.get('slot','').split('/')
            group=(f.get('action',slot[0] if slot else ''),f.get('direction',slot[1] if len(slot)>1 else ''))
            groups.setdefault(group,[]).append(f)
    evidence['characters'][cid]={'manifest':str(mf),'manifestSha256':hashlib.sha256(mf.read_bytes()).hexdigest(),'groups':{}}
    (OUT/cid).mkdir(parents=True,exist_ok=True)
    for (act,di),frames in sorted(groups.items()):
        frames.sort(key=lambda f:int(f.get('frame',f.get('number',f.get('index',f.get('slot','/0').split('/')[-1])))))
        rows=(len(frames)+3)//4
        sheet=Image.new('RGB',(1040,36+rows*368),(242,239,230)); draw=ImageDraw.Draw(sheet)
        draw.text((8,8),f'{cid[:2]} {act}/{di} current PNG; whole + lower body; static only',font=font,fill='black')
        entries=[]
        # Use one union crop for this sequence, not per-frame resizing.
        ims=[]; union=None
        for f in frames:
            path=base/f.get('file',f.get('path'))
            im=Image.open(path).convert('RGBA'); bb=im.getchannel('A').getbbox(); ims.append((f,path,im))
            union=bb if union is None else (min(union[0],bb[0]),min(union[1],bb[1]),max(union[2],bb[2]),max(union[3],bb[3]))
        x0,y0,x1,y1=union
        pad=12; size=max(x1-x0,y1-y0)+2*pad; cx=(x0+x1)//2; cy=(y0+y1)//2
        crop=(cx-size//2,cy-size//2,cx-size//2+size,cy-size//2+size)
        # Fixed lower-half area per group; layout is QA only.
        lower=(max(0,x0-15),max(0,y0+int((y1-y0)*0.59)),min(1024,x1+15),min(1024,y1+12))
        for n,(f,path,im) in enumerate(ims):
            sha=hashlib.sha256(path.read_bytes()).hexdigest(); declared=f.get('sha256'); label=path.stem
            entries.append({'frame':label,'file':str(path),'sha256':sha,'manifestSha256':declared,'shaMatchesManifest':sha==declared,'size':list(im.size)})
            xx=(n%4)*260; yy=36+(n//4)*368
            draw.rectangle((xx,yy,xx+259,yy+367),outline=(175,175,165))
            draw.text((xx+6,yy+4),f'{act}/{di}/{label} {sha[:8]}',font=small,fill='black')
            whole=im.crop(crop); whole.thumbnail((250,250),Image.Resampling.LANCZOS)
            sheet.paste(whole,(xx+(260-whole.width)//2,yy+22),whole)
            detail=im.crop(lower); detail.thumbnail((250,90),Image.Resampling.LANCZOS)
            sheet.paste(detail,(xx+(260-detail.width)//2,yy+274),detail)
        dest=OUT/cid/f'{act}-{di}.png'; sheet.save(dest)
        evidence['characters'][cid]['groups'][f'{act}/{di}']={'sheet':str(dest),'fixedQaCrop':list(crop),'fixedLowerCrop':list(lower),'frames':entries,'staticViewed':False}
(OUT/'source-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:len(v['groups']) for k,v in evidence['characters'].items()}))
