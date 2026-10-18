from workflow import *
from PIL import Image
import numpy as np,re,subprocess,sys
jobs=[]
tid='r08_c13';rev='root-full-20261016-v02';sp=read(ROOT/'qa/r08_c13-root-full-20261016-v01.spec.json');f=ROOT/'native/r08_c13_pillar_joint_whole_v01.png'
mf=ROOT/'qa'/f'{tid}-{rev}.overlays.json';write(mf,{'tile':tid,'overlays':[{'file':str(f),'sha256':sha(f),'sourceCrop':[115,115,1139,1139],'destinationBox':[512,1536,1536,2560]}]});sp['overlayManifests']=[str(mf)];spec=ROOT/'qa'/f'{tid}-{rev}.spec.json';write(spec,sp);jobs.append((spec,rev))
tid='r08_c12';rev='v16-foliage-20261016';base=ROOT/'tiles/r08_c12.candidate-v15.png';m=read(Path(str(base)+'.generation.json'));assert sha(base)==m['sha256']
im=Image.new('RGB',(4096,4096));vv={}
for e in m['contributions']:
 f=Path(e['file']);assert sha(f)==e['sha256'];match=re.search(r'_p(\d\d)_(v\d+)\.png$',f.name);rc,v=match.groups();vv[rc]=v
 r,c=map(int,rc);assert e['sourceCrop']==[115,115,1139,1139] and e['destinationBox']==[(c-1)*1024,(r-1)*1024,c*1024,r*1024]
 im.paste(Image.open(f).convert('RGB').crop(e['sourceCrop']),tuple(e['destinationBox'][:2]))
for e in m['repairOverlays']:
 f=Path(e['file']);assert sha(f)==e['sha256'];im.paste(Image.open(f).convert('RGB').crop(e['sourceCrop']),tuple(e['destinationBox'][:2]))
assert np.array_equal(np.array(im),np.array(Image.open(base).convert('RGB'))),'Legacy source reconstruction differs'
f=ROOT/'native/r08_c12_foliage_whole_v01.png';overlays=[dict(e) for e in m['repairOverlays']]+[{'file':str(f),'sha256':sha(f),'sourceCrop':[115,115,1139,1139],'destinationBox':[3072,3072,4096,4096]}]
mf=ROOT/'qa'/f'{tid}-{rev}.overlays.json';write(mf,{'tile':tid,'baseCandidate':str(base),'baseSha256':sha(base),'legacyReplayMismatch':0,'overlays':overlays});spec=ROOT/'qa'/f'{tid}-{rev}.spec.json';write(spec,{'tile':tid,'patchVersions':vv,'overlayManifests':[str(mf)]});jobs.append((spec,rev))
for spec,rev in jobs:
 subprocess.run([sys.executable,str(ROOT/'assemble_native_overlay_candidate_20261012.py'),str(spec),rev],check=True)
 subprocess.run([sys.executable,str(ROOT/'qa_from_candidate.py'),str(spec),rev],check=True)
