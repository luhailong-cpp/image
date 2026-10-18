import sys,json,hashlib,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from PIL import Image
Q=Path(__file__).resolve().parent;Z=Q.parent
def ref(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def png(p,a):
 assert not p.exists();Image.fromarray(a).save(p);return ref(p)
c=mod('corner_mask',Q/'repair-compose.py');h=mod('corner_seam',Z/'tools/seam_helpers.py')
old=rgb(Q/'west-corner-r08r09c04c05-v1-source-1254.png');new=rgb(Z/'native/r08_c05_repair_t_westcorner_v1.png')
b=[460,550,790,790];margin=40
mask,paths=c.closed_mask(old,new,b,margin,[0,0,1254,1254],h._minimum_vertical_seam)
out=old.copy();out[mask.astype(bool)]=new[mask.astype(bool)]
p=Q/'west-corner-r08r09c04c05-v2-mask.npy';assert not p.exists();np.save(p,mask,allow_pickle=False)
d={'mask':ref(p),'repair':ref(Z/'native/r08_c05_repair_t_westcorner_v1.png'),'source':ref(Q/'west-corner-r08r09c04c05-v1-source-1254.png'),'globalContextBox':[15757,32141,17011,33395],'repairBounds':b,'margin':margin,'paths':paths,'after':png(Q/'west-corner-r08r09c04c05-v2-after-1254.png',out),'nativePixelsResampled':False,'status':'pending_visual_qa'}
p=Q/'west-corner-r08r09c04c05-v2-mask-trace.json';assert not p.exists();p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'after':d['after'],'mask':d['mask']}))

