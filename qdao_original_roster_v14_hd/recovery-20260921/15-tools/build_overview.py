"""Derived review only: eight directions at the same phase, no runtime edits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image, ImageDraw, ImageSequence

R = Path(__file__).resolve().parents[1]
P = R / '15-delivery-preview'
DIRECTIONS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sources = {d: [P/'runtime/walk'/d/f'{n:02d}.png' for n in range(1,17)] for d in DIRECTIONS}
hashes = {d: [sha(p) for p in ps] for d,ps in sources.items()}
exports = []
for bg, color, ink in [('light',(242,235,214),'#23352d'),('dark',(26,40,48),'#f5eddb')]:
    frames = []
    for n in range(16):
        sheet = Image.new('RGB',(1024,564),color)
        draw = ImageDraw.Draw(sheet)
        for j,d in enumerate(DIRECTIONS):
            im = Image.open(sources[d][n]).convert('RGBA')
            view = Image.new('RGBA',im.size,(*color,255)); view.alpha_composite(im)
            x,y = j%4*256, j//4*282
            sheet.paste(view.convert('RGB').resize((256,256),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+8,y+260),f'{d}   {n+1:02d}/16   30 ms',fill=ink)
        frames.append(sheet)
    dest = P/'derived'/f'eight-directions-30ms-{bg}.gif'
    frames[0].save(dest,save_all=True,append_images=frames[1:],duration=30,loop=0,disposal=2,optimize=False)
    with Image.open(dest) as gif:
        durations = [im.info.get('duration') for im in ImageSequence.Iterator(gif)]
    assert durations == [30]*16
    frames[0].save(P/'derived'/f'eight-directions-first-frame-{bg}.png')
    exports.append({'path':str(dest),'sha256':sha(dest),'frameCount':16,'frameDurationsMs':durations,'cycleMs':480,'loop':0})
for d,ps in sources.items(): assert [sha(p) for p in ps] == hashes[d]
report={'generatedAt':datetime.now(timezone.utc).isoformat(),'sourceOutputHashes':hashes,'exports':exports,'dynamicPlaybackObserved':False,'derivedDisplayOnly':True}
(P/'derived'/'eight-directions-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'exports':exports,'sourceCount':128},indent=2))
