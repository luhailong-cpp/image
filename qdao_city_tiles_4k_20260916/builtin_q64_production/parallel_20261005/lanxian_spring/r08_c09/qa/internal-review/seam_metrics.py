from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent
manifest=json.loads((OUT/'contact-manifest.json').read_text(encoding='utf-8'))
canvas=Image.new('RGB',(4096,4096))
for s in manifest['derivedFrom']:
    p=Path(s['file'])
    if hashlib.sha256(p.read_bytes()).hexdigest()!=s['sha256']:raise RuntimeError(f'Source changed: {p}')
    r,c=[int(v[1:]) for v in s['patch'].split('_')]
    with Image.open(p) as im:canvas.paste(im.convert('RGB').crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
a=np.asarray(canvas).astype(np.int16)
metrics=[]
for output in manifest['outputs'][:-1]:
    for sec in output['sections']:
        ss=sec['seamCore']
        if 'x' in ss:
            x=ss['x'];y0,y1=ss['yRange'];diff=a[y0:y1,x]-a[y0:y1,x-1]
            baseline=np.concatenate([a[y0:y1,x-1]-a[y0:y1,x-2],a[y0:y1,x+1]-a[y0:y1,x]])
        else:
            y=ss['y'];x0,x1=ss['xRange'];diff=a[y,x0:x1]-a[y-1,x0:x1]
            baseline=np.concatenate([a[y-1,x0:x1]-a[y-2,x0:x1],a[y+1,x0:x1]-a[y,x0:x1]])
        metrics.append({'id':sec['id'],'medianSignedRGB_delta_rightOrBelowMinusLeftOrAbove':np.median(diff,axis=0).tolist(),
            'meanAbsoluteRGBJump':round(float(np.abs(diff).mean()),3),'nearbyMeanAbsoluteRGBGradient':round(float(np.abs(baseline).mean()),3),
            'p95MaxChannelJump':round(float(np.percentile(np.abs(diff).max(axis=1),95)),3)})
(OUT/'seam-metrics.json').write_text(json.dumps({'method':'direct adjacent pixel RGB deltas; descriptive only, no acceptance threshold; natural material edges can increase scores','sourceSnapshot':'contact-manifest.json','segments':metrics},indent=2)+'\n',encoding='utf-8')
boxes=[('V3072 top',(2992,1000,3152,1136)),('V3072 middle',(2992,1390,3152,1560)),('V3072 lower',(2992,1760,3152,1920)),('H1024 gold edge',(3480,956,3840,1092))]
sheet=Image.new('RGB',(916,228),'#ededed');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',14)
x=0
for label,box in boxes:
    draw.text((x+2,6),label,fill='black',font=font)
    draw.text((x+2,24),str(box[:2]),fill='black',font=font)
    crop=canvas.crop(box);sheet.paste(crop,(x,48));x+=crop.width+12
sheet.save(OUT/'geometry_findings_1to1.png')
print(json.dumps(metrics,indent=2))
