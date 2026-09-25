"""Render factual previews for isolated SE/SW source pixels; never fills missing slots."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;WORK=HERE/'work-SE-SW/candidate/06_thunder_caster_boy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--direction',choices=['SE','SW','both'],default='both');a=p.parse_args()
OUT=HERE/'sesw-previews'/a.revision;assert not OUT.exists();OUT.mkdir(parents=True)
dirs=['SE','SW'] if a.direction=='both' else [a.direction];rows=[];gifs=[]
for d in dirs:
    paths=[WORK/f'walk/{d}/{n:02d}.png' for n in range(1,17)]
    for mode,bg in [('dark',(30,38,46)),('light',(240,238,228))]:
        sheets=[];contact=Image.new('RGB',(2048,2176),bg)
        for n,path in enumerate(paths):
            canvas=Image.new('RGB',(512,512),bg)
            if path.exists():
                im=Image.open(path).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS);canvas.paste(im,(0,0),im)
                if mode=='dark':rows.append({'slot':f'{d}{n+1:02d}','path':str(path.resolve()),'sha256':sha(path)})
            else:ImageDraw.Draw(canvas).text((150,250),'MISSING / NO SUBSTITUTE',fill='red')
            sheets.append(canvas);x=(n%4)*512;y=(n//4)*544;contact.paste(canvas,(x,y+32));ImageDraw.Draw(contact).text((x+15,y+10),f'{d}{n+1:02d}',fill='white' if mode=='dark' else 'black')
        contact.save(OUT/f'{d}-contact-{mode}.png')
        seam=Image.new('RGB',(2048,544),bg)
        for col,n in enumerate((14,15,0,1)):
            seam.paste(sheets[n],(col*512,32));ImageDraw.Draw(seam).text((col*512+15,8),f'{d}{n+1:02d}',fill='white' if mode=='dark' else 'black')
        seam.save(OUT/f'{d}-seam15-16-01-02-{mode}.png')
        if all(path.exists() for path in paths):
            gif=OUT/f'{d}-30ms-{mode}.gif';sheets[0].save(gif,save_all=True,append_images=sheets[1:],duration=[30]*16,loop=0,disposal=2,optimize=False)
            im=Image.open(gif);times=[]
            for i in range(im.n_frames):im.seek(i);times.append(im.info['duration'])
            assert im.n_frames==16 and times==[30]*16
            gifs.append({'path':gif.name,'sha256':sha(gif),'frames':16,'durations_ms':times,'cycle_ms':480})
manifest={'created_at_utc':datetime.now(timezone.utc).isoformat(),'pngs':rows,'gifs':gifs,'missing':[f'{d}{n:02d}' for d in dirs for n in range(1,17) if not (WORK/f'walk/{d}/{n:02d}.png').exists()],
          'source_pngs_unchanged':True,'frame_duration_ms':30,'visual_review':'pending','client_review':False,
          'SE_phase_mapping':'SE05 source selected for SE13; SE13 source selected for SE05; remaining slots selected by observed phase'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
html='<!doctype html><meta charset="utf-8"><title>06 SE/SW 30ms previews</title><style>body{background:#eee9dc;color:#163831;font:18px system-ui;margin:24px}img{width:512px;max-width:95vw}a{color:#175d57}</style><h1>06 雷法少年 SE / SW 独立候选</h1><p>16帧 × 30ms = 480ms。每帧真实独立原图；美术/动态最终验收待root。</p>'
for d in dirs:
    html+=f'<h2>{d}</h2>'
    for mode in ('dark','light'):
        if (OUT/f'{d}-30ms-{mode}.gif').exists():html+=f'<img src="{d}-30ms-{mode}.gif" alt="{d} {mode}">'
        html+=f'<p><a href="{d}-contact-{mode}.png">16帧 {mode} 总览</a> / <a href="{d}-seam15-16-01-02-{mode}.png">15→16→01→02</a></p>'
(OUT/'index.html').write_text(html,encoding='utf-8')
print(json.dumps({'preview':str(OUT),'pngs':len(rows),'gifs':len(gifs),'missing':manifest['missing']}))
