from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,datetime
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/repairs/internal'); W=D/'wood-native-repairs'; Q=D/'qa-v4-wood';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def smooth(v):v=np.clip(v,0,1);return v*v*(3-2*v)
source=D/'r09_c13-internal-candidate-v3b.png'; old=np.asarray(Image.open(source).convert('RGB')); out=old.copy(); support=np.zeros((4096,4096),bool);jobs=[]
for name,origin,yrange,leftpoints,rightpoints,qbox in [
 ('wood2048',(397,1421),(460,960),[(460,634),(648,634),(665,594),(960,592)],[(460,740),(960,740)],(545,410,786,1010)),
 ('wood3072',(397,2445),(420,750),[(420,574),(627,559),(750,546)],[(420,746),(627,765),(750,777)],(492,380,824,820))]:
 aiPath=W/(name+'-native.png'); ai=np.asarray(Image.open(aiPath).convert('RGB')); h,w=ai.shape[:2];xx=np.arange(w)[None,:];yy=np.arange(h)[:,None]
 lx=np.interp(np.arange(h),[p[0] for p in leftpoints],[p[1] for p in leftpoints])[:,None];rx=np.interp(np.arange(h),[p[0] for p in rightpoints],[p[1] for p in rightpoints])[:,None]
 mask=(smooth((xx-lx)/8)*smooth((rx-xx)/8)*smooth((yy-yrange[0])/32)*smooth((yrange[1]-yy)/32)).astype(np.float32)
 ox,oy=origin;base=old[oy:oy+h,ox:ox+w];new=np.rint(base*(1-mask[:,:,None])+ai*mask[:,:,None]).astype(np.uint8)
 out[oy:oy+h,ox:ox+w]=new; support[oy:oy+h,ox:ox+w]|=mask>0
 maskPath=W/(name+'-v4-mask.png');Image.fromarray(np.rint(mask*255).astype(np.uint8)).save(maskPath);fieldPath=W/(name+'-v4-mask.npz');np.savez_compressed(fieldPath,alpha=mask)
 board=Image.new('RGB',((qbox[2]-qbox[0])*2+12,qbox[3]-qbox[1]+24),'#303030');board.paste(Image.fromarray(base).crop(qbox),(0,24));board.paste(Image.fromarray(new).crop(qbox),(qbox[2]-qbox[0]+12,24));ImageDraw.Draw(board).text((3,3),name+' SOURCE                       v4 LOCAL AI',fill='white');qa=Q/(name+'-before-after-native.png');board.save(qa)
 bounds=np.nonzero(mask); bbox=[int(bounds[1].min()+ox),int(bounds[0].min()+oy),int(bounds[1].max()+1+ox),int(bounds[0].max()+1+oy)]
 jobs.append({'name':name,'source':{'file':str(aiPath),'sha256':sha(aiPath),'generationRecord':str(aiPath)+'.generation.json'},'originXY':origin,'affectedGlobalBoxLTRB':bbox,'nativeSourceSize':[w,h],'resample':False,'geometricWarp':False,'colorCorrection':False,'mask':{'file':str(maskPath),'sha256':sha(maskPath),'floatField':str(fieldPath),'floatFieldSHA256':sha(fieldPath),'leftPointsYX':leftpoints,'rightPointsYX':rightpoints,'yRange':yrange,'method':'product of bounded cubic smoothstep; lateral support8px, vertical support32px; native pixels only; no blur on image'},'changedPixels':int(np.any(base!=new,axis=2).sum()),'qa':{'file':str(qa),'sha256':sha(qa),'scale':'1:1','sourceLocalBoxLTRB':qbox,'actuallyViewed':False}})
assert np.array_equal(out[~support],old[~support]); dst=D/'r09_c13-internal-candidate-v4.png';Image.fromarray(out).save(dst)
write(D/'candidate-record-v4.json',{'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file':str(dst),'sha256':sha(dst),'pixels':[4096,4096],'derivedFrom':{'file':str(source),'sha256':sha(source),'record':str(D/'candidate-record-v3b.json')},'operation':'Two native builtin AI edited wood interiors masked into v3b; no resize, warp, image blur, or color correction; exterior contours excluded from mask','jobs':jobs,'unchangedOutsideMasks':True,'newGeometricWarp':False,'inheritedMaxGeometricWarp':0.8151938342695622,'formalAccepted':False,'rootReviewPending':True,'sourceFilesModified':False})
print(json.dumps({'file':str(dst),'sha256':sha(dst),'jobs':[{k:v for k,v in j.items() if k in ['name','affectedGlobalBoxLTRB','changedPixels']} for j in jobs]}))

