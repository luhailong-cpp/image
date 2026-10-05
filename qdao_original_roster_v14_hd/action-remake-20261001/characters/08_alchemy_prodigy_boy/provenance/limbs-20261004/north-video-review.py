from pathlib import Path
from PIL import Image, ImageDraw
import av, hashlib, json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
source=json.loads((ROOT/'provenance/axis-20261004/video-source.json').read_text())
p=Path(source['file'])
assert hashlib.sha256(p.read_bytes()).hexdigest()==source['sha256']
frames=[]
with av.open(str(p)) as container:
    for frame in container.decode(video=0): frames.append(frame.to_image())
notes=[]
for start in [0,88,148,283]:
    canvas=Image.new('RGB',(1008,8*290),'#eee9db')
    draw=ImageDraw.Draw(canvas)
    for j in range(32):
        n=start+j
        im=frames[n].crop((580,185,706,316)).resize((252,262),Image.Resampling.NEAREST)
        x=(j%4)*252;y=(j//4)*290
        canvas.paste(im,(x,y+25))
        draw.text((x+5,y+5),f'frame {n} / {n/24:.3f} s',fill='#203b32')
    dest=OUT/f'north-video-{start:03d}.jpg'
    canvas.save(dest,quality=95)
    notes.append({'file':dest.relative_to(ROOT).as_posix(),'firstFrame':start,'lastFrame':start+31,'crop':[580,185,706,316],'inspectionUpscale':'2x nearest only'})
(OUT/'north-video-source-review.json').write_text(json.dumps({'source':source,'decodedFrameCount':len(frames),'segments':notes,'use':'motion direction/continuity/contact only, not style; small source character and overlays prevent precise individual finger/toe inspection'},ensure_ascii=False,indent=2),encoding='utf-8')
print({'decoded':len(frames),'segments':len(notes)})
