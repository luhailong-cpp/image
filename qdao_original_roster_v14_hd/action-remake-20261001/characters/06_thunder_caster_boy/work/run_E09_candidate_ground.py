from PIL import Image
import statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for v in [7,8]:
 im=Image.open(ROOT/'work'/f'run_E_09_v{v}.png').resize((901,901),Image.Resampling.LANCZOS)
 bg=Image.new('RGBA',(1024,1024));bg.alpha_composite(im,(61,97))
 a=bg.getchannel('A');vals=[]
 for x in range(575,690):
  ys=[y for y in range(900,985) if a.getpixel((x,y))>=128]
  if ys:vals.append(max(ys))
 print(v, min(vals),statistics.median(vals),max(vals))

