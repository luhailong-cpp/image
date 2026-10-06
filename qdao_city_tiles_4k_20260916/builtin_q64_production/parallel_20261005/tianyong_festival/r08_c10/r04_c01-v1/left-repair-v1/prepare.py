from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;P=O.parent;R=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(n,o):
 with (O/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
base=P/'registration-v1/joined-r04_c01.png'
assert sha(base)=='b9fb28e7b67fbc085523ec5e345296f33d475f6c59a9d59afc0603bb5a3599a2'
a=np.asarray(Image.open(base).convert('RGBA')).copy();m=Image.new('L',(1254,1254),0);d=ImageDraw.Draw(m)
d.polygon([(85,460),(190,460),(200,790),(225,810),(150,980),(40,980),(75,830)],fill=255)
mask=np.asarray(m)>0;a[mask]=[0,0,0,0]
Image.fromarray(a).save(O/'context.png');m.save(O/'repair-mask.png')
shutil.copy2(P/'layout-reference-only.png',O/'layout-reference-only.png')
refs=[O/'context.png',O/'layout-reference-only.png',R/'designs/gameplay-ui/04-guild.png']
prompt='''Use case: precise-object-edit. This is a surgical seam repair of a finished native1254x1254 game map tile. Inpaint ONLY the small narrow transparent strip near the LEFT edge in image1, and return the same opaque1254-square image. All other image1 pixels are completed artwork and must remain exactly in position and unchanged.
The hole crosses only the left warm ivory stone face and its narrow bright-white rounded edge near its lower corner. Repaint this short connection so there is NO straight vertical rectangular patch boundary near x115, and NO tiny jog where the existing bright edge crosses x115 around y910. Connect the already visible white edge smoothly through the hole using the visible ORIGINAL curve on the left of the hole as an exact endpoint/tangent anchor. Make one continuous thin white highlight with the same thickness, dark bevel and soft warm stone material. Do not copy the old vertical patch artifact. Match the subtle texture from both sides gradually with no visible strip. This is a surface/seam repair, not a new stone or new seam.
The big central warm slab, wide diagonal ivory cross-band, lower quiet gray slab, both main sweeping ivory bands, floral detail and the entire right three quarters are already correct. Preserve them pixel-for-pixel. In particular do NOT move or redraw the bottom gray slab outline and do NOT change its bevel width. Keep all lower rows y1000..1254 as they are. Also leave the original small horizontal tone step near left y115 unchanged because it belongs to the existing source outside this repair.
Image2 is the canonical low-resolution LOCATION reminder only; no pixels from it may be enlarged into the output and it cannot override the precise native image1 geometry. Image3 is approved rendering style only: bright clean rounded Daoist fantasy Q-version game artwork. Do not import UI, text, characters, icons or frames.
No new objects, stone cuts, cracks, carved motifs, blur, camera move, scaling, rotation, whole-image recolor, border, watermark or text. The transparency is an editing hole only. Finish only that hole at highest host quality and retain1254x1254 native scale.'''
(O/'prompt.txt').write_text(prompt,encoding='utf8')
write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'AI redraw narrow left material seam and local white-edge jog','globalCropLTRB':[36749,31629,38003,32883],'tileLocalCropLTRB':[-115,2957,1139,4211],'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'configSnapshot':json.loads((R/'config/image-generation.json').read_text(encoding='utf8')),'submittedModel':None,'submittedQuality':None,'submittedSize':None,'repairPixels':int(mask.sum())})
write('preparation.json',{'base':info(base),'references':[{**info(p),'role':role} for p,role in zip(refs,['edit target; only narrow left seam missing','location only; forbidden final pixels','approved style'])],'repairMask':info(O/'repair-mask.png'),'nativeScale':1,'allWritesConfinedTo':str(O),'formalAccepted':False})
for p in [O/'context.png',O/'repair-mask.png',O/'layout-reference-only.png']:
 write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[info(base)] if p.name!='layout-reference-only.png' else [info(P/'layout-reference-only.png')],'operation':'Native mask preparation; no new generated pixels','newModelCalls':0,'nativeScale':1})
print(json.dumps({'references':[str(p) for p in refs],'repairPixels':int(mask.sum())}))
