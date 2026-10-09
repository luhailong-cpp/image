import sys
sys.dont_write_bytecode=True
import ai_helper as h
import quilt as q
import numpy as np
from PIL import Image
O=h.O
base=O/'r09_c15-internal-candidate-v4.png';im=Image.open(base).convert('RGB')
old=Image.open(O/'rightpost-edit-input.png').convert('RGB');oldmask=Image.open(O/'rightpostedge-v4-mask.png').convert('L');im.paste(old,(2100,2445),oldmask)
gen=Image.open(O/'rightpost-ai-v1-generated.png').convert('RGB')
m=Image.new('L',(1254,1254));from PIL import ImageDraw
pixels=np.asarray(gen).astype('float32');draw=ImageDraw.Draw(m)
for y in range(610,711):
 edge=518+int(np.argmax(np.mean(abs(np.diff(pixels[y,518:532],axis=0)),axis=1)));draw.line((edge-3,y,edge+4,y),fill=255)
mp=O/'rightpost-edgecorridor-mask.png';m.save(mp);h.derived(mp,[O/'rightpostedge-v4-mask.png'],{'method':'edgecorridor binary edge-only ownership, excludes both external diagonal rail boundaries','rangeY':[610,711],'edgeSearchX':[518,532],'width':8})
im.paste(gen,(2100,2445),m)
p=O/'r09_c15-internal-candidate-v6.png';im.save(p);h.derived(p,[base,O/'rightpost-edit-input.png',O/'rightpostedge-v4-mask.png',O/'rightpost-ai-v1-generated.png',mp],{'method':'replace wide rejected post-edge mask with eight-pixel native outline corridor','noResampling':True,'noBlur':True,'outsideUnionMaskUnchanged':True})
qa=O/'qa-post-edgecorridor.png';im.crop((2550,2960,2880,3250)).save(qa);h.derived(qa,[p],{'method':'native330x290 detail'})
