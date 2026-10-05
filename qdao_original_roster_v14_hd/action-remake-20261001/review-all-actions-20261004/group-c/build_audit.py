import json, hashlib, datetime
from pathlib import Path
from PIL import Image, ImageDraw

BASE=Path('D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001')
OUT=BASE/'review-all-actions-20261004/group-c'
IDS=['10_crimson_spear_girl','14_short_hair_snow_summoner_girl','15_water_dragon_scholar_boy','17_ghost_script_calligrapher_boy','20_star_formation_master_girl']
OUT.mkdir(parents=True,exist_ok=True)
records=[]
for cid in IDS:
    home=BASE/'characters'/cid
    mf=home/('merge-manifest.json' if cid.startswith('20_') else 'manifest.json')
    raw=mf.read_bytes(); m=json.loads(raw)
    fs=m.get('slots') or m.get('frames')
    if fs is None:
        fs=[]
        for g in m.get('sequences',m.get('groups',[])):
            fs.extend(dict(f,action=g['action'],direction=g['direction']) for f in g['frames'])
    groups={}
    for f in fs:
        rel=f.get('file') or f.get('path') or f.get('output') or f.get('source')
        p=home/rel
        if not p.is_file():
            records.append(dict(character=cid,action=f['action'],direction=f['direction'],frame=f['frame'],path=str(p),error='missing'));continue
        sha=hashlib.sha256(p.read_bytes()).hexdigest()
        rec=dict(character=cid,action=f['action'],direction=f['direction'],frame=f['frame'],path=p.as_posix(),sha256=sha,manifestSHA=f.get('sha256'),shaMatches=sha==f.get('sha256'),mtimeUTC=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat())
        records.append(rec);groups.setdefault((f['action'],f['direction']),[]).append(rec)
    for (a,d), rows in groups.items():
        rows.sort(key=lambda f:f['frame'])
        cols=4; cellw=320; cellh=390
        sheet=Image.new('RGB',(cols*cellw,((len(rows)+3)//4)*cellh+40),(244,240,225));draw=ImageDraw.Draw(sheet)
        draw.text((8,8),f'{cid} | {a}/{d} | CURRENT MANIFEST FILES | full canvas + lower-leg crop',fill=(0,0,0))
        for j,r in enumerate(rows):
            im=Image.open(r['path']).convert('RGBA')
            x=(j%4)*cellw;y=40+(j//4)*cellh
            full=im.resize((256,256),Image.Resampling.LANCZOS)
            sheet.paste(full,(x+32,y+20),full)
            # Fixed source crop for QA only; never writes/repositions any game PNG.
            feet=im.crop((160,610,864,1024)).resize((304,179),Image.Resampling.LANCZOS)
            # Dedicated feet-only sheet is generated below for closer axis inspection.
            draw.text((x+8,y+2),f"{a}-{d}-{r['frame']:02d} SHA {r['sha256'][:10]}",fill=(0,0,0))
            hand=im.crop((128,352,896,736)).resize((304,112),Image.Resampling.LANCZOS)
            sheet.paste(hand,(x+8,y+275),hand)
        dest=OUT/cid/f'{a}-{d}-full.png';dest.parent.mkdir(exist_ok=True);sheet.save(dest)
        feet_sheet=Image.new('RGB',(1280,((len(rows)+3)//4)*210+35),(244,240,225));dd=ImageDraw.Draw(feet_sheet)
        dd.text((8,8),f'{cid} | {a}/{d} | fixed lower canvas crop',fill='black')
        for j,r in enumerate(rows):
            im=Image.open(r['path']).convert('RGBA');crop=im.crop((160,570,864,1024)).resize((304,196),Image.Resampling.LANCZOS)
            x=(j%4)*320;y=35+(j//4)*210
            dd.text((x+5,y),f"{r['frame']:02d} {r['sha256'][:10]}",fill='black');feet_sheet.paste(crop,(x+8,y+14),crop)
        feet_sheet.save(OUT/cid/f'{a}-{d}-feet.png')
    print(cid,len(fs),'frames',len(groups),'groups',sum(not r.get('shaMatches',False) for r in records if r['character']==cid),'SHA mismatches')
    (OUT/cid/'manifest-snapshot.json').write_bytes(raw)
(OUT/'source-evidence.json').write_text(json.dumps(dict(createdAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='read-only QA derivatives; no source images changed; static review is separate from playback review',frames=records),ensure_ascii=False,indent=2),encoding='utf-8')
