from pathlib import Path
import sys,json,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import compose_patch as c
h=c.h;R=T/'repairs';O=R/'internal-ai/output-v1';O.mkdir(parents=True,exist_ok=True)
src=R/'internal-quilt/r11_c11-internal-v2.png';canvas=c.q.arr(src);spec=h.p.read(R/'internal-ai/targets.json')
B={'rail':[[[350,385],[580,620],[540,580],[780,820]]],'floor-left':[[[585,625],[850,890],[460,500],[675,710]]],'crate-post':[[[500,540],[790,830],[155,190],[440,480]]],'cloth-post':[[[500,535],[630,670],[355,380],[445,475]],[[350,385],[495,525],[520,550],[650,690]]],'floor-right':[[[130,165],[300,340],[435,470],[600,640]],[[655,690],[845,880],[510,545],[715,750]]]}
B['floor-left']=[[[350,500],[1040,1100],[100,230],[1080,1190]]]
B['crate-post']=[[[280,365],[1080,1140],[135,215],[460,515]]]
B['floor-right']=[[[20,100],1254,[0,90],[1180,1254]]]
entries=[]
for e in spec:
 n=e['name'];x,y=e['origin'];old=canvas[y:y+1254,x:x+1254].copy();source=R/'internal-ai/native'/(n+'.png');new=c.q.arr(source);out=old.copy();mask=np.zeros((1254,1254),bool);rep=new.copy();field=np.zeros_like(new);cuts={}
 for k,b in enumerate(B[n]):
  _,rp,m,f,cs=c.patch(old,new,b);out[m]=rp[m];rep[m]=rp[m];field[m]=f[m];mask|=m;cuts.update({str(k)+'-'+key:v for key,v in cs.items()})
 rp=O/(n+'-replacement.png');mp=O/(n+'-mask.png');fp=O/(n+'-fields.npz');cp=O/(n+'-review.png')
 np.savez_compressed(fp,field=field,**cuts);Image.fromarray(mask.astype('uint8')*255).save(mp)
 c.save(rep,rp,[source,src],{'method':'native AI pixels with bounded12 RGB return field; binary source ownership','origin':e['origin'],'field':str(fp),'fieldSHA256':h.p.sha(fp),'imageBlur':False,'resampling':False,'warp':False,'feather':False})
 h.p.derived(mp,[source,src],{'method':'binary minimum error ownership mask','bands':B[n],'origin':e['origin'],'fields':str(fp),'fieldSHA256':h.p.sha(fp)})
 c.save(out,cp,[src,rp,mp],{'method':'native1254 exact binary repair return context','origin':e['origin']})
 assert np.array_equal(out[~mask],old[~mask])
 canvas[y:y+1254,x:x+1254]=out
 entries.append(dict(e,replacement=str(rp),mask=str(mp),fields=str(fp),review=str(cp),maskSHA256=h.p.sha(mp),replacementSHA256=h.p.sha(rp),changedPixels=int(mask.sum())))
dst=R/'r11_c11-internal-v3.png';c.save(canvas,dst,[src]+[e[k] for e in entries for k in ['replacement','mask']],{'method':'five native AI local repairs composed by exact masks','formalAccepted':False})
h.p.write(O/'manifest.json',{'base':str(src),'baseSHA256':h.p.sha(src),'candidate':str(dst),'sha256':h.p.sha(dst),'repairs':entries})
im=Image.open(dst);c.q.qa(im,'internal-v3',dst)
p=R/'preview-internal-v3.png';im.resize((1254,1254),Image.Resampling.LANCZOS).save(p);h.p.derived(p,[dst],{'method':'review-only downscale'})
print(h.p.sha(dst))

