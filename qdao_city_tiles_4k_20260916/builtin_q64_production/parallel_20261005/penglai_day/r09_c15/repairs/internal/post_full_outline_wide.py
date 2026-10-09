import sys
sys.dont_write_bytecode=True
from PIL import Image,ImageDraw
import numpy as np
import ai_helper as h
O=h.O
a=Image.open(O/'post-edit-input.png').convert('RGB');g=Image.open(O/'post-ai-v1-generated.png').convert('RGB');pix=np.asarray(g).astype('float32');m=Image.new('L',(1254,1254));d=ImageDraw.Draw(m)
for side,yrange in [('left',(220,1190)),('right',(235,775))]:
 for y in range(*yrange):
  expected=(536-(y-220)*.026) if side=='left' else (731-(y-235)*.031)
  lo=int(expected-8);hi=int(expected+9);e=lo+int(np.argmax(np.mean(abs(np.diff(pix[y,lo:hi],axis=0)),axis=1)));d.line((e-7,y,e+8,y),fill=255)
mp=O/'post-full-outline-wide-mask.png';m.save(mp);h.derived(mp,[O/'post-ai-v1-generated.png'],{'method':'native16pixel AI outline ownership corridor along full visible post outlines to natural rope/base endpoints','leftY':[220,1190],'rightY':[235,775],'noGeometryWarp':True})
src=O/'r09_c15-internal-candidate-v6.png';im=Image.open(src).convert('RGB')
oldm=np.maximum(np.asarray(Image.open(O/'postleft-v4-mask.png')),np.asarray(Image.open(O/'postright-v4-mask.png')));im.paste(a,(397,1421),Image.fromarray(oldm));im.paste(g,(397,1421),m)
p=O/'r09_c15-internal-candidate-v8.png';im.save(p);h.derived(p,[src,O/'post-edit-input.png',O/'postleft-v4-mask.png',O/'postright-v4-mask.png',O/'post-ai-v1-generated.png',mp],{'method':'replace rejected finite-height outline masks with native entire-outline corridors','noResampling':True,'imageBlur':False})
base=O/'r09_c15-west-joint-candidate-final2.png';out=Image.open(base).convert('RGB');patch=im.crop((397,1421,1651,2675));union=Image.fromarray(np.maximum(oldm,np.asarray(m)));out.paste(patch,(397,1421),union)
f=O/'r09_c15-local-candidate-final-v2.png';out.save(f);h.derived(f,[base,p,mp,O/'postleft-v4-mask.png',O/'postright-v4-mask.png'],{'method':'exact post-outline delta onto western repaired candidate','noResampling':True,'imageBlur':False})
qa=O/'qa-post-full-outline-wide.png';out.crop((880,1950,1200,2200)).save(qa);h.derived(qa,[f],{'method':'native320x250 detail'})

