from pathlib import Path
import sys,json,numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parent.parent
sys.path.insert(0,str(O));import ai_helper as h;import quilt as q
G=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,g in [('sail-lower-left','5de4abfa-21cc-4c08-9bf1-d534e67015e2'),('mast-lower','69755839-3ca7-4e22-a7a7-c939823e4e8c'),('sail-lower-right','3be53b41-74bf-4720-b681-4197393a324b'),('boom-lower','2b53e187-d52b-4a23-ac82-dcd73cda0843')]:h.ingest(n,G/('exec-'+g+'.png'))
def cut(cost,lo,hi):
 c=cost[:,lo:hi];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.2,dp,np.r_[dp[1:],1e12]+.2]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+z[k,np.arange(w)]
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+lo
def matte(m):
 z=m.copy();d=m.astype('float32')
 for _ in range(31):
  z &= np.roll(z,1,0)&np.roll(z,-1,0)&np.roll(z,1,1)&np.roll(z,-1,1);d+=z
 return np.rint(np.minimum(d/32,1)*255).astype('uint8')
ranges={
'yard-upper':{'v':[[430,520],[755,850]]},
'mast-upper':{'box':[[300,400],[800,920],[360,420],[940,1040]]},
'dock-upper':{'h':[[420,500],[780,890]],'v':[[110,165],[340,410]]},
'sail-middle-left':{'v':[[650,735],[980,1080]],'h':[[420,510],[750,850]]},
'mast-middle':{'box':[[270,360],[830,940],[400,510],[790,900]]},
'sail-middle-right':{'v':[[420,525],[795,880]],'h':[[420,510],[750,850]]},
'sail-lower-left':{'v':[[650,735],[980,1080]],'h':[[420,510],[750,850]]},
'mast-lower':{'box':[[270,360],[830,940],[400,510],[790,900]]},
'sail-lower-right':{'v':[[410,520],[795,890]],'h':[[80,155],[330,440]]},
'boom-lower':{'v':[[420,530],[770,890]]}}
src=O/'r11_c14-internal-candidate-v1.png';canvas=Image.open(src).convert('RGB');manifest=[];spec=json.loads((O/'ai-specs.json').read_text(encoding='utf8'))
for s in spec:
 n=s['name'];x,y=s['origin'];gen=O/(n+'-generated.png');a=np.asarray(canvas.crop((x,y,x+1254,y+1254)),np.float32);b=np.asarray(Image.open(gen),np.float32);cost=np.mean(np.minimum(abs(a-b),70)**2,axis=2);Y,X=np.indices((1254,1254));m=np.zeros((1254,1254),bool);rr=ranges[n];paths={}
 if 'v' in rr:
  l=cut(cost,*rr['v'][0]);r=cut(cost,*rr['v'][1]);m|=(X>=l[:,None])&(X<r[:,None]);paths.update(vleft=l,vright=r)
 if 'h' in rr:
  t=cut(cost.T,*rr['h'][0]);d=cut(cost.T,*rr['h'][1]);m|=(Y>=t[None,:])&(Y<d[None,:]);paths.update(htop=t,hbottom=d)
 if 'box' in rr:
  l=cut(cost,*rr['box'][0]);r=cut(cost,*rr['box'][1]);t=cut(cost.T,*rr['box'][2]);d=cut(cost.T,*rr['box'][3]);m=(X>=l[:,None])&(X<r[:,None])&(Y>=t[None,:])&(Y<d[None,:]);paths.update(left=l,right=r,top=t,bottom=d)
 l=cut(cost,45,135);r=cut(cost,1110,1210);t=cut(cost.T,65,145);d=cut(cost.T,1110,1210);m &= (X>=l[:,None])&(X<r[:,None])&(Y>=t[None,:])&(Y<d[None,:]);paths.update(cropLeft=l,cropRight=r,cropTop=t,cropBottom=d)
 if n=='dock-upper':m &= X<1100
 if n in ['sail-middle-left','sail-lower-left']:m &= X>180
 if n in ['sail-middle-right','sail-lower-right']:m &= X>160
 # Exact corner and exterior guide guards; external joint stage owns these pixels.
 m &= (X+x>=115)&(X+x<3981)&(Y+y>=115)&(Y+y<3981)
 m[((X+x<627)|(X+x>=3469))&(Y+y<627)]=False
 alpha=matte(m);al=alpha[:,:,None].astype('float32')/255;border=(alpha>0)&(alpha<255);grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);rel=border&(grad<35)&(np.max(abs(a-b),axis=2)<75);w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*rel[:,:,None]));f=np.clip(num/np.maximum(w,1e-6),-28,28)*np.clip(w*30,0,1)
 rep=np.clip(np.rint(b+f),0,255).astype('uint8');out=np.rint(rep*al+a*(1-al)).astype('uint8');assert np.array_equal(out[alpha==0],a.astype('uint8')[alpha==0]);mp=O/(n+'-v2-alpha.png');rp=O/(n+'-v2-replacement.png');cp=O/(n+'-v2-composite.png');fp=O/(n+'-v2-fields.npz');np.savez_compressed(fp,field=f,**paths);Image.fromarray(alpha).save(mp);Image.fromarray(rep).save(rp);Image.fromarray(out).save(cp);refs=[src,gen]+[Path(v[k]) for v in manifest for k in ['replacement','mask']]
 q.record(mp,refs,{'method':'exact32px alpha matte inside adaptive binary seam corridor','origin':[x,y],'ranges':rr,'protectedTopCorners627':True,'protectedExterior115':True,'noImageBlur':True,'noResampling':True})
 q.record(rp,refs+[mp],{'method':'genuine native AI repair plus bounded RGB perimeter field','cap':28,'actualMaxField':float(abs(f).max()),'fieldFile':str(fp),'fieldSha256':q.sha(fp),'noImageBlur':True,'noResampling':True})
 q.record(cp,refs+[rp,mp],{'method':'exact alpha composite once','outsideSupportIdentical':True});canvas.paste(Image.fromarray(out),(x,y));manifest.append({'name':n,'origin':[x,y],'replacement':str(rp),'replacementSha256':q.sha(rp),'mask':str(mp),'maskSha256':q.sha(mp),'maskType':'alpha composite once'})
dst=O/'r11_c14-internal-candidate-v2.png';canvas.save(dst);q.record(dst,[src]+[Path(v[k]) for v in manifest for k in ['replacement','mask']],{'method':'10 native AI seam repairs with exact masks and limited perimeter color fields','protectedTopCorners627':True,'noImageBlur':True,'noResampling':True});a=np.asarray(canvas);raw=np.asarray(Image.open(R/'tiles/r11_c14-candidate.png'));assert np.array_equal(a[:627,:627],raw[:627,:627]);assert np.array_equal(a[:627,-627:],raw[:627,-627:]);q.qa(a,'v2',dst);p=O/'preview-v2.png';canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(p);q.record(p,[dst],{'method':'preview only downscale'});(O/'ai-merge-manifest-v2.json').write_text(json.dumps({'base':str(src),'candidate':str(dst),'sha256':q.sha(dst),'repairs':manifest,'protectedTopCorners627Verified':True,'formalAccepted':False},indent=2),encoding='utf8');print(q.sha(dst))
