from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import helper as h
R=T/'repairs'
for axis,ids in [('north',[2,3,4]),('west',[1,2,3,4])]:
 for i in ids:
  d=R/(axis+'-joint');src=d/f's{i}-target.png';dest=d/f's{i}-gap-target.png'
  a=np.array(Image.open(src).convert('RGB'));mask=np.zeros((1254,1254),bool)
  if axis=='north':
   mask[557:697]=True
   if i==4:mask[:697,190:270]=True
  else:mask[:,557:697]=True
  a[mask]=[255,0,255];Image.fromarray(a).save(dest)
  h.p.derived(dest,[src],{'method':'explicit magenta missing repair guide; no final art pixels','gapBounds':'horizontal557:697' if axis=='north' else 'vertical557:697','extraLGap':axis=='north' and i==4})

