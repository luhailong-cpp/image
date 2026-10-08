from PIL import Image
from pathlib import Path
import numpy as np,json
O=Path(__file__).resolve().parent
n=np.array(Image.open(O.parent/'r03_c03-repair-v1/native.png').convert('RGB'));c=np.array(Image.open(O/'context.png').convert('RGBA'));known=c[:,:,3]==255
j=n.copy();j[known]=c[:,:,:3][known];Image.fromarray(j).save(O/'naive-current-context.png')
for name,b in [('left',(100,0,350,1100)),('bottom',(0,925,1254,1155)),('right',(930,0,1160,1254)),('cross',(130,600,570,900))]:Image.fromarray(j).crop(b).save(O/(name+'.png'))
