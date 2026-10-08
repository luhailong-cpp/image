"""Prepare and record two specifically observed native lighting seam repairs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
R=ROOT/'r08_c13/repairs/internal-lighting'
SRC=ROOT/'r08_c13/tone-assembly/output/r08_c13.png'
DAY=ROOT.parent/'donghai_day/r08_c13/output/r08_c13.png'
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
JOBS={
 'shadow':{'xy':[500,550],'repairBoundsTileXYXY':[1000,790,1290,1540], 'description':'Remove ONLY the unnatural perfectly vertical brightness cutoff at image x639 in the existing lavender crate shadow, roughly y300..930. This is a leftover pasted context edge, NOT a real cast-shadow boundary. Continue the shadow same color and painted texture smoothly across that vertical line. Keep the true diagonal outer shadow silhouette and every paving joint EXACTLY where image1 and image2 put them. Preserve board/crate outlines. Do not add, erase, move or soften true shadow edges or paving joints. Do not repaint other regions.'}
, 'wall':{'xy':[2300,500],'repairBoundsTileXYXY':[2660,995,3260,1310], 'description':'Remove ONLY the artificial straight horizontal color cutoff across the lavender front face of the stone retaining wall around image y639, approximately x400..920. Continue the existing lavender/peach stone paint naturally across that line. The horizontal cutoff is pasted lighting, NOT mortar, a crack or a physical block edge. Preserve every genuine dark oblique mortar line, bevel, wall silhouette, pillar, wooden crate and real cast-shadow contour EXACTLY as in image1 and image2. Preserve texture scale and the restrained warm festival palette. Do not create a new line or change other regions.'}
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
 write(R/'prompts'/f'{name}.job.json',{**job,'tileCropXYXY':box,'globalRectXYWH':[49152+x,28672+y,1254,1254]})
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
