from pathlib import Path
import json,hashlib,shutil
from datetime import datetime, timezone
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
B=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def info(p):
 im=Image.open(p);return {'file':str(p),'sha256':sha(p),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode}
out=Path('C:/Users/luyua/.codex/generated_images/01a1117d-169b-76c0-a92c-248983c1a1b7/exec-e4a42ca9-0c9a-45fd-a852-451b630c5f03.png')
(B/'native').mkdir(exist_ok=True)
shutil.copy2(out,B/'native/southwest-cap1254.png')
native=B/'native/southwest-cap1254.png'
target=B/'inputs/southwest-cap1254.png'
a=np.array(Image.open(target).convert('RGB'));g=np.array(Image.open(native).convert('RGB'))
assert a.shape==g.shape==(1254,1254,3)
r,green,blue=[a[:,:,i].astype('int16') for i in range(3)]
# Exact source color selection only inside visually identified orange coping envelope.
# Excludes lantern footing at upper left, cream masonry, leaves and stems.
env=Image.new('L',(1254,1254),0);p=ImageDraw.Draw(env)
p.polygon([(205,845),(260,820),(438,788),(590,752),(745,642),(900,553),(909,441),(939,451),(997,520),(1030,556),(1075,607),(1085,697),(1051,732),(693,953),(538,1060),(322,1158),(239,1136)],fill=255)
surface=(r>green+18)&(green>blue+22)&((r-blue)>60)&(np.array(env)>0)
# Warm white bevel highlights occur strictly inside these existing orange cap faces.
safe=Image.new('L',(1254,1254),0);q=ImageDraw.Draw(safe)
q.polygon([(615,755),(927,562),(1006,625),(685,829)],fill=255)
q.polygon([(511,801),(601,760),(665,847),(573,896)],fill=255)
q.polygon([(272,837),(432,813),(472,885),(291,920)],fill=255)
q.polygon([(286,1017),(477,975),(481,1003),(288,1048)],fill=255)
surface |= (np.array(safe)>0)&(r>green)&(green>blue+16)
shadow=Image.new('L',(1254,1254),0);s=ImageDraw.Draw(shadow)
shadow_polygons=[[(1028,616),(1066,612),(1074,633),(1075,693),(1030,725)],[(467,835),(489,824),(507,891),(505,1036),(492,1060),(472,1024)],[(509,969),(548,1001),(573,1027),(534,1053),(509,1066)],[(319,1038),(478,1009),(486,1062),(413,1104),(337,1140),(316,1099)],[(478,1016),(501,1016),(500,1062),(480,1075)]]
for poly in shadow_polygons:s.polygon(poly,fill=255)
surface |= (np.array(shadow)>0)&(r>green+3)&(r>blue+10)
# Cover old cream highlight speckles only in already verified cap top-face interiors.
surface |= np.array(safe)>0
# Independent QA found781 leaf pixels crossed by one safe bevel polygon.
# Reapply a strict source-green exclusion after every manual support union.
green_protected=(green>r+3)&(green>blue+10)
removed_green=int(np.count_nonzero(surface&green_protected))
surface &= ~green_protected
mask=Image.fromarray(surface.astype('uint8')*255)
# Alpha edge remains inside eligible surface: no dilation, translation, warp or resampling.
eroded=mask.filter(ImageFilter.MinFilter(3)); alpha=np.where(surface,np.where(np.array(eroded)>0,255,160),0).astype('uint8')
mix=np.round(g.astype('float32')*(alpha[:,:,None]/255)+a.astype('float32')*(1-alpha[:,:,None]/255)).astype('uint8')
assert np.array_equal(mix[~surface],a[~surface])
(B/'masks').mkdir(exist_ok=True);(B/'candidate').mkdir(exist_ok=True);(B/'qa').mkdir(exist_ok=True)
Image.fromarray(alpha).save(B/'masks/southwest-alpha1254.png')
Image.fromarray(mix).save(B/'candidate/southwest-composite1254.png')
overlay=a.copy();overlay[surface]=np.round(a[surface]*.4+np.array([255,0,200])*.6).astype('uint8')
Image.fromarray(overlay).save(B/'qa/southwest-mask-overlay1254.png')
record={**info(native),'generatedAt':datetime.fromtimestamp(out.stat().st_mtime,timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((B/'config-snapshot.json').read_text()),'submittedParameters':{'model':None,'quality':None,'referenced_image_paths':[str(target),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露／无可核实元数据','evidence':{'receipt':str(B/'southwest-cap.receipt.json'),'receiptSha256':sha(B/'southwest-cap.receipt.json'),'originalOutputPath':str(out),'originalOutputSha256':sha(out)},'prompt':str(B/'southwest-cap.prompt.txt'),'promptSha256':sha(B/'southwest-cap.prompt.txt'),'references':[{'file':str(target),'sha256':sha(target),'role':'Actual viewed native edit target from day core crop [700,2800,1954,4054]'}, {'file':'D:/work/image/designs/gameplay-ui/04-guild.png','sha256':sha('D:/work/image/designs/gameplay-ui/04-guild.png'),'role':'Actually viewed and attached primary approved style reference'}]}
write(B/'native/southwest-cap1254.png.generation.json',record)
write(B/'masks/southwest-mask-recipe.json',{'envelopePolygon':[(205,845),(260,820),(438,788),(590,752),(745,642),(900,553),(909,441),(939,451),(997,520),(1030,556),(1075,607),(1085,697),(1051,732),(693,953),(538,1060),(322,1158),(239,1136)],'sourceThreshold':'R>G+18 and G>B+22 and R>B+60','safeSurfaceHighlightPolygons':True,'safeShadowPolygons':shadow_polygons,'shadowThreshold':'R>G+3 and R>B+10 excludes green foliage','finalSourceGreenExclusion':'G>R+3 and G>B+10 after all polygon unions','independentQALeafSpillRemovedPixels':removed_green,'alpha':'inside only:255 eroded interior;160 eligible one-pixel boundary;0 outside','maskPixels':int(surface.sum()),'outsideMaskByteEqual':True,'cropCoreLTRB':[700,2800,1954,4054]})
print(json.dumps({'maskPixels':int(surface.sum()),'changedPixels':int(np.any(a!=mix,axis=2).sum()),'native':info(native)}))
