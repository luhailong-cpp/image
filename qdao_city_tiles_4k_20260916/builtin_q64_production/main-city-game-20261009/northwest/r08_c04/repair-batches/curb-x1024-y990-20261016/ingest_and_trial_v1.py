from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json,shutil
D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/curb-x1024-y990-20261016')
host=Path(r'C:/Users/luyua/.codex/generated_images/01a142ef-b2f7-7e30-9d4f-545e2c80f42f/exec-4ba8a35b-f7fc-4fde-9904-e55344f2a28f.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=D/'native.png';assert not out.exists();shutil.copyfile(host,out);assert sha(out)==sha(host)
raw=Image.open(out);assert raw.size==(1254,1254)
assert 'A' not in raw.getbands() or raw.getchannel('A').getextrema()==(255,255)
(D/'generation.json').write_text(json.dumps({'tool':'image_gen__imagegen','hostPath':str(host),'nativePath':str(out),'sha256':sha(out),'hostByteIdentical':True,'size':[1254,1254],'actualModel':None,'actualQuality':None,'sourceWorldBox':[12685,29069,13939,30323],'fullOutputAdopted':False},indent=2),encoding='utf-8')
base=Image.open(D/'edit-target.png').convert('RGB');raw=raw.convert('RGB')
roi=[480,470,820,735];x0,y0,x1,y1=roi
trial=base.copy();trial.paste(raw.crop(roi),roi[:2]);trial.save(D/'roi-trial-v1.png')
mask=np.zeros((1254,1254),np.uint8);mask[y0:y1,x0:x1]=255;Image.fromarray(mask).save(D/'selection-mask-v1.png')
for name,box in [('detail',[400,420,900,800]),('north',[x0-20,y0-35,x1+20,y0+35]),('south',[x0-20,y1-35,x1+20,y1+35]),('west',[x0-35,y0-20,x0+35,y1+20]),('east',[x1-35,y0-20,x1+35,y1+20])]:trial.crop(box).save(D/('v1-'+name+'.png'))
print({'sourceSha256':sha(out),'nativeSize':raw.size,'trial':'roi-trial-v1.png'})

