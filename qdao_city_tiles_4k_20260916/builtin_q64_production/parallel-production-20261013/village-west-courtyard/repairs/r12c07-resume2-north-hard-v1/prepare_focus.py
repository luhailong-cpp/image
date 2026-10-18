from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
R=Path(__file__).parent;Q=R.parent.parent/'qa/r12c07-resume2-north-hard-v1'
j=json.loads((Q/'assembly.json').read_text(encoding='utf-8'));s=np.asarray(Image.open(j['context']['path']).convert('RGB'));n=np.asarray(Image.open(j['northAnchor']['path']).convert('RGB'));out=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for i,x in enumerate([1139,2163,3187]):
 a=n[3991:4211,x-256:x+256];b=s[115:515,x-256:x+256];im=np.concatenate([a,b]);p=Q/f'J{i+1:02d}-segment-junction-native.png';Image.fromarray(im).save(p);out.append({'id':f'J{i+1:02d}','path':p.as_posix(),'sha256':sha(p),'size':[512,620],'northContextBox':[x-256,3991,x+256,4211],'southContextBox':[x-256,115,x+256,515],'cropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(p))!=im,axis=2).sum())})
for ident,box in [('F03',[2163,105,3187,300]),('F04',[3520,115,3850,280])]:
 x0,y0,x1,y1=box;im=s[y0:y1,x0:x1];p=Q/f'{ident}-new-cut-focus-native.png';Image.fromarray(im).save(p);out.append({'id':ident,'path':p.as_posix(),'sha256':sha(p),'size':[x1-x0,y1-y0],'contextBox':box,'cropIdentityDifferentPixels':int(np.any(np.asarray(Image.open(p))!=im,axis=2).sum())})
(Q/'focus-inputs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(out,ensure_ascii=False))
