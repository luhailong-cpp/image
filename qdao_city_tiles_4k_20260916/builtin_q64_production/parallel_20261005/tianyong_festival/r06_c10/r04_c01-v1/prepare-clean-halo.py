from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
save=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
ref=lambda p:{'file':str(p),'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()}
a=np.array(Image.open(D/'context.png').convert('RGBA')); a[1024:1139,280:410]=0;Image.fromarray(a).save(D/'context.png')
q=read(D/'request.json');q['knownPixels']=int((a[:,:,3]==255).sum());q['missingPixels']=int((a[:,:,3]==0).sum());q['payload']['referenced_image_paths'][3]=str(D.parent/'r04_c02-v1/final-v3/joined.png')
q['payload']['prompt']+='\nAt the TOP of this crop, continue the broad white stone flowerbed border seen at the right edge. The curb runs across the upper y0..145 with rounded clean bevels, a small hanging leafy tuft around x670..840/y0..110 and soft foliage shadows on the paving below it, precisely as the canonical layout. Fill the rest with warm ivory plaza slabs, preserving right seam endpoints y450 and y745, and the diagonal lower joint. The small transparent repair opening near x280..410/y1024..1139 removes a known triangular chip: paint one clean straight smooth diagonal slab edge there, no notch, no triangular crack or chip, even though the blurry layout has a tiny artifact. Keep the bottom two slab junctions and every right-edge contour at their exact positions. No added objects or lettering.'
q['excludedUnacceptedHaloLTRB']=[280,1024,410,1139];save(D/'request.json',q)
p=read(D/'preparation.json');p['references']=[ref(Path(f)) for f in q['payload']['referenced_image_paths']];p['excludedUnacceptedHaloLTRB']=[280,1024,410,1139];p['exclusionReason']='Unaccepted pointed notch in prior external halo, removed from the actual imagegen context for new native redraw. It is not committed r06 coverage.';save(D/'preparation.json',p)
save(D/'context.png.generation.json',{'operation':'native-source-context-composition-and-alpha-exclusion','sources':p['nativeInputs'],'excludedUnacceptedHaloLTRB':[280,1024,410,1139],'noResampling':True,'output':ref(D/'context.png')})
print(json.dumps(q))
