"""Read-only pixel diagnostics and background composites for staged 04 exports."""
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CHAR='04_mountain_guardian_boy'
OUT=HERE/'staging/candidate'/CHAR
REPORT=HERE/'review'
REPORT.mkdir(exist_ok=True)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def metrics(path):
 im=Image.open(path).convert('RGBA');a=np.array(im);y,x=np.where(a[:,:,3]>8)
 top=int(y.min());height=int(y.max()-top+1)
 body=float(np.sqrt(np.count_nonzero(a[:,256:768,3])/(im.width*im.height))) if im.size==(1024,1024) else None
 axis=float(np.median(x[y<top+max(1,int((height-1)*.42))]))
 return {'path':str(path),'sha256':sha(path),'size':list(im.size),'bbox_alpha_gt8':[int(x.min()),top,int(x.max()+1),int(y.max()+1)],
         'height':height,'axis':[axis,int(y.max())],'opaque_pixels':int((a[:,:,3]==255).sum()),
         'transparent_pixels':int((a[:,:,3]==0).sum()),'soft_alpha_pixels':int(((a[:,:,3]>0)&(a[:,:,3]<255)).sum()),
         'body_scale':body}
def pair(frame):
 old=ROOT/'candidate'/CHAR/f'walk/NW/{frame:02d}.png';new=OUT/f'walk/NW/{frame:02d}.png'
 m1,m2=metrics(old),metrics(new)
 result={'old':m1,'new':m2,'height_ratio_new_old':m2['height']/m1['height'],'body_scale_ratio_new_old':m2['body_scale']/m1['body_scale'],'previews':[]}
 for mode,color,text in [('dark',(30,38,46),'white'),('light',(240,238,228),'black')]:
  canvas=Image.new('RGB',(2048,1088),color);draw=ImageDraw.Draw(canvas)
  for i,(p,label) in enumerate([(old,'OLD preserved candidate'),(new,'NEW staged edit')]):
   im=Image.open(p).convert('RGBA');canvas.paste(im,(i*1024,48),im);draw.text((i*1024+20,16),f'NW{frame:02d} {label} | fixed .84 | root 512,942',fill=text)
  path=REPORT/f'NW{frame:02d}-old-new-{mode}.png';canvas.save(path);result['previews'].append(str(path))
 return result
def main():
 results={'comparisons':[pair(i) for i in (4,6,7)],'staging_only':True,'visual_review':'pending'}
 for mode,color,text in [('dark',(30,38,46),'white'),('light',(240,238,228),'black')]:
  canvas=Image.new('RGB',(3072,1088),color);draw=ImageDraw.Draw(canvas)
  for x,f in enumerate((8,10,11)):
   im=Image.open(OUT/f'walk/NW/{f:02d}.png').convert('RGBA');canvas.paste(im,(x*1024,48),im);draw.text((x*1024+20,16),f'NW{f:02d} archived original | newly processed | visual pending',fill=text)
  canvas.save(REPORT/f'NW08-10-11-{mode}.png')
 rawdir=ROOT/'recovery-20260921/04-generation'
 results['edited_raw_alpha']=[metrics(rawdir/f'NW{i:02d}-edge-v2/raw.png') for i in (4,6,7)]
 s=importlib.util.spec_from_file_location('fresh_verify',ROOT/'tools/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
 v.ROOT=HERE/'staging'
 def mod(name):
  spec=importlib.util.spec_from_file_location('fresh_'+name,ROOT/'tools/vendor'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 v.mod=mod
 results['fresh_reconstruction']=[v.verify(CHAR,'NW',False,i) for i in (4,6,7,8,10,11)]
 write(REPORT/'staging-analysis.json',results)
 print(json.dumps({k:val for k,val in results.items() if k!='fresh_reconstruction'},indent=2))
if __name__=='__main__':main()
