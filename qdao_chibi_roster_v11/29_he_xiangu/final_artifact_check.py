from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
import numpy as np
c=Path(__file__).resolve().parent
m=json.loads((c/'manifest.json').read_text(encoding='utf8'))
for f in m['files']:
 p=c/f['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],str(p)
for d,s in m['directional_original_sources'].items():
 for f in s['selected_frame_sources']:
  p=c/f['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],str(p)
report={'all_manifest_hashes_match':True,'all_selected_source_hashes_match':True,'gifs':{}}
for group,dirs in [('cardinal',['S','W','E','N']),('diagonal',['SW','NW','NE','SE'])]:
 canvas=Image.new('RGB',(1120,4*280),(233,231,224));draw=ImageDraw.Draw(canvas)
 sheet=Image.open(c/('walk-'+group+'.png')).convert('RGBA')
 for row,d in enumerate(dirs):
  g=Image.open(c/'walk'/d/'walk.gif');assert g.n_frames==4 and g.info['loop']==0
  strip=Image.open(c/'walk'/d/'strip.png').convert('RGBA');metric=[]
  for i in range(4):
   p=Image.open(c/'walk'/d/f'{i+1:02d}.png').convert('RGBA')
   assert np.array_equal(np.asarray(p),np.asarray(strip.crop((i*512,0,(i+1)*512,512))))
   assert np.array_equal(np.asarray(p),np.asarray(sheet.crop((i*512,row*512,(i+1)*512,(row+1)*512))))
   g.seek(i);assert g.info['duration']==120
   f=g.convert('RGBA');a=np.asarray(f);b=np.asarray(p);mask=(a[:,:,3]>128)&(b[:,:,3]>240)
   assert a[:,:,3].min()==0 and a[:,:,3].max()==255
   mae=float(np.abs(a[:,:,:3].astype(float)[mask]-b[:,:,:3].astype(float)[mask]).mean());assert mae<8
   metric.append(round(mae,4))
   bg=Image.new('RGBA',(512,512),(233,231,224,255));bg.alpha_composite(f);bg=bg.resize((260,260),Image.Resampling.LANCZOS);canvas.paste(bg.convert('RGB'),(50+i*265,row*280));draw.text((55+i*265,row*280+260),f'{d} GIF {i+1}',fill=(20,60,50))
  report['gifs'][d]={'frames':4,'duration_ms':120,'loop':0,'transparency':True,'rgb_quantization_mae':metric}
 canvas.save(c/'processing'/('gif-decoded-'+group+'.jpg'),quality=94)
report['strips_and_sheets_match_individual_pngs']=True
(c/'processing/final-integrity.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))
