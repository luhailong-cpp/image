import json,hashlib,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
stem,direction,frame=sys.argv[1:4]
assert direction in ['E','W','NE'] and frame.isdigit() and 0<=int(frame)<16 and stem.startswith('run_')
sp=(ROOT/'work'/(stem+'.png')).resolve();rp=sp.with_name(sp.name+'.generation.json')
im=Image.open(sp);im.load()
assert im.mode=='RGBA' and im.width>=1024 and im.height>=1024 and im.width==im.height and im.getchannel('A').getextrema()[0]==0
r=json.loads(rp.read_text(encoding='utf-8'))
dst=ROOT/'runtime/run'/direction/f'{int(frame):02d}.png';dr=dst.with_name(dst.name+'.generation.json')
if dr.exists():
 old=json.loads(dr.read_text(encoding='utf-8'));old['replacedBy']=stem
 (ROOT/'records'/f'run_{direction}_{int(frame):02d}_replaced_by_{stem}.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
im.resize((1024,1024),Image.Resampling.LANCZOS).save(dst)
d={'file':dst.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'width':1024,'height':1024,'format':'PNG','mode':'RGBA','derivedFrom':[{'file':r['file'],'sha256':r['sha256'],'generationRecord':rp.relative_to(ROOT).as_posix()}],'native':r['native'],'operation':'Full canvas uniform Lanczos downsample to 1024; no cropping, mirroring, warping or per-frame bbox alignment','actualModel':None,'actualQuality':None,'unverifiedReason':r['unverifiedReason'],'visualReview':r['visualReview'],'anchor':{'type':'provisional fixed virtual ground/root','x':512,'y':942,'normalizedUnityPivot':[.5,.08],'verified':False},'generatedAt':r['generatedAt']}
dr.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r['exported']=True;r['exportPath']=dst.relative_to(ROOT).as_posix();rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':d['file'],'sha256':d['sha256'],'source':r['file']},ensure_ascii=False))

