from pathlib import Path
import sys,json,numpy as np
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parent.parent;B=R.parent
sys.path.insert(0,str(R/'repairs/internal'));import ai_helper as h
from PIL import Image
for d in ['north','west']:(O/d).mkdir(parents=True,exist_ok=True)
j=json.loads((B/'repairs/corner-r09c14/integration-v1.json').read_text(encoding='utf8'))
src=R/'repairs/internal/r10_c15-internal-candidate-v4.png'
a=Image.open(src).convert('RGB');raw=Image.open(R/'tiles/r10_c15-candidate.png').convert('RGB')
assert np.array_equal(np.asarray(a.crop((0,0,627,627))),np.asarray(raw.crop((0,0,627,627))))
cp=Path(j['pendingSoutheast']['file']);assert h.sha(cp)==j['pendingSoutheast']['sha256']
a.paste(Image.open(cp).convert('RGB'),(0,0))
base=O/'r10_c15-with-corner-v1.png';a.save(base);h.derived(base,[src,cp],{'method':'exact627square already-composited root corner patch integer paste; no repeated alpha','boxLTRB':[0,0,627,627],'precondition':'internal627corner identical to original p11core confirmed','sourceResampling':False})
state={'base':{'file':str(base),'sha256':h.sha(base)},'rootCorner':j['pendingSoutheast'],'neighbors':{},'jointOrigins':{}}
for axis,tile in [('north','r09_c15'),('west','r10_c14')]:
 item=j['outputs'][tile];neighbor=Path(item['file']);assert h.sha(neighbor)==item['sha256'];state['neighbors'][axis]=item
 z=Image.open(neighbor).convert('RGB')
 if axis=='north':
  joint=Image.new('RGB',(4096,1254));joint.paste(z.crop((0,3469,4096,4096)),(0,0));joint.paste(a.crop((0,0,4096,627)),(0,627));origin=[57344,36237]
 else:
  joint=Image.new('RGB',(1254,4096));joint.paste(z.crop((3469,0,4096,4096)),(0,0));joint.paste(a.crop((0,0,627,4096)),(627,0));origin=[56717,36864]
 fp=O/(axis+'-joint-source.png');joint.save(fp);h.derived(fp,[neighbor,base],{'method':'exact native627+627 neighboring tile crop union','seam':627,'orientation':axis,'globalOrigin':origin})
 state['jointOrigins'][axis]=origin
 for k,s in enumerate([0,1024,2048,2842],1):
  crop=O/axis/(f'{axis}-{k}-source.png');box=(s,0,s+1254,1254) if axis=='north' else (0,s,1254,s+1254);joint.crop(box).save(crop);h.derived(crop,[fp],{'method':'exact native1254 joint crop','boxLTRB':box,'globalOrigin':[origin[0]+(s if axis=='north' else 0),origin[1]+(s if axis=='west' else 0)]})
 state[axis+'Patches']=[0,1024,2048,2842]
(O/'state-v1.json').write_text(json.dumps(state,indent=2),encoding='utf8')
print(base,h.sha(base))
