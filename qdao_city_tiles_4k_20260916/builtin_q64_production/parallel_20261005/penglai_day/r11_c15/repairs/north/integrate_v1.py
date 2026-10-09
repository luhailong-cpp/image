from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;R=O.parent.parent
sys.path.insert(0,str(R/'repairs/internal'));import ai_helper as h;import quilt as q
h.O=O
G=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for i,g in enumerate(['45623b90-a6be-4743-beb2-535a98f63ed7','738d8f89-39a2-45c0-989b-b9471723c5f7','2423e6ef-fa56-4477-8d3c-585dca3c0af8','8439ef26-3999-44cb-afc9-57486b0341cf'],1):h.ingest(f'north-{i}',G/('exec-'+g+'.png'))
def cut(cost,lo,hi):
 c=cost[:,lo:hi];n,w=c.shape;dp=c[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e12,dp[:-1]]+.2,dp,np.r_[dp[1:],1e12]+.2]);k=np.argmin(z,axis=0);back[y]=k-1;dp=c[y]+z[k,np.arange(w)]
 p=np.zeros(n,np.int32);p[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):p[y-1]=p[y]+back[y,p[y]]
 return p+lo
def alpha_inside(m,n):
 z=m.copy();d=m.astype('float32')
 for _ in range(n-1):
  z &= np.roll(z,1,0)&np.roll(z,-1,0)&np.roll(z,1,1)&np.roll(z,-1,1)
  d+=z
 return np.rint(np.minimum(d/n,1)*255).astype('uint8')
state=json.loads((O/'state-v1.json').read_text(encoding='utf8'));source=Path(state['source']);canvas=Image.open(source).convert('RGB');manifest=[]
for i,x in enumerate(state['patchOffsets'],1):
 n=f'north-{i}';gen=O/(n+'-generated.png');a=np.asarray(canvas.crop((x,0,x+1254,1254)),np.float32);b=np.asarray(Image.open(gen),np.float32);cost=np.mean(np.minimum(abs(a-b),70)**2,axis=2);Y,X=np.indices((1254,1254));t=cut(cost.T,315,420);d=cut(cost.T,865,980);m=(Y>=t[None,:])&(Y<d[None,:]);paths={'top':t,'bottom':d}
 if i>1:
  l=cut(cost,50,170 if i<4 else 240);m &= X>=l[:,None];paths['left']=l
 border=m&(~np.roll(m,1,0)|~np.roll(m,-1,0)|~np.roll(m,1,1)|~np.roll(m,-1,1));border[[0,-1]]=False;border[:,[0,-1]]=False
 grad=np.max(abs(a-np.roll(a,1,0))+abs(a-np.roll(a,1,1)),axis=2);rel=border&(grad<35)&(np.max(abs(a-b),axis=2)<80);w=q.smooth(q.smooth(rel[:,:,None].astype('float32')));num=q.smooth(q.smooth((a-b)*rel[:,:,None]));f=np.clip(num/np.maximum(w,1e-6),-32,32)*np.clip(w*240,0,1)
 alpha=alpha_inside(m,24);al=alpha[:,:,None].astype('float32')/255;rep=np.clip(np.rint(b+f),0,255).astype('uint8');out=np.rint(rep*al+a*(1-al)).astype('uint8');assert np.array_equal(out[alpha==0],a.astype('uint8')[alpha==0]);mp=O/(n+'-v1-alpha.png');rp=O/(n+'-v1-replacement.png');cp=O/(n+'-v1-composite.png');fp=O/(n+'-v1-fields.npz');np.savez_compressed(fp,field=f,**paths);Image.fromarray(alpha).save(mp);Image.fromarray(rep).save(rp);Image.fromarray(out).save(cp)
 refs=[source,gen]+[Path(z[k]) for z in manifest for k in ['replacement','mask']]
 q.record(mp,refs,{'method':'native adaptive ownership with exact24px alpha matte transition','origin':[x,0],'imageBlur':False,'sourceResampling':False,'topRange':[315,420],'bottomRange':[865,980]})
 q.record(rp,refs+[mp],{'method':'genuine AI1254 shared seam repair with bounded additive RGB perimeter field','cap':32,'actualMaxField':float(abs(f).max()),'fieldsFile':str(fp),'fieldsSha256':q.sha(fp),'imageBlur':False,'sourceResampling':False})
 q.record(cp,refs+[rp,mp],{'method':'exact alpha composite once','outsideSupportIdentical':True});canvas.paste(Image.fromarray(out),(x,0));manifest.append({'name':n,'origin':[x,0],'replacement':str(rp),'replacementSha256':q.sha(rp),'mask':str(mp),'maskSha256':q.sha(mp),'maskType':'alpha apply once'})
dst=O/'north-joint-final-v1.png';canvas.save(dst);q.record(dst,[source]+[Path(z[k]) for z in manifest for k in ['replacement','mask']],{'method':'four native AI joint patches composited using exact alpha mattes','globalOrigin':state['globalOrigin'],'seamY':627,'imageBlur':False,'sourceResampling':False})
outputs={}
for label,base,crop,pos in [('north',Path(state['north']['file']),(0,0,4096,627),(0,3469)),('self',Path(state['south']['file']),(0,627,4096,1254),(0,0))]:
 a=Image.open(base).convert('RGB');orig=np.asarray(a).copy();a.paste(canvas.crop(crop),pos);p=O/(('r10_c15-north-proposal-v1' if label=='north' else 'r11_c15-north-candidate-v1')+'.png');a.save(p);q.record(p,[base,dst],{'method':'native627-row joint half replacement','position':pos,'jointCrop':crop,'noResampling':True});diff=np.any(np.asarray(a)!=orig,axis=2);mp=O/(label+'-actual-diff-mask-v1.png');Image.fromarray((diff*255).astype('uint8')).save(mp);q.record(mp,[base,p],{'method':'exact binary RGB pixel difference'});yy,xx=np.where(diff);outputs[label]={'base':str(base),'baseSha256':q.sha(base),'file':str(p),'sha256':q.sha(p),'mask':str(mp),'maskSha256':q.sha(mp),'changedPixels':int(diff.sum()),'bboxLTRB':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'bottom115ChangedPixels':int(diff[-115:].sum())}
for line in [390,627,940]:
 board=Image.new('RGB',(1024,1152),(25,25,25));d=ImageDraw.Draw(board)
 for k in range(4):
  d.text((6,k*288+4),f'north joint y{line} segment{k+1} native',fill='white');board.paste(canvas.crop((k*1024,line-128,(k+1)*1024,line+128)),(0,k*288+26))
 p=O/f'qa-y{line}-v1.png';board.save(p);q.record(p,[dst],{'method':'four native strips no scaling','centerY':line})
for k,x in enumerate([1100,2140,3000]):
 p=O/f'qa-ai-junction-{k+1}-v1.png';canvas.crop((x-200,200,x+200,1100)).save(p);q.record(p,[dst],{'method':'native crop AI overlap join QA','crop':[x-200,200,x+200,1100]})
(O/'handoff-north-v1.json').write_text(json.dumps({'joint':str(dst),'sha256':q.sha(dst),'globalOrigin':state['globalOrigin'],'sources':state,'patches':manifest,'outputs':outputs,'formalAccepted':False},indent=2),encoding='utf8');print(json.dumps(outputs))
