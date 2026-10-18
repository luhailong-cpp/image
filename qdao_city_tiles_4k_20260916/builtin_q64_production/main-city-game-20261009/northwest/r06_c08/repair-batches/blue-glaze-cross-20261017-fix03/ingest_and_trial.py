from pathlib import Path
from datetime import datetime,timezone
import sys,shutil,numpy as np
from PIL import Image,ImageDraw
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');sys.path.insert(0,str(T.parent));import production_v2 as p
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08/repair-batches/blue-glaze-cross-20261017-fix03');r=p.read(B/'tool-result.json');src=Path(r['hostOutputPath']);dst=B/'native.png';assert not dst.exists();shutil.copyfile(src,dst);im=Image.open(dst)
assert im.size==(1254,1254) and im.mode in ['RGB','RGBA']
if im.mode=='RGBA':assert im.getchannel('A').getextrema()==(255,255)
p.write_json(B/'generation.json',dict(source=str(dst),sha256=p.sha(dst),hostOutputPath=str(src),worldBox=[28512,21901,29766,23155],tileOrigin=[-160,1421],size=list(im.size),native=True,resized=False,tool='image_gen.imagegen',route='builtin',actualModel=None,actualQuality=None,request=str(B/'request.json'),requestSha256=p.sha(B/'request.json'),receipt=str(B/'tool-result.json'),receiptSha256=p.sha(B/'tool-result.json')),replace=False)
C=Image.open(T/'candidate/native16-restart-20261017-v1/candidate.png').convert('RGB')
mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon([(160,562),(205,549),(366,557),(450,564),(1040,569),(1223,551),(1230,708),(1040,714),(870,716),(365,706),(160,704)],fill=255)
p.save_png(B/'mask-v1.png',mask)
a=np.array(C);s=np.array(im.convert('RGB'));ma=np.array(mask)>0;yy,xx=np.where(ma);tx=xx-160;ty=yy+1421
assert tx.min()>=0 and tx.max()<4096 and ty.min()>=0 and ty.max()<4096
a[ty,tx]=s[yy,xx];trial=Image.fromarray(a);p.save_png(B/'trial-v1.png',trial)
q=B/'qa-v1';q.mkdir();defs={'internal_y2048_seg1':[0,1888,1024,2208],'internal_x1024_seg2':[864,1024,1184,2048],'internal_x1024_seg3':[864,2048,1184,3072],'internal_jx1024_y2048':[864,1888,1184,2208]}
views=[]
for n,box in defs.items():
 f=q/(n+'.png');p.save_png(f,trial.crop(box));views.append(dict(name=n,file=str(f),sha256=p.sha(f),box=box))
W=Image.open(T.parent/'r06_c07/candidate/r06_c07-candidate-hard-4c0d654c3aae.png').convert('RGB')
for n,y0,y1 in [('west_seg2',1024,2048),('west_seg3',2048,3072),('west_joint2048',1888,2208)]:
 crop=Image.new('RGB',(320,y1-y0));crop.paste(W.crop((3936,y0,4096,y1)),(0,0));crop.paste(trial.crop((0,y0,160,y1)),(160,0));f=q/(n+'.png');p.save_png(f,crop);views.append(dict(name=n,file=str(f),sha256=p.sha(f)))
# Natural mask perimeter at native scale, includes old/new artwork on every side.
field=Image.open(B/'edit-target.png').convert('RGB');field.paste(im.convert('RGB'),(0,0),mask)
f=q/'local-composite.png';p.save_png(f,field.crop((0,500,1254,760)));views.append(dict(name='local-composite',file=str(f),sha256=p.sha(f)))
p.write_json(B/'trial-v1.json',dict(baseCandidate=str(T/'candidate/native16-restart-20261017-v1/candidate.png'),baseSha256=p.sha(T/'candidate/native16-restart-20261017-v1/candidate.png'),source=str(dst),sourceSha256=p.sha(dst),mask=str(B/'mask-v1.png'),maskSha256=p.sha(B/'mask-v1.png'),worldOrigin=[28512,21901],tileOrigin=[-160,1421],selectedPixelCount=len(xx),sameWorldNativeCopy=True,resampled=False,feathered=False,colorAdjusted=False,selected=False,formalAccepted=False,qa=views),replace=False)
print({'sourceSha256':p.sha(dst),'pixels':len(xx),'qa':len(views)})

