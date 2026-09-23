from pathlib import Path
import hashlib,json
from datetime import datetime, timezone
from PIL import Image,ImageDraw

OUT=Path(__file__).resolve().parent
SESSION=OUT.parents[1]/'tools/sessions/tianyong_festival/r09_c09'
SOURCE=SESSION/'output_resume_20260921/tianyong_r09_c09_q64_4k_candidate.png'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
im=Image.open(SOURCE);im.load()
assert im.size==(4096,4096)
entries=[]
def emit(name,image,boxes,role):
    p=OUT/(name+'.png');image.save(p)
    entries.append({'file':str(p),'sha256':sha(p),'pixels':list(image.size),'sourceBoxesLTRB':boxes,
                    'role':role,'resized':False,'artPixelsPerSourcePixel':1,'viewedAtOriginalPixels':False})
for axis in ['v','h']:
    for k in [1024,2048,3072]:
        boxes=[]
        if axis=='v':
            board=Image.new('RGB',(4*288+3*8,1048),(38,38,38)); draw=ImageDraw.Draw(board)
            for seg in range(4):
                box=[k-144,seg*1024,k+144,(seg+1)*1024];boxes.append(box)
                board.paste(im.crop(box),(seg*296,24))
                draw.text((seg*296+4,4),f'x={k} y={seg*1024}..{(seg+1)*1024-1}',fill='white')
        else:
            board=Image.new('RGB',(1024,4*312+3*8),(38,38,38)); draw=ImageDraw.Draw(board)
            for seg in range(4):
                box=[seg*1024,k-144,(seg+1)*1024,k+144];boxes.append(box)
                board.paste(im.crop(box),(0,seg*320+24))
                draw.text((4,seg*320+4),f'y={k} x={seg*1024}..{(seg+1)*1024-1}',fill='white')
        emit(f'{axis}{k}_full_4096_native',board,boxes,'all 4096 pixels of internal seam split into four ordered exact-scale panels')
for y in [1024,2048,3072]:
    for x in [1024,2048,3072]:
        box=[x-256,y-256,x+256,y+256]
        emit(f'junction_x{x}_y{y}',im.crop(box),[box],'512x512 native four-patch junction crop')
manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(SOURCE),
    'sourceSha256':sha(SOURCE),'sourcePixels':list(im.size),'imageFullyDecoded':True,
    'reviewScope':'r09_c09 internal native patch seams only; excludes neighboring delivery tiles and layout/navigation acceptance',
    'imageProcessing':'crop and non-overlapping board paste only; no resize, registration, color changes, filtering or pixel blend',
    'fullSeams':6,'segmentsPerSeam':4,'junctions':9,'entries':entries}
(OUT/'crop-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sourceSha256':manifest['sourceSha256'],'entries':len(entries)},indent=2))
