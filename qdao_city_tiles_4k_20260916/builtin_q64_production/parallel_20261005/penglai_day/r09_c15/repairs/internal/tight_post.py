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
ImageDraw.Draw(m).polygon([(519,610),(536,610),(537,710),(518,710)],fill=255)
mp=O/'rightpost-tight-mask.png';m.save(mp);h.derived(mp,[O/'rightpostedge-v4-mask.png'],{'method':'tight binary edge-only ownership, excludes both external diagonal rail boundaries','polygon':[(519,610),(536,610),(537,710),(518,710)]})
im.paste(gen,(2100,2445),m)
p=O/'r09_c15-internal-candidate-v5.png';im.save(p);h.derived(p,[base,O/'rightpost-edit-input.png',O/'rightpostedge-v4-mask.png',O/'rightpost-ai-v1-generated.png',mp],{'method':'replace wide rejected post-edge mask with narrow edge-only mask','noResampling':True,'noBlur':True,'outsideUnionMaskUnchanged':True})
qa=O/'qa-post-tight.png';im.crop((2550,2960,2880,3250)).save(qa);h.derived(qa,[p],{'method':'native330x290 detail'})

