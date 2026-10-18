from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,numpy as np
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/wood-post-style-20261016');T=D.parent.parent;sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
host=Path(r'C:/Users/luyua/.codex/generated_images/01a12075-f5cf-7c30-9edc-ceb79ed8cfbd/exec-969c1337-eee1-459f-8fa1-3ef0bd77aea9.png')
n=D/'native.png';assert not n.exists();shutil.copyfile(host,n);assert sha(host)==sha(n)
im=Image.open(n);assert im.size==(1254,1254) and ('A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255));im=im.convert('RGB');base=Image.open(D/'edit-target.png').convert('RGB')
poly=[(274,880),(278,864),(295,852),(323,840),(360,831),(416,828),(470,832),(513,841),(541,855),(556,874),(559,895),(559,1138),(273,1138)]
mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon(poly,fill=255);mask.save(D/'selection-mask.png');a=np.array(mask)
trial=base.copy();trial.paste(im,(0,0),mask);trial.save(D/'roi-trial.png');s=np.array(im);o=np.array(trial);orig=np.array(base);assert np.array_equal(o[a==255],s[a==255]);assert np.array_equal(o[a==0],orig[a==0])
for name,box in [('post-full',[230,790,610,1139]),('top',[240,800,590,950]),('left',[240,820,320,1139]),('right',[520,820,595,1139]),('bottom-edge',[240,1105,595,1139])]:trial.crop(box).save(D/(name+'.png'))
gen={'tool':'image_gen__imagegen','hostPath':str(host),'nativePath':str(n),'sha256':sha(n),'hostByteIdentical':True,'size':[1254,1254],'actualModel':None,'actualQuality':None,'sourceWorldBox':[14428,31629,15682,32883],'fullOutputAdopted':False}
(D/'generation.json').write_text(json.dumps(gen,indent=2))
p={'status':'pending_visual_review','source':str(n),'sourceSha256':sha(n),'sourceWorldBox':gen['sourceWorldBox'],'sourceOriginInTile':[2140,2957],'sameWorldNativeROI':[273,828,560,1139],'targetTileROI':[2413,3785,2700,4096],'mask':str(D/'selection-mask.png'),'maskSha256':sha(D/'selection-mask.png'),'maskMode':'L binary 0/255','maskPolygon':poly,'selectedPixelCount':int((a==255).sum()),'resampled':False,'blended':False,'outsideMaskPixelIdentical':True,'insideMaskNativePixelIdentical':True,'trial':str(D/'roi-trial.png'),'trialSha256':sha(D/'roi-trial.png'),'formalAccepted':False,'scope':'Only photographic wood material changed to painted chibi wood. Coping structural failure and other stone-style scope remain pending; bottom halo not adopted.'}
(D/'adoption-proposal.json').write_text(json.dumps(p,indent=2))
print({'sha':sha(n),'selectedPixels':p['selectedPixelCount']})

