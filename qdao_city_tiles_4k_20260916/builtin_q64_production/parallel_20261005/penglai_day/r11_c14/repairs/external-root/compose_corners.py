import corner_tools as h
import numpy as np
from PIL import Image
O=h.O;p=h.p
h.ingest('nw-corner-v2')
for name,version in [('nw','v2'),('ne','v1')]:
 source=O/f'{name}-corner-input.png';ai=O/'native'/f'{name}-corner-{version}.png';a=np.asarray(Image.open(source).convert('RGB'));b=np.asarray(Image.open(ai).convert('RGB'));assert a.shape==b.shape==(1254,1254,3)
 y,x=np.indices((1254,1254));alpha=np.clip(np.minimum(np.minimum(x-70,1183-x),np.minimum(y-70,1183-y))/48,0,1).astype('float32');out=np.rint(a*(1-alpha[:,:,None])+b*alpha[:,:,None]).clip(0,255).astype('uint8')
 mask=O/f'{name}-corner-alpha.npz';np.savez_compressed(mask,alpha=alpha);f=O/f'{name}-corner-composite-v1.png';Image.fromarray(out).save(f);p.derived(f,[source,ai],{'method':'native1254 corner repair, outer70 unchanged,48px return transition; no resampling','mask':str(mask),'maskSha256':p.sha(mask),'formalAccepted':False})
 state=p.read(O/f'{name}-corner-state.json');state.update(composite=str(f),compositeSha256=p.sha(f),mask=str(mask),maskSha256=p.sha(mask),visualReview='pending');p.write(O/f'{name}-corner-output.json',state)
 print(name,p.sha(f))
