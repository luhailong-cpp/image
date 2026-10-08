from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;T=P.parent.parent
ROOT=next(p for p in T.parents if (p/'config/image-generation.json').exists())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cp=read(T/'source-checkpoint.json');assert int(cp['version'][1:])>=12
assert not (P/'context.png').exists()
window=[-115,-115,1139,1139];world=[36749,28557,38003,29811]
canvas=Image.new('RGBA',(1254,1254),(0,0,0,0))
inputs=[]
def paste(r,b):
 assert sha(r['file'])==r['sha256']
 a=Image.open(r['file']).convert('RGBA');assert a.size==(b[2]-b[0],b[3]-b[1])
 l,t,rr,bb=max(b[0],window[0]),max(b[1],window[1]),min(b[2],window[2]),min(b[3],window[3])
 assert l<rr and t<bb
 incoming=a.crop((l-b[0],t-b[1],rr-b[0],bb-b[1]))
 orig=canvas.crop((l-window[0],t-window[1],rr-window[0],bb-window[1]))
 z,q=np.array(orig),np.array(incoming);known=(z[:,:,3]==255)&(q[:,:,3]==255)
 assert np.array_equal(z[known],q[known]),'Two sources disagree in shared world pixels'
 canvas.alpha_composite(incoming,(l-window[0],t-window[1]))
 inputs.append({**r,'tileLocalSourceLTRB':b})
paste(cp['fragment'],cp['fragment']['tileLocalLTRB'])
left=cp['coupledNeighbors']['r08_c09'];paste(left,[-4096,0,0,4096])
halo=T/'r08_c10/r01_c02-v1/registration-v1/joined.png'
paste(ref(halo),[909,-115,2163,1139])
canvas.save(P/'context.png')
aa=np.array(canvas);assert not aa[:115,:1024,3].any() and np.all(aa[:,1024:,3]==255)
assert np.all(aa[115:,:115,3]==255) and not aa[115:,115:1024,3].any()
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in world)).save(P/'layout-reference-only.png')
refs=[P/'context.png',P/'layout-reference-only.png',ROOT/'designs/gameplay-ui/04-guild.png']
prompt='''Use case: precise-object-edit / outpainting. Continue an exact native-detail crop of the original Daoist fantasy game 五行奇谈. Return one opaque 1254 by 1254 image, identical framing and scale to image 1.
Image 1 is the EDIT TARGET: authentic finished stone map pixels form narrow left and right strips, with transparent missing area in between. Keep ALL visible pixels as precisely as possible: edge positions, tangents, broad bevel widths, light/shadow and ivory/slate colors. Paint only the transparent missing area as the continuous same plaza surface. The left strip starts 115 pixels below the top. The right strip spans the full image height; neither boundary is an actual architectural edge.
Image 2 is the same-world canonical LAYOUT ONLY. It determines which broad plaza ring bands and existing carvings are in the missing area. Do not copy its blurred low-resolution pixels or accidental marks. Draw fresh sharp native detail while joining EXACTLY to both visible strips of image 1. The two sides belong to a single continuous map, never separate panels.
Image 3 is the primary approved STYLE ONLY: bright clean rounded full Q-style Daoist fantasy handpainted rendering; quiet warm ivory stone, fine restrained warm-gold shading, clean contours and gentle bevels. Do not import its UI, text, icons, figures or frames.
Preserve the existing map camera, proportions and lighting. Newly painted surfaces must be smooth and clean, not grainy, cracked, veiny or noisy. Broad stone architectural bands and softly carved relief have consistent thickness and no wobbles. Do not add extra seams or decorative symbols beyond the canonical layout. The transparent boundaries must disappear; do not draw borders or straight seams at them. No characters, buildings, foliage or props. No text, watermark, UI, frame, transparent output, zoom, rescale, rotation or camera change. Highest visual finish available through the host.'''
(P/'prompt.txt').write_text(prompt,encoding='utf-8')
payload={'prompt':prompt,'referenced_image_paths':[str(x) for x in refs],'transparent_background':False}
write(P/'request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'patch':'r01_c01','tile':'r08_c10','globalCropLTRB':world,'tileLocalCropLTRB':window,'knownPixels':int((aa[:,:,3]==255).sum()),'missingPixels':int((aa[:,:,3]==0).sum()),'payload':payload,'configSnapshot':read(ROOT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'size':None},'referenceRoles':['edit target: exact native ownership context','reference-only canonical geometry','approved primary art style']})
write(P/'source-checkpoint-input.json',cp)
write(P/'preparation.json',{'taskLocalSourceCheckpoint':ref(T/'source-checkpoint.json'),'savedCheckpoint':ref(P/'source-checkpoint-input.json'),'references':[ref(x) for x in refs],'nativeInputs':inputs,'master':ref(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'topLeftMissingSource':'No r07_c09 owned source; top-left115x115 remains transparent in input and is unverified future context after generation.'})
for img,sources,op in [(P/'context.png',inputs,'Exact native ownership crops at shared world coordinates; unknown alpha remains transparent'),(P/'layout-reference-only.png',[ref(master)],'Reference only enlarged canonical crop; forbidden as finished pixels')]:write(str(img)+'.generation.json',{'file':str(img),'sha256':sha(img),'derivedFrom':sources,'operation':op,'newModelCalls':0,'actualModel':None,'actualQuality':None})
print(json.dumps({'directory':str(P),'checkpoint':cp['version'],'knownPixels':int((aa[:,:,3]==255).sum()),'missingPixels':int((aa[:,:,3]==0).sum())}))
