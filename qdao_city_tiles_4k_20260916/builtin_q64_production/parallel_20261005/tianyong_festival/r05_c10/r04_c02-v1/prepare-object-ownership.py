from pathlib import Path
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c02-v1");B=D.parent
s=(B/"grid-assemble.py").read_text(encoding="utf-8").replace("F=D/'final-v1'","F=D/'final-v3'")
s=s.replace("cw=np.where(C[:,:,3]==255,cw,0)","leaf=1-smooth((x-450)/50);cw=cw*(1-leaf)+smooth((y-1080)/18)*leaf;cw=np.where(C[:,:,3]==255,cw,0)")
s=s.replace("'bottomSourceSmoothstepY':[1040,1200]","'bottomSourceSmoothstepY':[1040,1200],'leftObjectOwnership':{'xFullUntil':450,'xFadeTo':500,'nativeUntilY':1080,'sourceFromY':1098,'reason':'Transfer ownership in the flat tan gap between upper native bush and lower known-source bush, avoiding mixed object edges'}")
(D/"assemble-object-ownership.py").write_text(s,encoding="utf-8")

