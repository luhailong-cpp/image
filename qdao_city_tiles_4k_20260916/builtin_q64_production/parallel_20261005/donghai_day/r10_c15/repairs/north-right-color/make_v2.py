from pathlib import Path
p=Path('repair_r10_c15_north_right_color.py')
s=p.read_text(encoding='utf-8-sig').replace("repairs/north-right-color","repairs/north-right-color-v2")
s=s.replace("edge=np.clip(smooth(edge),-32,32)","edge=np.clip(smooth(edge),-32,32)\nexactEdge=np.clip(north[-1,x0:].astype(np.float32)-base[0,x0:].astype(np.float32),-32,32)")
s=s.replace("field=y[:,None,None]*x[None,:,None]*edge[None,:,:]","short=np.clip(1-np.arange(h,dtype=np.float32)/48,0,1);short=short*short*(3-2*short)\nfield=(y[:,None,None]*edge[None,:,:]+short[:,None,None]*(exactEdge-edge)[None,:,:])*x[None,:,None]")
s=s.replace("field*=material[:,:,None]","field=np.clip(field*material[:,:,None],-32,32)")
s=s.replace("'material':'continuous warm R-B weight; no hard class boundary'","'material':'continuous warm R-B weight; no hard class boundary','exactBoundaryResidual':'bounded per-column actual row RGB residual, smooth 48px vertical decay; artwork not resampled'")
Path('repair_r10_c15_north_right_color_v2.py').write_text(s,encoding='utf-8')

