"""Correct only lower native overlaps while preserving their original geometry masks."""
from pathlib import Path
import numpy as np
from PIL import Image
import assembly_r11_c16 as a
import repair_r09_c16_color as f
R=Path(__file__).resolve().parent;B=a.TILE/'qa/lower-only';D=a.TILE/'repairs/lower-color-v1'
f.a=a;f.DEST=D;f.MASKS=B/'masks';f.CAP=32;f.infos=[]
def lowpass(v):
 for _ in range(3):
  for axis in [0,1]:
   pad=[(0,0),(0,0)];pad[axis]=(8,8);p=np.pad(v,pad,mode='reflect');c=np.cumsum(p,axis=axis,dtype=np.float64);c=np.concatenate((np.take(c,[0],axis=axis)*0,c),axis=axis);v=(c[17:]-c[:-17])/17 if axis==0 else (c[:,17:]-c[:,:-17])/17
 return v.astype(np.float32)
f.lowpass=lowpass
def raw_append(base,inc,label,orientation):
 with np.load(f.MASKS/(label+'.npz')) as z:alpha=z['alpha_u8'].copy()
 if orientation=='horizontal':alpha=alpha.T
 return np.concatenate((base[:,:-230],a.blend(base[:,-230:],inc[:,:230],alpha),inc[:,230:]),axis=1)
def assemble(arrays,append):
 rows=[]
 for r in [2,3,4]:
  v=arrays[r,1]
  for c in [2,3,4]:v=append(v,arrays[r,c],f'vertical_r{r:02d}_c{c-1:02d}_c{c:02d}','vertical')
  rows.append(v)
 v=rows[0]
 for r in [3,4]:v=append(v.transpose(1,0,2),rows[r-2].transpose(1,0,2),f'horizontal_r{r-1:02d}_r{r:02d}','horizontal').transpose(1,0,2)
 return v
def main():
 arrays,entries,missing=a.load_sources();assert len(entries)>=12
 raw=assemble(arrays,raw_append);base=raw[115:3187,115:4211]
 with Image.open(B/'native-lower3072.png') as im:assert np.array_equal(base,np.asarray(im))
 corrected=assemble(arrays,f.append)[115:3187,115:4211]
 delta=np.clip(corrected.astype(np.int16)-base.astype(np.int16),-32,32)
 # Full-row-1 assembly can only change through core y1139; keep y<1280 immutable.
 y=np.arange(3072)+1024;fade=np.clip((y-1280)/128,0,1);fade=fade*fade*(3-2*fade)
 delta=np.rint(delta*fade[:,None,None]).astype(np.int16)
 final=np.clip(base.astype(np.int16)+delta,0,255).astype(np.uint8);delta=final.astype(np.int16)-base.astype(np.int16)
 assert np.array_equal(final[:256],base[:256])
 out=a.save_image(D/'native-lower3072.png',Image.fromarray(final));fp=a.writable(D/'fields/final-lower-correction.npz');np.savez_compressed(fp,correction_rgb_i16=delta,core_rect_xywh=np.array([0,1024,4096,3072]))
 Q=D/'qa';sheets=[]
 im=Image.fromarray(final)
 for y in [2048,3072]:
  for x in [1024,2048,3072]:sheets.append(a.save_image(Q/f'intersection-x{x}-y{y}.png',im.crop((x-256,y-1280,x+256,y-768))))
 for y in [2048,3072]:
  band=im.crop((0,y-1152,4096,y-896));sheet=Image.new('RGB',(1024,1024))
  for i in range(4):sheet.paste(band.crop((i*1024,0,(i+1)*1024,256)),(0,i*256))
  sheets.append(a.save_image(Q/f'internal-horizontal-y{y}-full.png',sheet))
 for x in [1024,2048,3072]:
  band=im.crop((x-128,256,x+128,3072));sheet=Image.new('RGB',(768,1024),(28,28,28))
  for i in range(3):sheet.paste(band.crop((0,i*1024,256,min(2816,(i+1)*1024))),(i*256,0))
  sheets.append(a.save_image(Q/f'internal-vertical-x{x}-y1280-4096.png',sheet))
 preview=a.save_image(Q/'overview-lower-only.png',im.resize((1024,768),Image.Resampling.LANCZOS))
 a.save_json(D/'manifest.json',{'createdAtUtc':a.utc_now(),'kind':'partial-lower-only-color-correction','notCompleteTile':True,'candidate':out,'baseline':{'file':str(B/'native-lower3072.png'),'sha256':a.sha(B/'native-lower3072.png')},'coreRectXYWH':[0,1024,4096,3072],'coreRowsBelow1280Unchanged':True,'northTransitionRows':[1280,1408],'sources':entries,'method':'Fixed original two-pixel DP geometry masks with material-agreement-weighted continuous normalized RGB difference fields, 17px three-pass separable smoothing; art itself is never blurred/resampled. Only overlap pixels change.','maxChannelCorrection':int(np.abs(delta).max()),'fields':f.infos,'finalCorrection':{'file':str(fp),'sha256':a.sha(fp)},'qa':sheets,'preview':preview,'visualReview':'pending','formalAccepted':False})
 print(out)
if __name__=='__main__':main()
