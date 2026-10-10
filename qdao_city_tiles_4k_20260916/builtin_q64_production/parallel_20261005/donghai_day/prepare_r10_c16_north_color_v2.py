from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'repair_r10_c16_north_color.py').read_text().replace("D=T/'repairs/north-integrated-color'","D=T/'repairs/north-integrated-color-v2'")
s=s.replace(" else:soft=smooth(alpha,33,2)\n corr=",''' else:
  soft=smooth(alpha,33,2)
  xx=np.minimum(np.arange(alpha.shape[1]),np.arange(alpha.shape[1])[::-1]);yy=np.arange(alpha.shape[0])[::-1]
  ramp=np.minimum(np.clip(xx[None,:]/160,0,1),np.clip(yy[:,None]/160,0,1));ramp=ramp*ramp*(3-2*ramp)
  rf=raw.astype(np.float32);blue=np.clip((rf[:,:,2]-rf[:,:,0]-10)/25,0,1)*np.clip((rf[:,:,1]-rf[:,:,0])/20,0,1)
  soft=soft*(1-blue)+ramp*blue
 corr=''' )
(p/'repair_r10_c16_north_color_v2.py').write_text(s,encoding='utf-8')
