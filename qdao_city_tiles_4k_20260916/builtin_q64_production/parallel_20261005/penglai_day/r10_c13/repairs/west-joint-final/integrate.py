from ai_helper import *
import numpy as np

def smooth(a,r=24):
 for ax in [0,1]:
  pad=[(0,0)]*3;pad[ax]=(r,r);p=np.pad(a,pad,mode='edge');pad[ax]=(1,0);cs=np.pad(np.cumsum(p,axis=ax,dtype=np.float64),pad);hi=[slice(None)]*3;lo=hi.copy();hi[ax]=slice(2*r+1,None);lo[ax]=slice(None,-2*r-1);a=((cs[tuple(hi)]-cs[tuple(lo)])/(2*r+1)).astype('float32')
 return a

def cut(cost,a,b):
 c=cost[:,a:b];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.3,dp,np.r_[dp[1:],1e12]+.3]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+np.min(z,axis=0)
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+a

def run():
 source=O/'joint-source.png';canvas=Image.open(source).convert('RGB');manifest=[];allmask=np.zeros((4096,1254),bool)
 for y in [0,1024,2048,2842]:
  gen=O/f'joint-{y}-ai-v1-generated.png';a=np.asarray(canvas.crop((0,y,1254,y+1254)),np.float32);b=np.asarray(Image.open(gen).convert('RGB'),np.float32)
  inp=O/f'stage-{y}-input.png';Image.fromarray(a.astype('uint8')).save(inp);derived(inp,[source]+[Path(m['replacement']) for m in manifest]+[Path(m['mask']) for m in manifest],{'method':'native current composite crop','originXY':[0,y]})
  cost=np.mean(np.minimum(abs(a-b),50)**2,axis=2)
  left=cut(cost,320,440);right=cut(cost,815,940);top=cut(cost.T,48,190 if y!=2842 else 310) if y else np.zeros(1254,int)
  Y,X=np.indices((1254,1254));m=(X>=left[:,None])&(X<right[:,None])&(Y>=top[None,:]);allmask[y:y+1254]|=m
  border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));border[0]=False;border[-1]=False
  grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);reliable=border&(grad<35)&(np.max(abs(a-b),axis=2)<35)
  weight=smooth(smooth(reliable[:,:,None].astype('float32')));num=smooth(smooth((a-b)*reliable[:,:,None]));f=np.clip(num/np.maximum(weight,1e-6),-12,12)*np.clip(weight*240,0,1)*m[:,:,None]
  rep=np.clip(np.rint(b+f),0,255).astype('uint8');rp=O/f'joint-{y}-replacement.png';mp=O/f'joint-{y}-mask.png';fp=O/f'joint-{y}-fields.npz';np.savez_compressed(fp,fields=f,left=left,right=right,top=top);Image.fromarray(rep).save(rp);Image.fromarray((m*255).astype('uint8')).save(mp)
  derived(mp,[inp,gen],{'method':'minimum-error binary ownership','ranges':{'left':[320,440],'right':[815,940],'top':None if not y else [48,190 if y!=2842 else 310]},'feather':False})
  derived(rp,[gen,inp,mp],{'method':'bounded additive RGB at reliable perimeter only; exclude canvas top/bottom edges','maxCorrection':float(abs(f).max()),'cap':12,'fieldFile':str(fp),'fieldSha256':sha(fp),'imageBlur':False,'imageResampling':False,'fieldSmoothing':'two 49px box filters of correction fields only'})
  canvas.paste(Image.fromarray(rep),(0,y),Image.fromarray((m*255).astype('uint8')));manifest.append(dict(name=f'joint-{y}',originXY=[0,y],replacement=str(rp),mask=str(mp),replacementSha256=sha(rp),maskSha256=sha(mp)))
 dest=O/'joint-candidate-v1.png';canvas.save(dest);derived(dest,[source]+[Path(m[k]) for m in manifest for k in ['replacement','mask']],{'method':'four native AI repairs exact binary masks in listed order','scale':1,'imageBlur':False,'imageWarp':False})
 am=O/'joint-mask-v1.png';Image.fromarray((allmask*255).astype('uint8')).save(am);derived(am,[Path(m['mask']) for m in manifest],{'method':'logical OR of placed binary ownership'})
 sources=json.loads((O/'sources.json').read_text(encoding='utf8'));tiles=[]
 for i,side in enumerate(['left','right']):
  base=Path(sources[i]['file']);tile=Image.open(base).convert('RGB');part=canvas.crop((0 if not i else 627,0,627 if not i else 1254,4096));tile.paste(part,(3469 if not i else 0,0));p=O/('r10_c12-west-joint-candidate-v1.png' if not i else 'r10_c13-west-joint-candidate-v1.png');tile.save(p);derived(p,[base,dest],{'method':'native exact replacement of 627px shared strip','unchangedOutsideStrip':True})
  tm=Image.new('L',(4096,4096));tm.paste(Image.fromarray(((allmask[:,0:627] if not i else allmask[:,627:])*255).astype('uint8')).convert('L'),(3469 if not i else 0,0));t=O/(side+'-tile-mask-v1.png');tm.save(t);derived(t,[am],{'method':'place joint mask into corresponding tile','side':side});tiles.append({'side':side,'base':str(base),'baseSha256':sha(base),'candidate':str(p),'sha256':sha(p),'mask':str(t),'maskSha256':sha(t),'bbox':tm.getbbox()})
 for y in [0,1024,2048,2842]:
  p=O/f'qa-v1-{y}.png';canvas.crop((0,y,1254,y+1254)).save(p);derived(p,[dest],{'nativeCrop':[0,y,1254,y+1254]})
 for y in [1139,2163,3072]:
  p=O/f'qa-v1-return-{y}.png';canvas.crop((220,y-180,1034,y+180)).save(p);derived(p,[dest],{'nativeCrop':[220,y-180,1034,y+180]})
 corner=Image.open(O/'north-four-corner.png').convert('RGB');corner.paste(canvas.crop((0,0,1254,627)),(0,627));p=O/'qa-v1-north-four-corner.png';corner.save(p);derived(p,[O/'north-four-corner.png',dest],{'operation':'native corner QA after south vertical seam repair; north untouched'})
 (O/'merge-manifest-v1.json').write_text(json.dumps({'joint':str(dest),'sha256':sha(dest),'globalOriginXY':[48525,36864],'seamX':627,'repairs':manifest,'tiles':tiles,'northCornerPending':True,'formalAccepted':False},indent=2),encoding='utf8')
 print(json.dumps(tiles,indent=2))
if __name__=='__main__':run()

