from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c01-v1");F=D/'final-v5';F.mkdir(exist_ok=True);Q=F/'qa';Q.mkdir(exist_ok=True)
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(Path(p).read_bytes()).hexdigest()}
J=np.array(Image.open(D/'final-v4/joined.png').convert('RGB'));W=np.array(Image.open(D/'wall-join-repair-v1/native.png').convert('RGB'));B=np.array(Image.open(D/'final-v2/joined.png').convert('RGB'));y,x=np.indices((1254,1254));smooth=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))
b=B[:1254].astype(float);w=W.astype(float);green=lambda a:smooth((a[:,:,1]-a[:,:,0]-1)/6)*smooth((a[:,:,1]-a[:,:,2]-1)/6)
leaf=np.maximum(green(b),green(w))*smooth((y-420)/30)
weight=smooth((x-970)/8)*(1-smooth((x-1192)/8))*(1-smooth((y-610)/40))*(1-leaf)
J[:1254]=np.rint(b*(1-weight[:,:,None])+w*weight[:,:,None]).astype(np.uint8)
C=np.zeros((2278,1254,4),np.uint8);C[:1254]=np.array(Image.open(D/'context.png').convert('RGBA'));prep=json.loads((D/'preparation.json').read_text(encoding='utf-8'));S=np.array(Image.open(prep['coupledBottom']['file']).convert('RGBA'));C[1139:,115:]=S[:1139,:1139]
yy,xx=np.indices((2278,1254));post=smooth((xx-1008)/32)*smooth((yy-690)/40);post=np.where(C[:,:,3]==255,post,0)
J=np.rint(J*(1-post[:,:,None])+C[:,:,:3]*post[:,:,None]).astype(np.uint8)
Image.fromarray(J).save(F/'joined.png');Image.fromarray(J[:1254]).save(F/'main1254.png');Image.fromarray(np.rint(weight*255).astype(np.uint8)).save(F/'wall-ownership.png');Image.fromarray(np.rint(post*255).astype(np.uint8)).save(F/'known-post-ownership.png')
for name,box in [('main1254',[0,0,1254,1254]),('lower-native',[0,1024,1254,2278]),('middle-overlap',[0,700,1254,1500]),('right-upper',[920,0,1254,1200]),('right-lower',[900,1024,1254,2278]),('left-perimeter',[105,1139,260,2278]),('return-tail',[0,2050,1254,2278])]:Image.fromarray(J).crop(box).save(Q/(name+'.png'))
asm=json.loads((D/'final-v4/assembly.json').read_text(encoding='utf-8'));asm.update({'output':ref(F/'joined.png'),'wallRepairWeight':ref(F/'wall-ownership.png'),'foregroundMatteStartsY':[420,450],'knownPostSourceOwnership':ref(F/'known-post-ownership.png'),'knownPostSource':prep['coupledBottom'],'knownPostContext':ref(D/'context.png'),'knownPostReason':'Preserve the complete actual known foreground white post and plants across the05/06 boundary, avoiding a source switch through the post itself.'});(F/'assembly.json').write_text(json.dumps(asm,indent=2),encoding='utf-8');print(json.dumps(ref(F/'joined.png')))

