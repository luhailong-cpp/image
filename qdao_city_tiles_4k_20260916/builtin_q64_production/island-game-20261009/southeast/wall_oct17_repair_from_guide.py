import os,sys
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
pid,v,oldv,desc=sys.argv[1:];src=ROOT/'native'/f'{pid}_{oldv}.png';im=Image.open(src).convert('RGB');oldguide=ROOT/'guides'/f'{pid}.selected-core-wall17-{oldv}.png';meta=read(Path(str(oldguide)+'.generation.json'))
for part in meta['derivedFrom'][1:]:
 f=Path(part['file']);assert sha(f)==part['sha256'];im.paste(Image.open(f).convert('RGB').crop(part['sourceCrop']),part['destination'])
g=ROOT/'guides'/f'{pid}.selected-repair-wall17-{v}.png';assert not g.exists();im.save(g);write(Path(str(g)+'.generation.json'),{'file':str(g),'sha256':sha(g),'derivedFrom':[{'file':str(src),'sha256':sha(src)}]+meta['derivedFrom'][1:],'usableAsFinalArt':False})
prompt=f'Use case: precise-object-edit. Return one exactly1254x1254 opaque image with identical framing. Image1 is the exact target. Its sharp outer115px strips are true selected adjacent art and must remain geometrically fixed. Make only this correction: {desc} Keep every other object, shape and texture at its position. Same hand-painted Q Daoist daylight art, no zoom, text, UI, people, new props or framing.'
pf=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';pf.write_text(prompt,encoding='utf-8');refs=[{'file':str(g),'sha256':sha(g),'role':'exact repair target with selected neighbor core anchors'}];write(ROOT/'prompts'/f'{pid}_{v}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}});write(ROOT/'prompts'/f'{pid}_{v}.args.json',{'prompt':prompt,'referenced_image_paths':[str(g)],'transparent_background':False});print(g)
