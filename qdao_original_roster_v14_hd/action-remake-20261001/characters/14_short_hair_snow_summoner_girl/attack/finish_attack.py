import sys,json,hashlib,shutil,importlib.util
from pathlib import Path
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parent.parent
sys.stdout.reconfigure(encoding='utf-8')
spec=importlib.util.spec_from_file_location('export_frame',BASE/'tools/export_frame.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
rows=[]
for recpath in sorted((BASE/'provenance').glob('attack-*.generation.json')):
    rec=json.loads(recpath.read_text(encoding='utf-8-sig'))
    f=Path(rec['file'])
    if 'staging' in f.parts:continue
    if f.parts[0]!='attack' or f.parts[1] not in ('E','W'):continue
    source=Path(rec['native']['path'])
    raw=BASE/'attack'/'native'/(rec['label']+'.png')
    raw.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,raw)
    req=json.loads((BASE/rec['request']).read_text(encoding='utf-8-sig'))
    rawrec={**req,'status':'generated','file':raw.relative_to(BASE).as_posix(),'sha256':sha(raw),'width':rec['native']['width'],'height':rec['native']['height'],'mode':rec['native']['mode'],'format':'PNG','hostSource':str(source),'receipt':f'provenance/{rec["label"]}.receipt.json','actualModel':None,'actualQuality':None}
    for ref in rawrec.get('submittedParameters',{}).get('referenced_image_paths',[]):
        if Path(ref).is_file():pass
    save(str(raw)+'.generation.json',rawrec)
    dest=BASE/f
    mod.run(raw,dest)
    derived=json.loads(Path(str(dest)+'.generation.json').read_text(encoding='utf-8'))
    rec['sha256']=derived['sha256'];rec['exportRecord']=str(dest.relative_to(BASE))+'.generation.json'
    rec['operation']=derived['operation'];rec['native']['localArchive']=raw.relative_to(BASE).as_posix()
    rec['native']['localGenerationRecord']=raw.relative_to(BASE).as_posix()+'.generation.json'
    save(recpath,rec)
    rows.append({'file':dest.relative_to(BASE).as_posix(),'sha256':sha(dest),'record':recpath.relative_to(BASE).as_posix(),'cleanup':derived['operation']['edgeColorCleanup']})
preview=BASE/'attack'/'preview';preview.mkdir(exist_ok=True)
for direction in ('E','W'):
    sheet=Image.new('RGB',(4*280,3*300),(34,40,48))
    for i in range(12):
        im=Image.open(BASE/'attack'/direction/f'{i+1:02d}.png').convert('RGBA').resize((280,280),Image.Resampling.LANCZOS)
        tile=Image.new('RGBA',(280,300),(34,40,48,255));tile.alpha_composite(im,(0,20))
        d=ImageDraw.Draw(tile);d.text((8,4),f'{direction} {i+1:02d}',fill='white')
        sheet.paste(tile.convert('RGB'),((i%4)*280,(i//4)*300))
    sheet.save(preview/f'contact-{direction}.png')
frames=[]
for i in range(12):
    canvas=Image.new('RGBA',(1024,536),(34,40,48,255));d=ImageDraw.Draw(canvas)
    for x,direction in [(0,'E'),(512,'W')]:
        im=Image.open(BASE/'attack'/direction/f'{i+1:02d}.png').convert('RGBA').resize((512,512),Image.Resampling.LANCZOS)
        canvas.alpha_composite(im,(x,24));d.text((x+10,8),f'{direction} {i+1:02d} / 12',fill='white')
    frames.append(canvas.convert('RGB'))
frames[0].save(preview/'attack-normal.webp',save_all=True,append_images=frames[1:],duration=30,loop=0,lossless=True)
frames[0].save(preview/'attack-slow.webp',save_all=True,append_images=frames[1:],duration=180,loop=0,lossless=True)
save(BASE/'attack'/'technical.json',{'count':len(rows),'expected':24,'uniquePixels':len(set(r['sha256'] for r in rows)),'root':[563,942],'canvas':[1024,1024],'durationMs':360,'frameMs':30,'hitFrames':[5,6],'frames':rows,'status':'technical-export-complete; artistic sequence review pending','client':'not-integrated'})
print(json.dumps({'exported':len(rows),'preview':str(preview)},ensure_ascii=False))

