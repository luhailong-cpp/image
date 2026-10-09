from pathlib import Path
import sys,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import internal_qa as q
h=q.h;O=T/'repairs/internal';O.mkdir(parents=True,exist_ok=True)
raw=T/'tiles/r10_c10-candidate.png';tile=Image.open(raw).convert('RGB');records=[]
for axis,i,j in [('x',3,1),('x',3,2),('y',1,4)]:
 aPath=T/'native'/f'p{j if axis=="x" else i}{i if axis=="x" else j}.png'
 bPath=T/'native'/f'p{j if axis=="x" else i+1}{i+1 if axis=="x" else j}.png'
 a=q.arr(aPath);b=q.arr(bPath)
 if axis=='x':a=a[:,1024:1254].transpose(1,0,2);b=b[:,:230].transpose(1,0,2)
 else:a=a[1024:1254];b=b[:230]
 ga=np.diff(a,axis=0,prepend=a[:1]);gb=np.diff(b,axis=0,prepend=b[:1])
 cost=np.mean(abs(a-b),2)+2*np.mean(abs(ga-gb),2)+.15*(np.mean(abs(ga),2)+np.mean(abs(gb),2))
 cost[:65]=1e6;cost[166:]=1e6
 for x in range(1254):
  reach=min(x,1253-x,50);cost[:115-reach,x]=1e6;cost[116+reach:,x]=1e6
 pp=q.path(cost.T);yy=np.arange(230)[:,None];xx=np.arange(1254)[None,:];choice=yy>=pp[None,:]
 w=np.minimum(np.clip(1-abs(yy-pp[None,:])/80,0,1),np.minimum(yy/65,(229-yy)/65));w=np.clip(w,0,1)**2*np.minimum(np.clip(xx/115,0,1),np.clip((1253-xx)/115,0,1))
 df=np.clip(q.smooth2(b-a,12),-16,16);af=.5*df*w[:,:,None];bf=-af
 rep=np.where(choice[:,:,None],b+bf,a+af);rep=np.clip(np.rint(rep),0,255).astype('uint8')
 origin=[i*1024-115,(j-1)*1024-115] if axis=='x' else [(j-1)*1024-115,i*1024-115]
 if axis=='x':rep=rep.transpose(1,0,2);choice=choice.T;af=af.transpose(1,0,2)
 name=f'{axis}{i*1024}-p{j}';rp=O/(name+'-replacement.png');mp=O/(name+'-source-choice.png');fp=O/(name+'-field.npz')
 Image.fromarray(rep).save(rp);Image.fromarray(choice.astype('uint8')*255).save(mp);np.savez_compressed(fp,fieldA=af,fieldB=-af,cut=pp)
 tile.paste(Image.fromarray(rep),origin)
 h.p.derived(rp,[aPath,bPath],{'method':'native overlap source ownership with symmetric bounded8 RGB field; zero resampling, warp, texture blur or feather','originTileXY':origin,'sourceChoice':str(mp),'fields':str(fp)})
 records.append({'sourceA':str(aPath),'sourceB':str(bPath),'replacement':str(rp),'sourceChoice':str(mp),'origin':origin,'fields':str(fp),'maxPerSideRGB':float(abs(af).max())})
out=O/'r10_c10-internal-v1.png';tile.save(out);h.p.derived(out,[raw]+[e['replacement'] for e in records],{'method':'native overlap patches clipped to tile','formalAccepted':False})
h.p.write(O/'record-v1.json',{'candidate':str(out),'sha256':h.p.sha(out),'source':str(raw),'repairs':records})
q.qa(tile,'internal-v1',out)
for y in [1024,2048,3072]:
 for x in [1024,2048,3072]:
  b=(x-627,y-627,x+627,y+627);f=T/'qa'/f'internal-v1-full-{x}-{y}.png';tile.crop(b).save(f);h.p.derived(f,[out],{'method':'native1254 context crop','boxLTRB':b})

