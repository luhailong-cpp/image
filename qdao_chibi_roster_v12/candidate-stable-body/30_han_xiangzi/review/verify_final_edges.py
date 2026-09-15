from pathlib import Path
from PIL import Image
import numpy as np,json,sys,hashlib
root=Path(r'E:\work\image\qdao_chibi_roster_v12\candidate-stable-body\30_han_xiangzi');sys.path.insert(0,str(root.parents[1]))
from edge_despill import shifted
records=[]
for before in (root/'review/edge-before').rglob('*.png'):
    rel=before.relative_to(root/'review/edge-before');after=root/rel
    a=np.array(Image.open(before).convert('RGBA'));b=np.array(Image.open(after).convert('RGBA'))
    assert a.shape==b.shape and np.array_equal(a[:,:,3],b[:,:,3]) and np.array_equal(a[:,:,1],b[:,:,1]),str(rel)
    changed=np.any(a[:,:,:3]!=b[:,:,:3],axis=2);fg=a[:,:,3]>8;band=np.zeros(fg.shape,dtype=bool)
    for y in range(-4,5):
      for x in range(-4,5):
        if x*x+y*y<=16:band|=shifted(~fg,y,x,True)
    assert not np.any(changed&~(fg&band)),str(rel)
    rr=a[:,:,0].astype(int);gg=a[:,:,1].astype(int);bb=a[:,:,2].astype(int);red=(rr-gg>=30)&(rr*10>bb*13)
    assert not np.any(changed&red),str(rel)
    records.append({'path':str(rel),'alpha_equal':True,'green_equal':True,'position_and_bounds_equal':True,'outside_four_pixel_band_changes':0,'protected_red_changes':0,'changed_pixels':int(changed.sum())})
assert len(records)==72,len(records)
(root/'review/edge-final-validation.json').write_text(json.dumps({'status':'passed','frames':72,'records':records},indent=2),encoding='utf-8')
print('72/72 alpha, green, placement and protected red unchanged; all added color correction within4px border')
