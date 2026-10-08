from pathlib import Path
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent
n=np.array(Image.open(O/'native.png').convert('RGB'));b=np.array(Image.open(O.parent/'final-registration-v1/joined.png'))
b[:300,230:300]=n[:300,230:300]
Image.fromarray(b).save(O/'naive.png');Image.fromarray(b).crop((170,0,410,380)).save(O/'naive-upper.png')
