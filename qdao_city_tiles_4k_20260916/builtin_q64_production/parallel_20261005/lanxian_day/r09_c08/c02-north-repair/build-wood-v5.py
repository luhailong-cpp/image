from pathlib import Path
from PIL import Image,ImageDraw
import sys,hashlib,json,numpy as np
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');R=T/'c02-north-repair';O=R/'wood-v5';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v4p=R/'candidate-v4/candidate1254.png';prior=np.array(Image.open(v4p).convert('RGB'));base=np.array(Image.open(R/'original/native/r01_c02.png').convert('RGB'));wood=np.array(Image.open(R/'wood-source02.png').convert('RGB'));ctx=json.loads((T/'regional/context.json').read_text());npth=Path(ctx['northCore']['file']);n=Image.open(npth).convert('RGB');nt=np.array(n.crop((909,3981,2163,4096)))
f4=np.load(R/'candidate-v4/fields.npz');dx4=f4['geometry_dx'];y,x=np.mgrid[:400,:1254].astype('float32')
# Restore original seat and entire lower support, retaining existing base registration and baseline material correction.
reg=cv2.remap(base,x+dx4,y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
restore=reg.copy();restore[115:400]=np.rint(np.clip(restore[115:400].astype(float)+f4['material_rgb'],0,255)).astype('uint8')
out=prior.copy();oldmask=f4['wood_mask'];out[oldmask]=np.concatenate([restore,base[400:]],axis=0)[oldmask]
def smooth(z):z=np.clip(z,0,1);return z*z*(3-2*z)
poly=[(695,115),(870,115),(870,230),(750,230),(750,155),(695,140)];mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon(poly,fill=255);m=np.array(mask)>0
xf=smooth((x-760)/40)*(1-smooth((x-848)/22));yf=1-smooth((y-115)/115)
dx=16*xf*yf
dy=22*smooth((x-700)/30)*(1-smooth((x-832)/38))*yf
swood=cv2.remap(wood,x+dx,y+512+dy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
out[:400][m[:400]]=swood[m[:400]]
# Exact constant-in-row wood-only material observations after geometry, not an accepted result.
joined=Image.new('RGB',(1254,512));joined.paste(n.crop((909,3840,2163,4096)),(0,0));joined.paste(Image.fromarray(out).crop((0,115,1254,371)),(0,256))
out[:115]=nt;assert np.array_equal(out[400:],base[400:])
Image.fromarray(out).save(O/'candidate1254.png');mask.save(O/'wood-mask.png');Image.fromarray(np.uint8(np.any(out!=prior,axis=2)*255)).save(O/'changed-from-v4-mask.png')
np.savez_compressed(O/'wood-fields.npz',dx=dx,dy=dy,mask=m)
joined.save(O/'north1254x512.png');joined.crop((680,186,1010,386)).save(O/'stone-wood330x200.png');Image.fromarray(out).crop((620,90,930,450)).save(O/'wood-seat310x360.png')
meta={'status':'geometric_experiment_not_adopted','baseV4':{'file':str(v4p),'sha256':sha(v4p)},'woodSource':{'file':str(R/'wood-source02.png'),'sha256':sha(R/'wood-source02.png')},'woodMask':poly,'sourceGeometry':{'dxMax':float(dx.max()),'dyMax':float(dy.max()),'reason':'Explicitly larger local source transform to test measured wood end face displacement; not described as old subpixel registration. Source offset fades tozero bycell230.','sampling':'bilinear'},'originalSeatRestored':True,'unchangedOutsideX430To870ExceptRestoringOldWoodMask':bool(np.array_equal(out[:,870:],prior[:,870:])),'allRows400To1253Exact':True,'outputs':[{'file':str(q),'sha256':sha(q)} for q in O.glob('*.png')],'fields':{'file':str(O/'wood-fields.npz'),'sha256':sha(O/'wood-fields.npz')},'formalAccepted':False}
(O/'manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps(meta['sourceGeometry']))

