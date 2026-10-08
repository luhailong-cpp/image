from pathlib import Path
import numpy as np,json,hashlib,datetime
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;R=O.parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(path,sources,op):
 d={'file':str(path),'sha256':sha(path),'derivedFrom':[{'file':str(p),'sha256':sha(p),'generationRecord':str(p)+'.generation.json'} for p in sources],'operation':op,'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False};Path(str(path)+'.generation.json').write_text(json.dumps(d,indent=2),encoding='utf8')
def save(a,path,sources,op):
 Image.fromarray(np.clip(np.rint(a),0,255).astype('uint8')).save(path);record(path,sources,op)
def smooth(a,r=24):
 for ax in [0,1]:
  pad=[(0,0)]*3;pad[ax]=(r,r);p=np.pad(a,pad,mode='edge');pad[ax]=(1,0);cs=np.pad(np.cumsum(p,axis=ax,dtype=np.float64),pad);hi=[slice(None)]*3;lo=hi.copy();hi[ax]=slice(2*r+1,None);lo[ax]=slice(None,-2*r-1);a=((cs[tuple(hi)]-cs[tuple(lo)])/(2*r+1)).astype('float32')
 return a
def seam(a,b,label,sources,cap=12):
 n,w,_=a.shape
 difference=a-b;f=np.clip(smooth(difference)/2,-cap,cap)
 fade=np.minimum(1,np.minimum(np.arange(w),np.arange(w)[::-1])/48)[None,:,None]
 fa=-f*fade;fb=f*fade;aa=a+fa;bb=b+fb
 cost=np.sqrt(np.mean((aa-bb)**2,axis=2))+.6*np.mean(abs(np.diff(a,axis=1,prepend=a[:,:1])-np.diff(b,axis=1,prepend=b[:,:1])),axis=2)
 cost+=np.abs(np.arange(w)-115)[None,:]*.015;cost[:,:42]=1e8;cost[:,w-42:]=1e8
 dp=cost[0].copy();back=np.zeros((n,w),np.int16)
 for y in range(1,n):
  z=np.stack([np.r_[1e9,dp[:-1]],dp,np.r_[dp[1:],1e9]]);k=np.argmin(z,axis=0);back[y]=k-1;dp=cost[y]+z[k,np.arange(w)]
 path=np.zeros(n,np.int16);path[-1]=np.argmin(dp)
 for y in range(n-1,0,-1):path[y-1]=path[y]+back[y,path[y]]
 own=np.arange(w)[None,:]<path[:,None];out=np.where(own[:,:,None],aa,bb)
 fields=O/(label+'-fields.npz');np.savez_compressed(fields,path=path,fieldA=fa.astype('float32'),fieldB=fb.astype('float32'),ownerA=own)
 mask=O/(label+'-owner-a.png');Image.fromarray((own*255).astype('uint8')).save(mask);record(mask,sources,{'method':'binary native ownership; no feather','fieldFile':str(fields),'fieldSha256':sha(fields),'sourceResampling':False,'imageBlur':False,'fieldSmoothingWindow':49,'capPerStage':cap,'maxFieldAbsolute':float(np.max(abs(f*fade))),'cutRange':[int(path.min()),int(path.max())]})
 return out
def qa(a,label,source):
 for axis in ['x','y']:
  for line in [1024,2048,3072]:
   board=Image.new('RGB',(1024,1152),(25,25,25));d=ImageDraw.Draw(board)
   for k in range(4):
    crop=a[k*1024:(k+1)*1024,line-128:line+128] if axis=='x' else a[line-128:line+128,k*1024:(k+1)*1024]
    if axis=='x':crop=np.rot90(crop)
    d.text((6,k*288+5),f'{axis}{line} segment{k+1} native',fill='white');board.paste(Image.fromarray(crop.astype('uint8')),(0,k*288+26))
   p=O/(label+f'-{axis}{line}.png');board.save(p);record(p,[source],{'method':'4 native256px strips; x rotated90 only; no resize'})
 board=Image.new('RGB',(1200,1284),(25,25,25));d=ImageDraw.Draw(board)
 for r,y in enumerate([1024,2048,3072]):
  for c,x in enumerate([1024,2048,3072]):
   d.text((c*400+6,r*428+5),f'{x},{y}',fill='white');board.paste(Image.fromarray(a[y-200:y+200,x-200:x+200].astype('uint8')),(c*400,r*428+26))
 p=O/(label+'-junctions.png');board.save(p);record(p,[source],{'method':'9 native400-square intersections; no resize'})
def run():
 shifts=json.loads((O/'overlap-diagnostics.json').read_text())['boundedPatchPlacementSuggestions']
 rows=[];allsrc=[]
 for r in range(1,5):
  fps=[R/'native'/f'p{r}{c}.png' for c in range(1,5)];allsrc+=fps
  row=np.zeros((1254,4326,3),np.float32)
  for c,p in enumerate(fps):
   im=Image.open(p).convert('RGB');dx,dy=shifts[p.stem];im=im.transform((1254,1254),Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.BICUBIC);reg=O/(p.stem+'-registered-v2.png');im.save(reg);record(reg,[p],{'method':'bounded native translation registration only','placementShiftXY':[dx,dy],'resample':'BICUBIC','scale':1,'noUpscaling':True,'diagnostic':str(O/'overlap-diagnostics.json')});b=np.asarray(im,np.float32);assert b.shape==(1254,1254,3)
   if c==0:row[:,:1254]=b
   else:
    x=c*1024;a=row[:,x:x+230].copy();out=seam(a,b[:,:230],f'v2-row{r}-x{c*1024}',fps[c-1:c+1]);row[:,x:x+1254]=b;row[:,x:x+230]=out
  rp=O/f'v2-row{r}.png';save(row,rp,fps,{'method':'native row quilt from1254sources, overlap230; binary ownership, <=12RGB field per source per join; no resampling or image blur'});rows.append(rp)
 canvas=np.zeros((4326,4326,3),np.float32)
 for i,rp in enumerate(rows):
  b=np.asarray(Image.open(rp).convert('RGB'),np.float32)
  if i==0:canvas[:1254]=b
  else:
   y=i*1024;a=canvas[y:y+230].copy();out=seam(a.transpose(1,0,2),b[:230].transpose(1,0,2),f'v2-y{i*1024}',rows[i-1:i+1]).transpose(1,0,2);canvas[y:y+1254]=b;canvas[y:y+230]=out
 final=np.clip(np.rint(canvas[115:4211,115:4211]),0,255).astype('uint8');dest=O/'r09_c14-internal-candidate-v2.png';save(final,dest,allsrc+rows,{'method':'native4x4 quilt: horizontal then vertical230overlap binary ownership; exact masks/fields saved; crop halo115','registration':'per-patch bounded translations, no scaling; see registered records','imageBlur':False,'feather':False,'perStageColorFieldCap':12,'maxCumulativeTheoreticalRGB':24,'formalAccepted':False});qa(final,'v2',dest);print(str(dest),sha(dest))
if __name__=='__main__':run()
