from pathlib import Path
from PIL import Image
import numpy as np,json,sys
r=Path(r'E:\work\image\qdao_chibi_roster_v12');sys.path.insert(0,str(r));from edge_despill import shifted
c=r/'candidate-natural-body/29_he_xiangu';before=c/'review/before-idle-proportion-correction';records=[]
for d in ['N','NE','E','SE','S','SW','W','NW']:
 for i in range(1,9):
  rel=Path('walk')/d/(f'{i:02d}.png');im=Image.open(before/rel).convert('RGBA');out=Image.open(c/rel).convert('RGBA');a=np.array(im.crop(im.getchannel('A').getbbox()));b=np.array(out.crop(out.getchannel('A').getbbox()))
  assert a.shape==b.shape and np.array_equal(a[:,:,3],b[:,:,3]) and np.array_equal(a[:,:,1],b[:,:,1]),str(rel)
  changed=np.any(a[:,:,:3]!=b[:,:,:3],axis=2);fg=a[:,:,3]>8;band=np.zeros(fg.shape,dtype=bool)
  for y in range(-4,5):
   for x in range(-4,5):
    if x*x+y*y<=16:band|=shifted(~fg,y,x,True)
  assert not np.any(changed&~(fg&band)),str(rel)
  rr=a[:,:,0].astype(int);gg=a[:,:,1].astype(int);bb=a[:,:,2].astype(int);red=(rr-gg>=30)&(rr*10>bb*13);assert not np.any(changed&red),str(rel)
  records.append({'path':str(rel),'intrinsic_shape_alpha_green_equal':True,'only_four_pixel_edge_color_cleanup':True,'protected_red_unchanged':True,'canvas_translation':'may differ because6 authored idle references were corrected; independently verified by verify_delivery'})
assert len(records)==64
(c/'review/idle-revision-walk-retention.json').write_text(json.dumps({'status':'passed','walk_frames':64,'new_idle_directions':['N','S','SE','SW','E','W'],'preserved_idle_directions':['NE','NW'],'records':records},indent=2)+'\n')
print('64 original walking silhouettes and green channel retained exactly after integer realignment and4px edge cleanup')

