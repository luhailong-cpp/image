from pathlib import Path
import json,hashlib,datetime
from PIL import Image
B=Path(__file__).resolve().parent
q=json.loads((B/'requests/r02_c04/s01_02-v003.json').read_text(encoding='utf-8'))
old=Image.open(B/'r02_c04/native/s01_02-v002.png').convert('RGB')
guide=Image.open(q['guide']['file']).convert('RGB')
# Reference construction only: approved low-resolution layout and actual selected cores.
# Remove all generated halo authority by starting from approved layout crop.
lay=Image.open(q['guide']['layout']).convert('RGB')
w=q['coordinates']['worldBoxWithHalo']
guide=lay.transform((1254,1254),Image.Transform.EXTENT,tuple(v*lay.width/65536 for v in w),resample=Image.Resampling.BICUBIC)
pix=guide.load();op=old.load()
for y in range(1254):
 for x in range(550):
  r,g,b=op[x,y]
  if g>r*.96 and g>b*1.3 and g>35:pix[x,y]=(r,g,b)
# Preserve a cropped tip identity in the guide, shifted to intended x705; not production pixels.
for y in range(165):
 for x in range(430,900):
  r,g,b=op[x,y]
  if r>g*1.25 and r>b*1.8:pix[x+28,y]=(r,g,b)
pastes=[]
for p in q['guide']['nativeContextPastes']:
 s=p['source']
 if s['role']!='selected_generated_batch_neighbor':continue
 sw=s['worldBox'];core=[sw[0]+115,sw[1]+115,sw[2]-115,sw[3]-115]
 x0,y0,x1,y1=max(w[0],core[0]),max(w[1],core[1]),min(w[2],core[2]),min(w[3],core[3])
 if x0>=x1 or y0>=y1:continue
 crop=[x0-sw[0],y0-sw[1],x1-sw[0],y1-sw[1]];xy=[x0-w[0],y0-w[1]]
 guide.paste(Image.open(s['file']).convert('RGB').crop(crop),xy)
 pastes.append({'source':s,'sourceCropLTRB':crop,'guidePasteXY':xy,'onlyActualCore':True})
slug='s01_02-correct-anchor-completion-v001';gp=B/'requests/r02_c04'/f'{slug}.guide.png';rp=gp.with_name(slug+'.json')
assert not gp.exists() and not rp.exists()
guide.save(gp)
q['prompt']='Use case: precise-object-edit. Output native1254 square opaque art. Image1 is a reference construction only: complete all BLURRED/unfinished wall regions with sharp native hand-painted detail; retain the sharp green foliage on left and the little red diamond bottom tip at top [705,151]. Image2 and3 STYLE ONLY; do not copy their UI. The sharp actual neighbor strip at RIGHT x1139..1253 fixes horizontal pale stone mortar at y215,420,625,830, stone cap y830..925, darker gray foundation below925. The actual BOTTOM strip y1139..1253 fixes the bottom course. Extend these exact existing lines seamlessly into the blank region, all the way left behind the green leaves. Do NOT keep blurred layout lines as geometry, ONLY sharp right/bottom references set course heights. Preserve narrow green leaf shapes. Keep the small red plaque tip only; no whole sign, no text. Unify hand-painted lighting and stone texture without rectangular masks, no honeycomb/scaly dots, no blur, no added objects, no change of scale or viewpoint. Every sharp boundary must flow naturally across x1139 and y1139, no course steps. Fill all1254 pixels with native detailed artwork.'
q['referenced_image_paths']=[str(gp),'D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png']
q['guide'].update(file=str(gp),sha256=hashlib.sha256(gp.read_bytes()).hexdigest(),productionNativeSource=False,guideOnly=True,nativeContextPastes=pastes,construction='approved enlarged layout plus actual neighbor cores, green leaf source mask and shifted bottom tip identity, all for guide only')
rp.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')
print(str(rp))

