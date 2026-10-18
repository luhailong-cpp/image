from pathlib import Path
from PIL import Image
import hashlib,json,datetime
R=Path(__file__).resolve().parent
base=R/'assembly-v2/context-native.png';im=Image.open(base)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for i,x in enumerate([0,1024,2048,3072],1):
    p=R/f'north-c{i}.input.png'
    with p.open('xb') as f:im.crop((x,0,x+1254,1254)).save(f,format='PNG')
    s=R/f'north-c{i}.qa-before.png'
    with s.open('xb') as f:im.crop((x,0,x+1254,345)).save(f,format='PNG')
    records.append({'id':f'north-c{i}','input':str(p),'sha256':sha(p),'contextBox':[x,0,x+1254,1254],'globalBox':[20365+x,44941,21619+x,46195],'protectedTopRows':115,'formalAccepted':False})
with (R/'north-plan-v1.json').open('x',encoding='utf-8') as f:json.dump({'base':str(base),'baseSha256':sha(base),'windows':records,'route':'builtin-image_gen','actualModel':'not returned','formalAccepted':False,'status':'prepared'},f,indent=2)
