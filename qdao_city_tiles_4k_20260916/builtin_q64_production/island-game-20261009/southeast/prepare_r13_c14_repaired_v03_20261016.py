from workflow import *
tid='r13_c14';rev='right-full-20261016-v03'
m={'tile':tid,'overlays':[]}
for name,crop,dest in [('repair_hull_v02',[115,115,1139,1139],[115,2560,1139,3584]),('repair_bowwater_v01',[115,115,1139,1139],[1536,1536,2560,2560])]:
 f=ROOT/'native'/f'{tid}_{name}.png';m['overlays'].append({'file':str(f),'sha256':sha(f),'sourceCrop':crop,'destinationBox':dest})
mp=ROOT/'qa'/f'{tid}-{rev}.overlays.json';write(mp,m)
s=read(ROOT/'qa/r13_c14-right-full-20261016-v01.spec.json');s['patchVersions']['21']='v02';s['overlayManifests']=[str(mp)];write(ROOT/'qa'/f'{tid}-{rev}.spec.json',s)

