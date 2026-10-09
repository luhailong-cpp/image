from pathlib import Path
import sys,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;B=R.parent;sys.path.insert(0,str(B));import production as p
D=R/'repairs/external-root';D.mkdir(parents=True,exist_ok=True)
cur=p.read(B/'tiles/current/current-overrides.json')['tiles'];raw=R/'tiles/r11_c14-candidate.png';cur['r11_c14']={'file':str(raw),'sha256':p.sha(raw)}
def arr(t):
 s=cur[t];assert p.sha(s['file'])==s['sha256'];return np.asarray(Image.open(s['file']).convert('RGB'))
internal=np.asarray(Image.open(R/'repairs/internal/r11_c14-internal-candidate-v1.png').convert('RGB'));a=arr('r11_c14');assert np.array_equal(a[:627,:627],internal[:627,:627]);assert np.array_equal(a[:627,3469:],internal[:627,3469:])
for name,ts,origin in [('nw',['r10_c13','r10_c14','r11_c13','r11_c14'],[52621,40333]),('ne',['r10_c14','r10_c15','r11_c14','r11_c15'],[56717,40333])]:
 im=np.concatenate([np.concatenate([arr(ts[0])[3469:,3469:],arr(ts[1])[3469:,:627]],axis=1),np.concatenate([arr(ts[2])[:627,3469:],arr(ts[3])[:627,:627]],axis=1)],axis=0)
 f=D/f'{name}-corner-input.png';Image.fromarray(im).save(f);p.derived(f,[cur[t]['file'] for t in ts],{'method':'four native627-square quadrants at exact global coordinates; no resampling','globalOrigin':origin,'tileOrderNW_NE_SW_SE':ts})
 p.write(D/f'{name}-corner-state.json',{'sources':{t:cur[t] for t in ts},'order':ts,'globalOrigin':origin,'rawR11c14CornersEqualInternalV1':True,'formalAccepted':False})
print(D)
