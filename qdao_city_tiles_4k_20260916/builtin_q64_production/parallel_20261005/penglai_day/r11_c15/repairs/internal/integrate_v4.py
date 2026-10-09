from pathlib import Path
import sys,json,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parent.parent
sys.path.insert(0,str(O));import quilt as q
spec=json.loads((O/'ai-specs.json').read_text(encoding='utf8'))
def cut(cost,lo,hi):
 c=cost[:,lo:hi];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.2,dp,np.r_[dp[1:],1e12]+.2]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+z[k,np.arange(w)]
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+lo
ranges={
'deck':{'v':[[425,515],[740,830]],'h':[[450,540],[740,830]]},
'left-pile':{'box':[[300,360],[660,730],[380,470],[1100,1180]]},
'hull-left':{'v':[[440,520],[760,850]],'h':[[120,190],[320,390]]},
'hull-mid':{'v':[[440,510],[770,850]]},
'hull-right':{'v':[[410,510],[780,870]]},
'sail-upper-right':{'v':[[440,525],[760,850]],'h':[[820,910],[1160,1235]]},
'sail-midright':{'v':[[460,540],[770,855]],'h':[[830,900],[1130,1220]]},
'sail-leftmiddle':{'v':[[550,645],[880,970]],'h':[[420,520],[765,850]]},
'boom-left':{'v':[[530,640],[870,980]]},'hull-low':{'h':[[450,530],[720,800]]}}
src=O/'r11_c15-internal-candidate-v1.png';canvas=Image.open(src).convert('RGB');manifest=[]
spec=[z for z in spec if z['name']!='sail-midright']+[z for z in spec if z['name']=='sail-midright']+[{'name':'hull-low','origin':[750,2445]}]
for s in spec:
 n=s['name'];x,y=s['origin'];gen=O/(('hull-mid-keep-joint' if n=='hull-mid' else n)+'-generated.png');a=np.asarray(canvas.crop((x,y,x+1254,y+1254)),np.float32);b=np.asarray(Image.open(gen).convert('RGB'),np.float32)
 cost=np.mean(np.minimum(abs(a-b),70)**2,axis=2);Y,X=np.indices((1254,1254));m=np.zeros((1254,1254),bool);rr=ranges[n];paths={}
 if 'v' in rr:
  l=cut(cost,*rr['v'][0]);r=cut(cost,*rr['v'][1]);m|=(X>=l[:,None])&(X<r[:,None]);paths.update(vleft=l,vright=r)
 if 'h' in rr:
  t=cut(cost.T,*rr['h'][0]);d=cut(cost.T,*rr['h'][1]);m|=(Y>=t[None,:])&(Y<d[None,:]);paths.update(htop=t,hbottom=d)
 if 'box' in rr:
  l=cut(cost,*rr['box'][0]);r=cut(cost,*rr['box'][1]);t=cut(cost.T,*rr['box'][2]);d=cut(cost.T,*rr['box'][3]);m=(X>=l[:,None])&(X<r[:,None])&(Y>=t[None,:])&(Y<d[None,:]);paths.update(left=l,right=r,top=t,bottom=d)
 # Bound all masks away from generated crop edges via adaptive low-error ownership.
 l=cut(cost,45,125) if x>0 else np.zeros(1254)
 r=cut(cost,1120,1210) if x+1254<4096 else np.full(1254,1254)
 t=cut(cost.T,45,125) if y>0 else np.zeros(1254)
 d=cut(cost.T,1120,1210) if y+1254<4096 else np.full(1254,1254)
 m &= (X>=l[:,None])&(X<r[:,None])&(Y>=t[None,:])&(Y<d[None,:])
 paths.update(cropLeft=l,cropRight=r,cropTop=t,cropBottom=d)

 if n=='sail-upper-right':
  m &= (X>220)&(X<985)
  m |= (X>280)&(X<470) # whole mast segment, continued by next generated segment
 if n=='sail-midright':
  m &= (X>470)&(X<930)
  mast=(X>280)&(X<480)&(Y<1085)&(Y>=cut(cost.T,60,150)[None,:])
  boom=(X<910)&(Y>940+.075*X)&(Y<1095+.05*X)&(X>=cut(cost,20,80)[:,None])
  m |= mast|boom
 if n=='sail-leftmiddle':
  edge=390-0.16*Y
  m &= X>edge-32
 if n=='boom-left':
  m &= Y<720
  boom=(X>180)&(Y>435+.108*(X-200))&(Y<580+.108*(X-200))
  m |= boom

 m[(X+x<627)&(Y+y<627)]=False
 border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));border[[0,-1]]=False;border[:,[0,-1]]=False
 grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);rel=border&(grad<35)&(np.max(abs(a-b),axis=2)<70)
 w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*rel[:,:,None]));f=np.clip(num/np.maximum(w,1e-6),-28,28)*np.clip(w*240,0,1)*m[:,:,None]
 rep=np.clip(np.rint(b+f),0,255).astype('uint8');rp=O/(n+'-v4-replacement.png');mp=O/(n+'-v4-mask.png');fp=O/(n+'-v4-fields.npz');np.savez_compressed(fp,field=f,**paths);Image.fromarray(rep).save(rp);Image.fromarray((m*255).astype('uint8')).save(mp)
 refs=[src,gen]+[Path(v[k]) for v in manifest for k in ['replacement','mask']]
 q.record(mp,[src,gen],{'method':'bounded native minimum-error binary ownership; only seam corridors','ranges':rr,'origin':[x,y],'protectedTopLeft627':True,'realPlankJointPreserved':n=='hull-mid'})
 q.record(rp,refs+[mp],{'method':'genuine native AI seam repair with limited additive RGB perimeter field','cap':28,'actualMaxField':float(abs(f).max()),'fieldFile':str(fp),'fieldSha256':q.sha(fp),'imageBlur':False,'imageResampling':False})
 cp=O/(n+'-v4-composite.png');out=np.where(m[:,:,None],rep,a.astype('uint8'));Image.fromarray(out).save(cp);q.record(cp,refs+[rp,mp],{'method':'exact binary composite','outsideMaskIdentical':True})
 canvas.paste(Image.fromarray(rep),(x,y),Image.fromarray((m*255).astype('uint8')));manifest.append({'name':n,'origin':[x,y],'replacement':str(rp),'replacementSha256':q.sha(rp),'mask':str(mp),'maskSha256':q.sha(mp)})
dest=O/'r11_c15-internal-candidate-v4.png';canvas.save(dest);q.record(dest,[src]+[Path(v[k]) for v in manifest for k in ['replacement','mask']],{'method':'10 native local AI seam repairs via exact binary masks','noFinalResampling':True,'protectedTopLeft627':True})
assert np.array_equal(np.asarray(canvas)[:627,:627],np.asarray(Image.open(src))[:627,:627])
q.qa(np.asarray(canvas),'v4',dest)
preview=R/'preview-internal-v4.png';canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(preview);q.record(preview,[dest],{'method':'preview only downscale'})
(O/'ai-merge-manifest-v4.json').write_text(json.dumps({'base':str(src),'candidate':str(dest),'sha256':q.sha(dest),'repairs':manifest,'formalAccepted':False},indent=2),encoding='utf8')
print(q.sha(dest))
