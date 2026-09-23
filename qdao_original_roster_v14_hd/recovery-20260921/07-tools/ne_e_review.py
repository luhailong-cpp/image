from pathlib import Path
from PIL import Image, ImageDraw
import sys,json,hashlib
here=Path(__file__).resolve().parent
d=sys.argv[1]
src=here/'candidate/07_moon_shadow_assassin_girl/walk'/d
out=here/'ne-e-review';out.mkdir(exist_ok=True)
frames=[Image.open(src/f'{i:02}.png').convert('RGBA') for i in range(1,17)]
for mode,bg in [('dark',(30,38,46)),('light',(240,238,228))]:
    ink='white' if mode=='dark' else 'black'
    sheet=Image.new('RGB',(1024,1160),bg);draw=ImageDraw.Draw(sheet)
    previews=[]
    for n,im in enumerate(frames):
        x=n%4*256;y=n//4*290
        thumb=im.resize((256,256),Image.Resampling.LANCZOS)
        sheet.paste(thumb,(x,y+28),thumb);draw.text((x+10,y+8),f'{d}{n+1:02}',fill=ink)
        f=Image.new('RGB',(512,512),bg);thumb=im.resize((512,512),Image.Resampling.LANCZOS);f.paste(thumb,(0,0),thumb);previews.append(f)
    sheet.save(out/f'{d}-contact-{mode}.png')
    previews[0].save(out/f'{d}-30ms-{mode}.gif',save_all=True,append_images=previews[1:],duration=[30]*16,loop=0,disposal=2,optimize=False)
    seam=Image.new('RGB',(2048,552),bg)
    for k,n in enumerate([14,15,0,1]):
        seam.paste(previews[n],(k*512,40));ImageDraw.Draw(seam).text((k*512+10,10),f'{d}{n+1:02}',fill=ink)
    seam.save(out/f'{d}-seam-{mode}.png')
rows=[]
for n in range(1,17):
    p=src/f'{n:02}.png';m=json.loads(Path(str(p)+'.generation.json').read_text())
    rows.append({'frame':n,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'attempt':m['attempt'],'height':m['outputMetrics']['subject_height'],'head':m['outputMetrics'].get('headBandWidth95'),'scale':m['wholeCanvasScale']})
(out/f'{d}-current.json').write_text(json.dumps({'frames':rows,'durationMs':30,'cycleMs':480,'status':'pending_visual_review'},indent=2))
print(json.dumps(rows))

