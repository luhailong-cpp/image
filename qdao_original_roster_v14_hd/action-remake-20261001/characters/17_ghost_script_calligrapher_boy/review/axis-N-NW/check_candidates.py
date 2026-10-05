from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
b=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metrics(im):
    a=im.getchannel('A'); w,h=im.size
    count=lambda box:sum(x>128 for x in a.crop(box).getdata())
    return {'size':list(im.size),'mode':im.mode,'alphaGt128Bbox':a.point(lambda x:255 if x>128 else 0).getbbox(),'alphaGt128EdgePixels':{'top':count((0,0,w,1)),'right':count((w-1,0,w,h)),'bottom':count((0,h-1,w,h)),'left':count((0,0,1,h))}}
items=[]
for key in ['run-N-16-v6','run-NW-15-v4']:
    p=b/'staging'/f'{key}.png'; im=Image.open(p); im.load(); normalized=im.resize((1024,1024),Image.Resampling.LANCZOS)
    recpath=p.with_suffix('.png.generation.json'); rec=json.loads(recpath.read_text(encoding='utf-8-sig'))
    rec['evidence']['toolResultFile']=f'provenance/{key}.tool-result.json'
    rec['editSource']={'file':'runtime/run/N/16.png' if key.startswith('run-N-') else 'runtime/run/NW/15.png'}
    rec['editSource']['sha256']=hashfile(b/rec['editSource']['file'])
    rec['validation']={'native':metrics(im),'fullCanvas1024Lanczos':metrics(normalized),'operation':'read-only in-memory full-canvas resize for verification; staging original untouched'}
    recpath.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    items.append({'key':key,'file':str(p),'sha256':hashfile(p),**rec['validation']})
groups=[('N',[('N14','runtime/run/N/14.png'),('N15','runtime/run/N/15.png'),('N16 old','runtime/run/N/16.png'),('N16 v6','staging/run-N-16-v6.png'),('N01','runtime/run/N/01.png')]),('NW',[('NW14','runtime/run/NW/14.png'),('NW15 old','runtime/run/NW/15.png'),('NW15 v4','staging/run-NW-15-v4.png'),('NW16','runtime/run/NW/16.png')])]
for direction,frames in groups:
    for mode in ['full240','legs']:
        w,h=(240,265) if mode=='full240' else (330,325)
        sheet=Image.new('RGB',(w*len(frames),h),(225,228,228));d=ImageDraw.Draw(sheet)
        for i,(label,file) in enumerate(frames):
            im=Image.open(b/file).convert('RGBA').resize((1024,1024),Image.Resampling.LANCZOS)
            if mode=='legs':im=im.crop((280,610,820,1024))
            im.thumbnail((w,h-25),Image.Resampling.LANCZOS)
            sheet.paste(im,(i*w+(w-im.width)//2,25),im);d.text((i*w+8,7),label,fill='#111111')
        sheet.save(out/f'{direction}-candidate-{mode}.png')
(out/'candidate-file-check.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(items,ensure_ascii=False,indent=2))
