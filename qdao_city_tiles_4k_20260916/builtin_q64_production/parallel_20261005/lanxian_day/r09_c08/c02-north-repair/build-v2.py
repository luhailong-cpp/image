from pathlib import Path
import sys,hashlib,json
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2,numpy as np
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');R=T/'c02-north-repair';O=R/'candidate-v2';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
basep=R/'original/native/r01_c02.png';northp=Path(json.loads((T/'regional/context.json').read_text())['northCore']['file']);eastp=T/'native/r01_c03.png'
a=np.asarray(Image.open(basep).convert('RGB'));north=np.asarray(Image.open(northp).convert('RGB').crop((909,3981,2163,4096)));east=np.asarray(Image.open(eastp).convert('RGB'))
src=cv2.cvtColor(a[:115],cv2.COLOR_RGB2GRAY);ref=cv2.cvtColor(north,cv2.COLOR_RGB2GRAY)
flow=cv2.calcOpticalFlowFarneback(ref,src,None,0.5,4,31,5,7,1.5,0)
rowflow=np.median(flow[91:113],axis=0)
rowflow=cv2.GaussianBlur(rowflow[None],(0,0),5,0)[0]
# measured registration requested bounded8 px in each channel. Clip robust estimates.
raw=rowflow.copy();rowflow=np.clip(rowflow,-8,8)
y,x=np.mgrid[:1254,:1254].astype(np.float32);d=np.clip((y-115)/285,0,1);weight=1-(d*d*(3-2*d));weight[y>=400]=0
dx=rowflow[None,:,0]*weight;dy=rowflow[None,:,1]*weight
warped=cv2.remap(a,x+dx,y+dy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
# All RGB matching comes from already existing native images; this candidate tests original source registration.
refgridx,refgridy=np.meshgrid(np.arange(1254,dtype=np.float32),np.arange(115,dtype=np.float32))
matched=cv2.remap(a,refgridx+rowflow[None,:,0],refgridy+rowflow[None,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
delta=np.median(north[107:115].astype(float)-matched[107:115].astype(float),axis=0)
delta=cv2.GaussianBlur(delta[None].astype(np.float32),(0,0),2,0)[0]
def probs(arr):
 z=arr.astype(float);rr,gg,bb=z[...,0],z[...,1],z[...,2]
 green=np.clip((gg-np.maximum(rr,bb)+2)/14,0,1)
 warm=np.clip((rr-gg-8)/24,0,1)*(1-green)
 orange=warm*np.clip((rr-150)/70,0,1)*np.clip((gg-bb-40)/35,0,1)
 wood=warm*(1-orange)
 stone=np.clip(1-green-wood-orange,0,1)
 return np.stack([green,orange,wood,stone],axis=-1)
boundary=probs(np.median(matched[107:115],axis=0))
cur=probs(warped);alpha=np.sum(cur*boundary[None],axis=-1)
lum=np.mean(warped.astype(float),axis=2);reflum=np.mean(matched[107:115].astype(float),axis=(0,2))
relative=delta/np.maximum(reflum[:,None],12)
limits=np.array([64,80,48.],dtype=float)
fields=np.zeros((285,1254,3),np.float32)
for yy in range(115,400):
 depth=yy-115;sig=2+16*min(depth/160,1)
 rel=cv2.GaussianBlur(relative[None].astype(np.float32),(0,0),sig,0)[0]
 fade=1-np.clip(depth/170,0,1)**2*(3-2*np.clip(depth/170,0,1))
 fields[depth]=np.clip(rel*lum[yy,:,None]*alpha[yy,:,None]*fade,-limits,limits)
corrected=warped.copy();corrected[115:400]=np.rint(np.clip(warped[115:400].astype(float)+fields,0,255)).astype(np.uint8)
out=a.copy();out[115:400,:1139]=corrected[115:400,:1139];out[:115]=north;out[115:400,1139:]=east[115:400,115:230]
assert np.array_equal(out[400:],a[400:])
Image.fromarray(out).save(O/'candidate1254.png');np.savez_compressed(O/'fields.npz',dx=dx[:400],dy=dy[:400],rgb=fields,material_alpha=alpha[115:400],raw_row_flow=raw,row_flow=rowflow)
Image.fromarray(np.uint8(np.any(out!=a,axis=2)*255)).save(O/'edit-mask.png')
nfull=Image.open(northp).convert('RGB')
joined=Image.new('RGB',(1254,512));joined.paste(nfull.crop((909,3840,2163,4096)),(0,0));joined.paste(Image.fromarray(out).crop((0,115,1254,371)),(0,256))
joined.save(O/'north1254x512.png')
for name,box in [('orange',[0,216,380,336]),('wood',[350,216,750,336]),('stone',[720,206,1010,346]),('leaves',[990,206,1254,346])]:joined.crop(box).save(O/(name+'.png'))
Image.fromarray(out).crop((0,300,1254,460)).save(O/'bottom1254x160.png')
meta={'status':'diagnostic_candidate_not_adopted','strategy':'Try bounded native registration of original candidate, which already has complete structural silhouettes. RepairAI01 is recorded but not a source in this test.','base':{'file':str(basep),'sha256':sha(basep)},'north':{'file':str(northp),'sha256':sha(northp)},'east':{'file':str(eastp),'sha256':sha(eastp)},'geometry':{'estimate':'Farneback true north115 to original candidate top115; median final22 rows, sigma5 numeric-field Gaussian','rawMin':raw.min(axis=0).tolist(),'rawMax':raw.max(axis=0).tolist(),'limit':8,'appliedMin':[float(dx.min()),float(dy.min())],'appliedMax':[float(dx.max()),float(dy.max())],'resampling':'OpenCV bilinear, edge replicate; displacement smoothstep to0 at y400'},'rgb':{'measuredDeltaMin':delta.min(axis=0).tolist(),'measuredDeltaMax':delta.max(axis=0).tolist(),'limits':limits.tolist(),'actualMin':fields.min(axis=(0,1)).tolist(),'actualMax':fields.max(axis=(0,1)).tolist(),'method':'Relative brightness field from overlapping real north107..114 vs registered original overlap; numeric field sigma2..18 with depth; soft green/orange/wood/stone confidence inner product; smoothstep tozero after170rows. No image blur.'},'unchangedRows400To1253Verified':True,'fields':{'file':str(O/'fields.npz'),'sha256':sha(O/'fields.npz')},'outputs':[{'file':str(f),'sha256':sha(f)} for f in O.glob('*.png')],'formalAccepted':False}
(O/'manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps({k:meta[k] for k in ['geometry','rgb','unchangedRows400To1253Verified']}))

