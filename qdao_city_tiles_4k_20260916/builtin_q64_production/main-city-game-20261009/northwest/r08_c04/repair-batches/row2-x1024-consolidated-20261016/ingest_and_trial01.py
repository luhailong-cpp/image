from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,hashlib,shutil
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/row2-x1024-consolidated-20261016');host=Path(r'C:/Users/luyua/.codex/generated_images/01a142ef-b2f7-7e30-9d4f-545e2c80f42f/exec-ed876ad4-c525-4505-8600-e14f3d4ffc32.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
native=D/'native.png';assert not native.exists();shutil.copyfile(host,native);assert sha(host)==sha(native)
raw=Image.open(native);assert raw.size==(1254,1254) and ('A' not in raw.getbands() or raw.getchannel('A').getextrema()==(255,255))
(D/'generation.json').write_text(json.dumps({'tool':'image_gen__imagegen','hostPath':str(host),'nativePath':str(native),'sha256':sha(native),'hostByteIdentical':True,'size':[1254,1254],'actualModel':None,'actualQuality':None,'sourceWorldBox':[12685,29581,13939,30835],'fullOutputAdopted':False},indent=2),encoding='utf-8')
base=Image.open(D/'edit-target.png').convert('RGB');raw=raw.convert('RGB')
# First conservative wide corridor trial: includes both changed intersections and full nearby endpoints.
poly=[(280,260),(1190,120),(1190,860),(760,1110),(720,1253),(600,1253),(90,1120),(90,700)]
mask=Image.new('L',(1254,1254));ImageDraw.Draw(mask).polygon(poly,fill=255)
trial=base.copy();trial.paste(raw,(0,0),mask);mask.save(D/'selection-mask-trial01.png');trial.save(D/'roi-trial01.png')
for name,box in {'upper':[250,200,1200,750],'lower':[100,650,1150,1220],'left':[0,650,300,1254],'bottom':[480,1040,820,1254],'right':[1070,100,1254,960],'upper-left':[180,160,480,420]}.items():trial.crop(box).save(D/('trial01-'+name+'.png'))
print({'sourceSha256':sha(native),'pixels':int((np.array(mask)==255).sum())})

