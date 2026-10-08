from pathlib import Path
from PIL import Image,ImageDraw
import sys,hashlib,json,numpy as np
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');R=T/'c02-north-repair';O=R/'candidate-v4';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=np.array(Image.open(R/'original/native/r01_c02.png').convert('RGB'));wood=np.array(Image.open(R/'wood-source02.png').convert('RGB'));e=np.array(Image.open(T/'native/r01_c03.png').convert('RGB'));ctx=json.loads((T/'regional/context.json').read_text());npth=Path(ctx['northCore']['file']);n=Image.open(npth).convert('RGB');nt=np.array(n.crop((909,3981,2163,4096)))
dx=np.load(R/'candidate-v3/geometry-fields.npz')['dx'];yy,xx=np.mgrid[:400,:1254].astype('float32');reg=cv2.remap(base,xx+dx,yy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
out=base.copy();out[115:400,:1139]=reg[115:400,:1139]
mask=Image.new('L',(1254,1254));poly=[(680,115),(870,115),(870,399),(755,399),(755,175),(680,150)];ImageDraw.Draw(mask).polygon(poly,fill=255);m=np.array(mask)>0
sourcewood=np.zeros_like(base);sourcewood[:742]=wood[512:1254];out[m]=sourcewood[m]
out[115:300,1024:1254]=e[115:300,:230]
out[:115]=nt;out[115:400,1139:]=e[115:400,115:230]
def probs(arr):
 z=arr.astype(float);rr,gg,bb=z[...,0],z[...,1],z[...,2]
 green=np.clip((gg-np.maximum(rr,bb)+2)/16,0,1)
 warm=np.clip((rr-gg-10)/25,0,1)*(1-green)
 orange=warm*np.clip((rr-170)/65,0,1)*np.clip((gg-bb-35)/40,0,1)
 wood=warm*(1-orange);stone=np.clip(1-green-wood-orange,0,1)
 return np.stack([green,orange,wood,stone],axis=-1)
upper=np.median(nt[-2:],axis=0);lower=np.median(out[115:117],axis=0);weights=probs(lower)
# Fit one bounded RGB translation per soft material; no per-column field.
edge=np.max(np.abs(np.diff(upper.astype(float),axis=0)),axis=1);valid=np.ones(1254,dtype=bool);valid[:-1]&=edge<28;valid[:5]=False;valid[1139:]=False
for a,b in [(150,185),(288,310),(318,336),(493,523),(700,730),(820,902),(938,985),(995,1008)]:valid[a:b]=False
A=weights[valid];B=upper[valid]-lower[valid];coef=np.linalg.lstsq(A,B,rcond=None)[0];coef=np.clip(coef,[-36,-42,-36],[36,42,36])
field=np.zeros((285,1254,3),np.float32)
for y in range(115,400):
 d=np.clip((y-115)/170,0,1);f=1-d*d*(3-2*d);field[y-115]=probs(out[y])@coef*f
field[:,1139:]=0
corrected=out.astype(float);corrected[115:400]+=field
# Match only quiet lower stone material inside wood patch; source and target contours must be verified.
bottom=np.zeros((285,1254,3),np.float32)
for y in range(365,400):
 alpha=(y-365)/35
 stone=probs(out[y])[:,3];targetdiff=base[y].astype(float)-np.rint(corrected[y])
 delta=np.clip(targetdiff,-24,24)*alpha*stone[:,None]*m[y,:,None]
 bottom[y-115]=delta;corrected[y]+=delta
final=np.rint(np.clip(corrected,0,255)).astype('uint8');final[:115]=nt;final[115:400,1139:]=e[115:400,115:230];final[400:]=base[400:]
assert np.array_equal(final[400:],base[400:])
Image.fromarray(final).save(O/'candidate1254.png');mask.save(O/'wood-mask.png');np.savez_compressed(O/'fields.npz',material_rgb=field,bottom_rgb=bottom,material_coefficients=coef,geometry_dx=dx,wood_mask=m)
joined=Image.new('RGB',(1254,512));joined.paste(n.crop((909,3840,2163,4096)),(0,0));joined.paste(Image.fromarray(final).crop((0,115,1254,371)),(0,256));joined.save(O/'north1254x512.png')
for name,box in [('orange',[0,216,380,336]),('wood',[350,216,750,336]),('stone',[680,186,1010,386]),('leaves',[990,206,1254,346])]:joined.crop(box).save(O/(name+'.png'))
Image.fromarray(final).crop((620,115,930,460)).save(O/'wood-patch310x345.png');Image.fromarray(final).crop((0,335,1254,465)).save(O/'bottom1254x130.png')
meta={'status':'pending_visual_review_not_adopted','derivedFromV3Geometry':{'file':str(R/'candidate-v3/geometry-fields.npz'),'sha256':sha(R/'candidate-v3/geometry-fields.npz')},'woodPolygon':poly,'woodSource':{'file':str(R/'wood-source02.png'),'sha256':sha(R/'wood-source02.png')},'woodCopy':'destination(x,y) samples woodSource(x,y+512); polygon integer pixel mask. Narrow to upright above occluding white rail; do not cut middle of wooden seat at y350.','rgb':{'materials':['green','orange','wood','stone'],'coefficients':coef.tolist(),'fit':'Least-squares true north last2 minus final pre-correction south first2 using continuous material probabilities; strong edge and known geometry crossing columns excluded; bounded translation per material, never per-column curtains.','limit':[36,42,36],'actualMin':field.min(axis=(0,1)).tolist(),'actualMax':field.max(axis=(0,1)).tolist(),'depthFade':'smoothstep y115..285 tozero','bottomCorrectionLimit':24,'bottomCorrectionActualMin':bottom.min(axis=(0,1)).tolist(),'bottomCorrectionActualMax':bottom.max(axis=(0,1)).tolist()},'unchangedRows400To1253Verified':True,'outputs':[{'file':str(f),'sha256':sha(f)} for f in O.glob('*.png')],'field':{'file':str(O/'fields.npz'),'sha256':sha(O/'fields.npz')},'formalAccepted':False}
(O/'manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps(meta['rgb']))

