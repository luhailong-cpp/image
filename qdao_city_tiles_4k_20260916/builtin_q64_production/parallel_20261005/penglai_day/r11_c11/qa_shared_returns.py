from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import compose_patch as c
h=c.h;O=T/'repairs/shared-output-v2';a={k:np.array(Image.open(O/(k+'-candidate.png')).convert('RGB')) for k in ['r10_c10','r10_c11','r11_c10','r11_c11']}
pos={'r10_c10':(-4096,-4096),'r10_c11':(0,-4096),'r11_c10':(-4096,0),'r11_c11':(0,0)}
def crop(box):
 x,y,w,hh=box;out=np.zeros((hh,w,3),np.uint8)
 for k,(xx,yy) in pos.items():
  l=max(x,xx);u=max(y,yy);r=min(x+w,xx+4096);b=min(y+hh,yy+4096)
  if r>l and b>u:out[u-y:b-y,l-x:r-x]=a[k][u-yy:b-yy,l-xx:r-xx]
 return out
for n,box in {'corner-top':[-627,-1254,1254,1254],'corner-bottom':[-627,0,1254,1254],'corner-left':[-1254,-627,1254,1254],'corner-right':[0,-627,1254,1254],'north4-top':[2842,-1254,1254,1254],'north3-bottom':[2048,0,1254,1254]}.items():
 c.save(crop(box),O/(n+'-return.png'),[O/(k+'-candidate.png') for k in a],{'method':'native1254 repair outsidecontext','relativeRectXYWH':box})
for axis in ['north','west']:
 for line in [-627,627]:
  board=np.zeros((1024,1024,3),np.uint8)
  for i in range(4):
   v=crop([i*1024,line-128,1024,256] if axis=='north' else [line-128,i*1024,256,1024])
   if axis=='west':v=np.array(Image.fromarray(v).transpose(Image.Transpose.ROTATE_90))
   board[i*256:(i+1)*256]=v
  c.save(board,O/f'{axis}-return{line}-board.png',[O/(k+'-candidate.png') for k in a],{'method':'native four1024x256 joined return slices; no resize','axis':axis,'line':line})

