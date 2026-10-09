from pathlib import Path
p=Path('repair_r10_c15_north_right_color_v2.py');s=p.read_text()
s=s.replace('repairs/north-right-color-v2','repairs/north-right-color-v3')
s=s.replace("short=np.clip(1-np.arange(h,dtype=np.float32)/48,0,1);short=short*short*(3-2*short)","short=np.clip(1-np.arange(h,dtype=np.float32)/48,0,1);short=short*short*(3-2*short)\nfine=np.clip((np.arange(w,dtype=np.float32)+x0-3260)/20,0,1)*np.clip((3600-np.arange(w,dtype=np.float32)-x0)/40,0,1)")
s=s.replace("short[:,None,None]*(exactEdge-edge)[None,:,:]","short[:,None,None]*(exactEdge-edge)[None,:,:]*fine[None,:,None]")
s=s.replace("'bounded per-column actual row RGB residual, smooth 48px vertical decay; artwork not resampled'","'bounded per-column actual row RGB residual only within post x3260..3600, smooth 48px vertical decay, horizontal20/40px fade; artwork not resampled'")
Path('repair_r10_c15_north_right_color_v3.py').write_text(s)

