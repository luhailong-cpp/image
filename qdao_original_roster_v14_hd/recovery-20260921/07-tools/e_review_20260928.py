from pathlib import Path
from PIL import Image,ImageDraw,ImageSequence
import json,hashlib
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
SRC=HERE/'candidate/07_moon_shadow_assassin_girl'
OUT=HERE/'e-review-20260928';OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for slot in ['idle/E.png']+[f'walk/E/{n:02}.png' for n in range(1,17)]:
 p=SRC/slot;m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'))
 rows.append({'path':slot,'attempt':m['attempt'],'status':'pending_visual_review','sha256':sha(p),'nativeSize':m['nativeMetrics']['size'],'actualModel':m.get('actualModel'),'actualQuality':m.get('actualQuality'),'sourceSha256':m['derivedFrom']['sha256'],'sourcePresent':Path(m['derivedFrom']['path']).is_file(),'metrics':m['outputMetrics']})
frames=[Image.open(SRC/f'walk/E/{i:02}.png').convert('RGBA') for i in range(1,17)]
gifs=[]
for mode,bg in [('dark',(30,38,46)),('light',(240,238,228))]:
 ink='white' if mode=='dark' else 'black'
 sheet=Image.new('RGB',(1024,1160),bg);draw=ImageDraw.Draw(sheet)
 previews=[]
 for n,im in enumerate(frames):
  x=n%4*256;y=n//4*290;thumb=im.resize((256,256),Image.Resampling.LANCZOS)
  sheet.paste(thumb,(x,y+28),thumb);draw.text((x+10,y+8),f'E{n+1:02}',fill=ink)
  f=Image.new('RGB',(512,512),bg);thumb=im.resize((512,512),Image.Resampling.LANCZOS);f.paste(thumb,(0,0),thumb);previews.append(f)
 sheet.save(OUT/f'E-contact-{mode}.png')
 gp=OUT/f'E-30ms-{mode}.gif';previews[0].save(gp,save_all=True,append_images=previews[1:],duration=[30]*16,loop=0,disposal=2,optimize=False)
 g=Image.open(gp);dur=[f.info['duration'] for f in ImageSequence.Iterator(g)];assert len(dur)==16 and dur==[30]*16
 gifs.append({'path':gp.name,'sha256':sha(gp),'frames':16,'durationMs':dur,'cycleMs':sum(dur)})
 seam=Image.new('RGB',(2048,552),bg)
 for k,n in enumerate([14,15,0,1]):
  seam.paste(previews[n],(k*512,40));ImageDraw.Draw(seam).text((k*512+10,10),f'E{n+1:02}',fill=ink)
 seam.save(OUT/f'E-seam-{mode}.png')
 idle=Image.open(SRC/'idle/E.png');idle_bg=Image.new('RGB',idle.size,bg);idle_bg.paste(idle,(0,0),idle);idle_bg.save(OUT/f'E-idle-{mode}.png')
manifest={'revision':'E 20260928 live QA','observedAt':datetime.now(timezone.utc).isoformat(),'files':rows,'walkCount':16,'idleCount':1,'missing':[],'directions':{'E':{'walk':16,'idle':True,'complete':True}},'gifs':gifs,'clientIntegration':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
html=(HERE/'preview-template.html').read_text(encoding='utf-8').replace('__MANIFEST__',json.dumps(manifest,ensure_ascii=False)).replace("'runtime/'","'../candidate/07_moon_shadow_assassin_girl/'").replace('preview/','').replace('idle-contact-light.png','E-idle-light.png').replace('8向站立总览','E独立站立').replace('八方向','E方向').replace('/128行走','/16行走').replace('/8独立站立','/1独立站立')
(OUT/'index.html').write_text(html,encoding='utf-8')
print(json.dumps({'out':str(OUT),'manifestSha256':sha(OUT/'manifest.json'),'gifs':gifs,'rows':[{'slot':r['path'],'attempt':r['attempt'],'height':r['metrics']['subject_height']} for r in rows]}))
