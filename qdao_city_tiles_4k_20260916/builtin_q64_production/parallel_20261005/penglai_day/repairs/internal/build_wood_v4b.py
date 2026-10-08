from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,datetime
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/repairs/internal');W=D/'wood-native-repairs';Q=D/'qa-v4b-contour';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
source=D/'r09_c13-internal-candidate-v4.png';old=np.array(Image.open(source).convert('RGB'));aiPath=W/'wood3072-native.png';ai=np.array(Image.open(aiPath).convert('RGB'));ox,oy=397,2445;crop=old[oy:oy+1254,ox:ox+1254]; xx=np.arange(1254)[None,:];yy=np.arange(1254)[:,None]
# AI's actual native brown/blue silhouette supplies the center of the local support only.
# No image pixels are displaced; all accepted artwork is sampled at exactly its original coordinate.
left=[];right=[]
for y in range(1254):
 v=ai[y];l=np.where(v[510:605,0].astype(int)-v[510:605,2].astype(int)>10)[0];r=np.where(v[720:810,0].astype(int)-v[720:810,2].astype(int)>10)[0]
 left.append(int(l[0]+510) if len(l) else 547);right.append(int(r[-1]+720) if len(r) else 768)
left=np.array(left)[:,None];right=np.array(right)[:,None]
yfactor=smooth((yy-592)/16)*smooth((664-yy)/16)
# Full AI coverage includes the outline. Lateral returns are entirely on flat blue or wood surfaces.
lmask=smooth((xx-(left-10))/5)*smooth(((left+22)-xx)/8)*yfactor
rmask=smooth((xx-(right-22))/8)*smooth(((right+10)-xx)/5)*yfactor
mask=np.maximum(lmask,rmask).astype(np.float32);new=np.rint(crop*(1-mask[:,:,None])+ai*mask[:,:,None]).astype(np.uint8);out=old.copy();out[oy:oy+1254,ox:ox+1254]=new
changed=np.any(old!=out,axis=2);support=np.zeros(changed.shape,bool);support[oy:oy+1254,ox:ox+1254]=mask>0;assert np.array_equal(old[~support],out[~support])
dst=D/'r09_c13-internal-candidate-v4b.png';Image.fromarray(out).save(dst);mp=W/'wood3072-v4b-contour-mask.png';Image.fromarray(np.rint(mask*255).astype(np.uint8)).save(mp);fp=W/'wood3072-v4b-contour-mask.npz';np.savez_compressed(fp,alpha=mask,leftAIOutline=left,rightAIOutline=right)
qabox=(492,540,824,740);board=Image.new('RGB',((qabox[2]-qabox[0])*2+12,qabox[3]-qabox[1]+24),'#303030');board.paste(Image.fromarray(crop).crop(qabox),(0,24));board.paste(Image.fromarray(new).crop(qabox),(qabox[2]-qabox[0]+12,24));ImageDraw.Draw(board).text((3,3),'wood3072 v4                          v4b native AI contour',fill='white');qa=Q/'both-contours-before-after-native.png';board.save(qa)
for name,box in [('left',(510,565,605,710)),('right',(729,565,801,710))]:
 a=Image.fromarray(crop).crop(box);b=Image.fromarray(new).crop(box);s=Image.new('RGB',(a.width*2+12,a.height+24),'#303030');s.paste(a,(0,24));s.paste(b,(a.width+12,24));ImageDraw.Draw(s).text((0,3),'v4             v4b',fill='white');s.save(Q/(name+'-contour-native.png'));s.resize((s.width*4,s.height*4),Image.Resampling.NEAREST).save(Q/(name+'-contour-nearest4x-QA.png'))
ys,xs=np.nonzero(changed);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
rec={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file':str(dst),'sha256':sha(dst),'pixels':[4096,4096],'derivedFrom':[{'file':str(source),'sha256':sha(source),'record':str(D/'candidate-record-v4.json')},{'file':str(aiPath),'sha256':sha(aiPath),'record':str(aiPath)+'.generation.json'}],'operation':'Exact native-coordinate overlay from successful AI wood repair, extended locally across left and right silhouettes at y3072; no resample, displacement, blur or color correction. Soft alpha returns remain bounded to at most16px vertical and8px lateral.','sourceOriginXY':[ox,oy],'mask':{'file':str(mp),'sha256':sha(mp),'floatField':str(fp),'floatFieldSHA256':sha(fp)},'changedGlobalBoxLTRB':bbox,'changedPixels':int(changed.sum()),'unchangedOutsideMask':True,'formalAccepted':False,'parentReviewPending':True,'nativeQA':{'file':str(qa),'sha256':sha(qa),'scale':'1:1','actuallyViewed':False},'geometryEvidence':'Old source has approx1-2px outline step at native y627/global3072. Existing successful AI source has continuous tapered contours. Only these two local contour strips now use AI pixels; no registration/warping was performed.'}
write(D/'candidate-record-v4b.json',rec);print(json.dumps({'sha256':rec['sha256'],'box':bbox,'changedPixels':rec['changedPixels']}))
