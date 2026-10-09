from pathlib import Path
D=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10/r04_c04-v1"); B=D.parent
s=(B/"grid-assemble.py").read_text(encoding="utf-8")
s=s.replace("F=D/'final-v1'","F=D/'final-v2'")
s=s.replace("cw=np.where(C[:,:,3]==255,cw,0)","cw=np.maximum(cw,smooth((y-1024)/24)*smooth((x-780)/50));cw=np.where(C[:,:,3]==255,cw,0)")
s=s.replace("'bottomSourceSmoothstepY':[1040,1200]","'bottomSourceSmoothstepY':[1040,1200],'knownFoliageSourcePreference':{'xSmoothstep':[780,830],'ySmoothstep':[1024,1048],'reason':'Prefer exact original known leaf outlines to avoid soft duplicate leaves; no geometry or recoloring'}")
(D/"assemble-known-foliage.py").write_text(s,encoding="utf-8")

