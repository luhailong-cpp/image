"""Native lower-three-row QA while the north source is still being finalized."""
from pathlib import Path
import numpy as np
from PIL import Image
import assembly_r11_c16 as a
D=a.TILE/'qa/lower-only';a.MASKS=D/'masks'
arrays,entries,missing=a.load_sources();assert len(entries)==12 and set(missing)=={f'r01_c{c:02d}' for c in range(1,5)}
fn=a.load_seam_function();rows=[];seams=[]
for r in [2,3,4]:
 v=arrays[r,1]
 for c in [2,3,4]:
  v,s=a.append(v,arrays[r,c],fn,f'vertical_r{r:02d}_c{c-1:02d}_c{c:02d}','vertical',[(c-1)*1024,(r-1)*1024,230,1254]);seams.append(s)
 rows.append(v)
v=rows[0]
for r in [3,4]:
 v,s=a.append(v.transpose(1,0,2),rows[r-2].transpose(1,0,2),fn,f'horizontal_r{r-1:02d}_r{r:02d}','horizontal',[0,(r-1)*1024,4326,230]);v=v.transpose(1,0,2);seams.append(s)
im=Image.fromarray(v).crop((115,115,4211,3187));assert im.size==(4096,3072)
fi=a.save_image(D/'native-lower3072.png',im);sheets=[]
for y in [2048,3072]:
 for x in [1024,2048,3072]:
  q=a.save_image(D/f'intersection-x{x}-y{y}.png',im.crop((x-256,y-1024-256,x+256,y-1024+256)));sheets.append(q)
for y in [2048,3072]:
 band=im.crop((0,y-1024-128,4096,y-1024+128));sheet=Image.new('RGB',(1024,1024))
 for i in range(4):sheet.paste(band.crop((i*1024,0,(i+1)*1024,256)),(0,i*256))
 sheets.append(a.save_image(D/f'internal-horizontal-y{y}-full.png',sheet))
for x in [1024,2048,3072]:
 band=im.crop((x-128,256,x+128,3072));sheet=Image.new('RGB',(768,1024),(28,28,28))
 for i in range(3):
  h=min(1024,2816-i*1024);sheet.paste(band.crop((0,i*1024,256,i*1024+h)),(i*256,0))
 sheets.append(a.save_image(D/f'internal-vertical-x{x}-y1280-4096.png',sheet))
preview=a.save_image(D/'overview-lower-only.png',im.resize((1024,768),Image.Resampling.LANCZOS))
a.save_json(D/'manifest.json',{'createdAtUtc':a.utc_now(),'kind':'partial-lower-only-native-assembly-for-QA','notCompleteTile':True,'finalCoreRectXYWH':[0,1024,4096,3072],'futureTopRowMayChangeRows':[909,1139],'source':fi,'sources':entries,'missing':missing,'seams':seams,'qa':sheets,'preview':preview,'visualReview':'pending','formalAccepted':False})
print(fi)
