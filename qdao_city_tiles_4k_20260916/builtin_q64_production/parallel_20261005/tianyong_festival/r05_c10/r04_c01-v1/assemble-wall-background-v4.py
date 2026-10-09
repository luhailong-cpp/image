from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c01-v1");F=D/'final-v4';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()}
J=np.array(Image.open(D/'final-v3/joined.png').convert('RGB'));base=np.array(Image.open(D/'final-v2/joined.png').convert('RGB'));R=np.array(Image.open(D/'wall-join-repair-v1/native.png').convert('RGB'))
# Preserve original native foreground leaves; choose native repaired background only behind them.
y,x=np.indices((1254,1254));smooth=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))
b=base[:1254].astype(float);a=R.astype(float)
greenB=smooth((b[:,:,1]-b[:,:,0]-1)/6)*smooth((b[:,:,1]-b[:,:,2]-1)/6)
greenR=smooth((a[:,:,1]-a[:,:,0]-1)/6)*smooth((a[:,:,1]-a[:,:,2]-1)/6)
w=smooth((x-970)/8)*(1-smooth((x-1192)/8))*(1-smooth((y-610)/40))*(1-np.maximum(greenB,greenR))
J[:1254]=np.rint(b*(1-w[:,:,None])+a*w[:,:,None]).astype(np.uint8);Image.fromarray(J).save(F/'joined.png');Image.fromarray(J[:1254]).save(F/'main1254.png');Image.fromarray(np.rint(w*255).astype(np.uint8)).save(F/'wall-background-native-ownership.png')
for name,box in [('main1254',[0,0,1254,1254]),('lower-native',[0,1024,1254,2278]),('middle-overlap',[0,700,1254,1500]),('right-upper',[920,0,1254,1200]),('right-lower',[900,1024,1254,2278]),('left-perimeter',[105,1139,260,2278]),('return-tail',[0,2050,1254,2278])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
asm=json.loads((D/'final-v3/assembly.json').read_text(encoding='utf-8'));asm.update({'output':ref(F/'joined.png'),'wallRepairWeight':ref(F/'wall-background-native-ownership.png'),'wallBackgroundOwnershipLTRB':[970,0,1200,650],'wallForegroundLeaves':'Original native foreground leaves kept; repaired native ivory background selected behind them. No foliage interpolation across object contours.','wallRepairSource':ref(D/'wall-join-repair-v1/native.png')});(F/'assembly.json').write_text(json.dumps(asm,indent=2),encoding='utf-8');print(json.dumps(ref(F/'joined.png')))

