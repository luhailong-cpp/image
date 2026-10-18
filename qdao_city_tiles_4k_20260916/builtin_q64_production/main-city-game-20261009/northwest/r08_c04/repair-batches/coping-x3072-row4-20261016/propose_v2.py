from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,numpy as np
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=T/'repair-batches/coping-x3072-row4-20261016'
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
p=json.loads((D/'adoption-proposal.json').read_text()); native=Image.open(D/'native.png').convert('RGB');base=Image.open(D/'edit-target.png').convert('RGB')
poly=[(0,0),(1253,0),(1253,170),(1150,275),(1150,415),(1090,445),(1090,1138),(275,1138),(275,820),(0,820)]
mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon(poly,fill=255)
m=np.array(mask);trial=base.copy();trial.paste(native,(0,0),mask)
trial.save(D/'roi-trial-v2.png');mask.save(D/'selection-mask-v2.png')
a=np.array(base);o=np.array(trial);s=np.array(native);assert np.array_equal(o[m==0],a[m==0]);assert np.array_equal(o[m==255],s[m==255])
p.update({'status':'pending_visual_review','sameWorldNativeROI':[0,0,1254,1139],'targetTileROI':[2445,2957,3699,4096],'mask':str(D/'selection-mask-v2.png'),'maskSha256':sha(D/'selection-mask-v2.png'),'maskPolygon':poly,'selectedPixelCount':int((m==255).sum()),'trial':str(D/'roi-trial-v2.png'),'trialSha256':sha(D/'roi-trial-v2.png'),'supersedesRejectedRectangle':str(D/'adoption-proposal.json')})
(D/'adoption-proposal-v2.json').write_text(json.dumps(p,indent=2))
candidate=Image.open(T/'candidate/native-24-source-incremental-20261016T092532143914Z-5c44435606119f4b/candidate.png').convert('RGB');candidate.paste(native,(2445,2957),mask)
for name,box in [('full-context-v2',[2365,2877,3779,4096]),('west-context-v2',[2365,2957,2800,4096]),('north-context-v2',[2365,2877,3779,3087]),('east-context-v2',[3485,2877,3779,4096]),('post-mask-v2',[2395,3727,2780,4096])]:
 candidate.crop(box).save(D/(name+'.png'))
print({'proposal':str(D/'adoption-proposal-v2.json'),'pixels':p['selectedPixelCount']})

