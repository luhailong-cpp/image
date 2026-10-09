from pathlib import Path
import json,sys,numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O));import quilt as q
src=O/'r11_c14-internal-candidate-v2.png';gen=O/'sail-middle-right-generated.png';can=Image.open(src).convert('RGB');x,y=2445,1421;a=np.asarray(can.crop((x,y,x+1254,y+1254)),np.float32);b=np.asarray(Image.open(gen),np.float32)
Y,X=np.indices((1254,1254));al=np.minimum.reduce([np.clip((X-415)/32,0,1),np.clip((890-X)/32,0,1),np.clip((Y-1100)/32,0,1),np.clip((1253-Y)/24,0,1)])
alpha=np.rint(al*255).astype('uint8');al=alpha[:,:,None]/255;grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);rel=(alpha>0)&(alpha<255)&(grad<35)&(np.max(abs(a-b),axis=2)<75);w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*rel[:,:,None]));f=np.clip(num/np.maximum(w,1e-6),-28,28)*np.clip(w*30,0,1);rep=np.clip(np.rint(b+f),0,255).astype('uint8');out=np.rint(rep*al+a*(1-al)).astype('uint8');assert np.array_equal(out[alpha==0],a.astype('uint8')[alpha==0])
refs=[src,gen];outs=[]
for n,arr in [('middle-right-return-v3-alpha',alpha),('middle-right-return-v3-replacement',rep),('middle-right-return-v3-composite',out)]:
 p=O/(n+'.png');Image.fromarray(arr).save(p);q.record(p,refs,{'method':'native AI lower batten return extended into previously masked source, exact alpha once; bounded RGB perimeter field cap28','origin':[x,y],'support':[416,1101,890,1253],'noImageBlur':True,'noResampling':True});outs.append(p)
np.savez_compressed(O/'middle-right-return-v3-field.npz',field=f);can.paste(Image.fromarray(out),(x,y));dst=O/'r11_c14-internal-candidate-v3.png';can.save(dst);q.record(dst,refs+outs,{'method':'extend native AI lower batten repair at y2626 missed by v2 crop boundary','noImageBlur':True,'noResampling':True});ar=np.asarray(can);raw=np.asarray(Image.open(O.parent.parent/'tiles/r11_c14-candidate.png'));assert np.array_equal(ar[:627,:627],raw[:627,:627]);assert np.array_equal(ar[:627,-627:],raw[:627,-627:]);q.qa(ar,'v3',dst)
p=O/'middle-right-return-v3-qa.png';can.crop((2800,2500,3350,2700)).save(p);q.record(p,[dst],{'method':'native QA crop','bbox':[2800,2500,3350,2700]});print(q.sha(dst))

