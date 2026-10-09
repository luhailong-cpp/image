from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;R=O.parent.parent;sys.path.insert(0,str(O));import ai_helper as h;sys.path.insert(0,str(R/'repairs/internal'));import quilt as q
axis=sys.argv[1]
G=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
ids=json.loads((O/'tool-results.json').read_text(encoding='utf8'))[axis]
for i,g in enumerate(ids):h.ingest(axis+'-'+str(i+1),G/('exec-'+g+'.png'))
spec=json.loads((O/(axis+'-spec.json')).read_text(encoding='utf8'));state=json.loads((O/spec['inputState']).read_text(encoding='utf8'));src=Path(spec['joint']);im=np.asarray(Image.open(src).convert('RGB')).copy()
if axis!='north':im=im.transpose(1,0,2).copy()
def cut(cost,lo,hi):
 c=cost[:,lo:hi];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for yy in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.2,dp,np.r_[dp[1:],1e12]+.2]);k=np.argmin(z,axis=0);back[yy]=k-1;dp=c[yy]+z[k,np.arange(w)]
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for yy in range(n-1,0,-1):p[yy-1]=p[yy]+back[yy,p[yy]]
 return p+lo
def matte(m):
 z=m.copy();d=m.astype('float32')
 for _ in range(31):
  z &= np.roll(z,1,0)&np.roll(z,-1,0)&np.roll(z,1,1)&np.roll(z,-1,1);d+=z
 return np.rint(np.minimum(d/32,1)*255).astype('uint8')
manifest=[];Y,X=np.indices((1254,1254))
for i,s in enumerate(spec['patches']):
 n=s['name'];z=s['offset'];gen=O/(n+'-generated.png');a=im[:,z:z+1254].astype('float32');b=np.asarray(Image.open(gen),np.float32)
 if axis!='north':b=b.transpose(1,0,2)
 cost=np.mean(np.minimum(abs(a-b),70)**2,axis=2);top=cut(cost.T,250,380);bottom=cut(cost.T,915,1030);left=cut(cost,35,145) if i else np.zeros(1254,int);right=cut(cost,1130,1230) if i<3 else np.full(1254,1254)
 m=(Y>=top[None,:])&(Y<bottom[None,:])&(X>=left[:,None])&(X<right[:,None]);m &= X+z>=557
 if axis=='north':m &= X+z<3539
 # Preserve first and last image edge as needed only for protected corners; open ungenerated southern edge remains editable.
 alpha=matte(m);al=alpha[:,:,None].astype('float32')/255;grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);rel=(alpha>0)&(alpha<255)&(grad<40)&(np.max(abs(a-b),axis=2)<90);w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*rel[:,:,None]));f=np.clip(num/np.maximum(w,1e-6),-32,32)*np.clip(w*30,0,1);rep=np.clip(np.rint(b+f),0,255).astype('uint8');out=np.rint(rep*al+a*(1-al)).astype('uint8');assert np.array_equal(out[alpha==0],a.astype('uint8')[alpha==0]);im[:,z:z+1254]=out
 refs=[src,gen]+[Path(v[k]) for v in manifest for k in ['replacement','mask']]
 outs={}
 for label,arr in [('alpha',alpha),('replacement',rep),('composite',out)]:
  if axis!='north':arr=arr.T if arr.ndim==2 else arr.transpose(1,0,2)
  p=O/(n+'-v1-'+label+'.png');Image.fromarray(arr).save(p);q.record(p,refs,{'method':'native AI repair masked once; exact alpha support with32px matte and boundedRGB32 perimeter field; no image blur/resampling','axis':axis,'jointOrigin':[z,0] if axis=='north' else [0,z],'cornerInner557Protected':True});outs[label]=str(p)
 fp=O/(n+'-v1-fields.npz');np.savez_compressed(fp,field=f,top=top,bottom=bottom,left=left,right=right);manifest.append({'name':n,'jointOrigin':[z,0] if axis=='north' else [0,z],'replacement':outs['replacement'],'mask':outs['alpha'],'field':str(fp),'fieldSha256':q.sha(fp),'composite':outs['composite']})
dst=O/(axis+'-joint-v1.png');final=im if axis=='north' else im.transpose(1,0,2);Image.fromarray(final).save(dst);q.record(dst,[src]+[Path(v[k]) for v in manifest for k in ['replacement','mask']],{'method':'four native1254 joint repairs; exact protected557corner; no image blur/resampling'})
for normal in [390,627,940]:
 board=Image.new('RGB',(1024,1152),(25,25,25));d=ImageDraw.Draw(board)
 for k in range(4):d.text((6,k*288+5),axis+' normal'+str(normal)+' segment'+str(k+1),fill='white');board.paste(Image.fromarray(im[normal-128:normal+128,k*1024:(k+1)*1024]),(0,k*288+26))
 p=O/(axis+'-qa-'+str(normal)+'-v1.png');board.save(p);q.record(p,[dst],{'method':'native4096 full line in four panels; vertical joint transposed for QA only','normal':normal,'noResampling':True})
for i,s in enumerate(spec['patches']):
 z=s['offset'];ar=im[:,z:z+1254];ar=ar if axis=='north' else ar.transpose(1,0,2);p=O/(s['name']+'-final-context-v1.png');Image.fromarray(ar).save(p);q.record(p,[dst],{'method':'native1254 final context','offset':z,'axis':axis})
selfim=Image.open(state['current']['r11_c14']).convert('RGB');neighbor=spec['neighbor'];neim=Image.open(state['current'][neighbor]).convert('RGB')
if axis=='north':neim.paste(Image.fromarray(final[:627]),(0,3469));selfim.paste(Image.fromarray(final[627:]),(0,0))
elif axis=='west':neim.paste(Image.fromarray(final[:,:627]),(3469,0));selfim.paste(Image.fromarray(final[:,627:]),(0,0))
else:selfim.paste(Image.fromarray(final[:,:627]),(3469,0));neim.paste(Image.fromarray(final[:,627:]),(0,0))
for key,obj in [('r11_c14',selfim),(neighbor,neim)]:
 p=O/(key+'-after-'+axis+'-v1.png');obj.save(p);q.record(p,[Path(state['current'][key]),dst],{'method':'paste exact joint half; no repeated alpha, no resampling','axis':axis});state['current'][key]=str(p)
state.setdefault('stages',[]).append({'axis':axis,'joint':str(dst),'sha256':q.sha(dst),'repairs':manifest});(O/('state-after-'+axis+'-v1.json')).write_text(json.dumps(state,indent=2),encoding='utf8');print(axis+' merged')

