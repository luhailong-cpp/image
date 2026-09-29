"""Read current NW only; build SHA-bound full-size offline review evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
from PIL import Image, ImageDraw, ImageSequence, ImageOps
import numpy as np
from finalize_current import metrics

HERE = Path(__file__).resolve().parent
SRC = HERE / 'candidate/07_moon_shadow_assassin_girl'
OUT = HERE / 'nw-final-repair-20260928'
OUT.mkdir(exist_ok=True)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
rows, pictures = [], {}
backgrounds = {'dark': (30, 38, 46), 'light': (240, 238, 228)}
for slot in ['idle/NW.png'] + [f'walk/NW/{n:02}.png' for n in range(1,17)]:
    p = SRC / slot
    record = Path(str(p) + '.generation.json')
    meta = read(record)
    im = Image.open(p)
    assert im.mode == 'RGBA' and im.size == (1024,1024)
    a = np.asarray(im.getchannel('A'))
    info = metrics(im)
    name = 'idle' if slot.startswith('idle') else p.stem
    pair = Image.new('RGB', (2048,1024))
    pictures[name] = {}
    for index, (kind, bg) in enumerate(backgrounds.items()):
        composite = Image.new('RGB', im.size, bg)
        composite.paste(im, (0,0), im)
        pictures[name][kind] = composite
        pair.paste(composite, (1024*index,0))
    review = OUT / f'NW-{name}-pair-1024.png'
    pair.save(review)
    raw = Path(meta.get('derivedFrom',{}).get('path',''))
    native_sha = meta.get('derivedFrom',{}).get('sha256')
    evidence = {}
    for key in ['requestEvidence', 'resultEvidence']:
        entry = meta.get(key,{})
        path = Path(entry.get('path',''))
        evidence[key] = {'path':str(path), 'sha256':sha(path) if path.is_file() else None,
                         'matchesSidecar':sha(path)==entry.get('sha256') if path.is_file() else None}
    rows.append({'slot':slot,'attempt':meta['attempt'],'sha256':sha(p),'sidecarSha256':sha(record),
                 'outputMatchesSidecar':sha(p)==meta['outputSha256'],'metrics':info,
                 'sourcePath':str(raw),'sourceSha256':native_sha,'sourcePresent':raw.is_file(),
                 'sourceCurrentHashMatches':sha(raw)==native_sha if raw.is_file() else None,
                 'nativeSize':list(Image.open(raw).size) if raw.is_file() else None,
                 'actualModel':meta.get('actualModel'),'actualQuality':meta.get('actualQuality'),
                 'evidence':evidence,'reviewImage':str(review),'reviewImageSha256':sha(review),
                 'pixelHash':hashlib.sha256(im.tobytes()).hexdigest(),
                 'mirrorHash':hashlib.sha256(ImageOps.mirror(im).tobytes()).hexdigest()})
gifs=[]
for kind in backgrounds:
    frames = [pictures[f'{n:02}'][kind] for n in range(1,17)]
    p = OUT / f'NW-{kind}-30ms.gif'
    frames[0].save(p,save_all=True,append_images=frames[1:],duration=30,loop=0,optimize=False,disposal=2)
    gif = Image.open(p)
    durations=[f.info.get('duration') for f in ImageSequence.Iterator(gif)]
    gifs.append({'path':str(p),'sha256':sha(p),'durationMs':durations,'frameCount':len(durations),
                 'metadataPass':durations==[30]*16,'visuallyPlayed':False})
    for name, numbers in [('all',list(range(1,17))),('height',[9,10,11,12,13,14]),('seam',[14,15,16,1,2])]:
        sheet = Image.new('RGB',(512*min(4,len(numbers)),548*((len(numbers)+3)//4)),backgrounds[kind])
        draw=ImageDraw.Draw(sheet)
        for i,n in enumerate(numbers):
            x,y=(i%4)*512,(i//4)*548
            sheet.paste(pictures[f'{n:02}'][kind].resize((512,512)),(x,y+36))
            draw.text((x+10,y+10),f'NW {n:02}',fill='white' if kind=='dark' else 'black')
        sheet.save(OUT/f'NW-{name}-{kind}.png')
duplicates=[]
for i,r in enumerate(rows):
    for prev in rows[:i]:
        if r['pixelHash']==prev['pixelHash'] or r['pixelHash']==prev['mirrorHash']:
            duplicates.append([prev['slot'],r['slot']])
report={'scope':'07 NW only; current candidate static review binding',
        'observedAt':datetime.now(timezone.utc).isoformat(),'files':rows,'gifs':gifs,
        'pixelOrExactMirrorDuplicates':duplicates,'browserPlaybackPerformed':False,
        'clientIntegration':False,'formalApproval':False,'reviewState':'pending_actual_image_inspection',
        'changedSlots':['walk/NW/11.png','walk/NW/12.png','walk/NW/13.png','walk/NW/16.png'],
        'sourceAbsenceNote':'idle/NW and walk/NW/01 have historical authorized deletion evidence only; missing native files were not reverified.',
        'generationCallsThisRepair':3,'paidApiCalls':0}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'out':str(OUT),'count':len(rows),'sidecarsMatch':all(r['outputMatchesSidecar'] for r in rows),
                  'height':{r['slot']:r['metrics']['subject_height'] for r in rows},'duplicates':duplicates}))
