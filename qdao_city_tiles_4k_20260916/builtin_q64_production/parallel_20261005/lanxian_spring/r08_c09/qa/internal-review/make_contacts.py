from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
NATIVE = OUT.parent.parent / 'native'
CORE, HALO, RADIUS = 1024, 115, 160
WIDTH = RADIUS * 2
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 16)
canvas = Image.new('RGB', (4096, 4096), '#50364f')
sources=[]
for r in range(1,5):
    for c in range(1,5):
        path=NATIVE/f'r{r:02d}_c{c:02d}.png'
        rec=path.with_name(path.name+'.generation.json')
        if not path.exists() or not rec.exists():
            raise RuntimeError(f'Missing image/record: {path}')
        before=digest(path)
        record=json.loads(rec.read_text(encoding='utf-8-sig'))
        if record['sha256'] != before:
            raise RuntimeError(f'Image/record mismatch: {path}')
        with Image.open(path) as im:
            im.load()
            assert im.size==(1254,1254)
            canvas.paste(im.convert('RGB').crop((115,115,1139,1139)), ((c-1)*1024,(r-1)*1024))
        if digest(path)!=before:
            raise RuntimeError(f'Changed during read: {path}')
        sources.append({'patch':path.stem,'file':str(path),'sha256':before,'record':str(rec),'recordSha256':digest(rec)})
created=datetime.now(timezone.utc).isoformat()
outputs=[]
for r in range(4):
    sheet=Image.new('RGB',(WIDTH*3+24,1064),'#ededed')
    draw=ImageDraw.Draw(sheet)
    sections=[]
    for k in range(1,4):
        x=k*1024; y=r*1024
        box=(x-RADIUS,y,x+RADIUS,y+1024)
        sheet.paste(canvas.crop(box),((k-1)*(WIDTH+12),40))
        label=f'V r{r+1:02d} x={x} y={y}:{y+1024}'
        draw.text(((k-1)*(WIDTH+12)+4,10),label,fill='black',font=font)
        sections.append({'id':f'V_r{r+1:02d}_x{x}','coreCropBox':box,'seamCore':{'x':x,'yRange':[y,y+1024]},'sheetXY':[(k-1)*(WIDTH+12),40]})
    name=f'vertical_row{r+1:02d}_1to1.png';sheet.save(OUT/name)
    outputs.append({'file':name,'sha256':digest(OUT/name),'sections':sections})
for c in range(4):
    sheet=Image.new('RGB',(1024,(WIDTH+40)*3+24),'#ededed')
    draw=ImageDraw.Draw(sheet)
    sections=[]
    for k in range(1,4):
        x=c*1024;y=k*1024
        box=(x,y-RADIUS,x+1024,y+RADIUS)
        start=(k-1)*(WIDTH+52)
        sheet.paste(canvas.crop(box),(0,start+40))
        draw.text((4,start+10),f'H c{c+1:02d} y={y} x={x}:{x+1024}',fill='black',font=font)
        sections.append({'id':f'H_c{c+1:02d}_y{y}','coreCropBox':box,'seamCore':{'y':y,'xRange':[x,x+1024]},'sheetXY':[0,start+40]})
    name=f'horizontal_col{c+1:02d}_1to1.png';sheet.save(OUT/name)
    outputs.append({'file':name,'sha256':digest(OUT/name),'sections':sections})
sheet=Image.new('RGB',(WIDTH*3+24,(WIDTH+40)*3+24),'#ededed');draw=ImageDraw.Draw(sheet);sections=[]
for r in range(1,4):
    for c in range(1,4):
        x=c*1024;y=r*1024;box=(x-RADIUS,y-RADIUS,x+RADIUS,y+RADIUS)
        dx=(c-1)*(WIDTH+12);dy=(r-1)*(WIDTH+52)
        sheet.paste(canvas.crop(box),(dx,dy+40))
        draw.text((dx+4,dy+10),f'J x={x}, y={y}',fill='black',font=font)
        sections.append({'id':f'J_x{x}_y{y}','coreCropBox':box,'junctionCoreXY':[x,y],'sheetXY':[dx,dy+40]})
name='junctions_1to1.png';sheet.save(OUT/name)
outputs.append({'file':name,'sha256':digest(OUT/name),'sections':sections})
for source in sources:
    if digest(Path(source['file']))!=source['sha256']:
        raise RuntimeError(f"Source changed before snapshot complete: {source['file']}")
write_json(OUT/'contact-manifest.json',{
    'createdAtUtc':created,'operation':'memory core crop/paste then seam/contact crop; original 1:1 pixels; no resizing, colour change, interpolation or registration',
    'tile':'r08_c09','localCoreSize':[4096,4096],'globalOriginXY':[32768,28672],
    'sourceNativeCoreBox':[115,115,1139,1139],'seamHalfWidth':160,
    'derivedFrom':sources,'outputs':outputs,'accepted':False,'outerNeighboursReviewed':False,
    'visualInspectionStatus':'pending; see review.json for individually viewed items'})
print(json.dumps({'sources':len(sources),'contacts':len(outputs),'createdAtUtc':created}))
