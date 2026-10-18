from workflow import *
tid='r14_c13';rev='right-full-20261016-v03';m=read(ROOT/'qa/r14_c13-right-full-20261016-v02.overlays.json');f=ROOT/'native/r14_c13_repair_p32edge_v01.png';m['overlays'].append({'file':str(f),'sha256':sha(f),'sourceCrop':[115,115,1139,1139],'destinationBox':[1421,2048,2445,3072]});mp=ROOT/'qa'/f'{tid}-{rev}.overlays.json';write(mp,m);spec=read(ROOT/'qa/r14_c13-right-full-20261016-v02.spec.json');spec['overlayManifests']=[str(mp)];write(ROOT/'qa'/f'{tid}-{rev}.spec.json',spec)

