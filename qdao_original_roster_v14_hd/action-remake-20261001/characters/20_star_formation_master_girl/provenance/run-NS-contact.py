from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,sys
B=Path(__file__).resolve().parents[1];d=sys.argv[1]
canvas=Image.new('RGB',(1200,1320),(232,229,217));draw=ImageDraw.Draw(canvas);refs=[]
for i in range(1,17):
 candidates=list((B/'generation/run'/d).glob(f'{i:02d}-v*.png'))
 if not candidates:continue
 p=max(candidates,key=lambda p:int(p.stem.split('-v')[1]))
 im=Image.open(p).convert('RGBA').resize((300,300),Image.Resampling.LANCZOS)
 x=((i-1)%4)*300;y=((i-1)//4)*330
 canvas.paste(im,(x,y),im);draw.text((x+8,y+305),d+str(i).zfill(2)+' '+p.stem,fill=(35,53,50))
 refs.append(dict(path=p.relative_to(B).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),generationRecord=p.relative_to(B).as_posix()+'.generation.json'))
 out=B/'provenance'/f'run-NS-{d}-contact.png'
canvas.save(out)
Path(str(out)+'.generation.json').write_text(json.dumps(dict(file=out.relative_to(B).as_posix(),sha256=hashlib.sha256(out.read_bytes()).hexdigest(),derivedFrom=refs,operation='Uniform full-canvas thumbnail contact sheet for QA only; no pose edit or new model call'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out)

