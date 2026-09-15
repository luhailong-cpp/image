from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,shutil,numpy as np
B=Path(__file__).resolve().parent.parent;G=Path(r'C:\Users\luyua\.codex\generated_images\01a09f27-0628-78e0-84b5-2472601dc072');names={'W':'exec-12e18120-41f9-4190-8220-dc4ca1557b43.png','SW':'exec-f7f09127-a58b-41c9-95e3-93d68a98e418.png'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
def metric(im):
 a=np.array(im.convert('RGB')).astype(int);m=~((a[:,:,0]>150)&(a[:,:,2]>140)&(a[:,:,1]<120)&(a[:,:,0]+a[:,:,2]-2*a[:,:,1]>180));y,x=np.nonzero(m);hh=x[y<y.min()+155];return {'alpha_like_top':int(y.min()),'upper155_width':int(hh.max()-hh.min()+1),'bbox':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]}
for d,g in names.items():
 f=B/d;raw=f/'low-gait-raw.png'
 if not raw.exists():shutil.copy2(G/g,raw)
 assert sha(raw)==sha(G/g);im=Image.open(raw).convert('RGB');assert im.size==(1254,1254);selection={};records=[];comp=Image.new('RGB',(886,1772+28),'#e8e5da');ImageDraw.Draw(comp).text((5,8),d+' original / low gait (02,06,04,08)',fill='black')
 for idx,phase in enumerate([2,6,4,8]):
  box=[idx%2*627,idx//2*627,(idx%2+1)*627,(idx//2+1)*627];native=im.crop(box);native.save(f/f'phase{phase:02d}-native.png');cell=native.resize((443,443),Image.Resampling.LANCZOS);cell.save(f/f'phase{phase:02d}-wholecell443.png');selection[f'{phase:02d}']={'raw':raw.name,'cell':f'phase{phase:02d}-wholecell443.png','prompt':'low-gait-prompt.txt','raw_box':box};old=Image.open(f/'original'/f'{phase:02d}.png');records.append({'original_phase':phase,'canonical_phase':phase,'raw_box':box,'native_rgba_sha256':rgba(native),'final_rgba_sha256':rgba(cell),'old_metric':metric(old),'new_metric':metric(cell)});comp.paste(old,(0,idx*443+28));comp.paste(cell,(443,idx*443+28))
 (f/'selection-pending.json').write_text(json.dumps(selection,indent=2)+'\n',encoding='utf-8');comp.save(f/'before-after.png');comp.resize((664,1350),Image.Resampling.LANCZOS).save(f/'before-after.jpg',quality=88)
 prov={'tool':'builtin image_gen','calls':1,'original_generated_path':str(G/g),'original_generated_sha256':sha(G/g),'saved_raw':str(raw),'saved_raw_sha256':sha(raw),'prompt':str(f/'low-gait-prompt.txt'),'prompt_sha256':sha(f/'low-gait-prompt.txt'),'reference':str(f/'reference-02-06-04-08.png'),'reference_sha256':sha(f/'reference-02-06-04-08.png'),'reference_mechanism':'num_last_images_to_include=1 after rendered whole reference preview','original_phase_to_canonical':{str(n):n for n in range(1,9)},'rotation':False,'protected_original_phases':[1,3,5,7],'no_part_transform_or_bbox_fit':True,'postprocess':'exact627-square crop and uniform whole-cell LANCZOS443','visual_review':'Four authored low poses reviewed before selection; final assembly pending root review','frames':records}
 (f/'generation-provenance.json').write_text(json.dumps(prov,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'direction':d,'raw_sha256':sha(raw),'selected':list(selection),'metrics':records},ensure_ascii=False))
