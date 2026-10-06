"""Prepare and record two specifically observed native lighting seam repairs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys
from PIL import Image
ROOT=Path(__file__).resolve().parent
R=ROOT/'r08_c11/repairs/internal-lighting'
SRC=ROOT/'r08_c11/tone-assembly/output/r08_c11.png'
DAY=ROOT.parent/'donghai_day/r08_c11/output/r08_c11.png'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
JOBS={
 'wood':{'xy':[800,400],'repairBoundsTileXYXY':[1080,870,1590,1290], 'description':'Remove ONLY the unnatural jagged near-horizontal dark-to-orange paste boundary on the wooden wall, around image x300..800,y500..800. Make the existing warm light and shadow a coherent painted transition. Preserve vertical board lines, roof shadow shape from image2, roof edges, foliage contours and all object geometry. No new dark stripe.'},
 'wall':{'xy':[450,1450],'repairBoundsTileXYXY':[850,1750,1150,2490], 'description':'Remove ONLY the thin jagged vertical paste/color edge on the pale cream wall around image x460..580,y350..950. Continue the same cream/lavender surface and existing leaf dapple colors across it. Do not create a wall crack or straight line. Preserve the existing leaf-shadow silhouette and warm dapple shapes as much as possible, exact roof/beam outlines, leaves, all geometry.'}
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def item(p,role):return {'file':str(p),'sha256':sha(p),'role':role}
def prepare(name):
 job=JOBS[name];x,y=job['xy'];box=[x,y,x+1254,y+1254]
 refs=[]
 for src,suffix,role in [(SRC,'target','exact current festival target at native resolution'),(DAY,'geometry','same-coordinate DAY geometry and true cast-shadow positions; not appearance')]:
  out=R/'guides'/f'{name}-{suffix}.png';out.parent.mkdir(parents=True,exist_ok=True)
  Image.open(src).crop(box).save(out)
  write(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'operation':'exact native unscaled crop','sourceCropXYXY':box,'derivedFrom':[item(src,role)],'finalArt':False})
  refs.append(item(out,role))
 refs.append(item(STYLE,'PRIMARY user-confirmed rounded clean luminous Daoist Q art style; no UI content'))
 prompt='Use case: precise-object-edit. Repair image1, a native1254-square fishing-village Lantern Festival map crop. '+job['description']+' Image2 is the exact same native crop in DAY appearance and is a structural reference ONLY: retain those positions, never replace the festival palette with day colors. Image3 is the confirmed PRIMARY rendering style only: rounded plump clean hand-painted Daoist Q style. Keep image1 color, texture, illumination and every shape outside the stated defect unchanged. No framing or camera changes, zoom, rescaling, architecture, props, lanterns, text, UI, border or watermark. Do not change clipped edge objects or shift any lines. No additional glow, orange wash, blur, noise or sharpening. Output one opaque1254 by1254 image in the exact same field of view. Repaint the defective local transition only.'
 pp=R/'prompts'/f'{name}.txt';pp.parent.mkdir(parents=True,exist_ok=True);pp.write_text(prompt,encoding='utf-8')
 args={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}
 write(R/'prompts'/f'{name}.request.json',args);write(R/'prompts'/f'{name}.references.json',refs)
 write(R/'prompts'/f'{name}.job.json',{**job,'tileCropXYXY':box,'globalRectXYWH':[40960+x,28672+y,1254,1254]})
 print(json.dumps(args,ensure_ascii=False))
def record(name,raw):
 raw=Path(raw);out=R/'native'/f'{name}.png';assert not out.exists();out.parent.mkdir(parents=True,exist_ok=True)
 im=Image.open(raw);im.load();assert im.size==(1254,1254)
 shutil.copyfile(raw,out);req=read(R/'prompts'/f'{name}.request.json')
 write(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':1254,'height':1254,'format':'PNG','route':'builtin','tool':'image_gen.imagegen','configSnapshot':read(ROOT/'batch-model-check.json')['configSnapshot'],
 'submittedParameters':{'model':None,'quality':None,**req},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed; model/quality selectors and actual metadata unavailable.',
 'evidence':{'toolResultSourcePath':str(raw),'sha256':sha(raw)},'prompt':str(R/'prompts'/f'{name}.txt'),'references':read(R/'prompts'/f'{name}.references.json'),'repairJob':read(R/'prompts'/f'{name}.job.json'),'resizedAfterGeneration':False,'visualQA':'pending'})
 print(json.dumps({'file':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(sys.argv[2])
 elif sys.argv[1]=='record':record(sys.argv[2],sys.argv[3])
