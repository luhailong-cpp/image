from helper import *
import numpy as np
a=R/'output/r08_c12-south-candidate-v3.png';d=R/'output/r09_c12-north-candidate-v3.png'
full=Image.new('RGB',(4096,8192));full.paste(Image.open(a),(0,0));full.paste(Image.open(d),(0,4096))
dest=R/'references/return-trim-input.png';box=[1500,3000,2754,4254];full.crop(box).save(dest);p.derived(dest,[a,d],{'method':'exact native crop','combinedBoxLTRB':box,'globalOriginXY':[46556,31672]})
