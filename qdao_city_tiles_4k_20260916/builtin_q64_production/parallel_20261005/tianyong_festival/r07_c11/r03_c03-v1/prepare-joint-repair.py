from pathlib import Path
from PIL import Image
import numpy as np,shutil,json,hashlib
D=Path(__file__).parent
src=Path('C:/Users/luyua/.codex/generated_images/01a11b00-53b8-70a3-bc9b-96606ec052ee/exec-7d263b94-e281-46e3-8ea3-f2985b65b66b.png');shutil.copy2(src,D/'repair-1-native.png')
a=np.asarray(Image.open(D/'native-original.png').convert('RGBA')).copy();b=np.asarray(Image.open(src).convert('RGBA'));a[470:560,870:940]=b[470:560,870:940];a[985:1090,415:1110]=0;Image.fromarray(a).save(D/'joint-repair-context.png')
print('Prepared exact native transparent joint repair [415,985,1110,1090]')
