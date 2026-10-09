from pathlib import Path
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c02-v1");B=D.parent
s=(B/"grid-assemble.py").read_text(encoding="utf-8").replace("F=D/'final-v1'","F=D/'final-v2'")
s=s.replace("cw=np.where(C[:,:,3]==255,cw,0)","cw=np.maximum(cw,smooth((y-1040)/40)*(1-smooth((x-450)/50)));cw=np.where(C[:,:,3]==255,cw,0)")
s=s.replace("'bottomSourceSmoothstepY':[1040,1200]","'bottomSourceSmoothstepY':[1040,1200],'leftFoliageSourcePreference':{'xFullUntil':450,'xFadeTo':500,'ySmoothstep':[1040,1080],'reason':'Restore exact known lower-left leaves and wall without soft duplicate contours'}")
(D/"assemble-known-foliage.py").write_text(s,encoding="utf-8")

