from repair import *
import numpy as np
from PIL import ImageDraw
old=np.array(Image.open(BASE).convert('RGB'))
newfile=TASK/'tiles/r09_c13-raw-candidate.png'
new=np.array(Image.open(newfile).convert('RGB'))
for seg in [2,3,4]:
    y0=(seg-1)*1024-115
    rows=np.clip(np.arange(y0,y0+1254),0,4095)
    im=Image.fromarray(np.concatenate([old[rows,3469:4096],new[rows,:627]],axis=1))
    p=R/f's{seg}-target-native.png'; im.save(p)
    derived(p,[BASE,newfile],{'method':'exact native crops and concatenation','globalOriginXY':[48525,32768+y0],'oldSourceX':[3469,4096],'newSourceX':[0,627],'tileYOrigin':y0,'boundaryClampIsReferenceOnly':True,'jointImageX':627,'resampling':None})
    gap=im.copy();ImageDraw.Draw(gap).rectangle((627,0,914,1253),fill=(255,0,255))
    p=R/f's{seg}-target-gap.png';gap.save(p)
    derived(p,[R/f's{seg}-target-native.png'],{'method':'explicit magenta edit mask','gapRectLTRB':[627,0,915,1254],'notProductionArt':True})
